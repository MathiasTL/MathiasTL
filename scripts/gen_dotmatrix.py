"""Generate SMIL-animated dot-matrix SVGs of a word.

Each glyph is a 7-row x 5-col bitmap ('#' = lit dot). The renderer lays glyphs
left-to-right and animates each lit dot's opacity so the word "types in" column
by column, holds, then fades out, looping forever.

CLI:  python3 scripts/gen_dotmatrix.py <word> <out.svg> [--color HEX]
"""

import sys

DOT_R = 6.0
GAP = 4.0
COLOR = "#58A6FF"

# 7 rows x 5 cols per glyph. '#' = lit, ' ' = off.
FONT = {
    "P": [
        "#### ",
        "#   #",
        "#   #",
        "#### ",
        "#    ",
        "#    ",
        "#    ",
    ],
    "C": [
        " ####",
        "#    ",
        "#    ",
        "#    ",
        "#    ",
        "#    ",
        " ####",
    ],
    "S": [
        " ####",
        "#    ",
        "#    ",
        " ### ",
        "    #",
        "    #",
        "#### ",
    ],
    "A": [
        " ### ",
        "#   #",
        "#   #",
        "#####",
        "#   #",
        "#   #",
        "#   #",
    ],
    "I": [
        "#####",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "#####",
    ],
    "u": [
        "     ",
        "     ",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
        " ####",
    ],
    "n": [
        "     ",
        "     ",
        "#### ",
        "#   #",
        "#   #",
        "#   #",
        "#   #",
    ],
    "t": [
        "  #  ",
        "  #  ",
        "#####",
        "  #  ",
        "  #  ",
        "  #  ",
        "  ## ",
    ],
    "a": [
        "     ",
        "     ",
        " ### ",
        "    #",
        " ####",
        "#   #",
        " ####",
    ],
    "l": [
        " ##  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        "  #  ",
        " ### ",
    ],
    "o": [
        "     ",
        "     ",
        " ### ",
        "#   #",
        "#   #",
        "#   #",
        " ### ",
    ],
    "e": [
        "     ",
        "     ",
        " ### ",
        "#   #",
        "#####",
        "#    ",
        " ### ",
    ],
    "p": [
        "     ",
        "     ",
        "#### ",
        "#   #",
        "#### ",
        "#    ",
        "#    ",
    ],
    "r": [
        "     ",
        "     ",
        "# ###",
        "##   ",
        "#    ",
        "#    ",
        "#    ",
    ],
    "k": [
        "#    ",
        "#    ",
        "#  # ",
        "# #  ",
        "##   ",
        "# #  ",
        "#  # ",
    ],
    "f": [
        "  ## ",
        " #   ",
        "#### ",
        " #   ",
        " #   ",
        " #   ",
        " #   ",
    ],
}


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


def render_word(word, *, dot_r=DOT_R, gap=GAP, color=COLOR,
                char_gap=1, type_ms=120, hold_ms=2500, fade_ms=600):
    pitch, width, height = _dims(word, dot_r, gap, char_gap)

    dots = []  # (global_col, row)
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
        t_start = (c * type_ms) / cycle
        t_in = (c * type_ms + type_ms) / cycle
        t_holdend = (type_total + hold_ms) / cycle
        kt = _monotonic([0, t_start, t_in, t_holdend, 1])
        vals = [0, 0, 1, 1, 0]
        anim = (
            f'<animate attributeName="opacity" '
            f'values="{";".join(str(v) for v in vals)}" '
            f'keyTimes="{";".join(f"{k:.4f}" for k in kt)}" '
            f'dur="{dur:.3f}s" repeatCount="indefinite" calcMode="linear" />'
        )
        circles.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{dot_r:.1f}" '
            f'fill="{color}" opacity="0">{anim}</circle>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" '
        f'height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'role="img" aria-label="{word}">'
        + "".join(circles)
        + "</svg>"
    )


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
