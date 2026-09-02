"""全局配置。"""
from __future__ import annotations

import os
from pathlib import Path

# 路径
BASE_DIR = Path(__file__).resolve().parents[1]          # 项目根目录
DATA_DIR = BASE_DIR / "data"
SCRIPTS_DIR = BASE_DIR / "scripts"

# 数据与模型参数
POOL_SIZE = 1800            # 球员库规模（首次运行时生成）
K_CLUSTERS = 5              # 风格聚类个数
N_BENCHMARKS = 3            # 对标球员数量
RANDOM_STATE = 42

# 六维能力顺序（全局统一）
SKILL_COLUMNS = ["pace", "shooting", "passing", "dribbling", "defending", "physical"]
# 聚类特征（六维 + 综合评分）
FEATURES = SKILL_COLUMNS + ["overall"]

# 细位置 → 主位置（用于聚类/建模/适配度比较）
POSITION_MAP = {
    "GK": "GK", "CB": "CB", "SW": "CB",
    "LB": "FB", "RB": "FB", "LWB": "FB", "RWB": "FB",
    "CDM": "CM", "CM": "CM",
    "CAM": "CAM", "LM": "W", "RM": "W", "LW": "W", "RW": "W", "LF": "W", "RF": "W",
    "CF": "ST", "ST": "ST", "SS": "ST",
}

# 可选：LLM 增强建议（配置后 Agent 会生成更自然的报告文本，未配置则使用规则引擎）
LLM_API_KEY = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

# ---- 应用元信息 ----
APP_NAME = "绿茵慧眼 · 球员能力评估系统"
APP_VERSION = "3.0.0"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
