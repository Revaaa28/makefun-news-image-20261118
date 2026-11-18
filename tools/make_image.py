#!/usr/bin/env python3
"""Render entry.png: the world news of Wednesday 18 November 2026 in one image.

Newspaper-poster style, drawn entirely with PIL shapes and DejaVu type so
every word stays crisp. The picture is a masthead naming the day, six story
panels (place, icon, headline) and a ticker strip along the bottom.

Run:  python3 tools/make_image.py   ->  writes entry.png next to main.py
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 241, 227)      # cream newsprint
NAVY = (20, 33, 61)          # ink navy
RED = (193, 39, 45)          # accent red
PANEL_BG = (255, 253, 246)   # panel paper
CREAM = (247, 241, 227)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SANS = f"{FONT_DIR}/DejaVuSans.ttf"
SANS_B = f"{FONT_DIR}/DejaVuSans-Bold.ttf"
SERIF = f"{FONT_DIR}/DejaVuSerif.ttf"
SERIF_B = f"{FONT_DIR}/DejaVuSerif-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(d, text, path, max_w, start, minimum=10):
    """Largest size <= start whose text still fits max_w."""
    size = start
    while size > minimum:
        f = font(path, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return font(path, minimum)


def wrap_text(d, text, f, max_w):
    """Greedy word wrap measured with textlength; nothing overflows."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def headline_lines(d, text, max_w, max_lines=3, start=33):
    """Shrink the headline font until the wrap fits max_lines lines."""
    size = start
    while size >= 22:
        f = font(SANS_B, size)
        lines = wrap_text(d, text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 2
    f = font(SANS_B, 22)
    return f, wrap_text(d, text, f, max_w)


def star_points(cx, cy, r_out, r_in, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = rot + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ---------------------------------------------------------------- icons
# Each icon draws inside a notional 110x110 box whose top-left is (x, y).

def icon_plane(d, x, y):
    """Airliner in side view, flying right."""
    d.rounded_rectangle([x + 6, y + 46, x + 86, y + 64], radius=9, fill=NAVY)
    d.polygon([(x + 84, y + 46), (x + 104, y + 55), (x + 84, y + 64)], fill=NAVY)
    d.polygon([(x + 8, y + 47), (x + 20, y + 26), (x + 30, y + 26),
               (x + 28, y + 47)], fill=NAVY)                       # tail fin
    d.polygon([(x + 42, y + 60), (x + 66, y + 60), (x + 80, y + 86),
               (x + 56, y + 86)], fill=NAVY)                        # wing
    for i in range(5):                                              # windows
        cx = x + 30 + i * 11
        d.ellipse([cx, y + 51, cx + 6, y + 57], fill=CREAM)


def icon_bridge(d, x, y):
    """Suspension bridge with a burst on the deck, waves below."""
    deck_y = y + 74

    def cable(x0, y0, x1, y1, sag):
        pts = []
        for i in range(17):
            t = i / 16
            pts.append((x0 + (x1 - x0) * t,
                        y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)))
        return pts

    d.line(cable(x + 2, deck_y - 4, x + 26, y + 26, 10), fill=NAVY, width=3)
    d.line(cable(x + 26, y + 26, x + 84, y + 26, 16), fill=NAVY, width=3)
    d.line(cable(x + 84, y + 26, x + 108, deck_y - 4, 10), fill=NAVY, width=3)
    for hx in range(x + 38, x + 80, 12):                            # hangers
        t = (hx - (x + 26)) / 58
        cy = y + 26 + 16 * 4 * t * (1 - t)
        d.line([hx, cy, hx, deck_y - 4], fill=NAVY, width=2)
    for tx in (x + 26, x + 84):                                     # towers
        d.rectangle([tx - 4, y + 26, tx + 4, deck_y], fill=NAVY)
        d.rectangle([tx - 7, y + 22, tx + 7, y + 30], fill=NAVY)
    d.line([x + 2, deck_y, x + 108, deck_y], fill=NAVY, width=7)    # deck
    d.polygon(star_points(x + 55, deck_y - 8, 17, 7, n=8), fill=RED)  # burst
    for wy in (deck_y + 12, deck_y + 22):                           # water
        pts = [(x + 4 + dx, wy + 3 * math.sin(dx / 9)) for dx in range(0, 104, 4)]
        d.line(pts, fill=NAVY, width=3)


def icon_radar(d, x, y):
    """Quadcopter drone (top-left) and a radar dish (bottom-right)."""
    cx, cy = x + 22, y + 18                                         # drone
    for rx, ry in ((x + 3, y + 3), (x + 41, y + 3), (x + 3, y + 33), (x + 41, y + 33)):
        d.line([cx, cy, rx, ry], fill=NAVY, width=3)
        d.ellipse([rx - 7, ry - 3, rx + 7, ry + 3], outline=NAVY, width=2)
    d.rounded_rectangle([x + 9, y + 10, x + 35, y + 26], radius=4, fill=NAVY)
    d.ellipse([x + 19, y + 26, x + 25, y + 32], fill=RED)           # camera eye
    d.chord([x + 38, y + 38, x + 102, y + 102], 180, 360, fill=NAVY)  # dish bowl
    d.polygon([(x + 62, y + 68), (x + 78, y + 68), (x + 84, y + 100),
               (x + 56, y + 100)], fill=NAVY)                       # stand
    d.line([x + 70, y + 70, x + 88, y + 42], fill=NAVY, width=4)    # feed arm
    d.ellipse([x + 84, y + 38, x + 92, y + 46], fill=RED)           # feed head
    for r in (14, 24):                                              # signal arcs
        d.arc([x + 88 - r, y + 42 - r, x + 88 + r, y + 42 + r],
              195, 285, fill=RED, width=3)


def icon_cyclone(d, x, y):
    """Logarithmic spiral storm over two wave lines."""
    cx, cy = x + 55, y + 44
    pts = []
    for i in range(121):
        t = i / 120
        ang = t * 3.2 * 2 * math.pi
        r = 4 + t * 44
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang) * 0.92))
    d.line(pts, fill=NAVY, width=8, joint="curve")
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED)           # eye
    for wy in (y + 97, y + 106):
        pts = [(x + 4 + dx, wy + 2.5 * math.sin(dx / 8)) for dx in range(0, 104, 4)]
        d.line(pts, fill=RED, width=3)


