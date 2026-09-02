"""OCR 图片识别服务：从球员图片中提取球员信息。

技术方案：RapidOCR（离线、CPU 可跑）识别图片文字，
再按中英文/游戏缩写关键词解析出 姓名、年龄、位置、六维能力、综合评分 等字段。
"""
from __future__ import annotations

import datetime
import io
import re

import numpy as np
from PIL import Image

from backend.config import POSITION_MAP

# ---------------- 关键词表 ----------------

# 六维能力别名（中文/英文/游戏缩写）→ 字段名
SKILL_ALIASES: dict[str, str] = {
    "速度": "pace", "pace": "pace", "spd": "pace", "pac": "pace", "速": "pace",
    "射门": "shooting", "shooting": "shooting", "射术": "shooting",
    "sho": "shooting", "shot": "shooting", "finishing": "shooting",
    "传球": "passing", "passing": "passing", "pass": "passing", "pas": "passing",
    "盘带": "dribbling", "dribbling": "dribbling", "控球": "dribbling",
    "带球": "dribbling", "dri": "dribbling",
    "防守": "defending", "defending": "defending", "def": "defending",
    "抢断": "defending", "拦截": "defending",
    "体能": "physical", "physical": "physical", "身体": "physical",
    "强壮": "physical", "phy": "physical", "strength": "physical",
}

# 中文位置 → 主位置缩写
POSITION_CN_ALIAS: dict[str, str] = {
    "门将": "GK", "守门员": "GK",
    "中后卫": "CB", "中卫": "CB",
    "边后卫": "FB", "左后卫": "FB", "右后卫": "FB", "边卫": "FB",
    "后腰": "CM", "中前卫": "CM", "中场": "CM",
    "前腰": "CAM", "攻击型中场": "CAM",
    "边锋": "W", "左边锋": "W", "右边锋": "W", "左翼": "W", "右翼": "W",
    "边前卫": "W", "左前卫": "W", "右前卫": "W",
    "前锋": "ST", "中锋": "ST", "影子前锋": "ST", "影锋": "ST",
}

# 排除关键词（判断某行是否可能是球员姓名）
_NAME_STOP = (
    list(SKILL_ALIASES)
    + list(POSITION_CN_ALIAS)
    + ["年龄", "岁", "综合", "总评", "潜力", "身价", "市值", "俱乐部", "联赛",
       "国籍", "身高", "体重", "惯用脚", "进球", "助攻", "评分", "能力", "属性",
       "age", "overall", "ovr", "rating", "potential", "pot", "club", "league",
       "nationality", "height", "weight", "market", "value", "goals", "position",
       "pos", "赛季", "头像", "姓名"]
)

_MAX_IMG_BYTES = 10 * 1024 * 1024  # 10MB


