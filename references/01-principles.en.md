# 01 · Source of truth (materialist-dev · Principle 1.1)

> Upstream: this skill's `SKILL.en.md` (index layer). This file is the **single source of truth** for "the premise + the three principles" (2026-10-21).
> **Writing contract (uniform slots)**: every principle = **theoretical anchor (one line, for reasoning to extend) → principle statement → operation (engineering action) → criteria (mechanically checkable) → counter-example / positive example**.
> Legend: 🔴 forbidden · ✅ positive example · ❌ negative example · ⚠️ caution. Philosophical formulations are standard paraphrases, not verbatim quotations.

## §1 General line and route of cognition

> **General line**: the object comes first, the rule comes after; the rule is determined by the object and in turn remakes it. A conclusion can only come from the object itself; a rule must be able to name the contradiction it reflects and state its domain of validity — if you cannot, it is a guess, and a guess must be labelled as one.
>
> **Route of cognition (spiral)**: investigate the object (§2) → process the material (discard the coarse, keep the fine; discard the false, keep the true; connect one thing to another; go from the surface to the interior) → take hold of the principal contradiction (§3) → locate the real object (§4) → rise to law (§5) → return to practice for verification (the dissolution of the contradiction is the criterion) → re-examine secondary contradictions → conditions change ⇒ investigate again, know again — repeated in cycles, each cycle reaching a higher level.
> 🔴 The reverse route (deriving the object from concepts or experience) is **subjectivism**, whatever it calls itself — experience, reason, or "the existing rule" (§6).

## §2 Premise: without investigation there is no right to speak

- **Theoretical anchor**: cognition happens after practice and has the object as its source — every assertion about an un-investigated object is a priori projection.
- **Principle statement**: 🔴 any conclusion / judgement / evaluation / ruling / plan must **already have completed its investigation** before it is written or spoken; if the investigation is incomplete ⇒ state only "to be checked (what exactly comes next)", do not produce a conclusion.
- **Operation**:
  1. List the "facts this conclusion depends on", annotating each with its evidence source (the file you read · the criteria script output you ran · the log line);
  2. Three admissible ways to obtain evidence: read the real artefact / run the criteria script / read the logs; ⚠️ when taking a baseline, take the newest artefact **by `mtime`** — taking an old artefact as baseline ⇒ you derive a problem that does not exist and then change the wrong place because of it;
  3. Entries without evidence ⇒ write "to be checked: check X"; 🔴 never write "probably / by experience".
- **Criteria**: every fact that enters a conclusion must come from **reproducible evidence acquisition**, never from inference, memory, or "probably".
  - 🔴 Violations (explicitly forbidden): "let me give a preliminary view and verify later" · "by experience it is probably X" · **un-evidenced arguments** of the form "it is expensive, so keep the status quo" — a preliminary view, once spoken, becomes someone's decision basis; **speaking first and evidencing later is a violation** (not "efficiency").
  - 🔴 When you hesitate "should I verify / should I take a look", the answer is yes.

## §3 Principle ① Take hold of the principal contradiction and resolve it thoroughly

- **Theoretical anchor**: a complex process is dominated by its principal contradiction; once it is resolved, the parties to the contradiction transform accordingly — change the phenomenon without changing the contradiction, and the contradiction only moves, it does not disappear.
- **Principle statement**: when choosing between two designs, take the one that **resolves it most thoroughly**; 🔴 never present "the smallest change / an expedient / let's do this for now" as the recommendation. 🔴 A phenomenon is the expression of a contradiction; changing the phenomenon without changing the contradiction ⇒ the contradiction moves, it does not vanish.
- **Operation (five steps for evaluating two designs)**:
  1. Write the **contradiction list**: how many contradictions does this problem have? Which is principal (it decides the process)?
  2. Annotate each design: does it remove the **contradiction itself** or only its **phenomenon**? Does the old form **disappear in the same change**? Do maintenance points grow or shrink?
  3. Output **one single plan** (🔴 do not hand over an "A minimal / B thorough" choice);
  4. Acceptance criteria state "is the original contradiction dissolved / is the condition for its transformation removed", 🔴 not "did the symptom disappear";
  5. **Close with two-point analysis**: after the plan lands, re-examine whether a secondary contradiction has risen to become the new principal one; 🔴 never "hit and run" — skipping transformation tracking is the source of the next round of "recurring symptoms".
