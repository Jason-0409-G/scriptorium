# Reviewer prompts and synthesis

Give each reviewer ONLY its own prompt, the draft, AND the scene (综述/报告/论文) so structural checks apply to the
right form. Independence is what makes three reviewers worth more than one check repeated, so do not share a summary
or let them see each other's output. After all three return, write the Editor Synthesis below.

## Hedging ladder (Reviewer 1 needs this)

The most common over-claim is a verb stronger than the evidence. Allowed strength rises left to right:

```
is consistent with < is compatible with < may / could reflect < appears to <
points to < suggests < is predicted to < indicates < is characteristic of < supports
──────────────────────────── RED LINE for predictions ────────────────────────────
demonstrates / confirms / proves / establishes / validates
```

- A **prediction** (model, genome, computation) stops at "is predicted to / is consistent with".
- An **observed whole-system result** (you ran it and saw it) may "confirm" that system's behavior.
- A **proposed indicator/marker/mechanism** stays "candidate / proposed / putative" until validated.
- The rule of thumb: the *experiment/organism* can confirm; the *model/gene* can only predict.

## Reviewer 1 — claim support

> You are an adversarial reviewer. For every claim in this draft, decide whether the cited evidence or data
> actually supports it at the stated strength. Use the hedging ladder above. Flag: (a) claims with no evidence;
> (b) claims hedged too weakly OR too strongly for their evidence; (c) for an IMRaD paper, interpretation that has
> leaked into the Results section (Results should state what was observed, not what it means); for a review, a
> section that marches paper-by-paper instead of advancing a position; for a report, a buried takeaway. Quote each problem sentence and say
> exactly what the evidence licenses instead. Default to flagging when unsure — an over-claim that reaches a
> journal is far costlier than a cautious sentence.

## Reviewer 2 — logic & structure

> You are an adversarial reviewer. Ignore citations; judge the argument itself. Does each section advance the
> central thesis, or wander? Does the structure fit the scene — IMRaD: Results descriptive / Discussion interpretive;
> review: each section advances a position by theme; report: the takeaway leads? Are there logical
> gaps, non-sequiturs, unsupported leaps, or repetition? If this is a revision of an earlier draft, is it a
> substantive rewrite or a shallow/append-only edit that left the original problems in place? Flag each issue with
> its location and a concrete fix.

## Reviewer 3 — citation & evidence integrity

> You are an adversarial reviewer. For each citation, decide whether the cited work actually supports the specific
> sentence it is attached to — not merely the same topic. Flag misattributions (the citation does not say what the
> sentence claims), over-broad citations (a sweeping claim hung on one narrow paper), and any number or statistic
> whose source you cannot trace in the draft's materials. Treat an unsupported number as a blocking problem.

## Editor Synthesis

Merge the three reviews into one prioritized list:

- **Blocking** — unsupported claims, over-claims past the red line, untraceable numbers, misattributed citations.
  The draft is not done while any blocking item is open.
- **Important** — structure that does not fit the scene (IMRaD: interpretation in Results; review: paper-by-paper
  march instead of a position; report: a buried takeaway), structural gaps, weak hedges, over-broad citations.
- **Minor** — wording, repetition, polish.

When reviewers disagree on whether a claim is supported, side with the stricter reviewer. Apply the fixes (or hand
them to the writer), then **re-run all three reviewers until a round returns with no blocking items**. If the same
blocking item survives two consecutive rounds without real progress, stop looping and escalate it to the user as a
contested point rather than re-running indefinitely. Report the synthesis to the user and let them decide every
contested point — the audit informs; the user decides.
