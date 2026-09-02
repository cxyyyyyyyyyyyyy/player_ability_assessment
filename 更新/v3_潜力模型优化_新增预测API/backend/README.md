# 绿茵慧眼 · 球员能力评估系统

基于 Python 技术栈的数据分析与可视化短学期项目：输入一名球员的信息，系统基于球员库数据，
通过 **KMeans 风格聚类 + 随机森林潜力预测 + 相似度匹配**，一键输出**预测潜力值、能力画像、
风格定位、生涯规划建议与对标球员**。

## 项目结构

```
task/
├── backend/                  # 后端（FastAPI）
│   ├── main.py               # 应用入口（数据+模型初始化）
│   ├── config.py             # 全局配置
│   ├── data/                 # 数据加载层
│   ├── models/               # 模型层：聚类 / 潜力预测 / 相似度
│   ├── agent/                # Agent：评估引擎 + 生涯规划建议
│   └── api/routes.py         # REST API
├── frontend/                 # 前端（Streamlit）
│   ├── app.py                # 交互界面
│   └── api_client.py         # 后端 API 客户端
├── data/
│   ├── star_players.csv      # 内置 32 名知名球星测试数据
│   └── player_pool.csv       # 球员库（首次运行自动生成，模型训练用）
├── scripts/
│   └── generate_pool.py      # 球员库生成脚本
└── tests/                    # 测试用例
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动后端（首次会自动生成球员库并训练模型）
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 3. 另开一个终端，启动前端
streamlit run frontend/app.py
```

浏览器会自动打开前端页面（默认 http://localhost:8501）。后端接口文档见 http://localhost:8000/docs。

## 使用说明

1. 左侧选择「从球星库选择」可直接评估 32 名知名球星；或选择「自定义球员」手动填写信息；
2. 点击「生成评估报告」，系统返回五部分报告：能力画像 / 风格定位 / 潜力预测 / 生涯规划建议 / 对标球员；
3. 测试数据包含：姆巴佩、哈兰德、贝林厄姆、维尼修斯、亚马尔、梅西、C罗 等。

## 核心算法

| 算法 | 用途 |
|------|------|
| KMeans 聚类（PCA 降维可视化） | 球员风格画像：速度冲击型 / 技术组织型 / 后防屏障型 / 门神守护型 / 锋线终结型 / 中场引擎型 等 |
| 随机森林回归 | 预测潜力峰值，绘制年龄-能力成长曲线 |
| 余弦相似度 | 位置适配分析 + 对标球员匹配 |
| 规则引擎 +（可选）LLM | 生成可解释的生涯规划建议 |

## API 一览

| 接口 | 说明 |
|------|------|
| `GET /api/health` | 健康检查 |
| `GET /api/stars` | 内置球星列表 |
| `GET /api/players?search=&limit=` | 球员库搜索 |
| `GET /api/cluster-map` | 风格聚类散点数据 |
| `POST /api/evaluate` | 球员评估：`{"name": "Kylian Mbappé"}` 或 `{"player": {...}}` |

## 可选：AI 球探报告（LLM 增强）

不配置也可运行（使用规则引擎生成建议）。如需生成更自然的球探报告文本，设置环境变量：

```bash
set LLM_API_KEY=你的Key            # Windows
set LLM_BASE_URL=https://api.deepseek.com/v1   # 可选，OpenAI 兼容接口
set LLM_MODEL=deepseek-chat                     # 可选
```

## 运行测试

```bash
pytest tests/ -v
```

## 数据说明

- `data/star_players.csv`：32 名知名球星（2023-24 赛季能力值），用于演示与对标；
- `data/player_pool.csv`：由 `scripts/generate_pool.py` 生成约 1800 名球员（覆盖各位置/年龄段/能力水平），
  用于聚类与回归模型训练，首次启动后端时自动生成；
- 如已下载 Kaggle *FIFA 24 Complete Player Dataset*，可将清洗后的 CSV 覆盖 `data/player_pool.csv`（保持相同列名）获得更真实的效果。


## 更新记录

### v1.0.0 - 基础框架初始化
- 搭建 FastAPI 后端框架（应用入口 / 配置 / REST API 路由）
- 集成数据加载、聚类、潜力预测、评估 Agent 的启动编排
- 实现前端静态资源托管（根路径返回 index.html）

### v2.0.0 - 后端框架完善
- 新增统一日志记录（logging），统计启动加载耗时
- `/api/health` 增加应用名、版本号、潜力模型 R² 指标
- 配置文件新增应用元信息（APP_NAME / APP_VERSION / LOG_LEVEL）

### v3.0.0 - 潜力预测模型优化
- 潜力模型新增特征重要性输出（训练后自动计算 Top 特征）
- 新增 5 折交叉验证，输出泛化误差 CV-RMSE
- 新增接口 `POST /api/predict-potential`（预测潜力峰值、成长曲线、库内百分位）
