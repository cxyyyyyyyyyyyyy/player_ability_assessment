"""Pydantic 数据模型。"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, model_validator


class PlayerInput(BaseModel):
    """球员输入信息（自定义评估）。

    校验策略：字段级约束尽量宽松（避免前端空值/非法值直接 422），
    再由 _sanitize 把不合理取值修正为安全默认值。
    """

    name: str = "自定义球员"
    nationality: str = ""
    age: int = Field(default=23, ge=-1000000)
    position: str = "ST"  # GK/CB/FB/CM/CAM/W/ST/CF/RB/RW/LW...
    overall: int = Field(default=75, ge=-1000000)
    potential: Optional[int] = Field(default=None, ge=-1000000)
    pace: int = Field(default=70, ge=-1000000)
    shooting: int = Field(default=70, ge=-1000000)
    passing: int = Field(default=70, ge=-1000000)
    dribbling: int = Field(default=70, ge=-1000000)
    defending: int = Field(default=70, ge=-1000000)
    physical: int = Field(default=70, ge=-1000000)
    market_value: Optional[int] = Field(default=None, ge=-1000000)
    club: str = ""
    league: str = ""
    foot: str = ""
    height: Optional[int] = None
    weight: Optional[int] = None
    season_goals: int = 0
    season_assists: int = 0

    @model_validator(mode="after")
    def _sanitize(self):
        """把 0/空/越界等不合理取值修正为安全默认值。"""
        if not self.position or len(self.position) > 4:
            self.position = "ST"
        if not (15 <= self.age <= 45):
            self.age = 23
        if not (40 <= self.overall <= 99):
            self.overall = 75
        for k in ("pace", "shooting", "passing", "dribbling", "defending", "physical"):
            v = getattr(self, k)
            if not (0 <= v <= 99):
                setattr(self, k, 70)
        if self.potential is not None and not (0 <= self.potential <= 99):
            self.potential = None
        if self.market_value is None or self.market_value < 0:
            self.market_value = 0
        return self


class EvaluateRequest(BaseModel):
    """评估请求：二者选一。"""

    name: Optional[str] = None          # 球员库/球星库中的名字（优先）
    player: Optional[PlayerInput] = None  # 自定义球员信息


class PlayerOut(BaseModel):
    """球员基本信息输出。"""

    name: str
    nationality: str
    age: int
    position: str
    overall: int
    potential: int
    pace: int
    shooting: int
    passing: int
    dribbling: int
    defending: int
    physical: int
    market_value: int
    club: str
    league: str
    foot: str
    height: int
    weight: int
    season_goals: int
    season_assists: int
