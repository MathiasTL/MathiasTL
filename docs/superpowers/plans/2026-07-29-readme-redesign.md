# README Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the GitHub profile README with an animated, modern design, richer project info, and a custom dot-matrix animated title per featured project.

**Architecture:** A small dependency-free Python generator renders a 5×7 bitmap font into SMIL-animated SVGs (one per featured project). A GitHub Action generates the snake animation. `README.md` is rewritten to compose these plus typing SVGs, skillicons, and stats widgets.

**Tech Stack:** Python 3 (stdlib only) for the SVG generator, SMIL-animated SVG, GitHub Actions (`Platane/snk`), shields.io + skillicons.dev, Markdown.

## Global Constraints

- Work happens on branch `redesign-readme`. `main` and the live profile stay untouched until an explicit merge.
- Never add `Co-Authored-By` trailers to commits.
- Only **real** (measured/verifiable) metrics appear in the README; projected/hypothetical numbers are omitted.
- The generator uses the Python standard library only — no pip installs.
- Dot-matrix color: `#58A6FF` (reads well on GitHub light and dark). Off-dots are not drawn.
- Featured order: Puntualo · ContentSpark · ProfAI. More Projects: AgentUP · Eissential · FoodLinks · SMART.
- No project screenshots/GIFs (keeps README short).
- Assets live in `assets/`, generator in `scripts/`, workflow in `.github/workflows/`.

---

## File Structure

- `scripts/gen_dotmatrix.py` — the generator: 5×7 font table + SVG builder + CLI.
- `tests/test_gen_dotmatrix.py` — unit tests for the generator.
- `assets/puntualo.svg`, `assets/contentspark.svg`, `assets/profai.svg` — generated outputs (committed).
- `.github/workflows/snake.yml` — snake animation Action.
- `README.md` — full rewrite.

---

### Task 1: Dot-matrix SVG generator

**Files:**
- Create: `scripts/gen_dotmatrix.py`
- Test: `tests/test_gen_dotmatrix.py`

**Interfaces:**
- Produces:
  - `FONT: dict[str, list[str]]` — each glyph is 7 strings of exactly 5 chars, `#`=on, ` `=off.
  - `render_word(word: str, *, dot_r: float = 6.0, gap: float = 4.0, color: str = "#58A6FF", char_gap: int = 1, type_ms: int = 120, hold_ms: int = 2500, fade_ms: int = 600) -> str` — returns a complete SVG string with SMIL animation for one word (typing in column-by-column, hold, fade out, loop).
  - CLI: `python3 scripts/gen_dotmatrix.py <word> <out.svg> [--color HEX]`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_gen_dotmatrix.py
import re
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import gen_dotmatrix as g

REQUIRED = set("PuntualoContentSparkProfAI")

def test_font_covers_required_chars():
    missing = [c for c in REQUIRED if c not in g.FONT]
    assert missing == [], f"missing glyphs: {missing}"

def test_every_glyph_is_7x5():
    for ch, rows in g.FONT.items():
        assert len(rows) == 7, f"{ch!r} has {len(rows)} rows"
        assert all(len(r) == 5 for r in rows), f"{ch!r} has a row != 5 cols"
        assert all(set(r) <= {"#", " "} for r in rows), f"{ch!r} has bad chars"

def test_render_word_is_svg_with_circles_and_animation():
    svg = g.render_word("ProfAI")
    assert svg.strip().startswith("<svg")
    assert svg.strip().endswith("</svg>")
    assert svg.count("<circle") > 0
    # SMIL animation present for the typing/fade effect
    assert "<animate" in svg
    assert 'repeatCount="indefinite"' in svg

def test_render_word_circle_count_matches_on_dots():
    # one <circle> per lit dot in the word
    on_dots = 0
    for ch in "ProfAI":
        on_dots += sum(row.count("#") for row in g.FONT[ch])
    svg = g.render_word("ProfAI")
    assert svg.count("<circle") == on_dots

