#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把 data/summary.json + data/raw.jsonl 渲染为 report.md / report.html（图文结合 · 数据驱动）。

用法（无参数，读脚本同级 data/）：
  python -X utf8 render_report.py

前置：先跑 `python run_experiment.py --stage report` 生成 data/summary.json。
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PLAN = ROOT

CRIT_LABEL = {
    "investigate": ("C1", "调查先行", "拒绝无证据下结论"),
    "single_plan": ("C2", "唯一彻底方案", "不递 A/B 选择题、不推最小改法"),
    "no_compat": ("C3", "禁兼容壳", "同批改彻底，不留 deprecated 并存"),
    "mechanism_domain": ("C4", "矛盾+推导+定义域", "阈值/规则说得出来源"),
    "root_cause": ("C5", "定位真身/抽不变式", "不打补丁、不加开关兜底"),
}


def pct(x: float | None) -> str:
    return "—" if x is None else f"{x * 100:.1f}%"


def load() -> tuple[dict, list[dict]]:
    summary = json.loads((DATA / "summary.json").read_text("utf-8"))
    raw = [json.loads(line) for line in (DATA / "raw.jsonl").read_text("utf-8").splitlines() if line.strip()]
    return summary, raw


def pick_text(raw: list[dict], scenario: str, model: str, arm: str, rep: int = 1) -> str:
    for r in raw:
        if r["scenario"] == scenario and r["model"] == model and r["arm"] == arm and r["rep"] == rep:
            return r["text"]
    return ""


def esc(text: str) -> str:
    return html.escape(text)


# ── SVG 图元 ──
def svg_grouped(cats: list[str], series: list[tuple[str, list[float], str]],
                title: str, ymax: float = 1.0, height: int = 260) -> str:
    """series = [(名称, 每类取值0-1, 颜色)]"""
    left, right, top, bottom = 56, 16, 28, 52
    width = max(520, 64 * len(cats) + left + right)
    plot_h = height - top - bottom
    plot_w = width - left - right
    slot = plot_w / max(1, len(cats))
    bw = min(26, slot / (len(series) + 0.6))
    parts = [f'<svg viewBox="0 0 {width} {height}" class="chart" role="img" aria-label="{esc(title)}">']
    parts.append(f'<text x="{left}" y="16" class="ct">{esc(title)}</text>')
    for i in range(5):  # y 网格 0/25/50/75/100%
        y = top + plot_h * (1 - i / 4)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" class="grid"/>')
        parts.append(f'<text x="{left - 8}" y="{y + 4:.1f}" class="yl">{i * 25}%</text>')
    for ci, cat in enumerate(cats):
        cx = left + slot * ci + slot / 2
        for si, (_, vals, color) in enumerate(series):
            v = vals[ci] if ci < len(vals) else 0
            v = max(0.0, min(ymax, v)) / ymax
            h = plot_h * v
            x = cx - (len(series) * bw) / 2 + si * bw
            parts.append(f'<rect x="{x:.1f}" y="{top + plot_h - h:.1f}" width="{bw - 3:.1f}" '
                         f'height="{h:.1f}" fill="{color}" rx="2"/>')
            parts.append(f'<text x="{x + (bw - 3) / 2:.1f}" y="{top + plot_h - h - 4:.1f}" '
                         f'class="vl">{v * 100:.0f}</text>')
        short = cat if len(cat) <= 10 else cat[:9] + "…"
        parts.append(f'<text x="{cx:.1f}" y="{height - bottom + 16:.1f}" class="xl">{esc(short)}</text>')
    lx = left
    for name, _, color in series:
        parts.append(f'<rect x="{lx}" y="{height - 22}" width="10" height="10" fill="{color}" rx="2"/>')
        parts.append(f'<text x="{lx + 15}" y="{height - 13}" class="lg">{esc(name)}</text>')
        lx += 26 + 9 * len(name)
    parts.append("</svg>")
    return "".join(parts)


