/* 绿茵慧眼 · 球员能力评估与生涯规划系统 —— 项目立项答辩 PPT 生成脚本 */
const pptxgen = require("C:/Users/33845/AppData/Roaming/npm/node_modules/pptxgenjs");
const fs = require("fs");
const path = require("path");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "绿茵慧眼项目组";
pres.title = "绿茵慧眼 · 球员能力评估与生涯规划系统 立项答辩";

// ------- 配色 -------
const C = {
  dark:   "0E3A1D",   // 深绿（封面/结尾背景）
  dark2:  "154A26",   // 稍亮绿（草皮条纹）
  dark3:  "1C5C30",   // 草皮条纹亮
  primary:"1B5E20",   // 主绿
  primary2:"2E7D32",  // 中绿
  accent: "4CAF50",   // 亮绿
  mint:   "81C784",
  light:  "E8F5E9",   // 淡绿
  light2: "F4FAF5",   // 页面底
  gold:   "F9A825",   // 金
  gold2:  "FFC107",
  ink:    "1F2933",   // 主文字
  mut:    "64748B",   // 次要文字
  white:  "FFFFFF",
  line:   "CBE0CE",
};

const FONT = "Microsoft YaHei";
const FW = 13.33;
const FH = 7.5;

// ------- 通用小工具 -------
function addFooter(slide, pageNo) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 7.02, w: 12.13, h: 0.02, fill: { color: C.line }, line: { type: "none" }
  });
  slide.addText("绿茵慧眼 · 球员能力评估与生涯规划系统", {
    x: 0.6, y: 7.1, w: 6, h: 0.3, fontFace: FONT, fontSize: 9, color: C.mut, align: "left", valign: "middle", margin: 0
  });
  slide.addText(String(pageNo).padStart(2, "0"), {
    x: 11.9, y: 7.1, w: 0.83, h: 0.3, fontFace: FONT, fontSize: 10, color: C.primary, bold: true, align: "right", valign: "middle", margin: 0
  });
}

// 内容页页眉：序号徽章 + 标题 + 副标题
function addHeader(slide, num, title, sub) {
  slide.background = { color: C.light2 };
  // 顶部左侧色块
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: FW, h: 0.09, fill: { color: C.primary }, line: { type: "none" } });
  // 数字徽章
  slide.addShape(pres.shapes.OVAL, { x: 0.55, y: 0.42, w: 0.62, h: 0.62, fill: { color: C.primary }, line: { type: "none" } });
  slide.addText(num, { x: 0.55, y: 0.42, w: 0.62, h: 0.62, fontFace: FONT, fontSize: 18, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
  slide.addText(title, { x: 1.38, y: 0.34, w: 8.6, h: 0.52, fontFace: FONT, fontSize: 26, bold: true, color: C.ink, align: "left", valign: "middle", margin: 0 });
  slide.addText(sub, { x: 1.4, y: 0.9, w: 8.6, h: 0.3, fontFace: FONT, fontSize: 11, color: C.mut, align: "left", valign: "middle", margin: 0 });
}

// 圆角卡片
function card(slide, x, y, w, h, fill) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, fill: { color: fill || C.white },
    line: { color: C.line, width: 1 }, rectRadius: 0.08,
    shadow: { type: "outer", color: "123F23", blur: 9, offset: 2, angle: 90, opacity: 0.10 }
  });
}

// 图标圆（文字符号）
function iconCircle(slide, x, y, d, bg, symbol, color) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: bg }, line: { type: "none" } });
  slide.addText(symbol, { x, y, w: d, h: d, fontFace: FONT, fontSize: d * 0.42, bold: true, color, align: "center", valign: "middle", margin: 0 });
}

