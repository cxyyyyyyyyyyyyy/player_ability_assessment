"""相似度匹配：位置适配、对标球员。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backend.config import N_BENCHMARKS, SKILL_COLUMNS

# 主位置六维能力原型（与数据生成脚本一致）
POSITION_PROFILE = {
    "GK": [42, 26, 52, 42, 84, 80],
    "CB": [64, 34, 64, 56, 86, 84],
    "FB": [82, 48, 72, 74, 78, 76],
    "CM": [66, 58, 82, 78, 70, 76],
    "CAM": [74, 70, 84, 84, 54, 68],
    "W": [87, 70, 74, 86, 42, 66],
    "ST": [80, 84, 68, 78, 38, 78],
}


def skill_vector(row: dict) -> np.ndarray:
    return np.array([row.get(c, 0) for c in SKILL_COLUMNS], dtype=float)


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def position_match_detail(row: dict) -> list[dict]:
    """球员能力结构与各主位置的适配度（按降序）。"""
    v = skill_vector(row)
    out = []
    for pos, proto in POSITION_PROFILE.items():
        out.append({"position": pos, "match": round(cosine_sim(v, np.array(proto)), 3)})
    out.sort(key=lambda x: x["match"], reverse=True)
    return out


def position_avg(df: pd.DataFrame) -> dict[str, dict]:
    """各主位置六维能力均值（用于训练重点对比）。"""
    from backend.config import POSITION_MAP

    result: dict[str, dict] = {}
    for pos, group in df.groupby("position"):
        main = POSITION_MAP.get(pos, pos)
        if main not in POSITION_PROFILE:
            continue
        result[main] = {c: round(float(group[c].mean()), 1) for c in SKILL_COLUMNS}
    return result


def find_benchmarks(row: dict, star_df: pd.DataFrame, top: int = N_BENCHMARKS) -> list[dict]:
    """对标球员：在知名球星库中找能力结构最相似者。"""
    v = skill_vector(row)
    scores = []
    for _, s in star_df.iterrows():
        if s["name"] == row.get("name"):
            continue
        sim = cosine_sim(v, skill_vector(s.to_dict()))
        scores.append({
            "name": str(s["name"]),
            "similarity": round(sim, 3),
            "position": str(s["position"]),
            "overall": int(s["overall"]),
            "age": int(s["age"]),
            "club": str(s["club"]),
        })
    scores.sort(key=lambda x: x["similarity"], reverse=True)
    return scores[:top]