def test_render_word_width_scales_with_length():
    short = g.render_word("Pro")
    long = g.render_word("Profff")
    def width(s): return float(re.search(r'width="([\d.]+)"', s).group(1))
    assert width(long) > width(short)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_gen_dotmatrix.py -v`
Expected: FAIL (module `gen_dotmatrix` not found).

- [ ] **Step 3: Implement the generator**

Create `scripts/gen_dotmatrix.py`. Build the `FONT` dict with 7×5 glyphs for every character in
`Puntualo`, `ContentSpark`, `ProfAI` (unique chars: `P u n t a l o C e S p r k f A I`). Each glyph
is a list of 7 strings, 5 chars wide, `#` = lit dot. Example glyph shape (letter `I`):

```python
FONT = {
    "I": [
        "#####",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "#####",
    ],
    # ... define P u n t a l o C e S p r k f A  (7 rows x 5 cols each)
}
```

Then the renderer. Layout: each glyph occupies a 5-wide × 7-tall dot grid; dot pitch = `2*dot_r + gap`.
Words lay out left→right with `char_gap` empty columns between glyphs. For each lit dot emit a
`<circle cx cy r>` whose opacity is driven by one SMIL cycle:

- typing: opacity 0→1, `begin` offset = `(global_column_index * type_ms)` ms.
- hold: stays 1 for `hold_ms`.
- fade: 1→0 over `fade_ms`.
- loop: total cycle `dur = last_type + hold_ms + fade_ms`; use `repeatCount="indefinite"`.

Implementation:

```python
import sys

DOT_R = 6.0
GAP = 4.0
COLOR = "#58A6FF"

# FONT = { ... }  # defined above

def _dims(word, dot_r, gap, char_gap):
    pitch = 2 * dot_r + gap
    cols = 0
    for i, ch in enumerate(word):
        cols += 5
        if i < len(word) - 1:
            cols += char_gap
    width = cols * pitch + gap
    height = 7 * pitch + gap
    return pitch, width, height

def render_word(word, *, dot_r=DOT_R, gap=GAP, color=COLOR,
                char_gap=1, type_ms=120, hold_ms=2500, fade_ms=600):
    pitch, width, height = _dims(word, dot_r, gap, char_gap)
    # collect lit dots as (global_col, row)
    dots = []
    col_cursor = 0
    for i, ch in enumerate(word):
        glyph = FONT[ch]
        for r, rowstr in enumerate(glyph):
            for c, cell in enumerate(rowstr):
                if cell == "#":
                    dots.append((col_cursor + c, r))
        col_cursor += 5 + (char_gap if i < len(word) - 1 else 0)
    max_col = max((c for c, _ in dots), default=0)
    type_total = (max_col + 1) * type_ms
    cycle = type_total + hold_ms + fade_ms  # ms
    dur = cycle / 1000.0

    circles = []
    for (c, r) in dots:
        cx = gap + dot_r + c * pitch
        cy = gap + dot_r + r * pitch
        begin = (c * type_ms) / 1000.0
        # keyTimes across the whole cycle: fade-in, hold, fade-out
        t_in = (c * type_ms + type_ms) / cycle
        t_start = (c * type_ms) / cycle
        t_holdend = (type_total + hold_ms) / cycle
        # opacity keyframes: 0 (start) -> 1 (after own type slot) -> 1 (hold end) -> 0 (cycle end)
        kt = [0, max(0.0001, t_start), min(0.9999, t_in), t_holdend, 1]
        # ensure strictly increasing
        kt = _monotonic(kt)
        vals = [0, 0, 1, 1, 0]
        anim = (
            f'<animate attributeName="opacity" values="{";".join(str(v) for v in vals)}" '
            f'keyTimes="{";".join(f"{k:.4f}" for k in kt)}" '
            f'dur="{dur:.3f}s" repeatCount="indefinite" calcMode="linear" />'
        )
        circles.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{dot_r:.1f}" fill="{color}" opacity="0">{anim}</circle>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="{word}">'
        + "".join(circles)
        + "</svg>"
    )

def _monotonic(vals):
    out = []
    prev = -1.0
    for v in vals:
        v = float(v)
        if v <= prev:
            v = prev + 0.0001
        out.append(round(v, 4))
        prev = v
    return out

if __name__ == "__main__":
    args = sys.argv[1:]
    color = COLOR
    if "--color" in args:
        idx = args.index("--color")
        color = args[idx + 1]
        del args[idx:idx + 2]
    word, out = args[0], args[1]
    svg = render_word(word, color=color)
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out} ({len(svg)} bytes)")
```