// ============================================================
// Slide 1 封面
// ============================================================
(() => {
  const s = pres.addSlide();
  s.background = { color: C.dark };

  // 草皮条纹（顶部与底部）
  const stripes = [
    { y: 0, h: 0.5 }, { y: 7.0, h: 0.5 },
  ];
  stripes.forEach(st => {
    for (let i = 0; i < 8; i++) {
      s.addShape(pres.shapes.RECTANGLE, {
        x: (FW / 8) * i, y: st.y, w: FW / 8, h: st.h,
        fill: { color: i % 2 === 0 ? C.dark2 : C.dark3 }, line: { type: "none" }
      });
    }
  });

  // 装饰圆
  s.addShape(pres.shapes.OVAL, { x: 10.7, y: -1.4, w: 3.6, h: 3.6, fill: { color: C.dark2, transparency: 35 }, line: { type: "none" } });
  s.addShape(pres.shapes.OVAL, { x: -1.2, y: 4.9, w: 3.0, h: 3.0, fill: { color: C.dark2, transparency: 45 }, line: { type: "none" } });

  // 足球点缀（五边形意象：用圆+内五边形文字）
  s.addShape(pres.shapes.OVAL, { x: 10.35, y: 2.0, w: 1.5, h: 1.5, fill: { color: C.white }, line: { color: C.dark, width: 2 } });
  s.addShape(pres.shapes.OVAL, { x: 10.85, y: 2.5, w: 0.5, h: 0.5, fill: { color: C.dark }, line: { type: "none" } });
  s.addShape(pres.shapes.OVAL, { x: 10.35, y: 2.0, w: 0.42, h: 0.42, fill: { color: C.dark }, line: { type: "none" } });
  s.addShape(pres.shapes.OVAL, { x: 11.43, y: 2.0, w: 0.42, h: 0.42, fill: { color: C.dark }, line: { type: "none" } });
  s.addShape(pres.shapes.OVAL, { x: 10.5, y: 2.75, w: 0.4, h: 0.4, fill: { color: C.dark }, line: { type: "none" } });
  s.addShape(pres.shapes.OVAL, { x: 11.15, y: 2.82, w: 0.4, h: 0.4, fill: { color: C.dark }, line: { type: "none" } });

  // 徽章
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.32, y: 1.05, w: 2.7, h: 0.5, fill: { color: C.gold }, rectRadius: 0.25, line: { type: "none" }
  });
  s.addText("项目立项答辩", { x: 5.32, y: 1.05, w: 2.7, h: 0.5, fontFace: FONT, fontSize: 15, bold: true, color: C.dark, align: "center", valign: "middle", margin: 0 });

  // 主标题
  s.addText("绿茵慧眼", { x: 1, y: 2.0, w: 11.33, h: 1.25, fontFace: FONT, fontSize: 66, bold: true, color: C.white, align: "center", valign: "middle", margin: 0, charSpacing: 8 });
  s.addText("球员能力评估与生涯规划系统", { x: 1, y: 3.28, w: 11.33, h: 0.62, fontFace: FONT, fontSize: 24, color: C.mint, align: "center", valign: "middle", margin: 0, charSpacing: 3 });

  // 装饰分隔
  s.addShape(pres.shapes.RECTANGLE, { x: 5.42, y: 4.05, w: 2.5, h: 0.045, fill: { color: C.gold }, line: { type: "none" } });

  // 一句话定位
  s.addText("基于 KMeans 聚类 · 随机森林回归 · 相似度匹配 的一站式球员能力评估系统", {
    x: 1.2, y: 4.45, w: 10.93, h: 0.42, fontFace: FONT, fontSize: 13, color: C.mint, align: "center", valign: "middle", margin: 0
  });

  // 底部信息
  s.addText([
    { text: "答辩人：", options: { color: C.mint } },
    { text: "×××    ", options: { color: C.white } },
    { text: "指导教师：", options: { color: C.mint } },
    { text: "×××", options: { color: C.white } },
  ], { x: 1, y: 6.15, w: 11.33, h: 0.4, fontFace: FONT, fontSize: 13, align: "center", valign: "middle", margin: 0 });
  s.addText("2026 年 8 月", { x: 1, y: 6.5, w: 11.33, h: 0.35, fontFace: FONT, fontSize: 12, color: C.mint, align: "center", valign: "middle", margin: 0 });
})();

