# -*- coding: utf-8 -*-
import sqlite3
con = sqlite3.connect(r"d:\chxy wants to study hard\short semester\task\球员能力评估系统\database.sqlite")
cur = con.cursor()

print("=== Player_Attributes 表字段 ===")
for r in cur.execute("PRAGMA table_info(Player_Attributes)"):
    print("  %-25s %s" % (r[1], r[2]))

print()
print("=== 示例：Aaron Appindangoye 的能力数据 ===")
for r in cur.execute(
    "SELECT overall_rating, potential, acceleration, sprint_speed, finishing, "
    "short_passing, long_passing, dribbling, ball_control, marking, standing_tackle, "
    "sliding_tackle, interceptions, stamina, strength FROM Player_Attributes "
    "WHERE player_api_id=(SELECT player_api_id FROM Player WHERE player_name='Aaron Appindangoye') LIMIT 3"):
    print("  overall=%s potential=%s 速度acc=%s spr=%s 射门fin=%s 传球短=%s 长=%s "
          "盘带dri=%s 控球=%s 防守mark=%s st_tackle=%s sl_tackle=%s 拦截=%s 体能stam=%s 力量=%s" % r)

con.close()
print()
print("完成")