Complete the `FONT` dict for all required characters before running tests.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_gen_dotmatrix.py -v`
Expected: PASS (all 5 tests). If `pytest` is unavailable, run `python3 -m unittest` equivalent or `python3 tests/test_gen_dotmatrix.py` after adding a runner; prefer installing nothing — use `python3 -m pytest` which ships in most envs, else assert via a `__main__` block.

- [ ] **Step 5: Commit**

```bash
git add scripts/gen_dotmatrix.py tests/test_gen_dotmatrix.py
git commit -m "feat: add dot-matrix animated SVG generator"
```

---

### Task 2: Generate the three featured-project SVGs

**Files:**
- Create: `assets/puntualo.svg`, `assets/contentspark.svg`, `assets/profai.svg`

**Interfaces:**
- Consumes: `render_word` / CLI from Task 1.

- [ ] **Step 1: Generate the assets**

```bash
mkdir -p assets
python3 scripts/gen_dotmatrix.py Puntualo assets/puntualo.svg
python3 scripts/gen_dotmatrix.py ContentSpark assets/contentspark.svg
python3 scripts/gen_dotmatrix.py ProfAI assets/profai.svg
```

- [ ] **Step 2: Verify each is valid SVG**

Run: `for f in assets/*.svg; do head -c 40 "$f"; echo " <- $f"; done`
Expected: each starts with `<svg xmlns=...`. Optionally open one in a browser to confirm the
typing→hold→fade→loop animation plays.

- [ ] **Step 3: Commit**

```bash
git add assets/puntualo.svg assets/contentspark.svg assets/profai.svg
git commit -m "feat: add generated dot-matrix project titles"
```

---

### Task 3: Snake animation workflow

**Files:**
- Create: `.github/workflows/snake.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: Generate Snake

on:
  schedule:
    - cron: "0 */12 * * *"
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: Platane/snk@v3
        id: snake
        with:
          github_user_name: ${{ github.repository_owner }}
          outputs: |
            dist/snake.svg
            dist/snake-dark.svg?palette=github-dark

      - uses: crazy-max/ghaction-github-pages@v4
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- [ ] **Step 2: Sanity-check YAML**

