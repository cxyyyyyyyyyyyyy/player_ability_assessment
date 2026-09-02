"""球员风格聚类模型（KMeans + 启发式风格标签）。"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from backend.config import FEATURES, K_CLUSTERS, RANDOM_STATE


class StyleClusterer:
    """基于六维能力 + 综合评分的球员风格聚类。"""

    def __init__(self, n_clusters: int = K_CLUSTERS):
        self.n_clusters = n_clusters
        self.kmeans: KMeans | None = None
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2, random_state=RANDOM_STATE)
        self.labels: np.ndarray | None = None
        self.style_names: dict[int, str] = {}

    # ---------- 训练 ----------
    def fit(self, df: pd.DataFrame) -> "StyleClusterer":
        X = df[FEATURES].values.astype(float)
        Xs = self.scaler.fit_transform(X)
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=RANDOM_STATE, n_init=10)
        self.labels = self.kmeans.fit_predict(Xs)
        self.pca.fit(Xs)  # 仅用于散点图
        for i in range(self.n_clusters):
            center = self.scaler.inverse_transform(
                self.kmeans.cluster_centers_[i].reshape(1, -1)
            )[0]
            pos_counts = df[self.labels == i]["position"].value_counts(normalize=True)
            self.style_names[i] = self._label_style(dict(zip(FEATURES, center)), pos_counts)
        return self

    @staticmethod
    def _label_style(d: dict, pos_counts=None) -> str:
        pace, sho, pas, dri, de_, phy = (
            d["pace"], d["shooting"], d["passing"],
            d["dribbling"], d["defending"], d["physical"],
        )
        overall = d["overall"]

        # 优先依据簇内位置构成命名（更贴合真实数据）
        if pos_counts is not None and len(pos_counts) > 0:
            top_pos = pos_counts.index[0]
            if top_pos == "GK":
                return "门神守护型"
            if top_pos in ("CB", "FB"):
                return "后防屏障型"
            if top_pos in ("ST", "W"):
                return "锋线终结型" if overall >= 68 else "进攻好手型"
            if top_pos == "CM":
                return "中场引擎型"
            if top_pos == "CAM":
                return "技术组织型"

        # 能力阈值兜底（无位置分布时）
        if de_ >= 76 and phy >= 78:
            if pace < 55 and sho < 45 and dri < 55:
                return "门神守护型"
            return "后防屏障型"
        if pace >= 85 and dri >= 84:
            return "速度冲击型"
        if pas >= 82 and dri >= 82:
            return "技术组织型"
        if sho >= 82:
            return "锋线终结型"
        if pas >= 76 and de_ >= 68:
            return "中场引擎型"
        if sho >= 55 or dri >= 58:
            return "进攻好手型"
        return "全能均衡型"

    # ---------- 预测 ----------
    def predict(self, row: dict) -> dict:
        x = np.array([[row.get(c, 0) for c in FEATURES]], dtype=float)
        xs = self.scaler.transform(x)
        cid = int(self.kmeans.predict(xs)[0])
        dist = float(np.linalg.norm(xs[0] - self.kmeans.cluster_centers_[cid]))
        center = self.scaler.inverse_transform(
            self.kmeans.cluster_centers_[cid].reshape(1, -1)
        )[0]
        coord = self.pca.transform(xs)[0].tolist()
        return {
            "cluster_id": cid,
            "style": self.style_names[cid],
            "distance": round(dist, 3),
            "center": {c: round(float(v), 1) for c, v in zip(FEATURES, center)},
            "coord": [round(coord[0], 2), round(coord[1], 2)],
        }

    # ---------- 汇总信息 ----------
    def cluster_summary(self, df: pd.DataFrame) -> list[dict]:
        out = []
        for i in range(self.n_clusters):
            members = df[self.labels == i]
            reps = members.nlargest(3, "overall")["name"].tolist()
            out.append({
                "id": i,
                "style": self.style_names[i],
                "count": int(len(members)),
                "representatives": reps,
            })
        return out

    def map_data(self, df: pd.DataFrame) -> list[dict]:
        """全库聚类散点（PCA 2D），供前端一次性绘制。"""
        X = df[FEATURES].values.astype(float)
        Xs = self.scaler.transform(X)
        coords = self.pca.transform(Xs)
        return [
            {
                "name": str(n),
                "label": self.style_names[int(l)],
                "x": float(x),
                "y": float(y),
                "overall": int(o),
            }
            for n, l, (x, y), o in zip(df["name"], self.labels, coords, df["overall"])
        ]