def icon_coin(d, x, y):
    """A big euro coin: navy disc, cream ring and glyph."""
    d.ellipse([x + 11, y + 11, x + 99, y + 99], fill=NAVY)
    d.ellipse([x + 18, y + 18, x + 92, y + 92], outline=CREAM, width=3)
    d.text((x + 55, y + 57), "€", font=font(SANS_B, 52), fill=CREAM, anchor="mm")


def icon_flags(d, x, y):
    """Two flags on poles: Canada-style (left) and China-style (right)."""
    for px in (x + 22, x + 66):
        d.line([px, y + 14, px, y + 100], fill=NAVY, width=5)
        d.ellipse([px - 4, y + 6, px + 4, y + 14], fill=RED)
    d.line([x + 6, y + 100, x + 104, y + 100], fill=NAVY, width=4)  # ground
    # Left flag: white, red bars, red centre mark.
    d.polygon([(x + 22, y + 16), (x + 58, y + 21), (x + 58, y + 45),
               (x + 22, y + 40)], fill=WHITE, outline=NAVY)
    d.polygon([(x + 22, y + 16), (x + 29, y + 17), (x + 29, y + 41),
               (x + 22, y + 40)], fill=RED)
    d.polygon([(x + 51, y + 20), (x + 58, y + 21), (x + 58, y + 45),
               (x + 51, y + 44)], fill=RED)
    d.ellipse([x + 34, y + 24, x + 46, y + 36], fill=RED)
    # Right flag: red field, cream star and dots.
    d.polygon([(x + 66, y + 16), (x + 102, y + 21), (x + 102, y + 45),
               (x + 66, y + 40)], fill=RED, outline=NAVY)
    d.polygon(star_points(x + 76, y + 27, 6, 2.5), fill=CREAM)
    for dx, dy in ((86, 22), (89, 28), (86, 34)):
        d.ellipse([x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2], fill=CREAM)


