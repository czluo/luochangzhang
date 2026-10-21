# materialist-dev · Principle 1.1

> A decision-gating skill for AI coding agents facing **hard technical choices**: investigate before asserting, resolve the principal contradiction thoroughly, locate the real object, and promote one-off fixes into invariants.
> Plain text, no runtime, drop-in. 中文版见 [README.md](README.md).

## What it treats

AI rarely fails at writing code; it fails at **judgement placement**:

| Typical behaviour | This skill's diagnosis |
|---|---|
| "Let me give a preliminary view and verify later" | violates §2 — no investigation, no right to speak |
| Hands you "Plan A: smallest change / Plan B: thorough" and asks you to choose | violates §3 — must output one thorough plan |
| Leaves `deprecated` parameters, compatibility shells, old-and-new coexisting | violates §3 — no backward compatibility |
| Recurring symptoms answered with de-duplication, feature flags, fallbacks | violates §4 — treats the phenomenon, not the contradiction |
| `TIMEOUT = measured_max * 2` promoted into a constant | violates §4 — a phenomenon boundary written as a universal constant |
| One special-case rule per new module | violates §5 — abstraction failed, maintenance points grow with scale |

## Three principles + one spot-check

| | Principle | In one line |
|---|---|---|
| §2 | Premise | Conclusions come only from reproducible evidence; hesitating whether to verify ⇒ verify |
| §3 | ① Principal contradiction | Take the most thorough of two designs; the old form must vanish in the same change; no compatibility shells |
| §4 | ② Locate the real object | Ask "how many places define this concept"; every rule must name its contradiction + domain |
| §5 | ③ Rise to law | Turn the incident into an invariant: zero new rules for new situations, maintenance points flat with scale |
| §6 | Self-check | The three subjectivist variants: empiricism / dogmatism / rationalism |
| §7 | Mechanical spot-check | For any threshold: which contradiction? which derivation? which domain? |

## Install

**CodeBuddy / Claude Code (skills directory)**

```bash
git clone https://github.com/czluo/materialist-dev.git ~/.codebuddy/skills/materialist-dev
# Claude Code: ~/.claude/skills/materialist-dev
# Shared inside a project: <repo>/.codebuddy/skills/materialist-dev
```

Windows (PowerShell):

```powershell
git clone https://github.com/czluo/materialist-dev.git "$HOME\.codebuddy\skills\materialist-dev"
```

**Other tools (Cursor / Cline / custom agents)**

- Paste `SKILL.en.md` (or `SKILL.md`) into your rules file or system prompt;
- When the full criteria are needed, let the model read `references/01-principles.en.md` (~150 lines, readable in one pass);
- Minimal version: the first nine lines of the skill file (general line + route) are already effective.

**Language**: `SKILL.md` + `references/01-principles.md` are Chinese; `SKILL.en.md` + `references/01-principles.en.md` are English. Install whichever the model is better at, or both.

## When it triggers

No command to remember — it loads on these situations (see the situation table in the skill file):

- hard bugs, recurring symptoms, the same problem fixed twice and still present
- choosing between two designs, "keep it compatible and delete it later"
- setting a threshold / timeout / cap / boundary value / parsing rule
- reviewing a plan or someone else's code change at the fundamental level
- suspecting you are concluding from experience

## Evidence (measured, not argued)

A real A/B run: 8 decision traps × 2 model families × 2 arms × 2 repetitions = 64 answers. The only variable is whether the skill is loaded into the system prompt; answers were scored by a **different model family** under blind conditions (no arm label in the judge input) against 5 mechanically checkable criteria.

| Metric | without skill | with skill |
|---|---|---|
| Criteria-level compliance | 58.1% (68/117) | **93.9%** (124/132) |
| Paired analysis (same cells both arms) | 58.3% | 92.5% |
| "Threshold must state its source" | 37.5% | **94.4%** |
| "No compatibility shells" | 55.6% | **100%** |

→ Report: [`experiments/materialist-dev-ab/report.md`](experiments/materialist-dev-ab/report.md) · HTML with charts [`report.html`](experiments/materialist-dev-ab/report.html) · Design [`design.md`](experiments/materialist-dev-ab/design.md) · Raw data + scripts [`experiments/`](experiments/)

**What this does not prove**: that the resulting code is more correct or that projects succeed more often. The scenarios are synthetic selection-style prompts (easier to trigger discipline than real conversations), judge and subject are same-generation models (shared preferences), and token cost is not measured. See section 4 of [`experiments/materialist-dev-ab/README.md`](experiments/materialist-dev-ab/README.md).

## Design trade-offs (why it is this short)

- The skill file (~26 lines) is an **index layer**: general line + 8-row situation table + three unconditional actions; negligible resident context cost;
- `references/01-principles.*` is the **source of truth**: the full criteria, read only when a situation matches, read in full, never truncated;
- Criteria are written to be **mechanically checkable** (greppable, countable definition sites, verifiable "old form gone in the same change"), to avoid principles that "look right but cannot be accepted".

## Repository layout

```
materialist-dev/
├── SKILL.md                     # index layer (zh)
├── SKILL.en.md                  # index layer (en)
├── references/
│   ├── 01-principles.md         # source of truth (zh)
│   └── 01-principles.en.md      # source of truth (en)
├── experiments/
│   └── materialist-dev-ab/      # A/B experiment: scripts + raw data + report (reproducible)
├── README.md / README.en.md
└── LICENSE
```

## What it is not

- not a code style guide (naming / formatting / layout belong elsewhere);
- not a process standard (review and release flows follow your own team's rules);
- it does not hand out answers — it forces you to state **the contradiction, the derivation, the domain**; if you cannot, you must label the rule as an assumption.

## License

MIT — see [LICENSE](LICENSE).
