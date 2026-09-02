# -*- coding: utf-8 -*-
"""
从 database.sqlite（European Soccer Database）提取真实球员数据，
转换为系统 player_pool.csv 同格式，用于训练聚类 / 潜力预测模型。

字段映射：
  name       <- Player.player_name
  age        <- 2016 - birthday.year（数据截止 2016 赛季）
  position   <- 由六维能力与位置原型匹配度推断（GK 用门将专属属性优先判定）
  overall    <- Player_Attributes.overall_rating（每人最新一条）
  potential  <- Player_Attributes.potential
  pace       <- avg(acceleration, sprint_speed)
  shooting   <- avg(finishing, long_shots, shot_power)
  passing    <- avg(short_passing, long_passing, vision)
  dribbling  <- avg(dribbling, ball_control)
  defending  <- avg(marking, standing_tackle, sliding_tackle, interceptions)
  physical   <- avg(stamina, strength, jumping)
  foot       <- preferred_foot
  height     <- 英寸 -> 厘米
  weight     <- 磅 -> 公斤
  club       <- 出场次数最多的球队
  league     <- 该球队所在联赛（映射为中文）
  nationality<- 联赛所在国家（数据库无国籍字段，近似）
  market_value <- 启发式（评分 + 年龄）
  season_goals <- 解析 Match.goal JSON 统计真实进球
  season_assists <- 启发式（数据库无助攻数据）

用法：python scripts/extract_from_db.py [输出行数上限]
"""
from __future__ import annotations

import os
import re
import sys
from collections import Counter

import numpy as np
import pandas as pd
import sqlite3

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DB_PATH = os.path.join(BASE_DIR, "database.sqlite")
OUT_PATH = os.path.join(BASE_DIR, "data", "player_pool.csv")
BAK_PATH = os.path.join(BASE_DIR, "data", "player_pool_synthetic.csv.bak")

REFERENCE_YEAR = 2016  # 数据库最后一个赛季为 2015/2016

# 主位置六维能力原型（与 backend.models.similarity 一致）
POSITION_PROFILE = {
    "GK": [42, 26, 52, 42, 84, 80],
    "CB": [64, 34, 64, 56, 86, 84],
    "FB": [82, 48, 72, 74, 78, 76],
    "CM": [66, 58, 82, 78, 70, 76],
    "CAM": [74, 70, 84, 84, 54, 68],
    "W": [87, 70, 74, 86, 42, 66],
    "ST": [80, 84, 68, 78, 38, 78],
}

# 联赛 -> 中文名 / 国家
LEAGUE_CN = {
    "Belgium Jupiler League": ("比利时甲级联赛", "比利时"),
    "England Premier League": ("英格兰超级联赛", "英格兰"),
    "France Ligue 1": ("法国甲级联赛", "法国"),
    "Germany 1. Bundesliga": ("德国甲级联赛", "德国"),
    "Italy Serie A": ("意大利甲级联赛", "意大利"),
    "Netherlands Eredivisie": ("荷兰甲级联赛", "荷兰"),
    "Poland Ekstraklasa": ("波兰甲级联赛", "波兰"),
    "Portugal Liga ZON Sagres": ("葡萄牙超级联赛", "葡萄牙"),
    "Scotland Premier League": ("苏格兰超级联赛", "苏格兰"),
    "Spain LIGA BBVA": ("西班牙甲级联赛", "西班牙"),
    "Switzerland Super League": ("瑞士超级联赛", "瑞士"),
}
FOOT_CN = {"left": "左", "right": "右"}

COLUMNS = [
    "name", "nationality", "age", "position", "overall", "potential",
    "pace", "shooting", "passing", "dribbling", "defending", "physical",
    "market_value", "club", "league", "foot", "height", "weight",
    "season_goals", "season_assists",
]


def infer_position(attrs: dict) -> str:
    """GK 优先用门将专属属性判定，其余按六维与位置原型余弦相似度匹配。"""
    gk = [attrs.get("gk_reflexes"), attrs.get("gk_handling"), attrs.get("gk_diving")]
    gk = [x for x in gk if x is not None]
    if len(gk) == 3 and np.mean(gk) >= 60:
        # 门将：守门能力突出且非门将属性平庸
        non_gk = np.mean([attrs.get("pace", 0) or 0, attrs.get("dribbling", 0) or 0])
        if non_gk < 65:
            return "GK"

    v = np.array([
        attrs.get("pace", 0) or 0,
        attrs.get("shooting", 0) or 0,
        attrs.get("passing", 0) or 0,
        attrs.get("dribbling", 0) or 0,
        attrs.get("defending", 0) or 0,
        attrs.get("physical", 0) or 0,
    ], dtype=float)
    if np.linalg.norm(v) == 0:
        return "CM"
    best, best_sim = "CM", -1.0
    for pos, proto in POSITION_PROFILE.items():
        p = np.array(proto, dtype=float)
        sim = float(np.dot(v, p) / (np.linalg.norm(v) * np.linalg.norm(p)))
        if sim > best_sim:
            best, best_sim = pos, sim
    return best