# ---------------------------------------------------------------- layout

PANELS = [
    ("MANILA", "Trump lands in Manila for Quad talks", icon_plane),
    ("CRIMEA & KYIV", "Ukraine hits Crimean Bridge again; Kyiv's bridges pounded",
     icon_bridge),
    ("BAHRAIN", "Iranian drones strike US radar in Bahrain", icon_radar),
    ("BAY OF BENGAL", "Cyclone Akvan bears down on India's east coast",
     icon_cyclone),
    ("BRUSSELS", "EU plans €45bn loan for Ukraine's budget", icon_coin),
    ("APEC", "Canada & China extend trade deals before APEC", icon_flags),
]


def draw_masthead(d):
    d.rectangle([0, 0, W, 96], fill=RED)
    f = fit_font(d, "WEDNESDAY · 18 NOVEMBER 2026", SANS_B, 980, 56)
    d.text((512, 48), "WEDNESDAY · 18 NOVEMBER 2026", font=f, fill=WHITE,
           anchor="mm")
    f = fit_font(d, "THE WORLD IN ONE DAY", SERIF_B, 968, 98)
    d.text((512, 158), "THE WORLD IN ONE DAY", font=f, fill=NAVY, anchor="mm")
    d.rectangle([28, 214, 996, 219], fill=RED)
    d.rectangle([28, 223, 996, 225], fill=NAVY)
    d.text((512, 250), "The day's biggest stories in a single picture",
           font=font(SERIF, 29), fill=NAVY, anchor="mm")


def draw_panel(d, px, py, pw, ph, place, headline, icon_fn):
    d.rectangle([px, py, px + pw, py + ph], fill=PANEL_BG, outline=NAVY, width=3)
    d.rectangle([px, py, px + pw, py + 42], fill=NAVY)
    d.text((px + 14, py + 21), place, font=font(SANS_B, 27), fill=WHITE,
           anchor="lm")
    d.rectangle([px + pw - 26, py + 15, px + pw - 14, py + 27], fill=RED)
    icon_fn(d, px + 12, py + 56)
    tx = px + 136
    tw = px + pw - 12 - tx
    f, lines = headline_lines(d, headline, tw)
    ty = py + 58
    lh = int(f.size * 1.24)
    for line in lines:
        d.text((tx, ty), line, font=f, fill=NAVY, anchor="la")
        ty += lh


def draw_grid(d):
    pw, ph = 477, 198
    for i, (place, headline, icon_fn) in enumerate(PANELS):
        px = 28 + (i % 2) * (pw + 14)
        py = 284 + (i // 2) * (ph + 14)
        draw_panel(d, px, py, pw, ph, place, headline, icon_fn)


TICKER_LINES = [
    "UK sanctions Israeli settlement firms",
    "Strong El Niño brings droughts and wildfires",
    "India beat Pakistan 2-1 in Dhaka to win a record 10th SAFF football title",
]


def draw_ticker(d):
    d.rectangle([0, 920, W, H], fill=NAVY)
    d.rectangle([0, 920, W, 924], fill=RED)
    for i, line in enumerate(TICKER_LINES):
        f = fit_font(d, line, SANS_B, 980, 24, minimum=16)
        d.text((512, 941 + i * 31), line, font=f, fill=WHITE, anchor="mm")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_grid(d)
    draw_ticker(d)
    out = Path(__file__).resolve().parent.parent / "entry.png"
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