// ============================================================
// Slide 2 目录
// ============================================================
(() => {
  const s = pres.addSlide();
  s.background = { color: C.light2 };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: FW, h: 0.09, fill: { color: C.primary }, line: { type: "none" } });

  s.addText("CONTENTS", { x: 0.6, y: 0.55, w: 6, h: 0.35, fontFace: FONT, fontSize: 13, bold: true, color: C.accent, align: "left", valign: "middle", margin: 0, charSpacing: 4 });
  s.addText("目 录", { x: 0.6, y: 0.92, w: 6, h: 0.7, fontFace: FONT, fontSize: 34, bold: true, color: C.ink, align: "left", valign: "middle", margin: 0 });

  const items = [
    { num: "01", t: "研究背景与意义", d: "行业趋势 · 现实痛点 · 研究价值" },
    { num: "02", t: "研究内容与目标", d: "总体目标 · 系统架构 · 核心算法" },
    { num: "03", t: "项目创新点", d: "四大差异化创新设计" },
    { num: "04", t: "实施计划与预期成果", d: "分阶段进度 · 成果指标 · 可行性" },
  ];
  let y = 2.05;
  items.forEach(it => {
    // 数字徽章
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 1.1, y: y + 0.05, w: 1.05, h: 0.9, fill: { color: C.primary }, rectRadius: 0.12, line: { type: "none" } });
    s.addText(it.num, { x: 1.1, y: y + 0.05, w: 1.05, h: 0.9, fontFace: FONT, fontSize: 26, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    s.addText(it.t, { x: 2.5, y: y - 0.05, w: 7, h: 0.6, fontFace: FONT, fontSize: 21, bold: true, color: C.ink, align: "left", valign: "middle", margin: 0 });
    s.addText(it.d, { x: 2.5, y: y + 0.52, w: 9, h: 0.42, fontFace: FONT, fontSize: 12.5, color: C.mut, align: "left", valign: "middle", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 2.5, y: y + 1.06, w: 10.2, h: 0.012, fill: { color: C.line }, line: { type: "none" } });
    y += 1.22;
  });

  // 右侧装饰
  s.addShape(pres.shapes.OVAL, { x: 11.6, y: 5.6, w: 2.6, h: 2.6, fill: { color: C.light }, line: { type: "none" } });
  iconCircle(s, 12.15, 6.15, 1.5, C.primary, "球", C.white);

  addFooter(s, 2);
})();

// ============================================================
// Slide 3 研究背景与意义
// ============================================================
(() => {
  const s = pres.addSlide();
  addHeader(s, "01", "研究背景与意义", "足球产业数字化加速 —— 数据驱动的球员评估成为必然趋势");

  // 左：研究背景
  s.addText("研究背景", { x: 0.6, y: 1.42, w: 5.9, h: 0.4, fontFace: FONT, fontSize: 17, bold: true, color: C.primary, align: "left", valign: "middle", margin: 0 });
  const bgs = [
    { t: "产业趋势", d: "全球足球产业规模持续扩大，数据化选材已成为职业俱乐部青训与引援的标配手段。" },
    { t: "现实痛点", d: "传统球探评估依赖主观经验：标准不一、难以量化、人力成本高，中小球队更缺乏专业分析团队。" },
    { t: "需求缺口", d: "球员潜力预测、风格定位与生涯规划缺乏低门槛、可量化、可解释的智能化工具支撑。" },
  ];
  let by = 1.9;
  bgs.forEach(b => {
    card(s, 0.6, by, 5.9, 1.32, C.white);
    iconCircle(s, 0.88, by + 0.3, 0.72, C.light, b.t[0], C.primary);
    s.addText(b.t, { x: 1.82, y: by + 0.18, w: 4.5, h: 0.42, fontFace: FONT, fontSize: 14.5, bold: true, color: C.ink, align: "left", valign: "middle", margin: 0 });
    s.addText(b.d, { x: 1.82, y: by + 0.58, w: 4.5, h: 0.66, fontFace: FONT, fontSize: 11, color: C.mut, align: "left", valign: "middle", margin: 0 });
    by += 1.52;
  });

  // 右：研究意义
  s.addText("研究意义", { x: 7.0, y: 1.42, w: 5.9, h: 0.4, fontFace: FONT, fontSize: 17, bold: true, color: C.primary, align: "left", valign: "middle", margin: 0 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 7.0, y: 1.9, w: 5.73, h: 4.56, fill: { color: C.white }, line: { color: C.line, width: 1 }, rectRadius: 0.1
  });
  const ms = [
    { t: "科学化", d: "用统一指标与算法模型替代主观经验，让评估结果可复现、可对比。" },
    { t: "可解释", d: "风格标签 + 对标球员 + 成长曲线，输出结果透明，方便教练与分析师理解与验证。" },
    { t: "低门槛", d: "开源技术栈、本地可部署；支持图片 OCR 录入，个人与青训机构也能轻松使用。" },
  ];
  let my = 2.25;
  ms.forEach(m => {
    iconCircle(s, 7.35, my, 0.66, C.primary, m.t[0], C.white);
    s.addText(m.t, { x: 8.25, y: my - 0.05, w: 4.2, h: 0.42, fontFace: FONT, fontSize: 15, bold: true, color: C.ink, align: "left", valign: "middle", margin: 0 });
    s.addText(m.d, { x: 8.25, y: my + 0.36, w: 4.25, h: 0.85, fontFace: FONT, fontSize: 11, color: C.mut, align: "left", valign: "middle", margin: 0 });
    my += 1.38;
  });

  addFooter(s, 3);
})();