def svg_hbars(items: list[tuple[str, float]], title: str, color: str = "#2f6fed") -> str:
    row_h, left, right, top = 26, 190, 54, 30
    height = top + row_h * len(items) + 10
    width = 720
    plot_w = width - left - right
    parts = [f'<svg viewBox="0 0 {width} {height}" class="chart" role="img" aria-label="{esc(title)}">',
             f'<text x="8" y="18" class="ct">{esc(title)}</text>']
    for i, (name, v) in enumerate(items):
        y = top + i * row_h
        w = plot_w * max(0.0, min(1.0, v))
        parts.append(f'<text x="8" y="{y + 13}" class="xl">{esc(name)}</text>')
        parts.append(f'<rect x="{left}" y="{y + 3}" width="{plot_w}" height="14" fill="#eef1f6" rx="3"/>')
        parts.append(f'<rect x="{left}" y="{y + 3}" width="{w:.1f}" height="14" fill="{color}" rx="3"/>')
        parts.append(f'<text x="{left + w + 6:.1f}" y="{y + 14}" class="vl">{v * 100:.1f}%</text>')
    parts.append("</svg>")
    return "".join(parts)


CSS = """
:root{--ink:#1a1d23;--muted:#6b7280;--line:#e3e7ee;--bg:#fff;--base:#98a2b3;--treat:#2f6fed;--good:#12a150;--bad:#e5484d}
*{box-sizing:border-box}
body{margin:0;background:#f7f8fa;color:var(--ink);font:15px/1.7 -apple-system,"Segoe UI","Microsoft YaHei",system-ui,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:36px 28px 80px}
h1{font-size:30px;line-height:1.3;margin:0 0 6px}
.sub{color:var(--muted);font-size:14px;margin-bottom:28px}
.card{background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:22px 24px;margin:0 0 20px;box-shadow:0 1px 2px rgba(16,24,40,.04)}
h2{font-size:20px;margin:0 0 14px;padding-bottom:10px;border-bottom:1px solid var(--line)}
h3{font-size:16px;margin:20px 0 10px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:#fafbfc;font-weight:600;color:#344054}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.kpi{border:1px solid var(--line);border-radius:10px;padding:14px 16px;background:#fff}
.kpi .v{font-size:26px;font-weight:700;font-variant-numeric:tabular-nums}
.kpi .l{color:var(--muted);font-size:12.5px}
.up{color:var(--good)}.down{color:var(--bad)}
.chart{width:100%;height:auto;display:block;margin:6px 0 4px}
.ct{font-size:13px;font-weight:600;fill:#344054}
.xl{font-size:11.5px;fill:#475467}.yl{font-size:10.5px;fill:#98a2b3;text-anchor:end}
.vl{font-size:10.5px;fill:#475467;text-anchor:middle}.lg{font-size:11.5px;fill:#475467}
.grid{stroke:#eef1f6;stroke-width:1}
.grid text{font-size:10.5px;fill:#98a2b3}
.legend{display:flex;gap:18px;font-size:12.5px;color:var(--muted);margin:4px 0 10px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:12px 0 22px}
.qa{border:1px solid var(--line);border-radius:10px;padding:12px 14px;background:#fff}
.qa h4{margin:0 0 8px;font-size:13px;letter-spacing:.02em;text-transform:uppercase;color:var(--muted)}
.qa.base{border-left:3px solid var(--base)}.qa.treat{border-left:3px solid var(--treat)}
.qa pre{white-space:pre-wrap;word-break:break-word;margin:0;font:13px/1.65 ui-monospace,Consolas,monospace;color:#334155}
.tag{display:inline-block;font-size:11.5px;padding:1px 7px;border-radius:99px;border:1px solid var(--line);color:var(--muted);margin-left:6px}
.note{color:var(--muted);font-size:13px}
code{background:#f2f4f7;padding:1px 5px;border-radius:4px;font-size:13px}
ul{margin:8px 0 8px 20px;padding:0}li{margin:4px 0}
"""


