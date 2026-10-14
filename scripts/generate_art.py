#!/usr/bin/env python3
"""Generate abstract ASCII art (no face) for the terminal profile panel.
92 cols x 68 rows — agentic core: central diamond + satellites + signal rings.
Deterministic, no dependencies.
"""
import math
from pathlib import Path

W, H = 92, 68
PALETTE = " .,:;irsXA253hMHGS#9B&@"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "art.txt"

CX, CY = W / 2, H / 2 - 2

# satellite nodes (x, y, radius)
SATS = [
    (W * 0.20, H * 0.24, 6.5),
    (W * 0.81, H * 0.30, 7.5),
    (W * 0.24, H * 0.74, 7.0),
    (W * 0.78, H * 0.72, 6.0),
]


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def field(x, y):
    # base vignette grid
    v = 0.06 + 0.04 * ((x % 4 == 0) and (y % 3 == 0))

    # central diamond core
    dc = abs(x - CX) / 22 + abs(y - CY) / 16
    if dc < 1.0:
        v += (1.0 - dc) * 0.95

    # inner bright nucleus
    dn = math.hypot((x - CX) / 9, (y - CY) / 6.5)
    if dn < 1.0:
        v += (1.0 - dn) * 0.9

    # concentric signal rings
    r = math.hypot((x - CX) / 1.5, y - CY)
    ring = abs((r % 9) - 4.5) / 4.5  # 0 at ring edge, 1 mid
    v += (1.0 - ring) * 0.22 * max(0.0, 1.0 - r / 48)

    # diagonal spokes from core
    for k in range(4):
        ang = math.pi / 4 + k * math.pi / 2
        bx, by = CX + math.cos(ang) * 44, CY + math.sin(ang) * 30
        d = seg_dist(x, y, CX, CY, bx, by)
        if d < 1.4:
            v += (1.4 - d) * 0.30

    # satellites + links to core
    for sx, sy, sr in SATS:
        d = math.hypot(x - sx, y - sy)
        if d < sr:
            v += (1.0 - d / sr) * 0.95
        dl = seg_dist(x, y, CX, CY, sx, sy)
        if dl < 1.0:
            v += (1.0 - dl) * 0.28

    # bottom pulse waveform
    wave_y = H - 6 + 3.2 * math.sin(x / 5.5) * math.sin(x / 13.0 + 1.2)
    if abs(y - wave_y) < 1.1:
        v += 0.55

    return max(0.0, min(1.0, v))


lines = []
for y in range(H):
    row = []
    for x in range(W):
        # circular mask — fade edges like a portrait vignette
        ex = abs(x - CX) / (W / 2)
        ey = abs(y - CY) / (H / 2)
        edge = max(0.0, 1.0 - max(0.0, (ex**2 + ey**2 - 0.55)) * 1.6)
        v = field(x, y) * edge
        idx = round(v * (len(PALETTE) - 1))
        row.append(PALETTE[idx])
    lines.append("".join(row).rstrip())

while lines and not lines[0].strip():
    lines.pop(0)
while lines and not lines[-1].strip():
    lines.pop()

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines) + "\n")
print(f"Generated {len(lines)} rows in {OUT}")
