# Signal Engine — public demo

Composite signal scoring, rebuilt from scratch on public data. Same mechanism
designed in a prior GTM engineering role for Amazon seller signal detection
(score real activity instead of buying a static contact list), applied fresh
here to open-source dev-tool companies using only GitHub's public API.

No employer code, data, or credentials used anywhere in this repo.

**Write-up:** https://aditya-chouhan.github.io/signal-engine-demo/

## Run it yourself

```
python3 signal_score.py
```

No API key required. Numbers will differ slightly from the write-up each time
you run it — GitHub's commit-activity data moves week to week, which is the
point: this is live, checkable data, not a fixed demo dataset.

## What it does

1. Pulls each repo's trailing 52-week commit activity from GitHub's public
   `/stats/commit_activity` endpoint.
2. Compares the last 4 weeks of commits to the 4 weeks before that.
3. Scores genuine acceleration; deceleration scores 0 rather than a
   fabricated negative — "no signal" is an honest answer, not a penalty.

## Closing the loop: `draft_outreach.py`

Scoring the signal is only half of "signal-based intent orchestration." This
second script takes the top-scoring company, pulls a few more real facts
(description, recent releases, recent commit subjects) via GitHub's API, and
has Claude draft a short, honest, diagnosis-style message grounded only in
those facts — never a generic pitch.

```
export ANTHROPIC_API_KEY=sk-ant-...
python3 draft_outreach.py
```

It only ever prints a draft. It does not send anything to anyone — the
design rule is AI drafts, a human approves every send.

Aditya Chouhan · ai.adityachouhan@gmail.com
