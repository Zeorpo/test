# Router tests: method and honest results

## What is tested

`router.py` is a deterministic stand-in for the procedure in `skills/art-router/SKILL.md`. It scores a prompt with
(1) hand-written keywords per skill and per stage (`routes.json`), plus (2) BM25 retrieval over the text of the skills
themselves (`index.py`), and returns a stage, a lead skill, supporting skills and whether the prompt describes a defect.
The skill itself is what Claude follows at run time; this script exists so that the routing table can be regression-tested
and so changes to the skills cannot silently break coverage.

## Cases

`cases.json` holds 364 labelled prompts in five splits. Each has a lead skill (plus acceptable alternatives), acceptable
stages, required supporting skills (where the task clearly needs one) and a defect flag.

| Split | Size | Role |
|---|---|---|
| `dev` | 72 | tuned on |
| `dev2` | 72 | written as a frozen holdout, then read and used for tuning |
| `dev3` | 72 | second fresh holdout, then read and used for tuning |
| `dev4` | 84 | third fresh holdout, then read and used for tuning |
| `holdout` | 64 | written before any tuning against it, frozen by `holdout.sha256`, **run once** |

Each time a holdout was read it became a tuning set and a new one was written first. `run_tests.py` refuses to run if
the frozen holdout changes.

## Results

First runs on each fresh holdout, before tuning on it:

| Holdout | Lead skill | Stage | Router version |
|---|---|---|---|
| fresh set 1 (now `dev3`) | 69% | 58% | keywords only (100% on its tuning set) |
| fresh set 2 (now `dev4`) | 76% | 63% | keywords + retrieval |
| fresh set 3 (`holdout`) | 73% (75% when re-run after the skills were upgraded) | 64% | keywords + retrieval + recall-first gate |

Declared targets for a fresh set: lead skill 85%, stage 75%, supporting skill 80%, defect flag 80%. Lead skill and stage
**missed** on all three. The defect flag passed (93-96%). Supporting-skill cases are too few to judge (11).
On the tuning sets the router scores 91% / 86%, which is the figure that overstates its real ability.

Because retrieval reads the text of `skills/*/SKILL.md`, **editing a skill can change routing**. That is intended (the router
follows the skills) but it means the holdout is only clean the first time it is run against a given version of the skills.

## Independent test of the skill itself

Fresh sub-agents given only `CLAUDE.md` and the router skill routed the same 64 held-out prompts without seeing labels:
lead skill 56/56 (100%), stage 52/56 (93%), defect flag 55/56 (98%), all 8 off-topic prompts declined with no wrong
declines. Targets (85% / 75% / 80%) were met. The script managed 80% / 64% / 93% on the on-topic subset. Method, limits and
the five misses: [llm_eval/README.md](llm_eval/README.md). This, not the script, is the evidence that the router works.

## Why the script falls short

- Natural prompts use words no list anticipated ("bones for a ponytail", "candle flame", "light a glass bottle").
- Many prompts span two stages; the label is a judgement and the script picks one.
- Word matching cannot tell on-topic from off-topic when the same word has two meanings ("bake a normal map" vs "bake a
  baguette", "rig a sailboat"). Best measured trade-off: about 54% of off-topic prompts declined, with about one decline
  in three being a wrongly declined 3D question. Those two numbers are reported as information only; deciding relevance
  is the router skill's section 0, not this script.

## Label changes made after seeing results (all on tuning sets)

D18, D35 and F09 were relabelled as describing a defect (they do); D61 and D62 were relabelled as spanning two
disciplines/stages; H37 was given a second acceptable stage. No holdout label was changed.

## Known contamination

The keyword lists were written by the same author as the prompts. Terms taken from prompts in a set were removed before
that set was first used as a holdout, but vocabulary overlap cannot be ruled out. The way to get an unbiased number is to
test on prompts someone else wrote: add them to `cases.json` as a new split and run once.

## Commands

```
python tests/router/run_tests.py tuning     # regression check, should pass
python tests/router/run_tests.py holdout    # generalisation, currently below target
python tests/router/router.py "bake a normal map from my high poly"
python tests/router/gen_table.py --write    # after editing routes.json
```