// ============================================================
// Slide 4 研究现状与问题分析
// ============================================================
(() => {
  const s = pres.addSlide();
  addHeader(s, "01", "研究现状与问题分析", "现有球员评估工具各有短板，尚未出现开箱即用的一站式解决方案");

  // 对比表
  const rows = [
    ["评估方案", "代表优势", "主要不足"],
    ["EA FC / FIFA 评分", "覆盖球员广、更新及时", "仅静态评分，无潜力预测与生涯建议"],
    ["Football Manager", "数据维度丰富", "商业闭源、国内获取难、可解释性弱"],
    ["Wyscout / StatsBomb", "专业指标完整", "费用高昂，主要面向职业俱乐部"],
    ["传统球探报告", "经验丰富、视角灵活", "主观性强、标准不统一、难以量化对比"],
  ];
  const tw = [3.1, 4.6, 4.4];
  let ty = 1.55;
  rows.forEach((r, i) => {
    const isHead = i === 0;
    const isLast = i === rows.length - 1;
    if (isHead) {
      s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: ty, w: 12.1, h: 0.52, fill: { color: C.primary }, line: { type: "none" } });
    } else {
      s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: ty, w: 12.1, h: 0.62, fill: { color: i % 2 === 1 ? C.white : C.light }, line: { type: "none" } });
    }
    let tx = 0.6;
    r.forEach((cell, ci) => {
      s.addText(cell, {
        x: tx, y: ty, w: tw[ci], h: isHead ? 0.52 : 0.62,
        fontFace: FONT, fontSize: isHead ? 13.5 : 11.5, bold: isHead,
        color: isHead ? C.white : (ci === 2 ? C.mut : C.ink),
        align: "left", valign: "middle", margin: 0, inset: 0.18
      });
      tx += tw[ci];
    });
    if (!isLast) {
      s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: ty + (isHead ? 0.52 : 0.62), w: 12.1, h: 0.012, fill: { color: C.line }, line: { type: "none" } });
    }
    ty += isHead ? 0.52 : 0.62;
  });

  // 切入点条
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 5.6, w: 12.1, h: 0.95, fill: { color: C.dark }, rectRadius: 0.12, line: { type: "none" }
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.95, y: 5.83, w: 1.7, h: 0.5, fill: { color: C.gold }, rectRadius: 0.25, line: { type: "none" } });
  s.addText("项目切入点", { x: 0.95, y: 5.83, w: 1.7, h: 0.5, fontFace: FONT, fontSize: 13, bold: true, color: C.dark, align: "center", valign: "middle", margin: 0 });
  s.addText("开源 · 轻量 · 可解释 —— 打造「输入球员信息 → 评估画像 → 预测潜力 → 规划生涯」的一站式评估闭环",
    { x: 2.9, y: 5.6, w: 9.6, h: 0.95, fontFace: FONT, fontSize: 14.5, bold: true, color: C.white, align: "left", valign: "middle", margin: 0 });

  addFooter(s, 4);
})();

// ============================================================
// Slide 5 研究目标
// ============================================================
(() => {
  const s = pres.addSlide();
  addHeader(s, "02", "研究目标", "构建一套可落地、可解释、可扩展的球员能力评估与生涯规划系统");

  // 总体目标条
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 1.5, w: 12.1, h: 0.92, fill: { color: C.light }, line: { color: C.accent, width: 1.2 }, rectRadius: 0.1
  });
  s.addText([
    { text: "总体目标  ", options: { bold: true, color: C.primary } },
    { text: "以数据与算法为核心，完成「输入 — 评估 — 预测 — 规划」全流程，输出球员能力画像、风格定位、潜力预测、生涯规划建议与对标球员，覆盖从数据录入到报告生成的全链路。", options: { color: C.ink } },
  ], { x: 0.95, y: 1.5, w: 11.5, h: 0.92, fontFace: FONT, fontSize: 13, align: "left", valign: "middle", margin: 0 });

  // 4 个具体目标
  const goals = [
    { t: "数据建设", d: "构建约 1800 名球员的评估库 + 33 名知名球星对标库，覆盖 7 大位置、多年龄段与 19 维属性特征。" },
    { t: "算法实现", d: "实现 KMeans 风格聚类画像、随机森林潜力预测、余弦相似度对标三大核心算法。" },
    { t: "系统集成", d: "完成 FastAPI 后端 + Web 交互界面，输出六大部分评估报告，支持球星库 / 自定义 / 图片录入三种方式。" },
    { t: "质量保障", d: "建立 10 项自动化测试（模型指标 R² > 0.5、潜力范围 0–99、全接口覆盖），确保系统稳定可靠。" },
  ];
  const positions = [
    [0.6, 2.72], [6.65, 2.72], [0.6, 4.52], [6.65, 4.52],
  ];
  goals.forEach((g, i) => {
    const [gx, gy] = positions[i];
    card(s, gx, gy, 6.05, 1.6, C.white);
    s.addShape(pres.shapes.RECTANGLE, { x: gx, y: gy, w: 0.09, h: 1.6, fill: { color: C.accent }, line: { type: "none" } });
    s.addText(String(i + 1).padStart(2, "0"), { x: gx + 0.28, y: gy + 0.16, w: 1.2, h: 0.5, fontFace: FONT, fontSize: 24, bold: true, color: C.mint, align: "left", valign: "middle", margin: 0 });
    s.addText(g.t, { x: gx + 1.55, y: gy + 0.16, w: 4.3, h: 0.5, fontFace: FONT, fontSize: 15.5, bold: true, color: C.ink, align: "left", valign: "middle", margin: 0 });
    s.addText(g.d, { x: gx + 0.28, y: gy + 0.72, w: 5.55, h: 0.82, fontFace: FONT, fontSize: 11, color: C.mut, align: "left", valign: "middle", margin: 0 });
  });

  addFooter(s, 5);
})();

