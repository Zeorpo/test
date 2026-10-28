# Independent test of the router skill (Claude following it)

The script in `../router.py` is a stand-in. This folder tests the real thing: fresh sub-agents that have only `CLAUDE.md`
and `skills/art-router/SKILL.md`, and route prompts without seeing any label.

## Procedure (2026-10-28)

1. The 64 `holdout` prompts (written before the router skill existed and never used for tuning) were shuffled (seed 7)
   into four unlabelled files, `prompts_0..3.json` (16 each).
2. A copy of `CLAUDE.md` and `skills/` (router skill sha256 prefix `8d91db10fcbe6817` at the time) was placed in a separate folder. Labels live in
   `tests/router/cases.json`, outside that folder.
3. Four fresh general-purpose sub-agents ran in parallel, one per file, each told: read only `CLAUDE.md` and the router
   skill, decide whether the router applies, and give stage, lead skill, 0-3 supporting skills and a defect flag as the
   skill instructs; do not answer the prompts; do not run scripts to classify; do not look outside the folder.
4. They wrote `out_0..3.json`. Each used five tool calls (reads and one write). Their transcripts contain no mention
   of `cases.json`.
5. `score.py` applies the same scoring rules as `run_tests.py`.

## Result

| Metric (56 on-topic prompts unless noted) | Sub-agents following the skill | Script (`router.py`), same prompts |
|---|---|---|
| Lead skill | **56/56 = 100%** | 45/56 = 80% |
| Stage | 52/56 = 93% | 36/56 = 64% |
| Defect flag | 55/56 = 98% | 52/56 = 93% |
| Off-topic prompts declined (8) | 8/8 | 3/8 |
| Declines that were correct | 8/8 | 3/9 |

Declared targets for a fresh set were lead 85%, stage 75%, defect 80%; all are met. Misses (5): M02 (draw a box in
perspective before modeling: said blockout, label brief), M30 (laying out a village: blockout vs modeling), M46 (dynamic
shadows on mobile: light vs engine), M52 (check assets before publish: tooling vs publish), and a defect flag on M45.
Four of five are stage calls where both answers are defensible.

## Limits of this test

- One run per prompt, 64 prompts: 100% means "no misses observed", not "never wrong" (a 95% interval for the lead-skill
  rate is roughly 94% to 100%).
- The prompts, labels and router text were written by the same author, and the agents are the same model family as the
  author. A test with prompts and labels from other people would be stronger.
- The agents read only the router skill, not the lead skills, so this tests routing and not whether the lead skills then
  give good answers.
- The router text was not edited in response to these results. If it is edited, this set stops being clean: write a
  new set.