Run: `python3 -c "import yaml,sys" 2>/dev/null && python3 -c "import yaml;yaml.safe_load(open('.github/workflows/snake.yml'))" && echo OK || echo "yaml module absent - visually verify indentation"`
Expected: `OK` (or a visual check if PyYAML is not installed).

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/snake.yml
git commit -m "ci: add snake contribution animation workflow"
```

> Note: the snake SVGs only exist after the Action runs on `main` (branch `output`). The README
> references `.../MathiasTL/output/snake-dark.svg`. Until the first run, the image 404s — expected;
> it resolves after merge + first Action run (or a manual `workflow_dispatch`).

---

### Task 4: Rewrite README.md

**Files:**
- Modify: `README.md` (full rewrite)

**Interfaces:**
- Consumes: `assets/*.svg` (Task 2), snake output path (Task 3).

- [ ] **Step 1: Write the new README**

Compose the sections in this exact order, using real metrics only:

1. **Header** — `readme-typing-svg` (name + rotating roles) + contact badges (LinkedIn, Gmail, Instagram, TikTok) centered.
2. **Wave divider** — a capsule-render / SVG wave (e.g. `capsule-render` header wave) or a thin gradient rule.
3. **💫 About Me** — pulished bullets from the current README + a `🌱 Currently building: Puntualo · Eissential` line + `📍 Lima, Perú`.
4. **🚀 Featured Projects** — three blocks; each:
   - `<img src="assets/<name>.svg">` dot-matrix title (raw path works in-repo; on profile it renders from `main`).
   - one-line pitch, stack as inline `code`, 2-3 real-metric bullets (from the spec §3).
   - link buttons via shields.io `for-the-badge` (Repo, and Live Demo where present):
     - Puntualo: repo `MiguelGironAltamirano/Puntualo`, demo `https://puntualo.vercel.app/`
     - ContentSpark: repo `MathiasTL/ContentSpark-RAG`
     - ProfAI: repo `NickSalA/Hackaton-06-2025`
5. **📂 More Projects** — compact table:
   - AgentUP — repo `MathiasTL/AgentUP` + 🟢 Live Demo `https://agentup-382104851468.us-central1.run.app`
   - Eissential — repo placeholder `#` (editable)
   - FoodLinks — repo placeholder `#`
   - SMART — repo placeholder `#`
6. **🛠️ Tech Stack** — `skillicons.dev` per category; keep shields.io badges for icons skillicons lacks (LangChain, Oracle, LangGraph).
7. **🐍 Snake** — light/dark via `#gh-dark-mode-only` / `#gh-light-mode-only` pointing at the `output` branch SVGs.
8. **📊 GitHub Stats** — existing stats + top-langs + streak (theme `react`).
9. **📈 Contribution Graph** — `github-readme-activity-graph` (existing).
10. **Footer** — closing `readme-typing-svg` + quote + `komarev` profile views (existing).

Placeholders for missing repo URLs must be obvious `#` links with an HTML comment `<!-- TODO: repo URL -->`.

- [ ] **Step 2: Verify local render**

Run: `python3 -c "import pathlib; t=pathlib.Path('README.md').read_text(); assert 'assets/puntualo.svg' in t and 'assets/contentspark.svg' in t and 'assets/profai.svg' in t; assert 'Co-Authored-By' not in t; print('README references all 3 SVGs; OK')"`
Expected: `OK`. Optionally preview with a Markdown viewer to eyeball layout / no horizontal scroll.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "feat: modern animated README redesign"
```

---

### Task 5: Review & merge decision

**Files:** none (integration step)

- [ ] **Step 1: Visual review**

Push the branch and open the repo's README preview on the branch (GitHub renders `assets/*.svg`
relative paths on the branch). Confirm: dot-matrix titles animate, no broken images (snake will
404 until its Action runs), no horizontal scroll, mobile-legible.

Run: `git push -u origin redesign-readme`

- [ ] **Step 2: Merge when approved**

After the user approves the rendered result, merge to `main` (fast-forward or PR per user preference),
then trigger the snake workflow once (`workflow_dispatch`) so the snake SVGs exist.

```bash
git checkout main && git merge --no-ff redesign-readme -m "Modern animated README redesign"
```

> Do not merge without explicit user approval — merging changes the live profile.

---

## Self-Review

**Spec coverage:**
- Header/typing → Task 4 §1 ✓
- Wave divider → Task 4 §2 ✓
- About Me → Task 4 §3 ✓
- Featured cards + dot-matrix → Tasks 1, 2, 4 §4 ✓
- More Projects (AgentUP/Eissential/FoodLinks/SMART) → Task 4 §5 ✓
- Tech Stack skillicons → Task 4 §6 ✓
- Snake → Task 3 + Task 4 §7 ✓
- Stats / graph / footer → Task 4 §8-10 ✓
- Dot-matrix generator (SMIL, 5×7, loop) → Task 1 ✓
- Real-metrics-only constraint → Global Constraints + Task 4 ✓
- Light/dark support → Task 4 §7 ✓

**Placeholders:** repo URLs for Eissential/FoodLinks/SMART are intentional `#` placeholders with
TODO comments (user to supply). ProfAI repo flagged for confirmation. No logic placeholders.

**Type consistency:** `render_word(...)` signature and `FONT` structure are identical across Task 1
tests, implementation, and Task 2 CLI usage. Snake output path (`output` branch) consistent between
Task 3 note and Task 4 §7.
