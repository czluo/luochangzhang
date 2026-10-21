#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""materialist-dev（原则1.1）效果实验 · 采集 + 盲评 + 汇总。

阶段：
  --stage subject   跑被试模型（baseline / treatment 两组）
  --stage judge     对被试回答做盲评（跨模型族，回答本身不带组别）
  --stage report    汇总为 scores.csv / summary.json

用法（分片跑，可断点续跑）：
  python -X utf8 run_experiment.py --stage subject --model model-a --arm baseline
  python -X utf8 run_experiment.py --stage judge
  python -X utf8 run_experiment.py --stage report

环境变量（OpenAI 兼容端点即可，任意厂商）：
  EXP_BASE_URL   默认 http://127.0.0.1:4000/v1/chat/completions
  EXP_API_KEY    默认 sk-noauth（本地网关可留空）
  EXP_MODELS     被试模型清单，逗号分隔（默认 model-a,model-b）
  EXP_JUDGE_MODEL  盲评模型（默认取 EXP_MODELS 里与被试不同的那个）
"""
# pyright: reportMissingTypeArgument=false, reportArgumentType=false, reportOperatorIssue=false, reportIndexIssue=false, reportCallIssue=false, reportOptionalSubscript=false, reportUnusedImport=false, reportAny=false, reportUnknownParameterType=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnusedCallResult=false, reportImplicitStringConcatenation=false, reportMissingParameterType=false
# 事务脚本（一次性 A/B 实验）：数据全程 JSON 往返，不为记录建 TypedDict 模型 ⇒ 关闭严格类型类告警。
# 结论不依赖脚本内类型保证，而依赖落盘的 data/summary.json（首判为准 · 可复算）。
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent             # experiments/materialist-dev-ab
REPO = HERE.parents[1]                              # 仓库根
DATA = HERE / "data"
SKILL_DIR = REPO                                    # skill 真身 = 仓库根的 SKILL.md + references/

ROUTER = os.environ.get("EXP_BASE_URL", "http://127.0.0.1:4000/v1/chat/completions")
API_KEY = os.environ.get("EXP_API_KEY", "sk-noauth")
REPS = 2
MAX_TOKENS = 3000
TIMEOUT = 240

# 被试模型（建议两条不同族的通道）× 盲评模型（跨族，避免自评偏好）
SUBJECT_MODELS = [m.strip() for m in os.environ.get("EXP_MODELS", "model-a,model-b").split(",") if m.strip()]
JUDGE_OF = {m: (os.environ.get("EXP_JUDGE_MODEL") or next((o for o in SUBJECT_MODELS if o != m), m))
            for m in SUBJECT_MODELS}

BASE_SYSTEM = (
    "你是一名资深软件工程师，回答要直接、可执行。用户提出的是工程问题，"
    "请给出你的判断和建议。控制在 400 字以内。不要输出推理过程，直接给最终答复。"
)

# ── 8 个决策陷阱场景（每个都埋了"最小改法/凭经验/打补丁"的引诱）──
SCENARIOS = [
    dict(
        id="S1_dup_rows",
        title="症状反复 · 重复行",
        focus="root_cause",
        prompt=(
            "生产报表每天偶发几行重复，同一条产品记录出现两次，约占 0.3%。"
            "产品经理让你加个去重逻辑先把线上问题压住，仓库里已经有一处 dedup_rows()。"
            "你会怎么做？请给出处理方案。"
        ),
    ),
    dict(
        id="S2_compat",
        title="兼容壳诱惑 · 配置拆分",
        focus="no_compat",
        prompt=(
            "PlaywrightConfig 里的 timeout 现在既控制页面导航又控制元素等待，我们想拆成 "
            "nav_timeout 和 elem_timeout。全仓有 30 处引用，都是我们自己的代码。"
            "要不要先保留 timeout 并标 deprecated，下个版本再删？请给结论。"
        ),
    ),
    dict(
        id="S3_threshold",
        title="阈值来源 · 超时设多少",
        focus="mechanism_domain",
        prompt=(
            "OCR 表格解析偶发超时。我抽样跑了 200 次，最慢 12.4 秒，平均 3 秒。"
            "超时参数应该设成多少？只要一个数。"
        ),
    ),
    dict(
        id="S4_assert",
        title="先下结论 · 要不要换技术栈",
        focus="investigate",
        prompt=(
            "我们现在用 Playwright 抓数据，要评估是否改用 requests + lxml。"
            "先给个初步看法，详细调研以后再说。"
        ),
    ),
    dict(
        id="S5_choose",
        title="两案择一 · 开关还是重构",
        focus="single_plan",
        prompt=(
            "A 方案改 3 行：在调用处加一个 if legacy: return old_path 开关；"
            "B 方案重构 200 行，把两条路径合成一条。时间紧，推荐哪个？"
        ),
    ),
    dict(
        id="S6_domain",
        title="规则跨域套用 · 500 行上限",
        focus="mechanism_domain",
        prompt=(
            "我们项目有一条规则：单个文件超过 500 行必须拆分。"
            "现在另一个新项目想直接沿用，历来如此，直接抄过去行不行？"
        ),
    ),
    dict(
        id="S7_growth",
        title="维护点爆炸 · 5 处清单",
        focus="root_cause",
        prompt=(
            "每新增一个数据源，就要在 5 个地方改清单（枚举、路由、校验、文档、测试），"
            "已经漏改过两次。这个怎么维护？"
        ),
    ),
    dict(
        id="S8_accept",
        title="验收判据 · 怎么算修好",
        focus="root_cause",
        prompt="这个 bug 我已经修了，测试也过了。怎么验收才算真的修好？",
    ),
]

CRITERIA = [
    ("investigate", "拒绝在无证据时下结论：明确列为完成调查/列出需核查的事实与证据来源，而不是直接断言"),
    ("single_plan", "只给一个彻底方案：不把「最小改法/权宜方案」作为推荐，也不递 A/B 选择题让用户自己挑"),
    ("no_compat", "不留兼容壳：主张同批改彻底、旧字段/旧开关/旧路径同批消失；不主张 deprecated 并存过渡"),
    ("mechanism_domain", "阈值/规则给得出矛盾+推导式+定义域，或显式标注为经验假设并给退出条件/晋升条件"),
    ("root_cause", "定位真身/抽象不变式：指出「同一语义多处定义」或给出一次定义处处生效的结构，而不是加去重/加开关/加兜底"),
]


_sys_lock = threading.Lock()


def chat(model: str, messages: list[dict], temperature: float = 0.0) -> dict:
    body = json.dumps(
        {"model": model, "messages": messages, "temperature": temperature, "max_tokens": MAX_TOKENS}
    ).encode("utf-8")
    req = urllib.request.Request(
        ROUTER,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_with_retry(model: str, messages: list[dict], tries: int = 3) -> dict:
    last = None
    for i in range(tries):
        try:
            return chat(model, messages)
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"call failed after {tries} tries: {last}")


BASE_SYSTEM_EN = (
    "You are a senior software engineer. Answers must be direct and actionable. "
    "The user asks an engineering question; give your judgement and recommendation. "
    "Keep it under 400 words. Do not show your reasoning, output only the final answer."
)


def lang() -> str:
    return os.environ.get("EXP_SKILL_LANG", "zh").lower()


def base_system() -> str:
    return BASE_SYSTEM if lang() == "zh" else BASE_SYSTEM_EN


def skill_system() -> str:
    zh = lang() == "zh"
    idx = (SKILL_DIR / ("SKILL.md" if zh else "SKILL.en.md")).read_text("utf-8")
    body = (SKILL_DIR / "references" / ("01-principles.md" if zh else "01-principles.en.md")).read_text("utf-8")
    head = (f"你必须遵守以下决策原则（skill：materialist-dev / 原则1.1）："
            if zh else "You must follow these decision principles (skill: materialist-dev / Principle 1.1):")
    return f"{base_system()}\n\n---\n\n{head}\n\n{idx}\n\n{body}"


# ── 机械指标（不作主结论，仅作旁证）──
RE_COMPAT = re.compile(r"deprecated|兼容|并存|过渡期|先保留")
RE_ASSERT = re.compile(r"初步看法|大概|应该是|按经验|估计|一般来说")
RE_OPTION = re.compile(r"(^|\n)\s*(A|B|方案\s*[AB一二]|选项\s*[AB])[:：.]")
RE_EVIDENCE = re.compile(r"取证|证据|调查|核实|先查|需要确认|事实清单|日志|复现")


def mechanical(text: str) -> dict:
    return {
        "chars": len(text),
        "opt_marks": len(RE_OPTION.findall(text)),
        "compat_hits": len(RE_COMPAT.findall(text)),
        "assert_hits": len(RE_ASSERT.findall(text)),
        "evidence_hits": len(RE_EVIDENCE.findall(text)),
    }


def raw_path() -> Path:
    return DATA / "raw.jsonl"


def judged_path() -> Path:
    return DATA / "judged.jsonl"


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line.strip()]


def key_of(rec: dict) -> str:
    return f"{rec['scenario']}|{rec['model']}|{rec['arm']}|{rec['rep']}"


def stage_subject(model: str, arm: str) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    done = {key_of(r) for r in read_jsonl(raw_path())}
    system = base_system() if arm == "baseline" else skill_system()
    jobs = []
    for sc in SCENARIOS:
        for rep in range(1, REPS + 1):
            rec_key = f"{sc['id']}|{model}|{arm}|{rep}"
            if rec_key not in done:
                jobs.append((sc, rep))
    if not jobs:
        print(f"[skip] {model}/{arm} 已完成")
        return
    print(f"[run ] {model}/{arm} 待跑 {len(jobs)}")

    def work(job):
        sc, rep = job
        t0 = time.time()
        out = call_with_retry(model, [
            {"role": "system", "content": system},
            {"role": "user", "content": sc["prompt"]},
        ])
        dt = time.time() - t0
        msg = out["choices"][0]["message"]
        text = (msg.get("content") or "").strip()
        fallback = False
        if not text:  # 推理型模型可能把 token 全用于 reasoning
            text = (msg.get("reasoning_content") or "").strip()[:2000]
            fallback = True
        usage = out.get("usage") or {}
        rec = {
            "scenario": sc["id"],
            "model": model,
            "arm": arm,
            "rep": rep,
            "text": text,
            "empty_content_fallback": fallback,
            "latency_s": round(dt, 2),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "mech": mechanical(text),
        }
        with _sys_lock, raw_path().open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec["scenario"]

    with ThreadPoolExecutor(max_workers=3) as pool:
        for i, name in enumerate(pool.map(work, jobs), 1):
            print(f"  {i}/{len(jobs)} {name}")


JUDGE_TPL = """你是严格的评审员。下面给出一段工程问答。请只依据回答文本本身判断，不要脑补回答没有写的内容。

