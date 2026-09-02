# -*- coding: utf-8 -*-
"""扩充球星库：保留现有最新球星 + 从 player_pool 补充高分真实球员。"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
STAR_PATH = BASE / "data" / "star_players.csv"
POOL_PATH = BASE / "data" / "player_pool.csv"

# 读取现有球星库 + 球员库
stars = pd.read_csv(STAR_PATH, encoding="utf-8-sig")
pool = pd.read_csv(POOL_PATH, encoding="utf-8-sig")

# 从球员库筛选 overall >= 82 的高分球员补充进来（排除已在球星库中的）
additions = pool[(pool["overall"] >= 82) & (~pool["name"].isin(stars["name"]))].copy()

# 只保留 star_players.csv 需要的字段
keep_cols = ["name", "nationality", "age", "position", "overall", "potential",
             "pace", "shooting", "passing", "dribbling", "defending", "physical",
             "market_value", "club", "league", "foot", "season_goals", "season_assists"]
additions = additions[keep_cols]

# 合并：球星优先（去重时保留 stars 里的）
merged = pd.concat([stars, additions], ignore_index=True)
merged = merged.drop_duplicates(subset=["name"], keep="first")
merged = merged.sort_values("overall", ascending=False).reset_index(drop=True)

merged.to_csv(STAR_PATH, index=False, encoding="utf-8-sig")
print(f"球星库已更新: {len(stars)} -> {len(merged)} 人")
print(f"新增 {len(additions)} 人 (overall>=82, 去重后保留 {len(merged)-len(stars)} 人)")
