"""
Signal-based company prioritization — public demo.

Same composite-scoring mechanism designed for Sydon's Amazon Signal Engine
(rank collapse, Buy Box loss, review-velocity spikes), rebuilt from scratch
here on a different, fully public data source: GitHub's commit-activity API.

No Sydon code, data, or credentials used anywhere in this file. The concept
(detect real distress/growth signals instead of relying on a static contact
list) is the same; the implementation and data source are new.

Run it yourself: python3 signal_score.py
Every number below is reproducible against GitHub's public API at the time
you run it — commit velocity moves week to week, so re-running later will
give different (still real) numbers.
"""

import json
import time
import urllib.request

# A candidate set of small, funded, AI-native dev-tool companies —
# exactly the kind of account a GTM team would want to prioritize.
REPOS = [
    "mem0ai/mem0",
    "browser-use/browser-use",
    "e2b-dev/E2B",
    "langflow-ai/langflow",
    "crewAIInc/crewAI",
    "ComposioHQ/composio",
    "letta-ai/letta",
    "block/goose",
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "signal-engine-demo"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def commit_velocity_change(repo):
    """Weekly commit counts for the trailing 52 weeks -> % change,
    last 4 weeks vs. the 4 weeks before that. GitHub computes this
    stats endpoint async, so retry until it's ready (202 = still computing)."""
    activity = []
    for _ in range(4):
        activity = fetch(f"https://api.github.com/repos/{repo}/stats/commit_activity")
        if isinstance(activity, list) and len(activity) == 52:
            break
        time.sleep(3)
    if not activity or len(activity) != 52:
        return None, None, None
    last4 = sum(w["total"] for w in activity[-4:])
    prev4 = sum(w["total"] for w in activity[-8:-4])
    if prev4 == 0:
        return last4, prev4, None
    return last4, prev4, round((last4 - prev4) / prev4 * 100, 1)


def signal_score(velocity_change_pct):
    """Composite score: reward genuine acceleration, don't reward or
    punish deceleration (a slowdown isn't a buying signal by itself,
    it just isn't a growth signal — the honest answer is 'no signal',
    not a fabricated negative one)."""
    if velocity_change_pct is None:
        return 0
    return max(0, round(velocity_change_pct, 1))


def main():
    results = []
    for repo in REPOS:
        try:
            meta = fetch(f"https://api.github.com/repos/{repo}")
            last4, prev4, change = commit_velocity_change(repo)
            results.append({
                "repo": repo,
                "stars": meta.get("stargazers_count"),
                "open_issues": meta.get("open_issues_count"),
                "commits_last_4wk": last4,
                "commits_prev_4wk": prev4,
                "velocity_change_pct": change,
                "signal_score": signal_score(change),
            })
        except Exception as e:
            results.append({"repo": repo, "error": str(e)})
        time.sleep(1)

    results.sort(key=lambda r: r.get("signal_score", 0), reverse=True)

    print(f"{'REPO':<28}{'STARS':>8}{'4WK NOW':>10}{'4WK PRIOR':>11}{'CHANGE':>9}{'SIGNAL':>9}")
    for r in results:
        if "error" in r:
            print(f"{r['repo']:<28}{'ERROR':>8}")
            continue
        change_str = f"{r['velocity_change_pct']:+.1f}%" if r["velocity_change_pct"] is not None else "n/a"
        print(f"{r['repo']:<28}{r['stars']:>8}{r['commits_last_4wk']:>10}{r['commits_prev_4wk']:>11}{change_str:>9}{r['signal_score']:>9}")

    return results


if __name__ == "__main__":
    main()
