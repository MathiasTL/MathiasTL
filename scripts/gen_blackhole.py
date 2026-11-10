"""Generate the dot-matrix black hole hero banner.

A rotating sphere of small dots, an orbiting ring of orange dots that passes
behind the sphere, and the profile info on the right. Transparent background;
text and sphere colors adapt to light/dark via prefers-color-scheme.

CLI:  python3 scripts/gen_blackhole.py [out.svg]
"""

import math
import sys

W, H = 1200, 340
CX, CY = 270, 170
SPHERE_R = 92
DOT_R = 1.7
SPIN_DUR = 24        # seconds per sphere rotation
SAMPLES = 24         # keyframes per rotation
RING_TILT = -12      # degrees
# (rx, dot spacing, seconds per orbit, color, dot radius)
RING_LANES = [
    (128, 9, 9, "#FFD9A0", 1.6),
    (160, 9, 13, "#F5A54A", 1.6),
    (195, 10, 18, "#F5A54A", 1.5),
    (232, 12, 25, "#B8521C", 1.4),
]
RING_FLATTEN = 0.2   # ry = rx * RING_FLATTEN

STYLE = """
  .sp { fill: #e6edf3; }
  .name { fill: #f0f6fc; }
  .role { fill: #F5A54A; }
  .sub { fill: #c9d1d9; }
  .meta { fill: #8b949e; }
  @media (prefers-color-scheme: light) {
    .sp { fill: #24292f; }
    .name { fill: #1f2328; }
    .role { fill: #B8521C; }
    .sub { fill: #424a53; }
    .meta { fill: #6e7781; }
  }
"""


def _fmt(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def sphere_dots():
    """Dots on latitude rings spinning around the vertical axis.

    Each latitude gets one CSS keyframe set; dots on it only differ by
    animation-delay, which keeps the file small.
    """
    dots, frames = [], []
    lat_step = 9
    n_lat = int(SPHERE_R * 2 / lat_step)
    for i in range(n_lat + 1):
        y = -SPHERE_R + i * lat_step
        if abs(y) >= SPHERE_R:
            continue
        ring_r = math.sqrt(SPHERE_R ** 2 - y ** 2)
        steps = []
        for k in range(SAMPLES + 1):
            a = 2 * math.pi * k / SAMPLES
            x = ring_r * math.sin(a)
            z = ring_r * math.cos(a) / SPHERE_R  # depth, front > 0
            op = _fmt(0.2 + 0.8 * z) if z > 0 else "0"
            steps.append(f"{_fmt(100 * k / SAMPLES)}%{{transform:translateX({_fmt(x)}px);opacity:{op}}}")
        frames.append(f"@keyframes l{i}{{{''.join(steps)}}}")
        count = max(4, int(2 * math.pi * ring_r / 9.5))
        for j in range(count):
            delay = -SPIN_DUR * j / count
            dots.append(
                f'<circle class="sp" cx="{CX}" cy="{_fmt(CY + y)}" r="{DOT_R}" '
                f'style="animation:l{i} {SPIN_DUR}s linear {_fmt(delay)}s infinite"/>'
            )
    return dots, frames


def ring_paths():
    paths = []
    for idx, (rx, *_rest) in enumerate(RING_LANES):
        ry = rx * RING_FLATTEN
        # Start at the right, go down (toward the viewer) and around.
        d = (f"M{_fmt(CX + rx)},{CY} A{rx},{_fmt(ry)} 0 1,1 {_fmt(CX - rx)},{CY} "
             f"A{rx},{_fmt(ry)} 0 1,1 {_fmt(CX + rx)},{CY}")
        paths.append(f'<path id="lane{idx}" d="{d}"/>')
    return paths


def ring_dots():
    out = []
    for idx, (rx, spacing, dur, color, r) in enumerate(RING_LANES):
        ry = rx * RING_FLATTEN
        perim = math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))
        count = int(perim / spacing)
        for j in range(count):
            begin = -dur * j / count
            # Gentle brightness variation so the ring reads as particles, not a line.
            op = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(j * 1.7 + idx))
            out.append(
                f'<circle r="{r}" fill="{color}" opacity="{_fmt(op)}">'
                f'<animateMotion dur="{dur}s" begin="{_fmt(begin)}s" repeatCount="indefinite">'
                f'<mpath href="#lane{idx}"/></animateMotion></circle>'
            )
    return out


def halo_dots():
    """Static dotted halo around the sphere, slowly rotating."""
    r = SPHERE_R + 16
    count = int(2 * math.pi * r / 11)
    dots = []
    for j in range(count):
        a = 2 * math.pi * j / count
        op = 0.25 + 0.35 * (0.5 + 0.5 * math.cos(a - math.pi / 2))
        dots.append(
            f'<circle cx="{_fmt(CX + r * math.cos(a))}" cy="{_fmt(CY + r * math.sin(a))}" '
            f'r="1.2" fill="#F5A54A" opacity="{_fmt(op)}"/>'
        )
    return (
        f'<g><animateTransform attributeName="transform" type="rotate" '
        f'from="0 {CX} {CY}" to="360 {CX} {CY}" dur="60s" repeatCount="indefinite"/>'
        + "".join(dots) + "</g>"
    )


def render():
    # The ring's far half is hidden where it passes behind the sphere.
    mask = (
        '<mask id="behind" maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="340">'
        '<rect width="1200" height="340" fill="#fff"/>'
        f'<circle cx="{CX}" cy="{CY}" r="{SPHERE_R + 4}" fill="#000" clip-path="url(#upper)"/>'
        "</mask>"
        f'<clipPath id="upper"><rect x="0" y="0" width="1200" height="{CY}"/></clipPath>'
    )
    text = (
        '<g font-family="\'Segoe UI\', -apple-system, Helvetica, Arial, sans-serif">'
        '<text class="name" x="560" y="140" font-size="58" font-weight="700" letter-spacing="1">Mathias Torres</text>'
        '<text class="role" x="562" y="184" font-size="23" font-weight="600">AI Engineer Intern @ InSalud</text>'
        '<text class="sub" x="562" y="218" font-size="18">GenAI · RAG · AI agents in production</text>'
        '<text class="meta" x="562" y="250" font-size="15">Software Engineering · UNMSM · Lima, Perú</text>'
        "</g>"
    )
    dots, frames = sphere_dots()
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" '
        'preserveAspectRatio="xMidYMid meet" role="img" '
        'aria-label="Mathias Torres — AI Engineer Intern at InSalud. A dot-matrix black hole with an orbiting orange ring.">',
        f"<style>{STYLE}{''.join(frames)}</style>",
        "<defs>", mask, *ring_paths(), "</defs>",
        halo_dots(),
        "<g>", *dots, "</g>",
        f'<g transform="rotate({RING_TILT} {CX} {CY})"><g mask="url(#behind)">',
        *ring_dots(),
        "</g></g>",
        text,
        "</svg>",
    ]
    return "\n".join(parts)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "assets/blackhole-hero.svg"
    svg = render()
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out} ({len(svg)} bytes)")
