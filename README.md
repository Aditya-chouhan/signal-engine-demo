# Signal Engine — public demo

Composite signal scoring, rebuilt from scratch on public data. Same mechanism
designed for Sydon's Amazon Signal Engine (score real activity instead of
buying a static contact list), applied fresh here to open-source dev-tool
companies using only GitHub's public API.

No Sydon code, data, or credentials used anywhere in this repo.

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

Aditya Chouhan · ai.adityachouhan@gmail.com