def parse_goal_events(goal_xml: str | None, player_ids: set[int]):
    """解析 Match.goal XML，返回 (进球数, 助攻数)。player1 为进球者，player2 为助攻者。"""
    if not goal_xml or "<type>goal</type>" not in goal_xml:
        return 0, 0
    goals = assists = 0
    for block in re.findall(r"<value>(.*?)</value>", goal_xml):
        if "<type>goal</type>" not in block:
            continue
        m1 = re.search(r"<player1>(\d+)</player1>", block)
        m2 = re.search(r"<player2>(\d+)</player2>", block)
        if m1 and int(m1.group(1)) in player_ids:
            goals += 1
        if m2 and int(m2.group(1)) in player_ids:
            assists += 1
    return goals, assists


def gen_market_value(rng, overall: float, age: int) -> int:
    """身价启发式（与 generate_pool 一致）：随能力指数上升，年轻加成、老将衰减。"""
    young_bonus = max(0, (24 - age)) * 0.012
    old_penalty = max(0, (age - 27)) * 0.010
    log_val = 3.0 + 0.058 * overall + young_bonus - old_penalty + rng.normal(0, 0.18)
    return int(round(10 ** min(log_val, 9.2)))


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    print("连接数据库:", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=OFF")
    cur = conn.cursor()

    # 1. 球员基本信息
    cur.execute("SELECT player_api_id, player_name, birthday, height, weight FROM Player")
    players = {}
    for pid, name, birthday, h_in, w_lb in cur.fetchall():
        if not pid or not name:
            continue
        birth_year = int(birthday[:4]) if birthday and birthday[:4].isdigit() else None
        age = None if birth_year is None else min(45, max(16, REFERENCE_YEAR - birth_year))
        height = round(h_in) if h_in else 178                  # 已是厘米
        weight = round(w_lb * 0.4536) if w_lb else 75          # 磅 -> 公斤
        players[pid] = {
            "name": name, "age": age, "height": height, "weight": weight,
        }
    print("Player 表:", len(players), "人")

    # 2. 每人最新能力快照
    cur.execute("""
        SELECT player_api_id, date, overall_rating, potential, preferred_foot,
               acceleration, sprint_speed, agility,
               finishing, long_shots, shot_power,
               short_passing, long_passing, vision,
               dribbling, ball_control,
               marking, standing_tackle, sliding_tackle, interceptions,
               stamina, strength, jumping,
               gk_diving, gk_handling, gk_reflexes
        FROM Player_Attributes
        WHERE player_api_id IS NOT NULL
        ORDER BY player_api_id, date
    """)
    latest: dict[int, dict] = {}
    for row in cur.fetchall():
        pid = row[0]
        rec = {
            "overall": row[2], "potential": row[3], "foot": row[4],
            "pace": (row[5] + row[6]) / 2 if (row[5] is not None and row[6] is not None) else None,
            "shooting": (row[8] + row[9] + row[10]) / 3 if all(x is not None for x in (row[8], row[9], row[10])) else None,
            "passing": (row[11] + row[12] + row[13]) / 3 if all(x is not None for x in (row[11], row[12], row[13])) else None,
            "dribbling": (row[14] + row[15]) / 2 if (row[14] is not None and row[15] is not None) else None,
            "defending": (row[16] + row[17] + row[18] + row[19]) / 4 if all(x is not None for x in (row[16], row[17], row[18], row[19])) else None,
            "physical": (row[20] + row[21] + row[22]) / 3 if all(x is not None for x in (row[20], row[21], row[22])) else None,
            "gk_reflexes": row[24], "gk_handling": row[23], "gk_diving": row[25],
        }
        latest[pid] = rec   # ORDER BY date，后者即最新
    print("Player_Attributes 最新快照:", len(latest), "条")

    # 3. 球员 -> 俱乐部 / 联赛（出场次数统计）
    cur.execute("""
        SELECT home_team_api_id, away_team_api_id, league_id,
               home_player_1, home_player_2, home_player_3, home_player_4, home_player_5,
               home_player_6, home_player_7, home_player_8, home_player_9, home_player_10, home_player_11,
               away_player_1, away_player_2, away_player_3, away_player_4, away_player_5,
               away_player_6, away_player_7, away_player_8, away_player_9, away_player_10, away_player_11
        FROM Match
    """)
    team_counter: dict[int, Counter] = {}
    league_of_team: dict[int, Counter] = {}
    for row in cur.fetchall():
        home_team, away_team, league_id = row[0], row[1], row[2]
        if league_id:
            league_of_team.setdefault(home_team, Counter())[league_id] += 1
            league_of_team.setdefault(away_team, Counter())[league_id] += 1
        for pid in row[3:25]:
            if pid is None:
                continue
            pid = int(pid)
            for team in (home_team, away_team):
                if team:
                    team_counter.setdefault(pid, Counter())[int(team)] += 1
    print("Match 表球队/球员关系扫描完成")

    # 4. 联赛 id -> 中文
    cur.execute("SELECT id, name FROM League")
    league_names = {r[0]: r[1] for r in cur.fetchall()}

    # 5. 统计真实进球/助攻（Match.goal，XML 格式）
    cur.execute("SELECT goal FROM Match")
    valid_ids = {pid for pid in latest if pid in players}
    goal_counter = Counter()
    assist_counter = Counter()
    for (goal_xml,) in cur.fetchall():
        if not goal_xml or "<type>goal</type>" not in goal_xml:
            continue
        for block in re.findall(r"<value>(.*?)</value>", goal_xml):
            if "<type>goal</type>" not in block:
                continue
            m1 = re.search(r"<player1>(\d+)</player1>", block)
            m2 = re.search(r"<player2>(\d+)</player2>", block)
            if m1 and int(m1.group(1)) in valid_ids:
                goal_counter[int(m1.group(1))] += 1
            if m2 and int(m2.group(1)) in valid_ids:
                assist_counter[int(m2.group(1))] += 1
    print("Match.goal 进球/助攻统计完成")

    conn.close()

    # 6. 组装球员记录
    rng = np.random.default_rng(42)
    rows = []
    for pid, attrs in latest.items():
        if pid not in players:
            continue
        if not attrs["overall"] or not attrs["potential"]:
            continue
        if attrs["pace"] is None or attrs["physical"] is None:
            continue
        base = players[pid]
        if base["age"] is None:
            continue

        # 位置推断
        position = infer_position(attrs)
        # 俱乐部 / 联赛 / 国籍
        counter = team_counter.get(pid)
        if counter:
            club_id = counter.most_common(1)[0][0]
            league_id = league_of_team.get(club_id)
            league_cn = league_names.get(league_id.most_common(1)[0][0], "") if league_id else ""
            club = club_id  # 用球队 api id 占位，下面换成真实队名
        else:
            club, league_cn = 0, ""
        rows.append({
            "pid": pid,
            "name": base["name"],
            "age": base["age"],
            "height": base["height"],
            "weight": base["weight"],
            "position": position,
            "overall": int(round(attrs["overall"])),
            "potential": int(round(attrs["potential"])),
            "pace": int(round(attrs["pace"])),
            "shooting": int(round(attrs["shooting"] or 0)),
            "passing": int(round(attrs["passing"] or 0)),
            "dribbling": int(round(attrs["dribbling"] or 0)),
            "defending": int(round(attrs["defending"] or 0)),
            "physical": int(round(attrs["physical"])),
            "foot": FOOT_CN.get(str(attrs["foot"]).lower(), "右"),
            "club_id": club,
            "league": league_cn,
            "goals": goal_counter.get(pid, 0),
            "assists": assist_counter.get(pid, 0),
        })

    if limit:
        rows = rows[:limit]
    print("组装完成:", len(rows), "名真实球员")

    # 7. 补齐俱乐部名称、联赛中文、国籍、身价、助攻
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT team_api_id, team_long_name FROM Team")
    team_names = {r[0]: r[1] for r in cur.fetchall()}
    conn.close()

    df = pd.DataFrame(rows)
    df["club"] = df["club_id"].map(team_names).fillna("自由球员")
    EN_TO_CN = {en: cn for en, (cn, _) in LEAGUE_CN.items()}
    CN_TO_COUNTRY = {cn: country for cn, country in LEAGUE_CN.values()}
    df["league"] = df["league"].map(EN_TO_CN).fillna(df["league"])
    df["nationality"] = df["league"].map(CN_TO_COUNTRY).fillna("国际")
    df["market_value"] = [gen_market_value(rng, o, a) for o, a in zip(df["overall"], df["age"])]

    df["season_goals"] = df["goals"]
    df["season_assists"] = df["assists"]
    df = df.drop(columns=["goals", "assists", "club_id"])

    # 8. 位置细节：推断出的主位置再映射回系统支持的细分位置
    df = df[COLUMNS]
    df = df.drop_duplicates(subset=["name"]).sort_values("overall", ascending=False).reset_index(drop=True)

    # 备份原模拟数据
    if os.path.exists(OUT_PATH) and not os.path.exists(BAK_PATH):
        os.rename(OUT_PATH, BAK_PATH)
        print("原模拟数据已备份 ->", BAK_PATH)

    df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print("已生成真实球员库 ->", OUT_PATH)
    print("规模:", len(df))
    print("\n位置分布:\n", df["position"].value_counts().to_string())
    print("\n联赛分布:\n", df["league"].value_counts().head(12).to_string())
    print("\n评分分布:\n", pd.cut(df["overall"], bins=[0, 40, 50, 60, 70, 80, 90, 100]).value_counts().sort_index().to_string())
    print("\n样例（前 10 名）:")
    print(df.head(10)[["name", "nationality", "age", "position", "overall", "potential", "club", "league"]].to_string(index=False))


if __name__ == "__main__":
    main()
