# -*- coding: utf-8 -*-
"""
生成球员库数据（用于模型训练）。
基于真实足球世界的分布特征生成 ~1800 名球员，覆盖各位置、年龄段与能力水平。

用法：python scripts/generate_pool.py [数量]
"""

from __future__ import annotations

import os
import random
import sys

import numpy as np
import pandas as pd

# 位置能力原型：六维能力 (pace, shooting, passing, dribbling, defending, physical) 的均值
POSITION_PROFILE = {
    "GK": {"weight": 0.08, "skills": [42, 26, 52, 42, 84, 80], "sigma": 5},
    "CB": {"weight": 0.16, "skills": [64, 34, 64, 56, 86, 84], "sigma": 6},
    "FB": {"weight": 0.12, "skills": [82, 48, 72, 74, 78, 76], "sigma": 6},
    "CM": {"weight": 0.18, "skills": [66, 58, 82, 78, 70, 76], "sigma": 6},
    "CAM": {"weight": 0.12, "skills": [74, 70, 84, 84, 54, 68], "sigma": 6},
    "W": {"weight": 0.16, "skills": [87, 70, 74, 86, 42, 66], "sigma": 6},
    "ST": {"weight": 0.18, "skills": [80, 84, 68, 78, 38, 78], "sigma": 6},
}

# 位置在综合评分中的权重（overall 由六维加权）
OVERALL_WEIGHT = {
    "GK": [0.02, 0.02, 0.12, 0.08, 0.58, 0.18],
    "CB": [0.10, 0.03, 0.18, 0.12, 0.37, 0.20],
    "FB": [0.22, 0.06, 0.20, 0.18, 0.20, 0.14],
    "CM": [0.12, 0.10, 0.28, 0.18, 0.18, 0.14],
    "CAM": [0.10, 0.16, 0.28, 0.28, 0.08, 0.10],
    "W": [0.28, 0.20, 0.16, 0.26, 0.04, 0.06],
    "ST": [0.18, 0.32, 0.12, 0.18, 0.04, 0.16],
}

NATIONS = ["法国", "英格兰", "西班牙", "德国", "意大利", "巴西", "阿根廷", "葡萄牙",
           "荷兰", "比利时", "乌拉圭", "克罗地亚", "塞内加尔", "日本", "韩国", "尼日利亚",
           "摩洛哥", "哥伦比亚", "丹麦", "挪威", "奥地利", "墨西哥", "美国", "波兰"]
LEAGUES = ["英超", "西甲", "德甲", "意甲", "法甲", "荷甲", "葡超", "沙特联", "美职联"]
CLUB_POOL = {
    "英超": ["曼城", "阿森纳", "利物浦", "曼联", "切尔西", "热刺", "纽卡斯尔", "阿斯顿维拉", "布莱顿", "西汉姆联"],
    "西甲": ["皇家马德里", "巴塞罗那", "马德里竞技", "皇家社会", "毕尔巴鄂竞技", "塞维利亚", "比利亚雷亚尔", "瓦伦西亚"],
    "德甲": ["拜仁慕尼黑", "多特蒙德", "勒沃库森", "莱比锡红牛", "法兰克福", "沃尔夫斯堡", "斯图加特", "门兴"],
    "意甲": ["国际米兰", "AC米兰", "尤文图斯", "那不勒斯", "罗马", "亚特兰大", "拉齐奥", "佛罗伦萨"],
    "法甲": ["巴黎圣日耳曼", "马赛", "摩纳哥", "里尔", "里昂", "尼斯", "朗斯", "雷恩"],
    "荷甲": ["阿贾克斯", "埃因霍温", "费耶诺德", "阿尔克马尔"],
    "葡超": ["本菲卡", "波尔图", "葡萄牙体育", "布拉加"],
    "沙特联": ["利雅得新月", "利雅得胜利", "吉达联合", "吉达国民"],
    "美职联": ["迈阿密国际", "洛杉矶FC", "纽约红牛", "西雅图海湾人"],
}
FOOTS = ["右", "左"]


def weighted_age(random) -> int:
    """年龄分布：16-38，高峰期 22-28。"""
    while True:
        age = int(np.random.default_rng().normal(24, 4.5))
        if 16 <= age <= 38:
            return age