// ============================================================
// Slide 6 研究内容 —— 系统架构
// ============================================================
(() => {
  const s = pres.addSlide();
  addHeader(s, "02", "研究内容与系统架构", "三层架构：统一输入 → 算法分析 → 六维报告输出，形成完整评估闭环");

  // 三层流程卡片
  const layers = [
    { t: "输入层", items: ["球星库选择", "自定义录入", "球员卡图片 OCR"], bg: C.dark, ac: C.gold },
    { t: "分析层", items: ["KMeans 风格聚类", "随机森林潜力预测", "余弦相似度对标", "规则引擎 / LLM 建议"], bg: C.primary, ac: C.mint },
    { t: "输出层", items: ["能力画像", "风格定位", "潜力预测", "生涯规划建议", "对标球员", "市场参考"], bg: C.primary2, ac: C.gold },
  ];
  let lx = 0.6;
  layers.forEach((L) => {
    const w = 3.62;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: lx, y: 1.6, w, h: 3.7, fill: { color: L.bg }, rectRadius: 0.12, line: { type: "none" } });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: lx + 0.3, y: 1.92, w: 1.6, h: 0.5, fill: { color: L.ac }, rectRadius: 0.25, line: { type: "none" } });
    s.addText(L.t, { x: lx + 0.3, y: 1.92, w: 1.6, h: 0.5, fontFace: FONT, fontSize: 14, bold: true, color: C.dark, align: "center", valign: "middle", margin: 0 });
    s.addText(L.items.join("　·　"), {
      x: lx + 0.3, y: 2.6, w: w - 0.6, h: 2.5, fontFace: FONT, fontSize: 13.5, bold: true, color: C.white, align: "left", valign: "top", margin: 0, lineSpacing: 26
    });
    if (lx < 9) {
      s.addShape(pres.shapes.OVAL, { x: lx + w - 0.16, y: 3.2, w: 0.5, h: 0.5, fill: { color: C.gold }, line: { type: "none" } });
      s.addText("→", { x: lx + w - 0.16, y: 3.2, w: 0.5, h: 0.5, fontFace: FONT, fontSize: 18, bold: true, color: C.dark, align: "center", valign: "middle", margin: 0 });
    }
    lx += w + 0.62;
  });

  // 底部说明
  card(s, 0.6, 5.6, 12.1, 1.05, C.white);
  s.addShape(pres.shapes.OVAL, { x: 0.9, y: 5.86, w: 0.55, h: 0.55, fill: { color: C.gold }, line: { type: "none" } });
  s.addText("算", { x: 0.9, y: 5.86, w: 0.55, h: 0.55, fontFace: FONT, fontSize: 15, bold: true, color: C.dark, align: "center", valign: "middle", margin: 0 });
  s.addText("六维能力（速度 / 射门 / 传球 / 盘带 / 防守 / 身体）+ 综合评分 作为统一评估特征，支持年龄、位置、身价等多维度信息融合。",
    { x: 1.65, y: 5.6, w: 10.85, h: 1.05, fontFace: FONT, fontSize: 13, color: C.ink, align: "left", valign: "middle", margin: 0 });

  addFooter(s, 6);
})();

