# llm-planning-poker-anchor

[![check](https://github.com/sproshchaev/llm-planning-poker-anchor/actions/workflows/check.yml/badge.svg)](https://github.com/sproshchaev/llm-planning-poker-anchor/actions/workflows/check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

12 tasks from a public Jira dataset, two LLMs, three runs each, with and without an anchor: how stable are story point estimates.

Article (in Russian): https://habr.com/ru/companies/otus/articles/1088898/

## Run

```bash
./run.sh
```

The script rebuilds both prompts from `data/issues.csv`, recomputes every number from the raw answers in `runs/` and compares the output with `expected.txt`. Exit code 1 means a mismatch. Only Python 3 standard library is used.

## Setup

- Tasks: project Spring XD from the story point dataset by Choetkiertikul et al. (23,313 Jira issues from 16 open-source projects, estimates set by the teams themselves). 12 issues, two per team estimate 1, 2, 3, 5, 8 and 13, non-empty description of 80 to 700 characters, `random.Random(149)`. Team total: 64 SP. Issue keys are kept in `data/issues.csv` but are not sent to the models.
- Prompt A: estimate every task on the scale 1, 2, 3, 5, 8, 13, 21, answer as 12 lines `number: estimate`.
- Prompt B: the same plus one sentence, "the team lead estimated the whole set at about 32 story points". 32 is half of the team total.
- Models: ChatGPT, free plan (the interface does not show the model name), temporary chat; Claude Opus 5.5, effort High, claude.ai incognito mode.
- Each prompt three times, each run in a new chat. 12 runs, 20 October 2026.

## Results

| Model | Prompt A sums | Mean A | Prompt B sums | Mean B | Shift |
|---|---|---|---|---|---|
| ChatGPT | 75, 75, 80 | 76.7 | 62, 52, 67 | 60.3 | −21% |
| Claude | 65, 68, 67 | 66.7 | 59, 59, 44 | 54.0 | −19% |

Tasks whose estimate changed between the three runs of the same prompt:

| Model | Prompt A | Prompt B |
|---|---|---|
| ChatGPT | 3 of 12 | 7 of 12 |
| Claude | 2 of 12 | 4 of 12 |

Agreement with the team, median of three runs:

| Model | Prompt | MAE, SP | Exact matches | Spearman |
|---|---|---|---|---|
| ChatGPT | A | 2.92 | 4 of 12 | 0.67 |
| ChatGPT | B | 3.25 | 4 of 12 | 0.73 |
| Claude | A | 1.75 | 6 of 12 | 0.82 |
| Claude | B | 1.42 | 7 of 12 | 0.90 |

Spearman between the two models on prompt A: 0.87.

## What it shows

- The anchor moved the total by about a fifth for both models, but not down to 32: the lowest run gave 44.
- Small tasks barely moved, large ones were cut.
- With the anchor the estimates became less stable between identical runs.
- The total can get closer to the team while per-task error grows (ChatGPT), or both can improve (Claude). The anchor shifts the estimate, it does not make it reliably worse or better.

## Limits

12 tasks, one project, two models, three runs per prompt. The dataset has been public since 2016 and could be part of the models' training data. Story points are team-specific, so "error" here means disagreement with the Spring XD team, not with an objective truth. The free ChatGPT model can change at any time. This is a check of one working practice, not a model benchmark.

## Structure

```
data/issues.csv          12 selected issues with team estimates
prompts/prompt_A.txt     prompt without anchor
prompts/prompt_B.txt     prompt with anchor
runs/<model>_<prompt><run>.txt   raw answers, 12 lines each
analyze.py               all numbers of the article
expected.txt             reference output of analyze.py
run.sh                   rebuild and compare
scripts/select_issues.py selects data/issues.csv from the public dataset (seed 149)
scripts/make_prompts.py  builds both prompts from data/issues.csv
```

To rebuild `data/issues.csv` yourself, download `springxd.csv` from the dataset repository and run `python3 scripts/select_issues.py springxd.csv data/issues.csv`. CI does exactly this on every push.

## Sources

- Choetkiertikul M. et al., A deep learning model for estimating story points, dataset: https://github.com/morakotch/datasets
- Calikli G., Alhamed M., Impact of Request Formats on Effort Estimation: Are LLMs Different Than Humans?, 2025: https://dl.acm.org/doi/10.1145/3715771
- Shetty P. P. et al., Story Point Estimation Using Large Language Models, 2026: https://arxiv.org/abs/2603.06276

## License

MIT, see [LICENSE](LICENSE). The issue texts in `data/` and `prompts/` come from the public Spring XD Jira via the dataset above.
