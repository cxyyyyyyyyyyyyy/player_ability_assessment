"""潜力预测模型（随机森林回归）+ 成长曲线。"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, train_test_split

from backend.config import POSITION_MAP, RANDOM_STATE, SKILL_COLUMNS

MAIN_POSITIONS = ["GK", "CB", "FB", "CM", "CAM", "W", "ST"]


class PotentialModel:
    """以年龄、当前能力、位置为特征，预测球员潜力峰值。"""

    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=200, max_depth=12, min_samples_leaf=2, random_state=RANDOM_STATE
        )
        self.rmse: float | None = None
        self.r2: float | None = None
        self.cv_rmse: float | None = None
        self.feature_importance: dict | None = None

    # ---------- 特征构建 ----------
    @staticmethod
    def _main_position(pos: str) -> str:
        return POSITION_MAP.get(pos, pos if pos in MAIN_POSITIONS else "ST")

    def _feature(self, row: dict) -> list[float]:
        pos = self._main_position(str(row.get("position", "ST")))
        base = [
            float(row.get("age", 23)),
            float(row.get("overall", 70)),
        ] + [float(row.get(c, 50)) for c in SKILL_COLUMNS]
        onehot = [1.0 if pos == p else 0.0 for p in MAIN_POSITIONS]
        return base + onehot

    # ---------- 训练 ----------
    def fit(self, df: pd.DataFrame) -> "PotentialModel":
        X = np.array([self._feature(r) for r in df.to_dict("records")])
        y = df["potential"].values.astype(float)
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)
        self.model.fit(Xtr, ytr)
        pred = self.model.predict(Xte)
        self.rmse = float(np.sqrt(np.mean((pred - yte) ** 2)))
        self.r2 = float(self.model.score(Xte, yte))

        # 特征重要性（age + overall + 六维能力 + 位置 one-hot）
        names = ["age", "overall"] + SKILL_COLUMNS + MAIN_POSITIONS
        self.feature_importance = dict(zip(names, self.model.feature_importances_.round(4)))

        # 5 折交叉验证：评估模型泛化能力
        scores = cross_val_score(self.model, X, y, cv=5, scoring="neg_root_mean_squared_error")
        self.cv_rmse = float(-scores.mean())
        return self

    # ---------- 预测 ----------
    def predict_peak(self, row: dict) -> float:
        x = np.array([self._feature(row)])
        val = float(self.model.predict(x)[0])
        return float(np.clip(val, 0, 99))

    def growth_curve(self, row: dict) -> list[dict]:
        """构造 16~36 岁的年龄-能力成长曲线。"""
        age = int(row.get("age", 23))
        overall = float(row.get("overall", 70))
        peak = self.predict_peak(row)

        if age < 27:
            peak_age = age + max(1.0, (22 - age) * 0.6)
        else:
            peak_age = age
        peak_age = min(31, peak_age)

        ages = list(range(16, 37))
        curve = []
        for a in ages:
            if a <= peak_age:
                span = max(1.0, peak_age - age)
                t = (a - age) / span
                val = overall if t <= 0 else overall + (peak - overall) * (1 - np.exp(-3 * t))
            else:
                val = peak - 0.45 * (a - peak_age)
            curve.append({"age": a, "value": round(float(np.clip(val, 20, 99)), 1)})
        return curve

    def potential_percentile(self, row: dict, df: pd.DataFrame) -> float:
        """预测潜力在球员库中的百分位。"""
        peak = self.predict_peak(row)
        all_peaks = df["potential"].values.astype(float)
        return float((all_peaks <= peak).mean() * 100)