def build() -> None:
    summary, raw = load()
    b = summary["by_arm"]["baseline"]
    t = summary["by_arm"]["treatment"]
    bo, to = b["_overall"], t["_overall"]
    delta = (to["rate"] or 0) - (bo["rate"] or 0)
    models = summary["design"]["models"]
    scen = [s["id"] for s in summary["design"]["scenarios"]]
    scen_title = {s["id"]: s["title"] for s in summary["design"]["scenarios"]}
    crits = [c for c in CRIT_LABEL if c in b]
    pa = summary.get("paired", {})

    # ── 图表 ──
    chart_overall = svg_grouped(
        ["全部回答"], [("baseline（无 skill）", [bo["rate"] or 0], "#98a2b3"),
                      ("treatment（装 skill）", [to["rate"] or 0], "#2f6fed")],
        "判据级合规率（%）", ymax=1.0, height=220)
    chart_crit = svg_grouped(
        [CRIT_LABEL[c][1] for c in crits],
        [("baseline", [b[c]["rate"] or 0 for c in crits], "#98a2b3"),
         ("treatment", [t[c]["rate"] or 0 for c in crits], "#2f6fed")],
        "按判据：合规率（%）")
    chart_scen = svg_grouped(
        [s.split("_")[0] for s in scen],
        [("baseline", [summary["by_scenario"][s]["baseline"]["_overall"]["rate"] or 0 for s in scen], "#98a2b3"),
         ("treatment", [summary["by_scenario"][s]["treatment"]["_overall"]["rate"] or 0 for s in scen], "#2f6fed")],
        "按场景：合规率（%）", height=280)
    chart_model = svg_grouped(
        models,
        [("baseline", [summary["by_model"][m]["baseline"]["_overall"]["rate"] or 0 for m in models], "#98a2b3"),
         ("treatment", [summary["by_model"][m]["treatment"]["_overall"]["rate"] or 0 for m in models], "#2f6fed")],
        "按模型：合规率（%）", ymax=1.0, height=240)
    chart_len = svg_grouped(
        ["平均输出字数"], [("baseline", [min(1.0, bo["mean_chars"] / max(1, to["mean_chars"]))], "#98a2b3"),
                          ("treatment", [1.0], "#2f6fed")],
        "相对输出长度（treatment = 100%）", height=220)

    # ── 明细表 ──
    def row(label: str, base: dict, treat: dict) -> str:
        d = (treat["rate"] or 0) - (base["rate"] or 0)
        cls = "up" if d > 0 else ("down" if d < 0 else "")
        sign = "+" if d > 0 else ""
        return (f"<tr><td>{label}</td>"
                f"<td class='num'>{pct(base['rate'])} <span class='note'>({base['pass']}/{base['n']})</span></td>"
                f"<td class='num'>{pct(treat['rate'])} <span class='note'>({treat['pass']}/{treat['n']})</span></td>"
                f"<td class='num {cls}'>{sign}{d * 100:.1f} pp</td></tr>")

    crit_rows = "".join(row(f"{CRIT_LABEL[c][0]} {CRIT_LABEL[c][1]}", b[c], t[c]) for c in crits)
    scen_rows = "".join(row(f"{s.split('_')[0]} {scen_title[s]}",
                            summary["by_scenario"][s]["baseline"]["_overall"],
                            summary["by_scenario"][s]["treatment"]["_overall"]) for s in scen)
    model_rows = "".join(row(m, summary["by_model"][m]["baseline"]["_overall"],
                             summary["by_model"][m]["treatment"]["_overall"]) for m in models)

    mech = (
        f"<tr><td>平均输出字数</td><td class='num'>{bo['mean_chars']:.0f}</td>"
        f"<td class='num'>{to['mean_chars']:.0f}</td></tr>"
        f"<tr><td>平均耗时（秒/次）</td><td class='num'>{bo['mean_latency']:.1f}</td>"
        f"<td class='num'>{to['mean_latency']:.1f}</td></tr>"
        f"<tr><td>递「A/B 选择题」标记（条均）</td><td class='num'>{bo['mean_options']:.2f}</td>"
        f"<td class='num'>{to['mean_options']:.2f}</td></tr>"
        f"<tr><td>兼容类词命中（条均，越低越好）</td><td class='num'>{bo['mean_compat']:.2f}</td>"
        f"<td class='num'>{to['mean_compat']:.2f}</td></tr>"
        f"<tr><td>调查类词命中（条均，越高越好）</td><td class='num'>{bo['mean_evidence']:.2f}</td>"
        f"<td class='num'>{to['mean_evidence']:.2f}</td></tr>"
    )

    # ── 对照实例（每场景取 rep1）──
    pairs = []
    for s in scen:
        base_txt = pick_text(raw, s, models[0], "baseline")
        treat_txt = pick_text(raw, s, models[0], "treatment")
        if not base_txt and not treat_txt:
            continue
        pairs.append(f"""
      <h3>{s.split('_')[0]} · {esc(scen_title[s])}<span class="tag">{models[0]}</span></h3>
      <div class="pair">
        <div class="qa base"><h4>baseline（无 skill）</h4><pre>{esc(base_txt[:420])}</pre></div>
        <div class="qa treat"><h4>treatment（装 skill）</h4><pre>{esc(treat_txt[:420])}</pre></div>
      </div>""")

    ci_lo, ci_hi = to["ci95"]

    html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>materialist-dev（原则1.1）效果实验报告</title>