- **Criteria**:
  - **Root cause removed** · **single source of truth** (one concept defined in exactly one place) · no leftover **second set of rules** / **dead fields** / **expired contracts** / **silent degradation paths** / 🔴 **backward-compatibility shells**.
  - 🔴 **No backward compatibility (change it thoroughly in one go)**: "backward compatibility / too many existing references / keep both and delete later / transition period" are never a **hard reason** — they are disguises for "not changing thoroughly"; a compatibility shell *is* a second set of rules (it drifts, it is misread, it stays forever). The test = **the old form must disappear in the same change** (old field / old parameter / old name / old shell / old identifier / old path / old value); 🔴 no "keep both and mark `deprecated` until next round".
  - **The only exception = external contracts**: cross-repository callers / already-published public APIs / upstream artefacts **cannot be changed in the same batch** ⇒ coexistence is allowed, but 🔴 you must register "exit condition + deadline" in the same change (unregistered coexistence = a permanent second set of rules). 🔴 Standards / documentation / internal structure have **no such exception** (there is no external contract to speak of).
  - **Three-piece kit for porting criteria from external artefacts** (operationalizing the exception; all three required): when porting criteria from an upstream artefact that **cannot be changed in the same batch**, deliver in the same change ① a **fingerprint baseline** (hash of the upstream original; any change ⇒ `FAIL`) ② a **differential guard** (run the upstream original over the same corpus and require 100% equivalence line by line) ③ a registered exit condition. 🔴 Copying the rules without ② ⇒ drift is invisible = a silent second set of rules.
  - **Judge the copy downstream actually consumes**: the data you judge / verify against must be **the one the consumer really receives**; 🔴 if the pipeline rewrites or wraps it ⇒ take **before ∪ after** (union) — looking at one end only guarantees missing a whole class of criteria that hold only in the other form.
  - **Verification is the dissolution of the contradiction**: the symptom gone while the contradiction remains = displacement, not a pass.
  - If a small change is still kept ⇒ it needs a **hard reason** for why thoroughness is impossible (external contract immutable · upstream artefact immutable · **evidence that the thorough plan costs more**).
  - ⚠️ Thorough ≠ maximum blast radius: you must still **gather evidence** for the real cost of the thorough plan (the thorough plan often turns out to have zero layout changes). (**Sublation**: what is eliminated is the old *form*; an already-verified behavioural core is **fully carried over** by the new form — carried over ≠ coexisting; the old form must still disappear in the same change.)
- **Counter-example / positive example**: ❌ duplicate rows in the output ⇒ add "de-duplication logic" downstream as a net (treats the phenomenon); ✅ find that "one meaning is defined in two places" ⇒ merge into a single source of truth and the duplicates vanish by themselves (treats the contradiction).

## §4 Principle ② Find the internal connection and locate the real object

- **Theoretical anchor**: the nature of an object is determined by its internal contradiction (the internal cause is the basis, the external cause is the condition); a phenomenon is the external expression of an essence, and the essence can be known through phenomena.
- **Principle statement**: when you do not know how to solve it, or symptoms recur, first ask: **where is the real object of this concept? How many places define it?** (The question is whether its internal determination has been split.)
- **Operation (four steps to locate the real object)**:
  1. **grep the definition sites**: search the symbol name / config key / rule text ⇒ list every definition point and count "how many";
  2. **>1 site ⇒ the internal determination has been split**: the essential problem is not the symptom but "one meaning defined in many places" ⇒ merge into a single source of truth and the symptom disappears by itself;
  3. **after fixing one case, always check same-shaped cases**: grep same-shaped calls / isomorphic code and confirm there is no same-class hazard;
  4. **after fixing one case, always check the external-cause chain**: upstream contract · environment · timing · data — the internal cause is the basis of change, the external cause is the condition of change; the root cause = the internal cause + the external conditions it depends on.
- **Criteria**:
  - Only when you can answer "where is the real object + **how many places** define it" have you located it; 🔴 never medicate a local symptom — patched-on de-duplication / added switches / added fallbacks **do not count as a solution**.
  - ✅ Positive example: duplicate rows appear in the output ⇒ do not fix "the de-duplication logic"; find out that "one meaning is defined in two places" ⇒ merge into a single source of truth and the duplicates vanish.

**Legitimacy criteria for rules / thresholds / boundaries / parsing criteria** (the core operation of ②)

> Every **rule / threshold / boundary / cap / parsing criterion** must answer: **what internal contradiction makes it necessarily exist? What is its domain of validity?**

