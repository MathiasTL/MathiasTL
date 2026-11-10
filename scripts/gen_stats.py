"""Generate dot-matrix GitHub stats cards for the profile README.

Writes two SVGs that match the black hole hero (orange dots, transparent
background, light/dark aware):
  - activity.svg: last year's contribution calendar as dots, plus streaks.
  - languages.svg: top languages across owned, non-fork public repos.

CLI:  GITHUB_TOKEN=... python3 scripts/gen_stats.py <user> <out_dir>
"""

import datetime as dt
import json
import os
import sys
import urllib.request

ORANGE = "#F5A54A"
LEVELS = {  # contribution level -> square opacity
    "NONE": 1,
    "FIRST_QUARTILE": 0.35,
    "SECOND_QUARTILE": 0.55,
    "THIRD_QUARTILE": 0.8,
    "FOURTH_QUARTILE": 1,
}
SQUARE, RADIUS = 11.5, 2.5  # calendar square size and corner radius
IGNORED_LANGS = {"Jupyter Notebook", "HTML", "CSS", "Dockerfile", "Makefile", "Shell", "PLSQL", "Mako", "TeX", "PowerShell"}
FONT = "'Segoe UI', -apple-system, Helvetica, Arial, sans-serif"

STYLE = f"""
  .dim {{ fill: #30363d; }}
  .on {{ fill: {ORANGE}; }}
  .title {{ fill: #f0f6fc; }}
  .num {{ fill: {ORANGE}; }}
  .label {{ fill: #c9d1d9; }}
  .meta {{ fill: #8b949e; }}
  .col {{ animation: wave 7s ease-in-out infinite; }}
  @keyframes wave {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.45; }} }}
  @media (prefers-color-scheme: light) {{
    .dim {{ fill: #d0d7de; }}
    .on {{ fill: #E07A1F; }}
    .title {{ fill: #1f2328; }}
    .num {{ fill: #B8521C; }}
    .label {{ fill: #424a53; }}
    .meta {{ fill: #6e7781; }}
  }}
"""

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } }
    }
  }
}
"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


# ---------- pure helpers (tested) ----------

def flatten_days(weeks):
    return [d for w in weeks for d in w["contributionDays"]]


def streaks(days, today=None):
    """Return (current, longest) streaks in days."""
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    # Current streak may start yesterday if today has no contributions yet.
    i = len(counts) - 1
    if today is not None and days and days[-1]["date"] == today and counts[-1] == 0:
        i -= 1
    current = 0
    while i >= 0 and counts[i] > 0:
        current += 1
        i -= 1
    return current, longest


def top_languages(repos, limit=4):
    totals = {}
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name in IGNORED_LANGS:
                continue
            totals[name] = totals.get(name, 0) + edge["size"]
    grand = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    return [(name, size / grand) for name, size in ranked]


def _svg(w, h, label, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" '
        f'preserveAspectRatio="xMidYMid meet" role="img" aria-label="{label}">'
        f"<style>{STYLE}</style>{body}</svg>"
    )


def render_activity(days, total, current, longest):
    cell, x0, y0 = 15.5, 20, 64
    # Align to weekday rows: the first week may be partial.
    first_wd = (dt.date.fromisoformat(days[0]["date"]).weekday() + 1) % 7 if days else 0
    parts = [
        f'<text class="title" x="{x0}" y="30" font-family="{FONT}" font-size="20" font-weight="600">Contributions · last 12 months</text>'
    ]
    idx = 0
    col = 0
    month_seen = None
    while idx < len(days):
        start_row = first_wd if col == 0 else 0
        dots = []
        for row in range(start_row, 7):
            if idx >= len(days):
                break
            d = days[idx]
            op = LEVELS.get(d["contributionLevel"], LEVELS["NONE"])
            cls = "dim" if d["contributionLevel"] == "NONE" else "on"
            dots.append(
                f'<rect class="{cls}" x="{x0 + col * cell:.1f}" y="{y0 + row * cell:.1f}" '
                f'width="{SQUARE}" height="{SQUARE}" rx="{RADIUS}" opacity="{op}"/>'
            )
            month = d["date"][:7]
            if row == start_row and month != month_seen and dt.date.fromisoformat(d["date"]).day <= 7:
                name = dt.date.fromisoformat(d["date"]).strftime("%b")
                parts.append(f'<text class="meta" x="{x0 + col * cell + 2:.1f}" y="{y0 - 8}" font-family="{FONT}" font-size="11">{name}</text>')
                month_seen = month
            idx += 1
        parts.append(f'<g class="col" style="animation-delay:{col * 0.09:.2f}s">{"".join(dots)}</g>')
        col += 1
    xs = 900
    stats = [(f"{total:,}", "contributions"), (str(current), "days · current streak"), (str(longest), "days · longest streak")]
    for i, (num, label) in enumerate(stats):
        y = 76 + i * 52
        parts.append(f'<text class="num" x="{xs}" y="{y}" font-family="{FONT}" font-size="32" font-weight="700">{num}</text>')
        parts.append(f'<text class="label" x="{xs}" y="{y + 20}" font-family="{FONT}" font-size="14">{label}</text>')
    label = f"{total} contributions in the last year. Current streak {current} days, longest {longest} days."
    return _svg(1200, 214, label, "".join(parts))


def render_languages(langs):
    parts = [f'<text class="title" x="20" y="30" font-family="{FONT}" font-size="20" font-weight="600">Most used languages</text>']
    dots_per_bar, gap = 30, 10
    for i, (name, share) in enumerate(langs):
        col, row = i % 2, i // 2
        x, y = 20 + col * 600, 70 + row * 44
        lit = max(1, round(share * dots_per_bar))
        parts.append(f'<text class="label" x="{x}" y="{y + 5}" font-family="{FONT}" font-size="15">{name}</text>')
        bar = []
        for j in range(dots_per_bar):
            cls = "on" if j < lit else "dim"
            bar.append(f'<rect class="{cls}" x="{x + 146 + j * gap}" y="{y - 4}" width="8" height="8" rx="1.5"/>')
        parts.append(f'<g class="col" style="animation-delay:{i * 0.4:.1f}s">{"".join(bar)}</g>')
        parts.append(f'<text class="num" x="{x + 150 + dots_per_bar * gap + 8}" y="{y + 5}" font-family="{FONT}" font-size="15" font-weight="600">{share * 100:.1f}%</text>')
    rows = (len(langs) + 1) // 2
    label = "Most used languages: " + ", ".join(f"{n} {s * 100:.1f}%" for n, s in langs)
    return _svg(1200, 70 + rows * 44, label, "".join(parts))


def main():
    login, out_dir = sys.argv[1], sys.argv[2]
    token = os.environ["GITHUB_TOKEN"]
    user = fetch(login, token)
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = flatten_days(cal["weeks"])
    current, longest = streaks(days, today=dt.date.today().isoformat())
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "activity.svg"), "w") as f:
        f.write(render_activity(days, cal["totalContributions"], current, longest))
    with open(os.path.join(out_dir, "languages.svg"), "w") as f:
        f.write(render_languages(top_languages(user["repositories"]["nodes"])))
    print(f"wrote stats for {login}: {cal['totalContributions']} contributions, streak {current}/{longest}")


if __name__ == "__main__":
    main()