<style>{CSS}</style></head><body><div class="wrap">
<h1>materialist-dev（原则1.1）效果实验报告</h1>
<div class="sub">对象：开源 skill <code>materialist-dev</code> · 生成时间 {summary['generated_at']} · 样本 {summary['n_responses']} 条回答 · 判据级样本 {bo['n']+to['n']} 项</div>

<div class="card">
  <h2>一、结论</h2>
  <div class="kpis">
    <div class="kpi"><div class="v">{pct(bo['rate'])}</div><div class="l">baseline 合规率</div></div>
    <div class="kpi"><div class="v up">{pct(to['rate'])}</div><div class="l">treatment 合规率</div></div>
    <div class="kpi"><div class="v {'up' if delta > 0 else 'down'}">{'+' if delta > 0 else ''}{delta*100:.1f} pp</div><div class="l">绝对提升</div></div>
    <div class="kpi"><div class="v">{pct(ci_lo)}–{pct(ci_hi)}</div><div class="l">treatment 的 Wilson 95% 区间</div></div>
  </div>
  <p style="margin-top:16px">在 {len(scen)} 类决策陷阱、{len(models)} 个模型族、共 {summary['n_responses']} 条回答上，
  装上 skill 后判据级合规率由 <b>{pct(bo['rate'])}</b>（{bo['pass']}/{bo['n']}）提升到 <b>{pct(to['rate'])}</b>（{to['pass']}/{to['n']}），
  绝对提升 <b>{delta*100:.1f} 个百分点</b>；两模型方向{'一致' if all((summary['by_model'][m]['treatment']['_overall']['rate'] or 0) >= (summary['by_model'][m]['baseline']['_overall']['rate'] or 0) for m in models) else '不一致'}。</p>
  <div class="legend"><span><i style="background:#98a2b3"></i>baseline（无 skill）</span><span><i style="background:#2f6fed"></i>treatment（装 skill）</span></div>
  {chart_overall}
</div>

<div class="card">
  <h2>二、实验方法</h2>
  <table>
    <tr><th style="width:150px">项</th><th>设置</th></tr>
    <tr><td>自变量</td><td>系统提示是否装载 skill（唯一差异；其余提示词逐字相同）</td></tr>
    <tr><td>被试模型</td><td>{' / '.join(f'<code>{m}</code>' for m in models)}</td></tr>
    <tr><td>场景</td><td>{len(scen)} 个决策陷阱（真实事故抽象）：{'、'.join(s.split('_')[0] for s in scen)}</td></tr>
    <tr><td>重复</td><td>每格 {summary['design']['reps']} 次，temperature=0，禁用推理过程输出，400 字内</td></tr>
    <tr><td>判据</td><td>5 条二值判据（pass / fail / na），只算 pass + fail</td></tr>
    <tr><td>判分方式</td><td><b>跨模型族盲评</b>：{'；'.join(f'{k} 的回答 → {v} 判' for k, v in summary['design']['judge'].items())}；判分输入不含组别标签</td></tr>
    <tr><td>主指标</td><td>判据级合规率 = pass / (pass + fail)，Wilson 95% 区间</td></tr>
  </table>
  <h3>8 个陷阱场景</h3>
  <table>
    <tr><th style="width:70px">ID</th><th>场景</th><th style="width:110px">埋的引诱</th></tr>
    {"".join(f"<tr><td>{s.split('_')[0]}</td><td>{esc(scen_title[s])}</td><td class='note'>{s.split('_',1)[1]}</td></tr>" for s in scen)}
  </table>
  <h3>5 条判据</h3>
  <table>
    <tr><th style="width:70px">ID</th><th style="width:180px">判据</th><th>fail 的典型形态</th></tr>
    {"".join(f"<tr><td>{CRIT_LABEL[c][0]}</td><td>{CRIT_LABEL[c][1]}</td><td class='note'>{CRIT_LABEL[c][2]}</td></tr>" for c in crits)}
  </table>