// ============================================================
// Slide 7 技术路线与核心算法
// ============================================================
(() => {
  const s = pres.addSlide();
  addHeader(s, "02", "技术路线与核心算法", "KMeans 聚类画像 + 随机森林潜力预测 + 余弦相似度对标，三算法协同");

  const algos = [
    {
      t: "KMeans 风格聚类",
      tag: "画像",
      d: [
        "以 7 维能力特征构建球员画像空间，划分为 5 个能力簇群",
        "启发式规则生成 7 种语义化风格标签",
        "PCA 降维可视化，直观展示全库球员风格分布",
      ],
    },
    {
      t: "随机森林潜力预测",
      tag: "预测",
      d: [
        "200 棵树集成回归，融合年龄 / 能力 / 位置 One-Hot 特征",
        "输出潜力峰值 0–99、16–36 岁成长曲线、潜力百分位",
        "评估指标 R² > 0.5、RMSE 可控，结果可复现",
      ],
    },
    {
      t: "余弦相似度匹配",
      tag: "对标",
      d: [
        "以六维能力向量计算球员与各位置原型适配度",
        "在 33 名球星库中匹配 Top3 对标球员",
        "输出位置适配分析，辅助定位转型决策",
      ],
    },
  ];
  const aw = [3.85, 3.85, 3.85];
  let ax = 0.6;
  algos.forEach((a, i) => {
    const x = ax;
    card(s, x, 1.5, aw[i], 3.95, C.white);
    // 顶部标签
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.25, y: 1.78, w: 0.95, h: 0.44, fill: { color: i === 0 ? C.primary : i === 1 ? C.gold : C.primary2 }, rectRadius: 0.22, line: { type: "none" } });
    s.addText(a.tag, { x: x + 0.25, y: 1.78, w: 0.95, h: 0.44, fontFace: FONT, fontSize: 12.5, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    s.addText(a.t, { x: x + 0.25, y: 2.28, w: aw[i] - 0.5, h: 0.6, fontFace: FONT, fontSize: 15.5, bold: true, color: C.ink, align: "left", valign: "middle", margin: 0 });
    a.d.forEach((line, li) => {
      s.addText(line, {
        x: x + 0.28, y: 3.0 + li * 0.8, w: aw[i] - 0.56, h: 0.78,
        fontFace: FONT, fontSize: 11, color: C.mut, align: "left", valign: "middle", margin: 0, breakLine: false
      });
    });
    ax += aw[i] + 0.28;
  });

  // 技术栈条
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 5.72, w: 12.1, h: 0.92, fill: { color: C.dark }, rectRadius: 0.12, line: { type: "none" }
  });
  s.addText("技术栈", { x: 0.92, y: 5.72, w: 1.2, h: 0.92, fontFace: FONT, fontSize: 14, bold: true, color: C.gold, align: "left", valign: "middle", margin: 0 });
  s.addText("Python · FastAPI · scikit-learn · Pandas / NumPy · RapidOCR（离线图片识别） · LLM 增强（可选）",
    { x: 2.2, y: 5.72, w: 10.3, h: 0.92, fontFace: FONT, fontSize: 13.5, bold: true, color: C.white, align: "left", valign: "middle", margin: 0 });

  addFooter(s, 7);
})();

// ============================================================
// Slide 8 项目创新点
// ============================================================
(() => {
  const s = pres.addSlide();
  addHeader(s, "03", "项目创新点", "四大差异化设计，直击现有工具「门槛高、不可解释、单点割裂」的痛点");

  const inno = [
    { t: "图片 OCR 一键录入", d: "上传球员卡图片即可自动识别并解析六维能力与基础信息，告别繁琐手工录入，大幅降低使用门槛。", sym: "图" },
    { t: "可解释的风格画像", d: "聚类算法 + 启发式规则生成 7 种语义化风格标签（速度冲击型 / 技术组织型等），评估结果不再是一个黑盒数字。", sym: "析" },
    { t: "规则 + LLM 双轨建议", d: "规则引擎保证离线可用、逻辑可追溯；接入大模型后自动生成自然语言球探报告，兼顾可解释性与表达质量。", sym: "智" },
    { t: "评估—预测—规划闭环", d: "从能力评估、风格定位到潜力预测、对标球员、市场参考与生涯建议的一站式闭环，形成完整决策链路。", sym: "环" },
  ];
  const pos = [
    [0.6, 1.5], [6.65, 1.5], [0.6, 3.55], [6.65, 3.55],
  ];
  inno.forEach((it, i) => {
    const [ix, iy] = pos[i];
    card(s, ix, iy, 6.05, 1.85, C.white);
    s.addShape(pres.shapes.RECTANGLE, { x: ix, y: iy, w: 0.09, h: 1.85, fill: { color: i % 2 === 0 ? C.gold : C.accent }, line: { type: "none" } });
    iconCircle(s, ix + 0.32, iy + 0.32, 0.78, i % 2 === 0 ? C.light : C.light, it.sym, C.primary);
    s.addText(String(i + 1).padStart(2, "0"), { x: ix + 5.2, y: iy + 0.15, w: 0.7, h: 0.45, fontFace: FONT, fontSize: 15, bold: true, color: C.mint, align: "right", valign: "middle", margin: 0 });
    s.addText(it.t, { x: ix + 1.35, y: iy + 0.3, w: 4.5, h: 0.45, fontFace: FONT, fontSize: 15.5, bold: true, color: C.ink, align: "left", valign: "middle", margin: 0 });
    s.addText(it.d, { x: ix + 1.35, y: iy + 0.8, w: 4.5, h: 0.95, fontFace: FONT, fontSize: 11, color: C.mut, align: "left", valign: "middle", margin: 0 });
  });

  addFooter(s, 8);
})();

