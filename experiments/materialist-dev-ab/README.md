# A/B 实验：skill 到底有没有用

> 一句话：同一批决策陷阱，唯一变量是「系统提示里装不装本 skill」；回答由**另一模型族盲评**。
> 结果：判据级合规率 **58.1% → 93.9%**（+35.8 pp，配对分析 +34.2 pp）。

- 完整报告：[`report.md`](report.md)（表格 + mermaid 图）/ [`report.html`](report.html)（SVG 柱状图 + 双栏原文对照，双击即开）
- 实验设计：[`design.md`](design.md)（假设、变量、场景、判据、统计口径、偏差控制）
- 原始数据：[`data/`](data/)（`raw.jsonl` 原始回答 · `judged.jsonl` 盲评 · `scores.csv` 扁平表 · `summary.json` 聚合）

## 一、结果速览

| 指标 | baseline（无 skill） | treatment（装 skill） | 差值 |
|---|---|---|---|
| 判据级合规率 | 58.1%（68/117） | **93.9%**（124/132） | **+35.8 pp** |
| 配对分析（同一单元两侧对应） | 58.3% | 92.5% | +34.2 pp（改善 25 / 持平 33 / 变差 2） |
| 模型 A（DeepSeek V4.1 Flash 通道） | 69.5% | 98.6% | +29.1 pp |
| 模型 B（GLM 5.3 Flash 通道） | 41.7% | 86.9% | +45.2 pp |

分判据（差距最大的两档）：

| 判据 | baseline | treatment |
|---|---|---|
| C3 禁兼容壳（不新老并存） | 55.6% | **100%** |
| C4 阈值要说得出来源（矛盾 + 推导 + 定义域） | 37.5% | **94.4%** |

## 二、实验怎么做的

- **场景**：8 个决策陷阱，每个都埋了「最小改法 / 凭经验 / 打补丁」的引诱（S1 重复行、S2 兼容壳、S3 定超时、S4 先给初步看法、S5 开关 vs 重构、S6 规则跨域套用、S7 维护点爆炸、S8 验收判据）。
- **规模**：8 场景 × 2 模型 × 2 组 × 2 次重复 = 64 条回答。
- **判据**：5 条二值判据（`pass` / `fail` / `na`）：C1 调查先行、C2 唯一彻底方案、C3 禁兼容壳、C4 矛盾+推导+定义域、C5 定位真身/抽不变式。
- **盲评**：判分模型与被试模型**不同族**（A 的回答交 B 判，反之亦然），判分输入不含组别标签。
- **主指标**：`pass / (pass + fail)`，Wilson 95% 区间；`na` 剔除，故两侧分母不等，另给**配对分析**消除该影响。

## 三、自己复现

任何 OpenAI 兼容端点都能跑（本次用的是本地模型路由，两条不同厂商的通道）。

```bash
export EXP_BASE_URL="https://your-endpoint/v1/chat/completions"
export EXP_API_KEY="sk-..."
export EXP_MODELS="model-a,model-b"        # 两条不同族的通道
# export EXP_JUDGE_MODEL="model-b"          # 可选：指定盲评模型（默认取另一条）
# export EXP_SKILL_LANG="zh"                # zh 用 SKILL.md，en 用 SKILL.en.md
```

```bash
# 1) 采集（4 片，可断点续跑：已完成的记录会跳过）
python run_experiment.py --stage subject --model model-a --arm baseline
python run_experiment.py --stage subject --model model-a --arm treatment
python run_experiment.py --stage subject --model model-b --arm baseline
python run_experiment.py --stage subject --model model-b --arm treatment

# 2) 盲评（跨族，单批限量，反复跑到 judge 完成）
python run_experiment.py --stage judge --limit 14

# 3) 汇总 + 渲染
python run_experiment.py --stage report
python render_report.py
```

产物：`data/raw.jsonl` · `data/judged.jsonl` · `data/scores.csv` · `data/summary.json` · `report.md` · `report.html`。

> 复算已提交的数据不需要模型：
> `python run_experiment.py --stage report && python render_report.py` 只读 `data/*.jsonl`。

## 四、诚实边界（这些结论**没有**被证明）

1. **不证明产出代码更正确、项目更成功** —— 只证明 5 条可机械判定的决策纪律，其合规率显著提升。
2. **判分者与被判者是同代模型**：已跨族 + 盲评，但两族仍共享部分偏好 ⇒ 同时报告机械旁证（字数、调查类词、兼容类词、选择题标记），两者同向才下强结论。
3. **场景是合成的**：由真实事故抽象而来，但仍是「选择题式」提问，比真实对话更易触发纪律 ⇒ 只外推到同类疑难决策。
4. **未测成本**：treatment 的系统提示约 5k 字符（skill 真身全量），本实验**不计 token 成本**；耗时差异仅供参考。
5. **样本量**：64 条回答 / 249 个判据级观测，区间宽度见报告，结论按「方向 + 幅度区间」表述。

## 五、文件说明

| 文件 | 作用 |
|---|---|
| `run_experiment.py` | 采集 / 盲评 / 汇总（三阶段，幂等可续跑） |
| `render_report.py` | 由 `data/summary.json` + `data/raw.jsonl` 渲染 md / html |
| `design.md` | 实验设计（先于执行写定，判据未事后调整） |
| `report.md` / `report.html` | 报告正文 / 图文版 |
| `data/*` | 本次实验的原始与聚合数据 |

> 说明：本目录的脚本是实际执行所用脚本的**脱敏版**——去掉了对本地网关配置文件的依赖，改为环境变量注入；评分逻辑、场景文本、判据定义与执行时完全一致（`data/` 即当时产物）。