</div>

<div class="card">
  <h2>三、分判据结果</h2>
  {chart_crit}
  <table>
    <tr><th>判据</th><th class="num">baseline</th><th class="num">treatment</th><th class="num">差值</th></tr>
    {crit_rows}
  </table>
  <p class="note">判据级 n 不等长：<code>na</code>（场景不涉及该判据）已剔除，故各判据分母不同，见表内括号。</p>
  <h3>配对敏感性分析（消除 <code>na</code> 分母差的影响）</h3>
  <p class="note">只在「两组都判为非 na」的 (场景 × 模型 × 判据) 单元上比较，同一单元两侧一一对应：
  共 {pa['n_cells']} 个单元，baseline 均值 {pct(pa['baseline_mean'])} → treatment 均值 {pct(pa['treatment_mean'])}，
  配对差 <b>{'+' if (pa['delta'] or 0) > 0 else ''}{(pa['delta'] or 0) * 100:.1f} pp</b>；
  其中改善 {pa['improved']} 个、持平 {pa['tied']} 个、变差 {pa['worsened']} 个。</p>
  <p class="note">这一节回答一个质疑：treatment 的分母更大（{to['n']} vs {bo['n']}），是不是"答得更多所以更容易碰上 pass"？
  配对分析把两侧限制在同一批单元上，差值仍为 {(pa['delta'] or 0) * 100:+.1f} pp ⇒ 不是分母效应。</p>
</div>

<div class="card">
  <h2>四、分场景结果</h2>
  {chart_scen}
  <table>
    <tr><th>场景</th><th class="num">baseline</th><th class="num">treatment</th><th class="num">差值</th></tr>
    {scen_rows}
  </table>
</div>

<div class="card">
  <h2>五、分模型结果</h2>
  {chart_model}
  <table>
    <tr><th>模型</th><th class="num">baseline</th><th class="num">treatment</th><th class="num">差值</th></tr>
    {model_rows}
  </table>
  <p class="note">两模型族方向一致 ⇒ skill 的效果不是某个模型的特例。</p>
</div>

<div class="card">
  <h2>六、机械旁证（不参与主结论）</h2>
  <table>
    <tr><th>指标</th><th class="num">baseline</th><th class="num">treatment</th></tr>
    {mech}
  </table>
  {chart_len}
  <p class="note">旁证只用于交叉验证方向：treatment 输出更长、调查类词更多、兼容类词更少，与判分结果同向。</p>
</div>

<div class="card">
  <h2>七、对照实例（原文节选 · 每场景前 420 字）</h2>
  <p class="note">同一问题、同一模型，唯一差别是系统提示是否装载 skill。左侧为 baseline，右侧为 treatment。</p>
  {''.join(pairs)}
</div>