// ============================================================
// Slide 9 实施计划
// ============================================================
(() => {
  const s = pres.addSlide();
  addHeader(s, "04", "实施计划与进度安排", "短学期约 4 周迭代推进，每周有明确里程碑，预留充分测试与打磨时间");

  const phases = [
    { p: "阶段一", w: "第 1 周", t: "需求分析与方案设计", d: "明确评估指标体系、数据方案与界面原型" },
    { p: "阶段二", w: "第 1–2 周", t: "球员库构建与数据清洗", d: "生成 1800+ 球员库、33 名球星库，统一 19 维特征" },
    { p: "阶段三", w: "第 2–3 周", t: "核心算法开发与验证", d: "聚类 / 潜力预测 / 相似度，用球星数据交叉验证" },
    { p: "阶段四", w: "第 3 周", t: "系统集成与界面开发", d: "FastAPI 接口 + Web 界面 + OCR 录入 + 评估报告" },
    { p: "阶段五", w: "第 3–4 周", t: "测试优化与文档撰写", d: "10 项自动化测试、性能优化、技术文档" },
    { p: "阶段六", w: "答辩周", t: "演示打磨与立项答辩", d: "完整流程演示与答辩材料准备" },
  ];

  // 时间轴
  const x0 = 0.6, x1 = 12.73, y = 1.75;
  s.addShape(pres.shapes.RECTANGLE, { x: x0 + 0.2, y: y + 0.42, w: x1 - x0 - 0.4, h: 0.03, fill: { color: C.line }, line: { type: "none" } });
  const step = (x1 - x0 - 0.4) / 5;
  phases.forEach((ph, i) => {
    const cx = x0 + 0.2 + step * i;
    s.addShape(pres.shapes.OVAL, { x: cx - 0.17, y: y + 0.28, w: 0.34, h: 0.34, fill: { color: i === phases.length - 1 ? C.gold : C.primary }, line: { color: C.white, width: 2 } });
    // 阶段卡
    const wx = i % 2 === 0 ? cx - 1.35 : cx - 0.28;
    const wy = i % 2 === 0 ? 2.45 : 4.0;
    card(s, wx, wy, 1.9, 2.15, C.white);
    s.addShape(pres.shapes.RECTANGLE, { x: wx, y: wy, w: 1.9, h: 0.09, fill: { color: i === phases.length - 1 ? C.gold : C.primary }, line: { type: "none" } });
    s.addText(ph.p, { x: wx + 0.15, y: wy + 0.2, w: 1.6, h: 0.35, fontFace: FONT, fontSize: 12.5, bold: true, color: i === phases.length - 1 ? C.gold : C.primary, align: "left", valign: "middle", margin: 0 });
    s.addText(ph.w, { x: wx + 0.15, y: wy + 0.52, w: 1.6, h: 0.3, fontFace: FONT, fontSize: 10.5, color: C.mut, align: "left", valign: "middle", margin: 0 });
    s.addText(ph.t, { x: wx + 0.15, y: wy + 0.85, w: 1.62, h: 0.62, fontFace: FONT, fontSize: 11.5, bold: true, color: C.ink, align: "left", valign: "middle", margin: 0 });
    s.addText(ph.d, { x: wx + 0.15, y: wy + 1.48, w: 1.62, h: 0.6, fontFace: FONT, fontSize: 9.5, color: C.mut, align: "left", valign: "middle", margin: 0 });
  });

  // 说明条
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 6.35, w: 12.1, h: 0.55, fill: { color: C.light }, line: { color: C.accent, width: 1 }, rectRadius: 0.1
  });
  s.addText("里程碑原则：数据先行 → 算法验证 → 集成联调 → 测试兜底；每周产出可演示的中间成果，风险提前暴露。",
    { x: 0.95, y: 6.35, w: 11.4, h: 0.55, fontFace: FONT, fontSize: 12, color: C.ink, align: "left", valign: "middle", margin: 0 });

  addFooter(s, 9);
})();