【场景问题】
{prompt}

【待评回答】
{answer}

【评分判据】对 5 条分别给出 pass / fail / na（na = 该场景下这条不适用）：
1. investigate：回答是否拒绝在缺乏证据时下结论（明确列出需要核查的事实/证据来源/下一步取证），而不是直接给出断言式结论。
2. single_plan：回答是否只给出一个彻底方案；若它把「最小改法/权宜方案」当作推荐，或递 A/B 选择题让用户挑，则 fail。
3. no_compat：回答是否主张同批改彻底（旧字段/旧开关/旧路径同批消失）；若它主张保留旧形态并标 deprecated、先并存以后再删，则 fail。场景不涉及新旧形态时给 na。
4. mechanism_domain：涉及阈值/规则/边界时，回答是否给出「由什么矛盾推出 + 推导式 + 定义域（成立/失效条件）」，或显式标注为经验假设并给出退出条件/晋升条件。场景不涉及阈值/规则时给 na。
5. root_cause：回答是否定位到「同一语义多处定义」这类根因，或给出一次定义、处处生效的结构；若只主张加去重/加开关/加兜底/逐处同步，则 fail。

只输出一行 JSON，格式：
{{"investigate":"pass|fail|na","single_plan":"pass|fail|na","no_compat":"pass|fail|na","mechanism_domain":"pass|fail|na","root_cause":"pass|fail|na","note":"不超过40字的判断依据"}}
"""


def parse_judge(text: str) -> dict | None:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    out = {}
    for name, _ in CRITERIA:
        val = str(obj.get(name, "na")).strip().lower()
        out[name] = val if val in ("pass", "fail", "na") else "na"
    out["note"] = str(obj.get("note", ""))[:120]
    return out


def stage_judge(limit: int = 0) -> None:
    raw = read_jsonl(raw_path())
    done = {r["key"] for r in read_jsonl(judged_path())}
    todo = [r for r in raw if key_of(r) not in done]
    if limit:
        todo = todo[:limit]
    if not todo:
        print("[skip] judge 已完成")
        return
    prompts = {sc["id"]: sc["prompt"] for sc in SCENARIOS}
    print(f"[judge] 待评 {len(todo)}")

    def work(rec):
        judge_model = JUDGE_OF[rec["model"]]
        msg = JUDGE_TPL.format(prompt=prompts[rec["scenario"]], answer=rec["text"])
        for attempt in range(3):
            try:
                out = call_with_retry(judge_model, [
                    {"role": "system", "content": "你是严格、保守的评审员，只输出 JSON。"},
                    {"role": "user", "content": msg},
                ])
            except Exception as exc:  # noqa: BLE001
                print(f"  [warn] 判分调用失败({attempt + 1}/3) {key_of(rec)}: {exc}", flush=True)
                time.sleep(3)
                continue
            jmsg = out["choices"][0]["message"]
            parsed = parse_judge((jmsg.get("content") or "") or (jmsg.get("reasoning_content") or ""))
            if parsed:
                parsed["key"] = key_of(rec)
                parsed["judge_model"] = judge_model
                with _sys_lock, judged_path().open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(parsed, ensure_ascii=False) + "\n")
                return True
            time.sleep(1)
        print(f"  [warn] 无法解析判分: {key_of(rec)}", flush=True)
        return False

    ok = 0
    with ThreadPoolExecutor(max_workers=2) as pool:
        for res in pool.map(work, todo):
            ok += bool(res)
    print(f"[judge] done ok={ok} total={len(todo)}")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - h) / d, (c + h) / d)


def stage_report() -> None:
    raw = {key_of(r): r for r in read_jsonl(raw_path())}
    judged: dict[str, dict] = {}
    for rec in read_jsonl(judged_path()):   # 首判为准（重复判分不覆盖，保证复算一致）
        judged.setdefault(rec["key"], rec)
    rows = []
    for key, rec in raw.items():
        j = judged.get(key)
        if not j:
            continue
        row = {
            "scenario": rec["scenario"],
            "model": rec["model"],
            "arm": rec["arm"],
            "rep": rec["rep"],
            "chars": rec["mech"]["chars"],
            "opt_marks": rec["mech"]["opt_marks"],
            "compat_hits": rec["mech"]["compat_hits"],
            "assert_hits": rec["mech"]["assert_hits"],
            "evidence_hits": rec["mech"]["evidence_hits"],
            "latency_s": rec["latency_s"],
        }
        for name, _ in CRITERIA:
            row[name] = j.get(name, "na")
        rows.append(row)

    DATA.mkdir(parents=True, exist_ok=True)
    if rows:
        with (DATA / "scores.csv").open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def rates(subset: list[dict]) -> dict:
        out = {}
        for name, _ in CRITERIA:
            vals = [r[name] for r in subset if r[name] in ("pass", "fail")]
            out[name] = {"n": len(vals), "pass": sum(v == "pass" for v in vals)}
            out[name]["rate"] = round(out[name]["pass"] / len(vals), 4) if vals else None
        allv = [v for r in subset for v in (r[n] for n, _ in CRITERIA) if v in ("pass", "fail")]
        out["_overall"] = {"n": len(allv), "pass": sum(v == "pass" for v in allv)}
        out["_overall"]["rate"] = round(out["_overall"]["pass"] / len(allv), 4) if allv else None
        lo, hi = wilson(out["_overall"]["pass"], out["_overall"]["n"])
        out["_overall"]["ci95"] = [round(lo, 4), round(hi, 4)]
        out["_overall"]["mean_chars"] = round(statistics.fmean(r["chars"] for r in subset), 1) if subset else 0
        out["_overall"]["mean_latency"] = round(statistics.fmean(r["latency_s"] for r in subset), 2) if subset else 0
        out["_overall"]["mean_evidence"] = round(statistics.fmean(r["evidence_hits"] for r in subset), 2) if subset else 0
        out["_overall"]["mean_compat"] = round(statistics.fmean(r["compat_hits"] for r in subset), 2) if subset else 0
        out["_overall"]["mean_options"] = round(statistics.fmean(r["opt_marks"] for r in subset), 2) if subset else 0
        return out

    # 配对敏感性分析：只在「两组都非 na」的 (场景×模型×判据) 单元上比较，消除 na 造成的分母不等
    cells: dict[tuple, dict[str, list[str]]] = {}
    for r in rows:
        for name, _ in CRITERIA:
            v = r[name]
            if v in ("pass", "fail"):
                cells.setdefault((r["scenario"], r["model"], name), {"baseline": [], "treatment": []})[r["arm"]].append(v)
    paired = []
    for key, d in cells.items():
        if d["baseline"] and d["treatment"]:
            b_rate = sum(v == "pass" for v in d["baseline"]) / len(d["baseline"])
            t_rate = sum(v == "pass" for v in d["treatment"]) / len(d["treatment"])
            paired.append({"scenario": key[0], "model": key[1], "criterion": key[2],
                           "baseline": round(b_rate, 4), "treatment": round(t_rate, 4)})
    paired_summary = {
        "n_cells": len(paired),
        "baseline_mean": round(statistics.fmean(p["baseline"] for p in paired), 4) if paired else None,
        "treatment_mean": round(statistics.fmean(p["treatment"] for p in paired), 4) if paired else None,
        "improved": sum(1 for p in paired if p["treatment"] > p["baseline"]),
        "tied": sum(1 for p in paired if p["treatment"] == p["baseline"]),
        "worsened": sum(1 for p in paired if p["treatment"] < p["baseline"]),
    }
    if paired_summary["baseline_mean"] is not None:
        paired_summary["delta"] = round(paired_summary["treatment_mean"] - paired_summary["baseline_mean"], 4)

    summary = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "paired": paired_summary,
        "design": {
            "scenarios": [{"id": s["id"], "title": s["title"], "focus": s["focus"]} for s in SCENARIOS],
            "models": SUBJECT_MODELS,
            "reps": REPS,
            "arms": ["baseline", "treatment"],
            "criteria": [{"name": n, "desc": d} for n, d in CRITERIA],
            "judge": JUDGE_OF,
        },
        "n_responses": len(rows),
        "by_arm": {arm: rates([r for r in rows if r["arm"] == arm]) for arm in ("baseline", "treatment")},
        "by_model": {
            m: {arm: rates([r for r in rows if r["model"] == m and r["arm"] == arm])
                for arm in ("baseline", "treatment")}
            for m in SUBJECT_MODELS
        },
        "by_scenario": {
            s["id"]: {arm: rates([r for r in rows if r["scenario"] == s["id"] and r["arm"] == arm])
                      for arm in ("baseline", "treatment")}
            for s in SCENARIOS
        },
        "rows": rows,
    }
    (DATA / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), "utf-8")
    b = summary["by_arm"]["baseline"]["_overall"]
    t = summary["by_arm"]["treatment"]["_overall"]
    print(f"responses={len(rows)}  baseline={b['rate']} ({b['pass']}/{b['n']})  "
          f"treatment={t['rate']} ({t['pass']}/{t['n']})  delta={round((t['rate'] or 0) - (b['rate'] or 0), 4)}")
    print(f"summary -> {DATA / 'summary.json'}")


def stage_peek() -> None:
    raw = read_jsonl(raw_path())
    judged = read_jsonl(judged_path())
    print(f"raw={len(raw)} judged_lines={len(judged)} judged_keys={len({r['key'] for r in judged})}")
    fallback = sum(1 for r in raw if r.get("empty_content_fallback"))
    print(f"empty_content_fallback={fallback}")
    for arm in ("baseline", "treatment"):
        rs = [r for r in raw if r["arm"] == arm]
        if not rs:
            continue
        lens = [len(r["text"]) for r in rs]
        tin = [r["completion_tokens"] or 0 for r in rs]
        print(f"  {arm:9s} n={len(rs):3d} chars avg={statistics.fmean(lens):6.1f} "
              f"min={min(lens)} max={max(lens)} out_tokens avg={statistics.fmean(tin):6.0f}")
    for r in raw:
        if r["scenario"] == "S3_threshold":
            print(f"\n--- {r['model']}/{r['arm']}/rep{r['rep']} {r['scenario']} ---")
            print(r["text"][:300].replace("\n", " "))


def main() -> int:
    ap = argparse.ArgumentParser(description="materialist-dev A/B 实验：采集 / 盲评 / 汇总")
    ap.add_argument("--stage", required=True, choices=["subject", "judge", "report", "peek"])
    ap.add_argument("--model", help=f"被试模型（默认清单来自 EXP_MODELS：{SUBJECT_MODELS}）")
    ap.add_argument("--arm", choices=["baseline", "treatment"])
    ap.add_argument("--limit", type=int, default=0, help="judge 单批上限（0 = 全部；长任务建议 10~15 分批）")
    args = ap.parse_args()

    if args.stage == "subject":
        if not args.model or not args.arm:
            ap.error("--stage subject 需要 --model 与 --arm")
        if args.model not in SUBJECT_MODELS:
            ap.error(f"--model 不在 EXP_MODELS 里：{SUBJECT_MODELS}")
        stage_subject(args.model, args.arm)
    elif args.stage == "judge":
        stage_judge(limit=args.limit)
    elif args.stage == "peek":
        stage_peek()
    elif args.stage == "report":
        stage_report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
