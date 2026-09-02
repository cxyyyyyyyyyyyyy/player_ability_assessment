"""绿茵慧眼 —— FastAPI 后端入口。

启动：python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
或直接双击项目根目录的 start.bat。
"""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("backend.main")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend import config
from backend.agent.evaluator import Evaluator
from backend.api.routes import router
from backend.data.loader import load_all_players, load_star_players
from backend.models.clustering import StyleClusterer
from backend.models.potential_model import PotentialModel

# 前端静态目录（与 silent-project-6.0 结构一致：后端托管前端页面）
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"


class Registry:
    """应用级共享资源（数据 + 模型）。"""

    def __init__(self):
        self.all_players = None
        self.star_df = None
        self.clusterer = None
        self.potential_model = None
        self.evaluator = None

    def build(self) -> None:
        print("加载数据...")
        self.all_players = load_all_players()
        self.star_df = load_star_players()
        print(f"球员库 {len(self.all_players)} 名，球星库 {len(self.star_df)} 名")

        print("训练风格聚类模型...")
        self.clusterer = StyleClusterer().fit(self.all_players)
        print(f"聚类完成：{dict(self.clusterer.style_names)}")

        print("训练潜力预测模型...")
        self.potential_model = PotentialModel().fit(self.all_players)
        print(f"潜力模型 R2={self.potential_model.r2:.3f}, RMSE={self.potential_model.rmse:.3f}, CV-RMSE={self.potential_model.cv_rmse:.3f}")
        top = sorted(self.potential_model.feature_importance.items(), key=lambda kv: kv[1], reverse=True)[:5]
        print("关键特征 Top5:", "、".join(f"{k}({v:.3f})" for k, v in top))

        self.evaluator = Evaluator(
            self.all_players, self.star_df, self.clusterer, self.potential_model
        )
        print("评估 Agent 就绪。")


@asynccontextmanager
async def lifespan(app: FastAPI):
    start = time.perf_counter()
    logger.info("应用启动，正在加载数据与模型...")
    registry = Registry()
    registry.build()
    app.state.registry = registry
    logger.info("数据与模型加载完成，耗时 %.1fs", time.perf_counter() - start)
    yield
    logger.info("应用关闭")


app = FastAPI(title=config.APP_NAME + " API", version=config.APP_VERSION, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
# API 路由（必须先于静态托管注册，确保 /api/* 优先命中）
app.include_router(router)


@app.get("/")
def root():
    """根路径返回前端页面（与 silent-project-6.0 一致）。"""
    return FileResponse(FRONTEND_DIR / "index.html")


# 静态资源托管：/css、/js 及前端目录内所有文件
app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend",
)