| Answer | Classification | Treatment |
|---|---|---|
| The state **necessarily transitions** here (a **nodal point** of degree) · the contract is **exclusive** here · order and splitting are decided by the **mechanism** | **Law** (inferential) | Take the boundary from the derivation, no margin needed; 🔴 **must state the domain of validity** (conditions where it holds / fails) |
| The mechanism is nameable but **depends on specific conditions** (necessary when they hold, not necessarily otherwise) | **Conditional law** (relative truth) | Same: state the domain; 🔴 when conditions change ⇒ re-evaluate |
| Measured maximum × factor · the sample ran without incident · tried until it passed | **Phenomenon** (empirical) | **A quantification of ignorance, not knowledge** ⇒ explicitly mark `assumption (empirical)` + impact surface + **exit condition** + **promotion condition** (promote to law once the mechanism is found or coverage is sufficient) |

- 🔴 **Never write a phenomenon boundary as a universal constant** (treating "what I saw" as "what must be").
- 🔴 **Never apply across domains (dogmatism)**: before migrating a law / threshold into a new situation, check whether its domain still holds — if it does, use it; if not ⇒ go back to §2 and investigate again; 🔴 never apply it by "it has always been this way".
- 🔴 **Probability / statistics are legitimate only when "many factors and no determinate mechanism to follow"**, and must be labelled as **confidence**, not **mechanism**; using probability as a fallback when a mechanism exists = evading the contradiction, which is not a solution.
- **The verification method must match the type of assumption**: inferential assumptions verify "the criterion holds **on its domain**"; empirical ones can only reduce risk through **coverage at many points** and 🔴 must never claim to be "proven".

## §5 Principle ③ Rise from phenomenon to law: define once, effective everywhere

- **Theoretical anchor**: one practice yields the **particular**; a law is the **universal**; taking the particular directly as the universal = empiricism. Relative truth is tested in practice and advances toward absolute truth.
- **Principle statement**: distil one incident into a **reusable invariant**, so that rules and structures are **defined once and take effect everywhere**; 🔴 never write case details into a general rule.
- **Operation (four steps from incident to invariant)**:
  1. De-case it: delete one-off numbers / transaction instances / machine-specific names;
  2. Find the commonality: ask "which contradiction is the essence of this incident" ⇒ write it as an invariant / criterion (not another special-case rule);
  3. Self-check against the three criteria (below);
  4. Return to practice once: verify on a real new situation that "zero new rules" holds; only then has the abstraction landed.
- **Criteria (three, mechanically checkable)**: ① a new situation **needs no new rule** (covered by the existing abstraction) ② maintenance points **do not grow with scale** (e.g. "maintenance points for the version header are always 2") ③ the rule contains **no one-off number / transaction instance / machine-specific name**.
- **Counter-example / positive example**:
  - ❌ add one special-case rule per new module; every new file requires editing a list; write a measured number into a threshold.
  - ✅ abstract "the set of documents" as `references/*.md` ⇒ adding a document needs zero code change; collapse "the real object of the version header" into one place ⇒ maintenance points do not grow with the number of documents.

## §6 The three subjectivist variants (all violate this skill)

| Variant | What is wrong | Engineering form |
|---|---|---|
| **Empiricism** | takes the **observed form** as law | threshold = measured maximum × 2; rule = an induction over the current sample |
| **Dogmatism** | takes **relative truth as absolute truth** and drops the domain | old threshold / old rule applied straight to a new situation without checking conditions; "it has always been this way" / "the standard says so" replaces investigation |
| **Rationalism** | builds a self-consistent system **detached from the object** | abstraction for abstraction's sake / over-unification / fixing concepts first and forcing facts to fit |

> All three share one error: **taking the subjective order as the objective order**. Materialism knows one road only: investigate the object → find the contradiction → rise to law → return to practice for verification.
> ⚠️ The "high abstraction" of §5 **is not detachment from reality** — it demands extracting the commonality from a mass of particulars (induction, then verification in practice), not fixing a concept first and forcing facts to fit it.

## §7 Mechanical spot-check (one hit is enough to rule a violation)

> Take any constant / threshold / rule and ask three things: **what contradiction necessarily yields it? What is the derivation? What is the domain of validity (conditions where it holds / fails)?**
> Cannot name the contradiction or the derivation ⇒ it must be an **explicit assumption** (with impact surface + exit condition); otherwise it is a violation.
> Cannot name the domain ⇒ treat it as an **application across domains** violation (dogmatism).
