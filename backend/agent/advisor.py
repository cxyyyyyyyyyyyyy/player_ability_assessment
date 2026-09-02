"""生涯规划建议 Agent：规则引擎 + 可选 LLM 增强。"""
from __future__ import annotations

from backend.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, POSITION_MAP, SKILL_COLUMNS
from backend.models.similarity import position_avg

SKILL_CN = {
    "pace": "速度",
    "shooting": "射门",
    "passing": "传球",
    "dribbling": "盘带",
    "defending": "防守",
    "physical": "体能",
}

STAGE_ADVICE = {
    "成长期": "年龄处于成长期，潜力远未兑现。建议优先打磨基本功与对抗能力，控制负荷、预防伤病，稳步提升战术理解力。",
    "巅峰期": "处于职业生涯黄金期，能力接近或达到巅峰。建议以扬长为主、补短为辅，在关键比赛中保持稳定输出，冲击更高平台。",
    "成熟期": "进入成熟期，身体机能小幅下降但经验大幅增长。可承担更多战术角色（如组织核心、定位球主罚、更衣室领袖），用智慧弥补速度。",
    "转型期": "身体机能明显下降，建议主动向减少速度依赖的角色转型（如边锋→前腰/中场），依靠经验与技术延续职业生涯。",
}


def development_stage(age: int) -> str:
    if age < 20:
        return "成长期"
    if age < 27:
        return "巅峰期"
    if age < 31:
        return "成熟期"
    return "转型期"


def _main_position(pos: str) -> str:
    return POSITION_MAP.get(pos, pos)


def training_focus(row: dict, avg_by_pos: dict, n: int = 3) -> list[dict]:
    """找出相对同位置球员均值最薄弱的几项能力。"""
    main = _main_position(str(row.get("position", "ST")))
    base = avg_by_pos.get(main, {}) or {c: 70 for c in SKILL_COLUMNS}
    gaps = sorted(
        ((c, row.get(c, 0) - base.get(c, 70)) for c in SKILL_COLUMNS),
        key=lambda x: x[1],
    )
    return [
        {"skill": c, "skill_cn": SKILL_CN[c], "gap": round(g, 1),
         "value": row.get(c, 0), "avg": base.get(c, 70)}
        for c, g in gaps[:n]
    ]


def build_advice(row: dict, cluster: dict, potential: dict,
                 match_detail: list[dict], benchmarks: list[dict], avg_by_pos: dict) -> dict:
    """规则引擎生成生涯规划建议。"""
    age = int(row.get("age", 23))
    stage = development_stage(age)
    current_pos = str(row.get("position", "ST"))
    main_current = _main_position(current_pos)
    best_pos = match_detail[0]["position"]
    need_transition = main_current != best_pos

    if need_transition:
        transition = (
            f"当前注册位置为 {current_pos}，而能力结构与 {best_pos} 更匹配。"
            f"建议增加 {best_pos} 位置的出场时间或尝试转型，以最大化能力价值。"
        )
    else:
        transition = f"当前位置 {current_pos} 与能力结构高度适配，建议深耕该位置、打磨细节。"

    focus = training_focus(row, avg_by_pos)
    focus_text = "、".join(
        f"{f['skill_cn']}（当前 {f['value']}，同位置均值 {f['avg']}）" for f in focus
    )
    bench_text = "、".join(b["name"] for b in benchmarks) if benchmarks else "暂无"

    summary = (
        f"综合评估：{row.get('name', '该球员')} 现年 {age} 岁，当前综合评分 {row.get('overall', 0)}，"
        f"预测潜力峰值 {potential['peak']:.1f}。风格类型为「{cluster['style']}」，处于{stage}。"
        f"{transition} 建议训练重点：{focus_text}。发展模板：{bench_text}。"
    )

    return {
        "stage": stage,
        "stage_advice": STAGE_ADVICE[stage],
        "current_position": current_pos,
        "best_position": best_pos,
        "need_transition": need_transition,
        "transition_suggestion": transition,
        "training_focus": focus,
        "benchmarks_text": bench_text,
        "summary": summary,
    }


def build_advice_with_llm(context: dict) -> str | None:
    """可选：调用 LLM 生成更自然的球探报告。未配置 API Key 或调用失败时返回 None。"""
    if not LLM_API_KEY:
        return None

    prompt = (
        "你是一名资深足球球探。请基于以下球员数据与系统分析结果，"
        "撰写一份 200 字以内的专业球探评估报告（中文），要求：条理清晰、专业客观、给出明确建议。\n\n"
        f"球员数据：{context.get('player')}\n"
        f"风格聚类：{context.get('cluster')}\n"
        f"潜力预测：{context.get('potential')}\n"
        f"位置适配：{context.get('position_match')}\n"
        f"对标球员：{context.get('benchmarks')}\n"
        f"规则建议：{context.get('rule_advice')}"
    )
    try:
        import requests

        resp = requests.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {LLM_API_KEY}"},
            json={
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 600,
            },
            timeout=25,
        )
        resp.raise_for_status()
        return str(resp.json()["choices"][0]["message"]["content"]).strip()
    except Exception:
        return None
