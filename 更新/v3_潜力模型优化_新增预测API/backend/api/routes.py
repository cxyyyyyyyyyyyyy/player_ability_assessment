"""API 路由定义。"""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile

from pydantic import BaseModel

from backend import config

from backend.data.loader import get_player_by_name
from backend.data.schema import EvaluateRequest
from backend.services.ocr import get_ocr

router = APIRouter(prefix="/api")


def _reg(request: Request):
    return request.app.state.registry


@router.get("/health")
def health(request: Request):
    reg = _reg(request)
    return {
        "status": "ok",
        "app": config.APP_NAME,
        "version": config.APP_VERSION,
        "pool_size": int(len(reg.all_players)),
        "clusters": len(reg.clusterer.style_names),
        "potential_r2": reg.potential_model.r2,
    }


@router.get("/stars")
def list_stars(request: Request):
    reg = _reg(request)
    return {"players": reg.star_df.to_dict("records")}


@router.get("/players")
def search_players(
    request: Request,
    search: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=500),
):
    """按名字搜索球员库。"""
    reg = _reg(request)
    df = reg.all_players
    if search:
        df = df[df["name"].str.contains(search, case=False, na=False)]
    df = df.nlargest(limit, "overall")
    return {"total": int(len(df)), "players": df.to_dict("records")}


@router.get("/cluster-map")
def cluster_map(request: Request):
    """全库风格聚类散点 + 聚类汇总。"""
    reg = _reg(request)
    return {
        "points": reg.clusterer.map_data(reg.all_players),
        "summary": reg.clusterer.cluster_summary(reg.all_players),
    }


@router.post("/recognize")
async def recognize_player_image(request: Request, file: UploadFile = File(...)):
    """上传球员图片（球员卡/截图），OCR 识别并解析球员信息。"""
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件（jpg / png 等）")
    data = await file.read()
    try:
        return get_ocr().recognize(data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


class PotentialRequest(BaseModel):
    """潜力预测请求（自定义球员六维能力）。"""
    name: str | None = None
    age: int = 23
    overall: float = 70
    pace: float = 70
    shooting: float = 70
    passing: float = 70
    dribbling: float = 70
    defending: float = 70
    physical: float = 70
    position: str = "ST"


@router.post("/predict-potential")
def predict_potential(request: Request, req: PotentialRequest):
    """预测潜力峰值、成长曲线与库内百分位（版本 3 新增）。"""
    reg = _reg(request)
    row = req.model_dump()
    peak = reg.potential_model.predict_peak(row)
    curve = reg.potential_model.growth_curve(row)
    percentile = reg.potential_model.potential_percentile(row, reg.all_players)
    return {
        "potential": peak,
        "percentile": round(percentile, 1),
        "curve": curve,
        "cv_rmse": reg.potential_model.cv_rmse,
        "feature_importance": reg.potential_model.feature_importance,
    }


@router.post("/evaluate")
def evaluate_player(request: Request, req: EvaluateRequest):
    """评估一名球员，返回完整评估报告。"""
    reg = _reg(request)

    if req.name:
        hit = get_player_by_name(reg.all_players, req.name)
        if hit is None:
            raise HTTPException(status_code=404, detail=f"球员库中未找到：{req.name}")
        row = hit.iloc[0].to_dict()
    elif req.player is not None:
        row = req.player.model_dump()
        row["potential"] = row.get("potential") or row["overall"]
        row["market_value"] = row.get("market_value") or 0
    else:
        raise HTTPException(status_code=400, detail="请提供 name（库内球员）或 player（自定义球员）")

    report = reg.evaluator.evaluate(row)
    return {"player": row, **report}
