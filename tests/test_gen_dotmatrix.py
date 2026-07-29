import re
import sys
import os

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
    assert "<animate" in svg
    assert 'repeatCount="indefinite"' in svg


def test_render_word_circle_count_matches_on_dots():
    on_dots = 0
    for ch in "ProfAI":
        on_dots += sum(row.count("#") for row in g.FONT[ch])
    svg = g.render_word("ProfAI")
    assert svg.count("<circle") == on_dots


def test_render_word_width_scales_with_length():
    short = g.render_word("Pro")
    long = g.render_word("Profff")

    def width(s):
        return float(re.search(r'width="([\d.]+)"', s).group(1))

    assert width(long) > width(short)


if __name__ == "__main__":
    # Runnable without pytest: execute every test_* function.
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                failures += 1
                print(f"FAIL {name}: {e}")
    sys.exit(1 if failures else 0)
