"""模型层测试：数据加载、聚类、潜力预测、评估引擎。"""
from __future__ import annotations

import pytest

from backend.agent.evaluator import Evaluator
from backend.data.loader import load_all_players, load_star_players
from backend.models.clustering import StyleClusterer
from backend.models.potential_model import PotentialModel


@pytest.fixture(scope="module")
def registry():
    df = load_all_players()
    stars = load_star_players()
    clusterer = StyleClusterer().fit(df)
    model = PotentialModel().fit(df)
    evaluator = Evaluator(df, stars, clusterer, model)
    return df, stars, clusterer, model, evaluator


def test_data_loaded(registry):
    df, stars, *_ = registry
    assert len(df) > 1000, "球员库应包含 1000+ 球员"
    assert len(stars) >= 20, "球星库应包含 20+ 球星"
    assert {"pace", "shooting", "passing", "dribbling", "defending", "physical"} <= set(df.columns)


def test_clustering(registry):
    df, _, clusterer, *_ = registry
    assert len(clusterer.style_names) == clusterer.n_clusters
    # 每类都应有球员
    summary = clusterer.cluster_summary(df)
    assert all(c["count"] > 0 for c in summary)


def test_potential_model(registry):
    _, _, _, model, _ = registry
    assert model.r2 is not None and model.r2 > 0.5, "潜力模型 R² 应大于 0.5"
    row = {"age": 20, "position": "W", "overall": 80,
           "pace": 90, "shooting": 70, "passing": 75, "dribbling": 88,
           "defending": 35, "physical": 65}
    peak = model.predict_peak(row)
    assert 0 <= peak <= 99
    curve = model.growth_curve(row)
    assert len(curve) == 21  # 16~36 岁
    assert curve[0]["age"] == 16 and curve[-1]["age"] == 36


def test_evaluator_star(registry):
    df, stars, clusterer, model, evaluator = registry
    row = stars[stars["name"] == "Kylian Mbappé"].iloc[0].to_dict()
    report = evaluator.evaluate(row)
    assert report["cluster"]["style"] in ("速度冲击型", "锋线终结型", "技术组织型", "全能均衡型")
    assert report["potential"]["peak"] > 0
    assert report["career_advice"]["stage"] in ("成长期", "巅峰期", "成熟期", "转型期")
    assert len(report["benchmarks"]) == 3
    assert len(report["position_match"]) >= 5