def gen_market_value(rng, overall: float, age: int) -> int:
    """身价（欧元）：随能力指数上升，年轻加成、老将衰减。"""
    young_bonus = max(0, (24 - age)) * 0.012
    old_penalty = max(0, (age - 27)) * 0.010
    log_val = 3.0 + 0.058 * overall + young_bonus - old_penalty + rng.normal(0, 0.18)
    return int(round(10 ** min(log_val, 9.2)))


def gen_potential(rng, overall: float, age: int) -> int:
    """潜力：年轻球员潜力高于当前能力。"""
    growth = max(0, (22 - age)) * 0.85 + (5.0 if age < 20 else 0.0)
    potential = overall + growth + rng.normal(0, 1.2)
    return int(round(min(99, max(overall, potential))))


def gen_player(rng, pos: str, profile: dict) -> dict:
    """生成一名球员。"""
    skills_mean = np.array(profile["skills"], dtype=float)
    sigma = profile["sigma"]
    skills = np.clip(rng.normal(skills_mean, sigma), 18, 99).round(0).astype(int)
    overall = int(round(np.dot(skills, np.array(OVERALL_WEIGHT[pos]))))
    overall = min(95, max(45, overall))
    age = weighted_age(rng)
    potential = gen_potential(rng, overall, age)

    league = rng.choice(LEAGUES, p=[0.22, 0.20, 0.14, 0.14, 0.12, 0.05, 0.05, 0.04, 0.04])
    club = rng.choice(CLUB_POOL[league])
    nationality = rng.choice(NATIONS)
    foot = rng.choice(FOOTS)
    height = int(rng.normal(178 if pos != "GK" else 189, 6))
    weight = int(rng.normal(74 if pos != "GK" else 86, 5))

    # 赛季表现：前锋进球多，组织者助攻多
    if pos in ("ST", "W", "CF"):
        goals = max(0, int(rng.normal(overall / 10 * 1.6, 6)))
        assists = max(0, int(rng.normal(overall / 30, 3)))
    elif pos in ("CAM", "CM"):
        goals = max(0, int(rng.normal(overall / 30, 4)))
        assists = max(0, int(rng.normal(overall / 10, 4)))
    else:
        goals = max(0, int(rng.normal(2, 2)))
        assists = max(0, int(rng.normal(overall / 20, 3)))

    first = ["马丁", "卢卡斯", "加布里埃尔", "马特奥", "尼古拉斯", "蒂亚戈", "安德烈", "路易斯",
             "哈里", "杰克", "奥利弗", "马库斯", "莱昂", "费利克斯", "达尼", "拉斐尔"]
    last = ["席尔瓦", "桑托斯", "费尔南德斯", "戈麦斯", "罗德里格斯", "穆勒", "约翰逊", "威廉姆斯",
            "科斯塔", "马丁内斯", "洛佩斯", "加西亚", "萨拉赫-阿明", "范德伯格", "科瓦奇", "奥孔"]
    name = f"{rng.choice(first)} {rng.choice(last)}"

    return {
        "name": name,
        "nationality": nationality,
        "age": age,
        "position": pos,
        "overall": overall,
        "potential": potential,
        "pace": int(skills[0]),
        "shooting": int(skills[1]),
        "passing": int(skills[2]),
        "dribbling": int(skills[3]),
        "defending": int(skills[4]),
        "physical": int(skills[5]),
        "market_value": gen_market_value(rng, overall, age),
        "club": club,
        "league": league,
        "foot": foot,
        "height": height,
        "weight": weight,
        "season_goals": goals,
        "season_assists": assists,
    }


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1800
    rng = np.random.default_rng(42)

    positions = list(POSITION_PROFILE.keys())
    weights = [p["weight"] for p in POSITION_PROFILE.values()]
    pool = [gen_player(rng, pos, POSITION_PROFILE[pos]) for pos in rng.choice(positions, size=count, p=weights)]

    df = pd.DataFrame(pool)
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    out_path = os.path.normpath(os.path.join(out_dir, "player_pool.csv"))
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"已生成 {len(df)} 名球员 -> {out_path}")
    print("位置分布:\n", df["position"].value_counts().to_string())


if __name__ == "__main__":
    main()
