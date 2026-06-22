---
name: research-to-paper-audit
description: >-
  Adversarially review an academic draft with independent multi-reviewer rounds, depending on no other skill.
  It spawns three independent reviewer agents — claim-support, logic/structure, and citation/evidence integrity —
  each reading only its own prompt and the draft, then writes an Editor Synthesis and re-runs until a round comes
  back clean. It catches unsupported claims, claims drifted from their evidence tier, interpretation leaking into
  Results, shallow/append-only revisions, and citations that do not actually support the sentence. Use whenever
  the user has an EXISTING draft to peer-review or stress-test — this skill reviews a draft, it does NOT write a
  综述/review article; if the user has no draft yet and wants a review article written, use research-to-paper-write.
  Triggers: the user says 审一下这篇草稿, 多轮审, 帮我挑毛病, 查无据claim, 逻辑审一遍,
  这篇有没有过度声称, "review my draft", "audit this manuscript", "check for unsupported claims", "is anything
  overclaimed", "stress-test the argument". Works on a whole paper or a section; called by research-to-paper-write
  after drafting, or invoked directly on any draft.
---

# Audit — independent multi-reviewer adversarial review (self-contained)

A draft you wrote and also approve is not reviewed — you share its blind spots. Real review needs independence,
so this skill runs three reviewers who cannot see each other's work, then reconciles them. The most common reason
a manuscript fails peer review is a claim stronger than its evidence; this audit is built to catch exactly that
before a journal does.

## Workflow

1. **Dispatch three independent reviewers in parallel.** Spawn three Agent calls at once, each given ONLY its own
   prompt (from `references/audit-prompts.md`), the draft, AND the scene (综述/报告/论文) so structural checks apply
   to the right form — independence is the whole point, so do not let one reviewer see another's output or a shared
   summary. The three lenses are deliberately different:
   - **Reviewer 1 — claim support:** is every claim backed by its cited evidence at the stated strength? Are
     hedges matched to the evidence (a prediction stays "predicted"; only a measured whole-system result may
     "confirm")? Does the structure fit the scene — for an IMRaD paper, has interpretation leaked into Results;
     for a review, does a section march paper-by-paper instead of advancing a position; for a report, is the
     takeaway buried?
   - **Reviewer 2 — logic & structure:** does each section advance the thesis? Any gaps, non-sequiturs, repetition?
     Is this a substantive draft or a shallow/append-only edit?
   - **Reviewer 3 — citation & evidence integrity:** does each citation actually support its sentence (not just
     relate topically)? Any misattribution, over-broad citation, or untraceable number?

2. **Write the Editor Synthesis.** Merge the three reviews into one prioritized list — **blocking / important /
   minor**. When reviewers disagree about whether a claim is supported, defer to the stricter one; over-claiming is
   the costlier error. An unsupported number is always blocking.

3. **Fix, then re-run until clean.** Apply the fixes (or hand them to the writer), then run the audit again. Do not
   declare the draft done while any blocking item is open. One clean round, not one round, is the bar — the point
   of "多轮" is that fixing one issue often exposes another. If the same blocking item survives two consecutive
   rounds without real progress, stop looping and escalate it to the user as a contested point (step 4) rather than
   re-running indefinitely.

4. **Report to the user.** Show the synthesis and let the user decide on each contested point. The audit informs;
   the user has the final say on every claim.

When used inside the full workflow, run this after each draft revision in research-to-paper-write, before the
de-AI pass. Standalone, run it on any draft the user brings.

## Files

- `references/audit-prompts.md` — the three independent reviewer prompts and the Editor-Synthesis rules.
