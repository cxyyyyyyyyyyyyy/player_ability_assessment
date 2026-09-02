"""评估 Agent：编排完整的球员评估流程。"""
from __future__ import annotations

import pandas as pd

from backend.agent.advisor import build_advice, build_advice_with_llm
from backend.config import POSITION_MAP, SKILL_COLUMNS
from backend.models.similarity import find_benchmarks, position_avg, position_match_detail


class Evaluator:
    """输入一名球员信息 → 输出完整评估报告。"""

    def __init__(self, df: pd.DataFrame, star_df: pd.DataFrame, clusterer, potential_model):
        self.df = df
        self.star_df = star_df
        self.clusterer = clusterer
        self.potential_model = potential_model
        self.avg_by_pos = position_avg(df)

    def evaluate(self, row: dict) -> dict:
        # 1. 能力画像
        overall_pct = float((self.df["overall"] <= row["overall"]).mean() * 100)
        main = POSITION_MAP.get(str(row.get("position", "ST")), str(row.get("position", "ST")))
        profile = {
            "overall": int(row["overall"]),
            "overall_percentile": round(overall_pct, 1),
            "skills": {c: int(row[c]) for c in SKILL_COLUMNS},
            "position_avg": self.avg_by_pos.get(main, {}),
        }

        # 2. 风格聚类
        cluster = self.clusterer.predict(row)

        # 3. 潜力预测
        peak = self.potential_model.predict_peak(row)
        curve = self.potential_model.growth_curve(row)
        pct = self.potential_model.potential_percentile(row, self.df)
        potential = {
            "current": int(row.get("potential") or row["overall"]),
            "peak": round(peak, 1),
            "percentile": round(pct, 1),
            "curve": curve,
            "model_r2": round(self.potential_model.r2, 3) if self.potential_model.r2 is not None else None,
            "model_rmse": round(self.potential_model.rmse, 3) if self.potential_model.rmse is not None else None,
        }

        # 4. 位置适配 + 对标球员
        match_detail = position_match_detail(row)
        benchmarks = find_benchmarks(row, self.star_df)

        # 5. 生涯规划建议（规则引擎）
        advice = build_advice(row, cluster, potential, match_detail, benchmarks, self.avg_by_pos)

        # 可选：LLM 增强报告
        llm_text = build_advice_with_llm({
            "player": row,
            "cluster": cluster,
            "potential": potential,
            "position_match": match_detail,
            "benchmarks": benchmarks,
            "rule_advice": advice["summary"],
        })
        if llm_text:
            advice["llm_report"] = llm_text

        # 6. 市场参考
        market = self._market_reference(row)

        return {
            "profile": profile,
            "cluster": cluster,
            "potential": potential,
            "position_match": match_detail,
            "benchmarks": benchmarks,
            "career_advice": advice,
            "market": market,
        }

    def _market_reference(self, row: dict) -> dict:
        """市场参考：与当前球员能力相近（±2）的球员身价 25%~75% 分位区间。"""
        near = self.df[
            (self.df["overall"] >= row["overall"] - 2)
            & (self.df["overall"] <= row["overall"] + 2)
        ]["market_value"]
        if near.empty:
            return {"low": None, "high": None, "count": 0, "player_value": row.get("market_value")}
        return {
            "low": int(near.quantile(0.25)),
            "high": int(near.quantile(0.75)),
            "count": int(len(near)),
            "player_value": row.get("market_value"),
        }
