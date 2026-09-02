"""数据加载：球员库 + 内置球星库。"""
from __future__ import annotations

import subprocess
import sys

import pandas as pd

from backend.config import DATA_DIR, SCRIPTS_DIR

STAR_FILE = DATA_DIR / "star_players.csv"
POOL_FILE = DATA_DIR / "player_pool.csv"

# 字段顺序统一
COLUMNS = [
    "name", "nationality", "age", "position", "overall", "potential",
    "pace", "shooting", "passing", "dribbling", "defending", "physical",
    "market_value", "club", "league", "foot", "height", "weight",
    "season_goals", "season_assists",
]


def _ensure_pool() -> None:
    """若球员库不存在则先生成。"""
    if not POOL_FILE.exists():
        print("球员库不存在，正在生成...")
        subprocess.run([sys.executable, str(SCRIPTS_DIR / "generate_pool.py")], check=True)


def load_star_players() -> pd.DataFrame:
    """加载内置知名球星测试数据。"""
    df = pd.read_csv(STAR_FILE, encoding="utf-8-sig")
    # 补齐球星数据中缺失的可选字段
    df["height"] = df.get("height", pd.Series(178, index=df.index)).fillna(178).astype(int)
    df["weight"] = df.get("weight", pd.Series(75, index=df.index)).fillna(75).astype(int)
    return df[COLUMNS]


def load_player_pool() -> pd.DataFrame:
    """加载/生成球员库（模型训练用）。"""
    _ensure_pool()
    df = pd.read_csv(POOL_FILE, encoding="utf-8-sig")
    df["height"] = df.get("height", pd.Series(178, index=df.index)).fillna(178).astype(int)
    df["weight"] = df.get("weight", pd.Series(75, index=df.index)).fillna(75).astype(int)
    return df[COLUMNS]


def load_all_players() -> pd.DataFrame:
    """球员库 + 球星库合并（按名字去重，球星优先保留）。"""
    pool = load_player_pool()
    stars = load_star_players()
    stars = stars[~stars["name"].isin(pool["name"])]
    return pd.concat([pool, stars], ignore_index=True)


def get_player_by_name(df: pd.DataFrame, name: str) -> pd.DataFrame | None:
    """按名字精确/模糊查找球员。"""
    hit = df[df["name"].str.lower() == name.strip().lower()]
    if hit.empty:
        hit = df[df["name"].str.contains(name.strip(), case=False, na=False)]
    return hit.head(1) if not hit.empty else None