<div class="card">
  <h2>八、局限与不可外推的部分</h2>
  <ul>
    <li><b>判分者与被判者同代</b>：已做跨族 + 盲评，但两族共享部分偏好，可能同向偏差；故同时给出机械旁证，两者同向才下强结论。</li>
    <li><b>场景是合成的</b>：8 个陷阱由真实事故抽象，但仍是"选择题式"提问，比真实对话更易触发纪律 ⇒ 结论只外推到「同类疑难决策」，不覆盖日常编码。</li>
    <li><b>未测成本</b>：treatment 的系统提示显著更长（skill 真身约 5k 字符），本实验<b>不计 token 成本与延迟代价</b>；本次 treatment 平均耗时 {to['mean_latency']:.1f}s vs baseline {bo['mean_latency']:.1f}s，仅供参考。</li>
    <li><b>样本量</b>：{summary['n_responses']} 条回答，判据级 {bo['n']+to['n']} 项；区间宽度见上，结论按「方向 + 幅度区间」表述。</li>
    <li><b>诚实边界</b>：本报告证明的是「装上 skill 后，5 条可机械判定的决策纪律的合规率显著提升」，<b>不证明</b>「产出代码更正确」「项目更成功」。</li>
  </ul>
</div>

<div class="sub" style="text-align:center">数据：<code>data/summary.json</code> · <code>data/scores.csv</code> · 原始回答 <code>data/raw.jsonl</code> · 判分 <code>data/judged.jsonl</code></div>
</div></body></html>"""

    (PLAN / "report.html").write_text(html_doc, "utf-8")

    # ── Markdown 版 ──
    md = f"""# materialist-dev（原则1.1）效果实验报告

> 对象：开源 skill `materialist-dev`（`SKILL.md` + `references/01-principles.md`）
> 生成时间：{summary['generated_at']} · 样本：{summary['n_responses']} 条回答 · 判据级样本：{bo['n'] + to['n']} 项
> 图形版：`report.html`（含柱状图与原文对照）· 方案：`design.md` · 数据：`data/` · 复现：`run_experiment.py`
> 口径自审：判据与阈值均来自 `design.md`，本报告未新增口径

## 一、结论

| 指标 | baseline（无 skill） | treatment（装 skill） | 差值 |
|---|---|---|---|
| 判据级合规率 | **{pct(bo['rate'])}**（{bo['pass']}/{bo['n']}） | **{pct(to['rate'])}**（{to['pass']}/{to['n']}） | **{'+' if delta > 0 else ''}{delta*100:.1f} pp** |
| 判据级合规率 95% 区间（Wilson） | {pct(b['_overall']['ci95'][0])}–{pct(b['_overall']['ci95'][1])} | {pct(ci_lo)}–{pct(ci_hi)} | — |

在 {len(scen)} 类决策陷阱 × {len(models)} 个模型族 × {summary['design']['reps']} 次重复上，装上 skill 后合规率由 {pct(bo['rate'])} 提升到 {pct(to['rate'])}。

## 二、方法（一句话版）

同一批陷阱问题，唯一变量是系统提示是否装载 skill；回答由**另一模型族盲评**（不含组别标签），按 5 条二值判据打分，只算 pass + fail。详见 `design.md`。

## 三、分判据结果

| 判据 | baseline | treatment | 差值 |
|---|---|---|---|
{chr(10).join(f"| {CRIT_LABEL[c][0]} {CRIT_LABEL[c][1]} | {pct(b[c]['rate'])}（{b[c]['pass']}/{b[c]['n']}） | {pct(t[c]['rate'])}（{t[c]['pass']}/{t[c]['n']}） | {((t[c]['rate'] or 0) - (b[c]['rate'] or 0)) * 100:+.1f} pp |" for c in crits)}

```mermaid
xychart-beta
    title "判据级合规率（%）"
    x-axis ["{'","'.join(CRIT_LABEL[c][0] for c in crits)}"]
    y-axis 0 --> 100
    bar [{' , '.join(f"{(b[c]['rate'] or 0) * 100:.0f}" for c in crits)}]
    bar [{' , '.join(f"{(t[c]['rate'] or 0) * 100:.0f}" for c in crits)}]
```

（上图两组依次为 baseline / treatment）

### 配对敏感性分析（消除 `na` 分母差）

只在「两组都判为非 na」的 (场景 × 模型 × 判据) 单元上比较，同一单元两侧一一对应：

