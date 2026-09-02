/* ================================================================
 * C小罗 · 可隐藏智能导览
 * 说明：纯前端实现，双击 index.html 也能用。
 * 知识库分三类：系统功能(system) / 足球知识(football) / 世界杯与球星(event)
 * ================================================================ */
(function () {
    "use strict";

    var AVATAR = "Ronaldo.jpg";          // 与 index.html 同级
    var NAME = "C小罗";
    var SUB = "绿茵慧眼 · 智能导览";

    /* ---------------- 知识库 ---------------- */
    var KB = [
        /* ===== 系统功能 ===== */
        {
            tag: "system", q: "这个系统能做什么？",
            kws: ["能做什么", "有什么功能", "功能", "系统是什么", "是什么系统", "简介", "导览", "怎么使用", "怎么用这个", "有什么用", "新手", "介绍系统"],
            a: "这个系统叫「绿茵慧眼 · 球员能力评估系统」，帮你评估球员并规划生涯。核心功能：\n\n1️⃣ 球员评估：输入球员信息，一键生成评估报告\n2️⃣ 风格聚类：KMeans 把球员按能力结构分成多种风格\n3️⃣ 潜力预测：随机森林回归预测潜力峰值和成长曲线\n4️⃣ 生涯规划：给出发育阶段、位置适配、训练重点建议\n5️⃣ 对标匹配：找出与你最相似的球星\n6️⃣ OCR 识别：上传球员卡片图片自动提取信息\n\n想先了解哪块？比如问我「怎么评估球员」或「什么是潜力预测」～"
        },
        {
            tag: "system", q: "怎么评估球员？",
            kws: ["怎么评估", "如何评估", "评估球员", "评估报告", "怎么生成", "生成报告", "开始评估", "评估步骤", "怎么用"],
            a: "评估球员很简单：\n\n1️⃣ 左侧选择模式\n   · 「从球星库选择」：输入姓名搜索（如 Messi、Haaland），点选即可\n   · 「自定义球员」：手动填年龄、位置、六维能力等；也可以先上传图片自动识别\n2️⃣ 点「生成评估报告」\n\n右侧会展示：能力画像雷达图、风格定位、潜力预测曲线、生涯规划建议、对标球员和市场参考身价。"
        },
        {
            tag: "system", q: "球星库怎么用？",
            kws: ["球星库", "搜索球员", "选球星", "怎么找球星"],
            a: "球星库模式：\n· 左侧输入球星姓名，支持中英文（Messi / 梅西 / 哈兰德都行）\n· 下方实时列出匹配结果，点击即选中\n· 选中后能看到国籍、位置、年龄、评分、潜力、俱乐部、身价\n· 点「生成评估报告」开始评估"
        },
        {
            tag: "system", q: "自定义球员模式是什么？",
            kws: ["自定义", "手动填写", "手动输入", "新建球员", "自建球员", "自己建"],
            a: "自定义模式适合评估你创造的球员（比如青训新星）：\n· 填姓名、年龄、位置、综合评分\n· 六维能力滑条：速度/射门/传球/盘带/防守/体能\n· 俱乐部、联赛、赛季进球、身价\n· 也可以先上传球员卡图片，OCR 自动识别后微调\n填完点「生成评估报告」即可。"
        },
        {
            tag: "system", q: "图片识别（OCR）怎么用？",
            kws: ["图片", "识别", "ocr", "上传图片", "球员卡", "截图", "照片"],
            a: "OCR 图片识别：\n· 在自定义模式点📷区域，选择或拖入球员卡 / 资料页截图（jpg、png）\n· 系统自动识别姓名、年龄、位置、能力值等信息\n· 识别结果自动填入表单，可微调后直接生成报告\n· 识别不清时可以手动修改，不影响使用"
        },
        {
            tag: "system", q: "风格聚类是什么？",
            kws: ["风格", "聚类", "kmeans", "风格定位", "什么风格"],
            a: "风格聚类：\n· 用 KMeans 无监督学习，把球员库按能力结构分成若干种风格类型（如全能进攻核心、防守铁闸、技术流组织者等）\n· 评估时把你的球员投影到风格空间，找到最接近的类型\n· 报告 Tab2「风格定位」有散点图和各类风格的代表球员\n· 聚类数由系统自动选择，保证类型可解释"
        },
        {
            tag: "system", q: "潜力预测是怎么算的？",
            kws: ["潜力", "预测", "随机森林", "成长曲线", "峰值", "潜力值", "潜力模型"],
            a: "潜力预测：\n· 用随机森林回归模型，以年龄、当前综合能力、位置等为特征\n· 在球员池数据上训练，预测潜力峰值\n· 绘制 16~35 岁的「年龄-能力成长曲线」\n· 报告给出潜力百分位（同龄球员中的位置）\n· 模型质量用 R² 和 RMSE 衡量，可在 Tab3 看到"
        },
        {
            tag: "system", q: "生涯规划建议是怎么生成的？",
            kws: ["规划", "建议", "训练重点", "生涯", "发展方向", "转会", "转型"],
            a: "生涯规划建议由规则引擎生成（若配置了大模型，还会附加一段 AI 球探报告）：\n· 当前发展阶段判断：潜力巨大 / 接近巅峰 / 需要转型等\n· 最佳位置适配：根据能力结构建议最适合的位置\n· 训练重点表：对比你的能力与同位置均值，列出差距项目\n· 结论都基于数据，不是随便给的建议"
        },
        {
            tag: "system", q: "对标球员是怎么匹配的？",
            kws: ["对标", "相似球员", "模板", "最像谁", "像哪位", "像谁", "对标球员"],
            a: "对标匹配：\n· 用余弦相似度计算你的球员与球星库每个球星的六维能力相似度\n· 列出最相似的几位球星及相似度百分比\n· 比如身体强、速度快的支点前锋，往往会对标 Haaland\n· 用处：找到自己的发展模板，看标杆怎么踢"
        },
        {
            tag: "system", q: "报告里的图怎么看？",
            kws: ["报告", "标签页", "雷达图", "画像", "看结果", "怎么读", "分析结果"],
            a: "生成报告后右侧有五个标签页：\n· 能力画像：六维雷达图，红=你、蓝=同位置均值，下方列出优势项和短板\n· 风格定位：聚类散点图，★ 是你的位置\n· 潜力预测：成长曲线，虚线标出你当前年龄\n· 生涯规划建议：阶段判断 + 训练重点表\n· 对标球员：最相似的球星\n底部还有市场参考身价区间。"
        },
        {
            tag: "system", q: "系统数据从哪来？",
            kws: ["数据", "数据来源", "数据库", "csv", "欧洲足球", "球员数据"],
            a: "系统数据来自公开数据集 European Soccer Database（欧洲足球数据库）：\n· star_players.csv —— 球星库（供搜索与对标）\n· player_pool.csv —— 球员池（训练聚类与潜力模型）\n数据已随仓库提供，不需要联网。"
        },

        /* ===== 足球知识 ===== */
        {
            tag: "football", q: "什么是越位？",
            kws: ["越位", "越位规则", "越位位置", "越位了"],
            a: "越位：传球瞬间，进攻球员比对方倒数第二名防守球员（通常包括门将）更靠近对方底线，且正参与进攻，就处于越位位置。\n\n注意：\n· 站在越位位置本身不犯规\n· 只有接球、干扰比赛或对方时才判罚\n· 简单记：传球的一刹那，别站在所有后卫身后"
        },
        {
            tag: "football", q: "任意球规则是什么？",
            kws: ["任意球", "直接任意球", "间接任意球", "任意球怎么罚"],
            a: "任意球分两种：\n· 直接任意球：可直接射门得分。常见犯规：铲人、拉人、手球等\n· 间接任意球：不能直接射门，必须经第二名球员触碰后才算进球（如门将持球超时、故意回传球等）\n· 防守方要退出 9.15 米，通常会排人墙"
        },
        {
            tag: "football", q: "点球是怎么回事？",
            kws: ["点球", "点球大战", "十二码", "点球规则", "点球怎么判"],
            a: "点球：\n· 禁区内犯规（含手球）判罚点球\n· 点球点距球门 11 米（12 码），单挑门将\n\n点球大战：\n· 淘汰赛加时后仍平局才用\n· 双方各派 5 人交替主罚，5 轮后进球多者胜\n· 仍平则突然死亡，一球定胜负"
        },
        {
            tag: "football", q: "一场比赛踢多长时间？",
            kws: ["多长时间", "比赛时间", "踢多久", "几分钟", "加时", "补时", "上下半场", "时长"],
            a: "一场标准足球赛：\n· 90 分钟 = 上下两个 45 分钟半场，中场休息 15 分钟\n· 每半场末有伤停补时\n· 淘汰赛打平 → 30 分钟加时（上下半场各 15 分钟）\n· 加时仍平 → 点球大战\n· 被红牌罚下的球员不能再上场，球队少一人应战"
        },
        {
            tag: "football", q: "足球场有多大？",
            kws: ["场地", "球场", "球门", "大小", "尺寸", "多长", "足球场"],
            a: "标准足球场：\n· 长度 90~120 米，宽度 45~90 米\n· 国际比赛常用 105×68 米\n· 球门：宽 7.32 米、高 2.44 米\n· 点球点距球门 11 米，禁区线距球门 16.5 米，中圈半径 9.15 米"
        },
        {
            tag: "football", q: "红黄牌是怎么用的？",
            kws: ["红牌", "黄牌", "警告", "罚下", "犯规"],
            a: "黄牌 = 警告：\n· 恶意犯规、拖延时间、脱衣庆祝等\n· 一场两黄变一红，直接被罚下\n\n红牌 = 罚下：\n· 严重犯规、暴力行为、故意手球破坏进球、破坏明显得分机会等\n· 被罚下者停赛至少一场，球队少一人"
        },
        {
            tag: "football", q: "常见阵型有哪些？",
            kws: ["阵型", "4-3-3", "4-4-2", "4-2-3-1", "战术", "怎么排阵容"],
            a: "阵型数字从后往前数（后卫-中场-前锋）：\n· 4-3-3：四后卫+三中场+三前锋，攻守均衡，现代主流\n· 4-4-2：经典双前锋打法\n· 4-2-3-1：双后腰保护 + 前腰组织，攻防层次好\n· 3-5-2：三中卫 + 五中场，靠边翼卫拉开宽度"
        },
        {
            tag: "football", q: "五大联赛是哪些？",
            kws: ["英超", "联赛", "西甲", "德甲", "意甲", "法甲", "五大联赛", "欧洲足球"],
            a: "欧洲五大联赛：\n· 英超（英格兰）：节奏快、竞争激烈，曼联、利物浦、曼城、切尔西、阿森纳\n· 西甲（西班牙）：皇马、巴萨双雄争霸\n· 德甲（德国）：拜仁慕尼黑长期统治\n· 意甲（意大利）：战术底蕴深，尤文、国米、AC米兰\n· 法甲（法国）：巴黎圣日耳曼领衔"
        },
        {
            tag: "football", q: "欧冠是什么？",
            kws: ["欧冠", "冠军联赛", "欧洲杯冠军", "俱乐部赛事"],
            a: "欧冠（欧洲冠军联赛）：欧洲俱乐部最高水平赛事，联赛 + 杯赛决出的顶级强队参赛。\n· 历史夺冠最多：皇家马德里（15 次）\n· 经典时刻：2005 利物浦「伊斯坦布尔奇迹」、2016-18 皇马欧冠三连冠\n· 每个赛季从 9 月打到次年 6 月决赛"
        },
        {
            tag: "football", q: "金球奖是什么？",
            kws: ["金球奖", "世界足球先生", "最佳球员", "个人奖项"],
            a: "金球奖由《法国足球》杂志颁发给年度世界最佳球员，是足坛最重要的个人荣誉。\n· 获次数最多：梅西 8 次（2023 年第八座）\n· C 罗 5 次\n· 2024 年金球奖得主：曼城/西班牙中场罗德里"
        },

        /* ===== 世界杯与球星故事 ===== */
        {
            tag: "event", q: "世界杯历史上有哪些冠军？",
            kws: ["世界杯", "大力神杯", "冠军", "历届"],
            a: "世界杯每四年一届，1930 年首届在乌拉圭举办。夺冠次数：\n· 巴西 5 次（1958/1962/1970/1994/2002）\n· 德国、意大利各 4 次\n· 阿根廷 3 次（1978/1986/2022）\n· 法国、乌拉圭各 2 次\n· 英格兰、西班牙各 1 次\n\n想听哪一届的故事？比如问我「2022世界杯」或「2014巴西世界杯」"
        },
        {
            tag: "event", q: "2022 卡塔尔世界杯发生了什么？",
            kws: ["2022", "卡塔尔", "梅西夺冠", "卢赛尔", "阿根廷夺冠"],
            a: "2022 卡塔尔世界杯是史上最精彩的决赛之一：\n· 阿根廷 vs 法国，常规时间 2:2，加时 3:3\n· 点球大战阿根廷胜出，梅西捧起大力神杯并当选赛事最佳\n· 姆巴佩上演帽子戏法（决赛进 3 球），以 8 球穿走金靴\n· 梅西集齐世界杯后，职业生涯大满贯达成"
        },
        {
            tag: "event", q: "2014 巴西世界杯是怎么回事？",
            kws: ["2014", "巴西世界杯", "7比1", "7-1", "格策", "米内罗"],
            a: "2014 巴西世界杯：\n· 半决赛德国 7:1 血洗东道主巴西，史称「米内罗惨案」\n· 决赛德国 1:0 阿根廷，格策第 113 分钟绝杀\n· 梅西获当届赛事金球奖，但无缘冠军\n· 那届比赛在巴西本土举办，见证桑巴足球的遗憾"
        },
        {
            tag: "event", q: "1998 法国世界杯呢？",
            kws: ["1998", "法国世界杯", "齐达内", "东道主夺冠"],
            a: "1998 法国世界杯：\n· 东道主法国 3:0 击败巴西，队史首夺大力神杯\n· 齐达内头球梅开二度，一战封神\n· 决赛前罗纳尔多突发身体不适的「决赛之谜」至今成谜\n· 那一代法国黄金一代正式开启"
        },
        {
            tag: "event", q: "介绍下梅西",
            kws: ["梅西", "messi", "巴萨", "巴黎", "迈阿密", "阿根廷人"],
            a: "梅西（Lionel Messi，1987-）：\n· 出生于阿根廷罗萨里奥，公认的 GOAT（史上最佳）候选\n· 巴萨青训出品，效力巴萨 20 年，后转投巴黎圣日耳曼，现效力迈阿密国际\n· 荣誉：8 次金球奖、4 次欧冠、10 次西甲冠军、1 次世界杯（2022）\n· 特点：盘带如入无人之境，传球视野顶级，任意球和射门俱佳\n· 2022 世界杯夺冠后，生涯再无遗憾"
        },
        {
            tag: "event", q: "介绍下 C 罗",
            kws: ["c罗", "cristiano", "罗纳尔多", "葡萄牙", "利雅得", "总裁", "siu"],
            a: "C 罗（Cristiano Ronaldo，1985-）：\n· 出生于葡萄牙马德拉，外号「总裁」\n· 效力过葡萄牙体育、曼联、皇马、尤文，现效力利雅得胜利\n· 荣誉：5 次金球奖、5 次欧冠（曼联 1 + 皇马 4）、2016 葡萄牙欧洲杯\n· 特点：历史级自律、头球与任意球顶级、进球机器（900+ 球）\n· 经典庆祝：Siuuuu～\n\nPS：我这个「C小罗」的头像和名字就是致敬他！⚽"
        },
        {
            tag: "event", q: "贝利是谁？",
            kws: ["贝利", "球王", "桑托斯", "三冠"],
            a: "贝利（Pelé，1940-2022）：\n· 巴西「球王」，足球史上第一个超级巨星\n· 唯一三次夺得世界杯的球员（1958/1962/1970）\n· 生涯总进球超 1200 球\n· 他让世界第一次认识到足球可以是「艺术」"
        },
        {
            tag: "event", q: "马拉多纳的故事",
            kws: ["马拉多纳", "上帝之手", "世纪进球", "1986", "那不勒斯"],
            a: "马拉多纳（Diego Maradona，1960-2020）：\n· 阿根廷传奇，1986 世界杯近乎一己之力夺冠\n· 对英格兰一战上演「上帝之手」+「世纪最佳进球」\n· 俱乐部层面把那不勒斯带上意甲之巅\n· 他是天才与争议并存的足坛图腾"
        },
        {
            tag: "event", q: "伊斯坦布尔奇迹是什么？",
            kws: ["伊斯坦布尔", "ac米兰", "2005", "利物浦", "奇迹", "大逆转"],
            a: "2005 欧冠决赛「伊斯坦布尔奇迹」：\n· 利物浦上半场 0:3 落后 AC 米兰\n· 下半场 6 分钟连进 3 球扳成 3:3\n· 点球大战 3:2 逆转夺冠\n· 被誉为欧冠史上最伟大的翻盘之战"
        },
        {
            tag: "event", q: "皇马欧冠三连冠？",
            kws: ["皇马", "皇家马德里", "三连冠", "齐达内执教", "欧冠之王"],
            a: "皇家马德里是「欧冠之王」，队史 15 次夺冠。\n· 2016-2018 年齐达内执教实现欧冠三连冠，历史唯一\n· 三届决赛对手：马竞、尤文、利物浦\n· C 罗是那三年最重要的得分手\n· 皇马在欧冠淘汰赛的表现常被津津乐道"
        },
        {
            tag: "event", q: "2026 世界杯在哪办？",
            kws: ["2026", "美加墨", "北美", "48队"],
            a: "2026 世界杯：\n· 由美国、加拿大、墨西哥三国联合举办\n· 首次扩军到 48 支球队参赛\n· 墨西哥将成为史上第一个三次举办世界杯的国家（1970/1986/2026）\n· 比赛将在三国多个城市举行"
        }
    ];

    /* ---------------- 工具 ---------------- */
    function norm(s) {
        return String(s || "").toLowerCase().replace(/[\s,，。.!！?？、；;：:··「」『』（）()《》<>"'“”‘’\-—–/\\]/g, "");
    }

    function answerFor(text) {
        var t = norm(text);
        if (!t) return null;
        var best = null, bestScore = 0;
        KB.forEach(function (item) {
            var score = 0;
            item.kws.forEach(function (kw) {
                if (t.indexOf(norm(kw)) >= 0) score++;
            });
            if (score > bestScore) { bestScore = score; best = item; }
        });
        if (best && bestScore > 0) return best;

        var hiWords = ["你好", "您好", "嗨", "哈喽", "hello", "hi", "在吗", "早上好", "晚上好", "中午好", "干嘛", "你是谁"];
        var hiHit = false;
        hiWords.forEach(function (h) { if (t.indexOf(norm(h)) >= 0) hiHit = true; });
        if (hiHit) {
            return {
                q: "你是谁？",
                a: "你好呀！我是 C小罗 ⚽ 绿茵慧眼系统的智能导览。\n\n· 想了解系统功能 → 问我「怎么评估球员」「什么是潜力预测」\n· 想聊足球知识 → 问我「什么是越位」「五大联赛」\n· 想听故事 → 问我「2022世界杯」「介绍下梅西」\n\n也可以点下方的快捷问题试试 👇"
            };
        }
        return null;
    }

    var FALLBACK =
        "这个问题我暂时还不会 😅\n\n不过我可以帮你了解这些，点下方的问题就能快速问：\n\n🏟️ 系统功能：怎么评估球员、潜力预测、风格聚类\n⚽ 足球知识：越位、点球、阵型、五大联赛\n🏆 世界杯与球星：2022世界杯、梅西、C罗、伊斯坦布尔奇迹\n\n换个问法，或者点下面的快捷问题试试～";

    var QUICK_QUESTIONS = [
        "这个系统能做什么？", "怎么评估球员？", "什么是潜力预测？",
        "什么是越位？", "什么是点球？", "五大联赛有哪些？",
        "2022世界杯发生了什么？", "介绍下梅西", "介绍下C罗"
    ];

    /* ---------------- UI ---------------- */
    var msgsBox, inputEl, sendBtn, panel, floatBtn, tip;

    function el(tag, cls, html) {
        var node = document.createElement(tag);
        if (cls) node.className = cls;
        if (html !== undefined) node.innerHTML = html;
        return node;
    }

    function buildUI() {
        var css = document.createElement("link");
        css.rel = "stylesheet";
        css.href = "css/assistant.css";
        document.head.appendChild(css);

        // 悬浮按钮
        floatBtn = el("button", "xl-float-btn", '<img src="' + AVATAR + '" alt="C小罗">');
        floatBtn.title = "C小罗 · 智能导览";
        document.body.appendChild(floatBtn);

        // 引导气泡
        tip = el("div", "xl-tip");
        tip.textContent = "我是 C小罗 ⚽ 点我了解系统用法，还能聊足球和世界杯～";
        document.body.appendChild(tip);

        // 面板
        panel = el("div", "xl-panel");
        panel.innerHTML =
            '<div class="xl-head">' +
            '  <div class="xl-avatar"><img src="' + AVATAR + '" alt="' + NAME + '"></div>' +
            '  <div class="xl-title"><div class="name">' + NAME + '</div><div class="sub">' + SUB + '</div></div>' +
            '  <button class="xl-close" title="收起">×</button>' +
            '</div>' +
            '<div class="xl-msgs"></div>' +
            '<div class="xl-inputbar">' +
            '  <input type="text" placeholder="问我点什么…（回车发送）" autocomplete="off">' +
            '  <button class="xl-send">发送</button>' +
            '</div>';
        document.body.appendChild(panel);

        msgsBox = panel.querySelector(".xl-msgs");
        inputEl = panel.querySelector("input");
        sendBtn = panel.querySelector(".xl-send");
        var closeBtn = panel.querySelector(".xl-close");

        // 事件
        floatBtn.addEventListener("click", toggle);
        closeBtn.addEventListener("click", hide);
        sendBtn.addEventListener("click", function () { send(inputEl.value); });
        inputEl.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(inputEl.value); }
        });
        // 点面板外收起面板
        document.addEventListener("click", function (e) {
            if (panel.classList.contains("open") &&
                !panel.contains(e.target) && e.target !== floatBtn && !floatBtn.contains(e.target)) {
                hide();
            }
        });

        // 首次引导气泡（每个浏览器只弹一次）
        try {
            if (!localStorage.getItem("xl_tip_shown")) {
                setTimeout(function () { tip.classList.add("show"); }, 1200);
                setTimeout(function () { tip.classList.remove("show"); }, 7000);
                localStorage.setItem("xl_tip_shown", "1");
            }
        } catch (e) { /* localStorage 不可用时忽略 */ }
    }

    function toggle() {
        if (panel.classList.contains("open")) hide();
        else show();
    }

    function show() {
        panel.classList.add("open");
        tip.classList.remove("show");
        if (!msgsBox.childElementCount) {
            var welcome =
                "Hola～我是 C小罗 ⚽\n绿茵慧眼系统的智能导览！\n\n" +
                "我可以：\n🏟️ 教你系统怎么用\n⚽ 科普足球规则知识\n🏆 讲世界杯和球星故事\n\n" +
                "直接输入问题，或点下面的快捷问题试试 👇";
            addMsg("bot", welcome, QUICK_QUESTIONS);
        }
        inputEl.focus();
        scrollBottom();
    }

    function hide() {
        panel.classList.remove("open");
    }

    function scrollBottom() {
        msgsBox.scrollTop = msgsBox.scrollHeight;
    }

    /* ---------------- 消息 ---------------- */
    function addMsg(who, text, chips) {
        var row = el("div", "xl-msg " + who);
        if (who === "bot") {
            var ava = el("div", "mini-ava", '<img src="' + AVATAR + '" alt="">');
            row.appendChild(ava);
        }
        var bubble = el("div", "bubble");
        bubble.textContent = text;
        row.appendChild(bubble);
        msgsBox.appendChild(row);

        if (chips && chips.length) {
            var chipWrap = el("div", "xl-chips");
            chips.forEach(function (q) {
                var c = el("button", "xl-chip", q);
                c.addEventListener("click", function () { send(q); });
                chipWrap.appendChild(c);
            });
            row.appendChild(chipWrap);
        }
        scrollBottom();
        return row;
    }

    function addTyping() {
        var row = el("div", "xl-msg bot");
        var ava = el("div", "mini-ava", '<img src="' + AVATAR + '" alt="">');
        var bubble = el("div", "bubble");
        bubble.textContent = "…";
        row.appendChild(ava);
        row.appendChild(bubble);
        msgsBox.appendChild(row);
        scrollBottom();
        return bubble;
    }

    var busy = false;
    function send(raw) {
        var text = String(raw || "").trim();
        if (!text || busy) return;
        addMsg("user", text);
        inputEl.value = "";
        scrollBottom();
        busy = true;
        sendBtn.disabled = true;

        var hit = answerFor(text);
        var answer = hit ? hit.a : FALLBACK;
        var chips = null;
        var t = norm(text);
        if (!hit) chips = QUICK_QUESTIONS;
        else if (t.indexOf("你是谁") >= 0 || t.indexOf("你叫什么") >= 0) chips = QUICK_QUESTIONS;

        var typing = addTyping();
        setTimeout(function () {
            typing.textContent = answer;
            var row = typing.parentNode;
            if (chips) {
                var chipWrap = el("div", "xl-chips");
                chips.forEach(function (q) {
                    var c = el("button", "xl-chip", q);
                    c.addEventListener("click", function () { send(q); });
                    chipWrap.appendChild(c);
                });
                row.appendChild(chipWrap);
            }
            scrollBottom();
            busy = false;
            sendBtn.disabled = false;
        }, 450 + Math.min(answer.length * 6, 800));
    }

    /* ---------------- 启动 ---------------- */
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", buildUI);
    } else {
        buildUI();
    }
})();
