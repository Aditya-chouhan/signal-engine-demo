"""
Signal-to-draft — the second half of "signal-based intent orchestration."

signal_score.py finds the signal (a company's commit velocity accelerating).
This script closes the loop: take the top-scoring company, pull a few more
real public facts about what it's actually shipping right now, and have
Claude draft a short, honest, diagnosis-style message grounded in those
facts — not a generic pitch.

Design rule (same one already used for every outreach draft in this
project): AI drafts, a human approves every send. This script only ever
prints a draft. It does not send anything to anyone.

Requires an Anthropic API key: export ANTHROPIC_API_KEY=sk-ant-...
No other dependencies — raw stdlib HTTP call, same as signal_score.py.

Run it yourself: python3 draft_outreach.py
"""

import json
import os
import urllib.request

REPO = "ComposioHQ/composio"  # the top-scoring company from signal_score.py


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "signal-engine-demo"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def gather_real_facts(repo):
    """Pull a few more real, current facts to ground the draft — no invented details."""
    meta = fetch(f"https://api.github.com/repos/{repo}")
    releases = fetch(f"https://api.github.com/repos/{repo}/releases?per_page=3")
    commits = fetch(f"https://api.github.com/repos/{repo}/commits?per_page=8")
    return {
        "description": meta.get("description"),
        "recent_release_cadence": [r.get("published_at") for r in releases],
        "recent_commit_subjects": [
            c["commit"]["message"].split("\n")[0] for c in commits
        ],
    }


SYSTEM_PROMPT = """You draft short, honest outbound messages grounded ONLY in
the specific facts you're given. Rules:
- This is a diagnosis, not a pitch. Observe something real and specific, then ask a genuine question.
- Never invent a pain point, a metric, or a detail not present in the input facts.
- No generic sales language ("I noticed you might be interested in...", "revolutionize", "synergy").
- 3-5 sentences maximum. Plain text, no subject line needed unless asked.
- If the facts don't support a clear observation, say so instead of forcing one."""


def draft_message(company, signal_summary, facts):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit(
            "Set ANTHROPIC_API_KEY to run this step "
            "(e.g. export ANTHROPIC_API_KEY=sk-ant-...)."
        )

    user_prompt = f"""Company: {company}
Signal: {signal_summary}
Real facts pulled from their public GitHub activity:
- Description: {facts['description']}
- Recent release timestamps: {facts['recent_release_cadence']}
- Recent commit subjects: {facts['recent_commit_subjects']}

Draft the message."""

    body = json.dumps({
        "model": "claude-sonnet-4-5",
        "max_tokens": 300,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read())
    return resp["content"][0]["text"]


def main():
    signal_summary = "Commit velocity +183.3% in the trailing 4 weeks (42 -> 119 commits) vs. the 4 weeks before that."
    facts = gather_real_facts(REPO)
    print("REAL FACTS PULLED:")
    print(json.dumps(facts, indent=2))
    print()
    draft = draft_message(REPO, signal_summary, facts)
    print("DRAFTED MESSAGE (not sent — human review required before any send):")
    print(draft)


if __name__ == "__main__":
    main()
