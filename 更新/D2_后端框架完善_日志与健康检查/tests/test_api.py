"""API 层测试。"""
from __future__ import annotations

from fastapi.testclient import TestClient

from backend.main import app


def _client():
    return TestClient(app)


def test_health():
    with _client() as client:
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["pool_size"] > 1000


def test_stars():
    with _client() as client:
        resp = client.get("/api/stars")
        assert resp.status_code == 200
        assert len(resp.json()["players"]) >= 20


def test_cluster_map():
    with _client() as client:
        resp = client.get("/api/cluster-map")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["points"]) > 1000
        assert len(data["summary"]) >= 4


def test_evaluate_by_name():
    with _client() as client:
        resp = client.post("/api/evaluate", json={"name": "Lamine Yamal"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["player"]["name"] == "Lamine Yamal"
        assert data["potential"]["peak"] > 85, "亚马尔预测潜力应较高"
        assert data["career_advice"]["stage"] == "成长期"


def test_evaluate_custom():
    with _client() as client:
        payload = {
            "player": {
                "name": "测试新星", "age": 18, "position": "W", "overall": 78,
                "pace": 90, "shooting": 70, "passing": 75, "dribbling": 88,
                "defending": 30, "physical": 65, "market_value": 10000000,
            }
        }
        resp = client.post("/api/evaluate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["player"]["name"] == "测试新星"
        assert data["cluster"]["style"]


def test_evaluate_not_found():
    with _client() as client:
        resp = client.post("/api/evaluate", json={"name": "不存在的人"})
        assert resp.status_code == 404