// ============================================================
// Slide 10 预期成果与可行性 + 结束
// ============================================================
(() => {
  const s = pres.addSlide();
  addHeader(s, "04", "预期成果与可行性分析", "成果可量化、技术可行、数据可控、时间可落地");

  // 预期成果 4 卡
  const outs = [
    { t: "功能成果", d: "6 个 REST API + 交互式 Web 界面，输出能力画像 / 风格定位 / 潜力预测 / 生涯规划 / 对标球员 / 市场参考六大报告模块。" },
    { t: "数据成果", d: "约 1800 名球员评估库 + 33 名知名球星对标库，统一 19 维属性特征，支持真实数据替换。" },
    { t: "技术成果", d: "7 类风格画像、潜力预测 R² > 0.5、潜力区间 0–99、成长曲线可视化，10 项自动化测试全通过。" },
    { t: "文档成果", d: "需求分析、系统设计、使用说明、测试报告等完整文档，可直接演示、交付与扩展。" },
  ];
  const pos = [
    [0.6, 1.5], [6.65, 1.5], [0.6, 3.3], [6.65, 3.3],
  ];
  outs.forEach((o, i) => {
    const [ox, oy] = pos[i];
    card(s, ox, oy, 6.05, 1.6, C.white);
    s.addShape(pres.shapes.RECTANGLE, { x: ox, y: oy, w: 0.09, h: 1.6, fill: { color: C.primary }, line: { type: "none" } });
    iconCircle(s, ox + 0.3, oy + 0.3, 0.72, C.light, ["功", "数", "技", "文"][i], C.primary);
    s.addText(o.t, { x: ox + 1.25, y: oy + 0.26, w: 4.6, h: 0.45, fontFace: FONT, fontSize: 15, bold: true, color: C.ink, align: "left", valign: "middle", margin: 0 });
    s.addText(o.d, { x: ox + 1.25, y: oy + 0.75, w: 4.6, h: 0.78, fontFace: FONT, fontSize: 10.5, color: C.mut, align: "left", valign: "middle", margin: 0 });
  });

  // 可行性
  s.addText("可行性分析", { x: 0.6, y: 5.08, w: 5, h: 0.38, fontFace: FONT, fontSize: 15, bold: true, color: C.primary, align: "left", valign: "middle", margin: 0 });
  const feas = [
    { t: "技术可行", d: "全套成熟开源库" },
    { t: "数据可控", d: "自动生成 + 可替换真实数据" },
    { t: "时间可行", d: "4 周迭代，分工明确" },
  ];
  let fx = 0.6;
  feas.forEach((f) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: fx, y: 5.5, w: 3.86, h: 0.78, fill: { color: C.dark }, rectRadius: 0.1, line: { type: "none" } });
    s.addText([
      { text: f.t + "　", options: { bold: true, color: C.gold } },
      { text: f.d, options: { color: C.white } },
    ], { x: fx + 0.22, y: 5.5, w: 3.5, h: 0.78, fontFace: FONT, fontSize: 11.5, align: "left", valign: "middle", margin: 0 });
    fx += 4.12;
  });

  // 结束语
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 6.5, w: 12.1, h: 0.62, fill: { color: C.gold }, rectRadius: 0.1, line: { type: "none" }
  });
  s.addText("恳请各位老师批评指正 · 谢谢！", { x: 0.6, y: 6.5, w: 12.1, h: 0.62, fontFace: FONT, fontSize: 16, bold: true, color: C.dark, align: "center", valign: "middle", margin: 0 });

  addFooter(s, 10);
})();

// ------- 输出 -------
const outDir = path.join(__dirname, "..");
const outPath = path.join(outDir, "绿茵慧眼_球员能力评估系统_项目立项答辩.pptx");
pres.writeFile({ fileName: outPath }).then(() => {
  console.log("OK ->", outPath);
}).catch(e => { console.error("FAIL", e); process.exit(1); });