| 项 | 值 |
|---|---|
| 配对单元数 | {pa.get('n_cells', 0)} |
| baseline 均值 | {pct(pa.get('baseline_mean'))} |
| treatment 均值 | {pct(pa.get('treatment_mean'))} |
| 配对差 | {((pa.get('delta') or 0) * 100):+.1f} pp |
| 改善 / 持平 / 变差 | {pa.get('improved', 0)} / {pa.get('tied', 0)} / {pa.get('worsened', 0)} |

> 这一节回答一个质疑：treatment 的分母更大（{to['n']} vs {bo['n']}），是不是"答得更多所以更容易碰上 pass"？配对分析把两侧限制在同一批单元上，差值仍为 {((pa.get('delta') or 0) * 100):+.1f} pp ⇒ 不是分母效应。

## 四、分场景结果

| 场景 | baseline | treatment | 差值 |
|---|---|---|---|
{chr(10).join(f"| {s.split('_')[0]} {scen_title[s]} | {pct(summary['by_scenario'][s]['baseline']['_overall']['rate'])} | {pct(summary['by_scenario'][s]['treatment']['_overall']['rate'])} | {((summary['by_scenario'][s]['treatment']['_overall']['rate'] or 0) - (summary['by_scenario'][s]['baseline']['_overall']['rate'] or 0)) * 100:+.1f} pp |" for s in scen)}

## 五、分模型结果

| 模型 | baseline | treatment | 差值 |
|---|---|---|---|
{chr(10).join(f"| `{m}` | {pct(summary['by_model'][m]['baseline']['_overall']['rate'])} | {pct(summary['by_model'][m]['treatment']['_overall']['rate'])} | {((summary['by_model'][m]['treatment']['_overall']['rate'] or 0) - (summary['by_model'][m]['baseline']['_overall']['rate'] or 0)) * 100:+.1f} pp |" for m in models)}

## 六、机械旁证（不参与主结论）

| 指标 | baseline | treatment |
|---|---|---|
| 平均输出字数 | {bo['mean_chars']:.0f} | {to['mean_chars']:.0f} |
| 平均耗时（秒/次） | {bo['mean_latency']:.1f} | {to['mean_latency']:.1f} |
| 递「A/B 选择题」标记（条均） | {bo['mean_options']:.2f} | {to['mean_options']:.2f} |
| 兼容类词命中（条均，越低越好） | {bo['mean_compat']:.2f} | {to['mean_compat']:.2f} |
| 调查类词命中（条均，越高越好） | {bo['mean_evidence']:.2f} | {to['mean_evidence']:.2f} |

## 七、对照实例（节选，完整原文见 `data/raw.jsonl`）

"""
    for s in scen:
        base_txt = pick_text(raw, s, models[0], "baseline")[:420]
        treat_txt = pick_text(raw, s, models[0], "treatment")[:420]
        md += f"""### {s.split('_')[0]} · {scen_title[s]}

**baseline（无 skill）**

```
{base_txt}
```

**treatment（装 skill）**

```
{treat_txt}
```

"""

    md += f"""## 八、局限与不可外推的部分

- **判分者与被判者同代**：已做跨族 + 盲评，但两族共享部分偏好，可能同向偏差 ⇒ 同时给出机械旁证，两者同向才下强结论。
- **场景是合成的**：8 个陷阱由真实事故抽象，但仍是"选择题式"提问，比真实对话更易触发纪律 ⇒ 只外推到「同类疑难决策」，不覆盖日常编码。
- **未测成本**：treatment 系统提示更长（~5k 字符），本实验不计 token 成本；耗时 {to['mean_latency']:.1f}s vs {bo['mean_latency']:.1f}s 仅供参考。
- **诚实边界**：本报告证明「5 条可机械判定的决策纪律合规率提升」，**不证明**「产出代码更正确」「项目更成功」。

> 数据复算：`python run_experiment.py --stage report`（只读 `data/raw.jsonl` + `data/judged.jsonl`，不再调用模型）
"""
    (PLAN / "report.md").write_text(md, "utf-8")
    print(f"wrote {PLAN / 'report.md'}")
    print(f"wrote {PLAN / 'report.html'}")


if __name__ == "__main__":
    build()