class PlayerOCR:
    """球员图片 → 球员信息。RapidOCR 引擎懒加载。"""

    def __init__(self) -> None:
        self._engine = None

    # ---------- 对外接口 ----------
    def recognize(self, image_bytes: bytes) -> dict:
        """识别球员图片，返回结构化球员信息。

        返回: {"player": {...}, "recognized": {字段: True}, "notes": [...], "raw_text": "..."}
        """
        if not image_bytes:
            raise ValueError("图片内容为空")
        if len(image_bytes) > _MAX_IMG_BYTES:
            raise ValueError("图片过大（限制 10MB）")

        engine = self._get_engine()
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"无法解析图片（支持 jpg/png 等格式）：{exc}") from exc

        # 过大图片压缩，保证检测速度与准确性
        max_side = 1800
        if max(img.size) > max_side:
            img.thumbnail((max_side, max_side), Image.LANCZOS)

        result, _elapse = engine(np.array(img))
        if not result:
            raise ValueError("图片中没有识别到文字，请换一张包含球员名称和能力的清晰图片")

        blocks = [
            {"text": str(item[1]), "box": item[0], "score": float(item[2])}
            for item in result
        ]
        player, recognized, notes = self._parse(blocks)

        raw_text = "\n".join(b["text"] for b in blocks)
        return {
            "player": player,
            "recognized": recognized,
            "notes": notes,
            "raw_text": raw_text,
        }

    # ---------- 内部实现 ----------
    def _get_engine(self):
        if self._engine is None:
            from rapidocr_onnxruntime import RapidOCR

            self._engine = RapidOCR()
        return self._engine

    def _parse(self, blocks: list[dict]) -> tuple[dict, dict, list[str]]:
        """解析 OCR 文本块 → 球员信息。"""
        # 1. 计算每块中心坐标
        for b in blocks:
            xs = [p[0] for p in b["box"]]
            ys = [p[1] for p in b["box"]]
            b["x"] = float(sum(xs)) / 4.0
            b["y"] = float(sum(ys)) / 4.0
            b["w"] = abs(max(xs) - min(xs))
            b["h"] = abs(max(ys) - min(ys))

        # 2. 按 y 聚成行，行内按 x 排序
        rows = self._group_rows(blocks)
        row_texts = []
        for r in rows:
            r["blocks"].sort(key=lambda b: b["x"])
            parts = []
            prev_right = None
            for b in r["blocks"]:
                xs = [p[0] for p in b["box"]]
                left, right = min(xs), max(xs)
                if prev_right is not None and left - prev_right > 8:
                    parts.append(" ")
                parts.append(b["text"])
                prev_right = right
            r["text"] = "".join(parts).strip()
            row_texts.append(r["text"])

        # 3. 解析字段
        player: dict = {
            "name": "自定义球员",
            "nationality": "",
            "age": 23,
            "position": "ST",
            "overall": 75,
            "potential": None,
            "pace": 70, "shooting": 70, "passing": 70,
            "dribbling": 70, "defending": 70, "physical": 70,
            "market_value": None,
            "club": "", "league": "", "foot": "",
            "height": None, "weight": None,
            "season_goals": 0, "season_assists": 0,
        }
        recognized: dict[str, bool] = {}
        notes: list[str] = []

        # 3.1 六维能力（先行内匹配，再尝试"标签行 + 下一行数字"）
        aliases = sorted(SKILL_ALIASES.items(), key=lambda kv: -len(kv[0]))
        for row_text in row_texts:
            for alias, field in aliases:
                if field in recognized:
                    continue
                m = re.search(alias + r"[ \t]*[:：]?[ \t]*(\d{1,2})\b", row_text)
                if m:
                    val = int(m.group(1))
                    if 20 <= val <= 99:
                        player[field] = val
                        recognized[field] = True
        # 标签与数字分离时（如"速度"一行、"88"下一行）
        for i, row_text in enumerate(row_texts):
            pure_label = row_text.strip()
            if pure_label in SKILL_ALIASES and SKILL_ALIASES[pure_label] not in recognized:
                num = self._next_pure_number(row_texts, i)
                if num and 20 <= num <= 99:
                    player[SKILL_ALIASES[pure_label]] = num
                    recognized[SKILL_ALIASES[pure_label]] = True

        # 3.2 年龄（支持"年龄：24"或"生日：1993年3月5日"）
        joined = "\n".join(row_texts)
        m = re.search(r"(?:年龄|age)\s*[:：]?\s*(\d{1,2})\b", joined, re.I)
        if m and 15 <= int(m.group(1)) <= 45:
            player["age"] = int(m.group(1))
            recognized["age"] = True
        else:
            m = re.search(r"生日\s*[:：]\s*(\d{4})[年.\-/](\d{1,2})[月.\-/](\d{1,2})", joined)
            if m:
                try:
                    bd = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                    age = (datetime.date.today() - bd).days // 365
                    if 15 <= age <= 45:
                        player["age"] = age
                        recognized["age"] = True
                except ValueError:
                    pass

        # 3.3 位置
        pos = self._parse_position(joined)
        if pos:
            player["position"] = pos
            recognized["position"] = True

        # 3.4 综合评分（优先行内；否则按六维均值估算）
        m = re.search(r"(?:综合|总评|overall|ovr|rating)\s*(?:评分|评|值)?\s*[:：]?\s*(\d{1,2})\b", joined, re.I)
        if m and 0 <= int(m.group(1)) <= 99:
            player["overall"] = int(m.group(1))
            recognized["overall"] = True
        else:
            skill_vals = [player[c] for c in ("pace", "shooting", "passing", "dribbling", "defending", "physical")]
            if any(v != 70 for v in skill_vals):
                player["overall"] = round(sum(skill_vals) / len(skill_vals))
                notes.append("未识别到综合评分，已按六维能力均值估算")
            else:
                notes.append("未识别到综合评分与六维能力，报告基于默认值生成，仅供参考")

        # 3.5 潜力
        m = re.search(r"(?:潜力|potential|pot)\s*[:：]?\s*(\d{1,2})\b", joined, re.I)
        if m and 0 <= int(m.group(1)) <= 99:
            player["potential"] = int(m.group(1))
            recognized["potential"] = True

        # 3.6 身价（万/亿 → 欧元）
        m = re.search(r"(?:身价|市值|market)\s*[:：]?\s*([\d.]+)\s*(亿|万)?\s*(?:欧元|欧)?", joined, re.I)
        if m:
            num = float(m.group(1))
            unit = m.group(2) or ""
            player["market_value"] = self._to_euro(num, unit)
            recognized["market_value"] = True

        # 3.7 俱乐部 / 联赛 / 国籍 / 惯用脚 / 身高 / 体重 / 进球 / 助攻
        pair_rules = {
            "club": r"(?:俱乐部|club)\s*[:：]?\s*([\u4e00-\u9fa5A-Za-z0-9 .\-]{2,24})",
            "league": r"(?:联赛|league)\s*[:：]?\s*([\u4e00-\u9fa5A-Za-z0-9 .\-]{2,24})",
            "nationality": r"(?:国籍|nationality)\s*[:：]?\s*([\u4e00-\u9fa5A-Za-z .]{2,16})",
            "foot": r"(?:惯用脚|脚)\s*[:：]?\s*(左|右)",
        }
        for field, pattern in pair_rules.items():
            m = re.search(pattern, joined, re.I)
            if m and m.group(1).strip():
                player[field] = m.group(1).strip()
                recognized[field] = True

        m = re.search(r"(?:身高|height)\s*[:：]?\s*(\d{3})\s*(?:cm)?", joined, re.I)
        if m:
            player["height"] = int(m.group(1))
            recognized["height"] = True
        m = re.search(r"(?:体重|weight)\s*[:：]?\s*(\d{2,3})\s*(?:kg)?", joined, re.I)
        if m:
            player["weight"] = int(m.group(1))
            recognized["weight"] = True

        m = re.search(r"(?:进球|goals)\s*[:：]?\s*(\d{1,2})\b", joined, re.I)
        if m:
            player["season_goals"] = int(m.group(1))
            recognized["season_goals"] = True
        m = re.search(r"(?:助攻|assists)\s*[:：]?\s*(\d{1,2})\b", joined, re.I)
        if m:
            player["season_assists"] = int(m.group(1))
            recognized["season_assists"] = True

        # 3.8 姓名：取顶部第一个非关键词行
        for row_text in row_texts:
            candidate = row_text.strip()
            if self._is_name_row(candidate):
                player["name"] = candidate
                recognized["name"] = True
                break

        # 3.9 缺失字段提示
        if "age" not in recognized:
            notes.append("未识别到年龄，已使用默认值 23（影响潜力预测）")
        if "position" not in recognized:
            notes.append("未识别到位置，已使用默认位置 ST")

        return player, recognized, notes

    # ---------- 工具方法 ----------
    @staticmethod
    def _group_rows(blocks: list[dict]) -> list[dict]:
        """按 y 中心距离聚行。"""
        blocks = sorted(blocks, key=lambda b: (b["y"], b["x"]))
        rows: list[dict] = []
        for b in blocks:
            placed = False
            for r in rows:
                if abs(b["y"] - r["y"]) < max(12.0, b["h"] * 0.6):
                    r["blocks"].append(b)
                    n = len(r["blocks"])
                    r["y"] = (r["y"] * (n - 1) + b["y"]) / n
                    placed = True
                    break
            if not placed:
                rows.append({"y": b["y"], "blocks": [b]})
        return rows

    @staticmethod
    def _next_pure_number(row_texts: list[str], idx: int) -> int | None:
        """标签行之后的 1~2 行内寻找纯数字行。"""
        for j in range(idx + 1, min(idx + 3, len(row_texts))):
            m = re.fullmatch(r"\s*(\d{1,2})\s*", row_texts[j])
            if m:
                return int(m.group(1))
        return None

    def _parse_position(self, joined: str) -> str | None:
        # 中文位置（先匹配较长的）
        for cn, abbr in sorted(POSITION_CN_ALIAS.items(), key=lambda kv: -len(kv[0])):
            if re.search(cn, joined):
                return abbr
        # 英文缩写
        m = re.search(
            r"\b(GK|CB|SW|LB|RB|LWB|RWB|CDM|CM|CAM|LM|RM|LW|RW|LF|RF|CF|ST|SS)\b",
            joined,
            re.I,
        )
        if m:
            raw = m.group(1).upper()
            return POSITION_MAP.get(raw, raw)
        # 位置标签后的词
        m = re.search(r"(?:位置|pos)\s*[:：]?\s*([A-Za-z]{2,3})", joined, re.I)
        if m:
            raw = m.group(1).upper()
            return POSITION_MAP.get(raw, raw)
        return None

    def _is_name_row(self, text: str) -> bool:
        if not text:
            return False
        if len(text) > 24:
            return False
        if re.search(r"[0-9:：,，、.。%]", text):
            return False
        upper = text.upper()
        if upper in POSITION_MAP:
            return False
        for kw in _NAME_STOP:
            if kw.lower() in text.lower():
                return False
        # 跳过纯 ASCII 短缩写（logo / 水印，如 HE、TeamViewer）
        if re.fullmatch(r"[A-Za-z\s]{1,3}", text):
            return False
        # 中文名至少 2 字，其他语言至少 3 字符
        is_cjk = bool(re.search(r"[\u4e00-\u9fa5]", text))
        if (not is_cjk and len(text) < 3) or (is_cjk and len(text) < 2):
            return False
        return True

    @staticmethod
    def _to_euro(num: float, unit: str) -> int:
        if unit == "亿":
            return int(num * 1e8)
        if unit == "万":
            return int(num * 1e4)
        return int(num)


# 模块级单例（引擎懒加载）
_ocr_instance: PlayerOCR | None = None


def get_ocr() -> PlayerOCR:
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = PlayerOCR()
    return _ocr_instance
