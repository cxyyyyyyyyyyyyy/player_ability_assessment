# -*- coding: utf-8 -*-
"""生成 3 张带完整属性的示例球员卡，供用户测试图片识别。"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.config import POSITION_MAP  # noqa: E402

FONT = "C:/Windows/Fonts/simhei.ttf"
GOLD_LIGHT = (232, 206, 150)
GOLD = (201, 164, 92)
BG = (22, 25, 35)
BG2 = (30, 34, 48)
WHITE = (235, 238, 245)
GRAY = (150, 155, 170)
LINE = (70, 75, 92)

SKILLS = ["速度", "射门", "传球", "盘带", "防守", "体能"]


def draw_card(path: Path, name_cn: str, name_en: str, overall: int, age: int,
              pos: str, height: int, weight: int, foot: str,
              skills: list[int], value_wan: int, club: str) -> None:
    W, H = 800, 1300
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # 背景渐变
    for y in range(H):
        t = y / H
        c = tuple(int(BG[i] + (BG2[i] - BG[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    d.rectangle([10, 10, W - 10, H - 10], outline=GOLD, width=4)

    f = lambda sz: ImageFont.truetype(FONT, sz)

    y = 60
    d.text((60, y), f"综合评分：{overall}", fill=GOLD_LIGHT, font=f(80)); y += 110
    d.text((60, y), name_cn, fill=WHITE, font=f(78)); y += 100
    d.text((60, y), name_en, fill=GRAY, font=f(38)); y += 60

    d.text((60, y), f"年龄：{age}    位置：{pos}", fill=WHITE, font=f(50)); y += 75
    d.text((60, y), f"身高：{height}cm    体重：{weight}kg", fill=WHITE, font=f(50)); y += 95

    d.line([(60, y), (W - 60, y)], fill=LINE, width=2); y += 25

    for cn, val in zip(SKILLS, skills):
        d.text((60, y), f"{cn}  {val}", fill=WHITE, font=f(60)); y += 80

    d.line([(60, y), (W - 60, y)], fill=LINE, width=2); y += 25

    d.text((60, y), f"俱乐部：{club}", fill=WHITE, font=f(50)); y += 75
    d.text((60, y), f"身价：{value_wan}万欧元", fill=WHITE, font=f(50))

    img.save(path)
    print(f"saved: {path}")


def main():
    out_dir = Path(__file__).resolve().parents[1] / "示例图片"
    out_dir.mkdir(exist_ok=True)
    cards = [
        ("姆巴佩", "Mbappe", 91, 24, "ST", 185, 80, "右",
         [97, 89, 80, 92, 36, 78], 18000, "皇家马德里"),
        ("德布劳内", "De Bruyne", 91, 33, "CM", 181, 70, "右",
         [76, 86, 93, 88, 64, 77], 3500, "曼城"),
        ("范迪克", "Van Dijk", 89, 33, "CB", 193, 92, "右",
         [78, 60, 71, 72, 90, 86], 2500, "利物浦"),
    ]
    for c in cards:
        draw_card(out_dir / f"示例球员卡_{c[0]}.png", *c)


if __name__ == "__main__":
    main()