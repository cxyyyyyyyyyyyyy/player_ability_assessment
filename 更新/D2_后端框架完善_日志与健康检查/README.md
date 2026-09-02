# 绿茵慧眼 · 球员能力评估系统

## 一、项目简介
基于 Python 的球员能力评估与生涯规划系统：输入球员信息，通过 KMeans 风格聚类、随机森林潜力预测、余弦相似度匹配，一键输出预测潜力、能力画像、风格定位、生涯规划建议与对标球员。短学期五人团队项目。

## 二、技术栈
Python / FastAPI / scikit-learn / pandas；前端原生 HTML/CSS/JS；数据来自 European Soccer Database（CSV）。

## 三、核心功能
球员评估（六维能力）、KMeans 风格聚类（PCA 可视化）、随机森林潜力预测与成长曲线、生涯规划建议（规则引擎+可选 LLM）、对标球星匹配（余弦相似度）、OCR 球员卡片识别。

## 四、项目结构
backend/（FastAPI）、frontend/（页面）、data/（CSV）、scripts/（脚本）、tests/、daily/（日报）、prompts/（AI 记录）、docs/（文档）

## 五、运行方式
pip install -r backend/requirements.txt；backend\start.bat 或 uvicorn backend.main:app --port 8000，打开 http://localhost:8000。

## 六、团队分工
cxyyyyyyyyyyyyyyy（统筹/框架/潜力模型）、成员2（数据特征工程）、成员3（KMeans聚类）、成员4（画像/规划/匹配）、成员5（前端/Streamlit）。

## 七、当前进度
后端框架、聚类、潜力预测、评估 Agent、前端均完成联调；按课程要求每日 push 并维护 daily/prompts/docs。
