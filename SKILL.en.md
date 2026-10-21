---
name: materialist-dev
description: Materialist decision principles for hard technical choices (a.k.a. "Principle 1.1"). Investigate before asserting; resolve the principal contradiction completely (root cause, single source of truth, no compatibility shells); locate the real object (law / conditional law / phenomenon, always with an explicit domain of validity); abstract so one definition holds everywhere. Use for hard technical decisions, choosing between two designs, setting thresholds / boundaries / rules, recurring symptoms, auditing the legitimacy of an existing rule, self-checking empiricism / dogmatism / rationalism, and fundamental review of plans or code changes.
---

# materialist-dev (Principle 1.1) — a materialist line of cognition for hard decisions

**The object comes first, the rule comes after; a rule must name the contradiction it resolves and state its domain of validity — if you cannot, it is a guess, and a guess must be labelled as one.**
**Route**: investigate (§2) → process the material → take hold of the principal contradiction (§3) → locate the real object (§4) → rise to law (§5) → return to practice for verification (the dissolution of the contradiction is the criterion) → re-examine the secondary contradiction → conditions change ⇒ know again.

## Situation → anchor (source of truth `references/01-principles.en.md` — **read it in full per situation**, ~150 lines, below the read-whole-file forbidden threshold; do not re-read within the same task, jump back by §N)

| What you are doing | Anchor (§N = main section) |
|---|---|
| About to state a conclusion / ruling / evaluation | **§2** Investigate before speaking; if you hesitate whether to verify ⇒ verify |
| Choosing between two designs; someone proposes "the smallest change / keep both for now, delete later" | **§3** Take the most thorough one; 🔴 no compatibility shells |
| Symptoms recur / you don't know how to solve it / you see duplicates or two sets of rules | **§4** Where is the real object? How many places define it? |
| Setting a threshold / boundary / rule; auditing an existing rule | **§4 law table** classify into three tiers + state the domain; no contradiction ⇒ it is a guess |
| Writing a rule after an incident / extracting shared logic | **§5** Define once, effective everywhere; three mechanically checkable criteria |
| Designing acceptance criteria / closing a plan | **§3** Acceptance asks whether the contradiction dissolved; re-examine secondary contradictions at the end |
| Applying an old rule / old experience to a new situation | **§6** Self-check against the three subjectivist variants |
| Re-reviewing code / reviewing someone else's change (plan or code) | **§7 + §4** The three mechanical questions; after fixing one case, check same-shaped cases + the external-cause chain |

🔴 **Three unconditional actions**: every conclusion carries evidence (§2) · offer exactly one thorough plan (§3) · pass the mechanical spot-check before publishing a plan (§7).

> Legend: 🔴 forbidden · ✅ positive example · ❌ negative example · ⚠️ caution. This skill governs **decision gating only**; run it alongside your team's own plan-review / code-review process, whose details follow your own standards.
