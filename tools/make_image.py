#!/usr/bin/env python3
"""Render entry.png: the world news of Wednesday 18 November 2026 in one image.

Newspaper-poster style, drawn entirely with PIL shapes and DejaVu type so
every word stays crisp. V2 layout: the masthead naming the day, a dotted
world map with numbered pins for the six panel stories (plus dots for the
briefs), the six story panels in a 3x2 grid, and an "Around the world in
brief" section of eleven one-line briefs — 17 stories in all.

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
MAP_BG = (233, 238, 243)     # pale sea grey-blue
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


def headline_lines(d, text, max_w, max_lines=3, start=33, minimum=22,
                   max_h=None):
    """Shrink the headline font until the wrap fits max_lines lines
    (and, when max_h is given, fits that pixel height too)."""
    size = start
    while size >= minimum:
        f = font(SANS_B, size)
        lines = wrap_text(d, text, f, max_w)
        lh = int(size * 1.18)
        if len(lines) <= max_lines and (max_h is None
                                        or len(lines) * lh <= max_h):
            return f, lines
        size -= 1
    f = font(SANS_B, minimum)
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


def render_icon(icon_fn, size):
    """Draw an icon in its native 110x110 box, then scale it to size."""
    tmp = Image.new("RGBA", (110, 110), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    icon_fn(td, 0, 0)
    return tmp.resize((size, size), Image.LANCZOS)


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


# ------------------------------------------------------------- world map
# Equirectangular landmask, 104 columns (lon -180..180) by 24 rows
# (lat +80..-58). '#' is land, '.' is sea. Authored by hand; the pins and
# dots below are (column, row) cells in the same grid.

LANDMASK = [
    "....................########...........#####...........##..###....#############.......#########.....###.",
    "...########....####################...########.......##################################################.",
    "...#########...##########.....########..#####..#....##################################################..",
    "....########....###########...########...##.......###################################################...",
    "...............############..########.............###############################################.###...",
    "................#####################.............############################################...##.....",
    "................###################..............##########...####################################......",
    "...............##################................###..#######.##############################...##.......",
    "...............################.................###########################################.............",
    "................###########.##.................######################...#################...............",
    "..................##########.###...............#################.........#####..######.##...............",
    "........................###########............#######################....###....#####.##...............",
    "..........................###########...........####################........#.....###########...........",
    "...........................##############........################..................########...#######...",
    "...........................###############............##########.....................#########.######...",
    "............................###############............#########.........................###.#####......",
    ".............................############..............#########.......................###########......",
    "..............................#########................########.###....................###########......",
    "..............................########..................######..##......................#########.......",
    "...............................######....................#####...........................#######......##",
    "...............................#####........................................................#####....###",
    "...............................####..................................................................##.",
    "...............................###......................................................................",
    "...............................##.......................................................................",
]

# (label, column, row): the six panel stories.
MAP_PINS = [
    ("1", 87, 11),    # Manila
    ("2", 61, 5),     # Kyiv (Crimea just below)
    ("3", 67, 9),     # Bahrain
    ("4", 78, 11),    # Bay of Bengal
    ("5", 53, 5),     # Brussels
    ("6a", 86, 7),    # Beijing
    ("6b", 30, 6),    # Ottawa
]

# (column, row): small unnumbered dots for the briefs' regions.
MAP_DOTS = [
    (69, 8),    # Hormuz
    (81, 11),   # Thailand
    (24, 7),    # United States
    (74, 9),    # New Delhi
    (75, 10),   # India
    (51, 4),    # London
    (65, 7),    # Tehran
    (80, 10),   # Dhaka
    (9, 14),    # El Niño, mid-Pacific
]

MAP_X0, MAP_Y0 = 48.5, 319.2     # centre of the (0, 0) cell
MAP_PX, MAP_PY = 9.0, 6.42       # cell pitch in pixels


def map_cell(col, row):
    return (MAP_X0 + col * MAP_PX, MAP_Y0 + row * MAP_PY)


def draw_map(d):
    d.rectangle([28, 276, 996, 476], fill=MAP_BG, outline=NAVY, width=3)
    d.rectangle([28, 276, 996, 308], fill=NAVY)
    d.text((44, 292), "THE DAY ON THE MAP", font=font(SANS_B, 21),
           fill=WHITE, anchor="lm")
    note = "numbered pins: the six panels · red dots: the briefs"
    f = fit_font(d, note, SANS, 470, 15, minimum=11)
    d.text((980, 292), note, font=f, fill=CREAM, anchor="rm")
    for row, line in enumerate(LANDMASK):
        for col, ch in enumerate(line):
            if ch == "#":
                cx, cy = map_cell(col, row)
                d.ellipse([cx - 2.7, cy - 2.7, cx + 2.7, cy + 2.7], fill=NAVY)
    for col, row in MAP_DOTS:
        cx, cy = map_cell(col, row)
        d.ellipse([cx - 3.2, cy - 3.2, cx + 3.2, cy + 3.2], fill=RED,
                  outline=WHITE, width=1)
    for label, col, row in MAP_PINS:
        cx, cy = map_cell(col, row)
        if len(label) > 1:
            r, fs = 11, 10
        else:
            r, fs = 10, 13
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=WHITE,
                  width=2)
        d.text((cx, cy), label, font=font(SANS_B, fs), fill=WHITE, anchor="mm")


def draw_panel(img, d, px, py, pw, ph, place, headline, icon_fn):
    d.rectangle([px, py, px + pw, py + ph], fill=PANEL_BG, outline=NAVY, width=3)
    d.rectangle([px, py, px + pw, py + 30], fill=NAVY)
    d.text((px + 12, py + 15), place, font=font(SANS_B, 21), fill=WHITE,
           anchor="lm")
    d.rectangle([px + pw - 24, py + 9, px + pw - 12, py + 21], fill=RED)
    icon = render_icon(icon_fn, 84)
    img.paste(icon, (px + 10, py + 36), icon)
    tx = px + 106
    tw = pw - 106 - 10
    f, lines = headline_lines(d, headline, tw, max_lines=4, start=20,
                              minimum=14, max_h=86)
    ty = py + 38
    lh = int(f.size * 1.18)
    for line in lines:
        d.text((tx, ty), line, font=f, fill=NAVY, anchor="la")
        ty += lh


def draw_grid(img, d):
    pw, ph = 314, 124
    for i, (place, headline, icon_fn) in enumerate(PANELS):
        px = 28 + (i % 3) * (pw + 13)
        py = 486 + (i // 3) * (ph + 8)
        draw_panel(img, d, px, py, pw, ph, place, headline, icon_fn)


# ---------------------------------------------------------------- briefs

BRIEFS = [
    ("HORMUZ", "Attack on the Panama-flagged tanker MT Tara Gas; 21 of 24 "
               "Indian crew evacuated safely at Khasab."),
    ("THAILAND", "A major fire kills 11 people and injures more than a dozen."),
    ("UNITED STATES", "Outages hit Chase, Wells Fargo and Zelle; Microsoft "
                      "services restored after 36 hours down."),
    ("MANILA", "Modi offers free e-visas and deeper maritime ties to ASEAN."),
    ("NEW DELHI", "India re-elected to the ITU Council for 2027-2030."),
    ("INDIA", "Amazon announces a $7 billion investment in renewable energy."),
    ("LONDON", "Clashes between Bangladeshi party supporters injure at "
               "least four."),
    ("TEHRAN", "Iran warns of worsening gas shortages this winter as energy "
               "sites take damage."),
    ("LONDON", "UK sanctions Israeli settlement firms."),
    ("GLOBAL", "Strong El Niño brings droughts and wildfires."),
    ("DHAKA", "India beat Pakistan 2-1 to win a record 10th SAFF "
              "football title."),
]


def draw_brief(d, x, y, place, body, max_w):
    """One brief: bold-caps place lead-in, regular body, wrapped by hand so
    the bold lead-in is measured with the bold font. At most two lines."""
    f_b = font(SANS_B, 14)
    f_r = font(SANS, 14)
    space_w = d.textlength(" ", font=f_r)
    tokens = [(w, True) for w in place.split()]
    tokens.append(("—", True))
    tokens += [(w, False) for w in body.split()]
    lines, cur, cur_w = [], [], 0.0
    for word, bold in tokens:
        ww = d.textlength(word, font=f_b if bold else f_r)
        add = ww if not cur else ww + space_w
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w = [(word, bold, ww)], ww
        else:
            cur.append((word, bold, ww))
            cur_w += add
    if cur:
        lines.append(cur)
    for i, line in enumerate(lines[:2]):
        lx = x
        for word, bold, ww in line:
            d.text((lx, y + i * 17), word, font=f_b if bold else f_r,
                   fill=NAVY, anchor="la")
            lx += ww + space_w


def draw_briefs(d):
    d.rectangle([28, 752, 996, 1016], fill=PANEL_BG, outline=NAVY, width=3)
    d.rectangle([28, 752, 996, 782], fill=NAVY)
    d.text((44, 767), "AROUND THE WORLD IN BRIEF", font=font(SANS_B, 21),
           fill=WHITE, anchor="lm")
    d.text((980, 767), "11 more stories from the day", font=font(SANS, 15),
           fill=CREAM, anchor="rm")
    d.line([512, 794, 512, 1006], fill=(203, 199, 186), width=1)
    for i, (place, body) in enumerate(BRIEFS[:6]):
        draw_brief(d, 44, 796 + i * 36, place, body, 448)
    for i, (place, body) in enumerate(BRIEFS[6:]):
        draw_brief(d, 524, 796 + i * 36, place, body, 448)


def main():
    for row in LANDMASK:
        assert len(row) == 104, f"landmask row has {len(row)} cells"
    assert len(LANDMASK) == 24
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_map(d)
    draw_grid(img, d)
    draw_briefs(d)
    out = Path(__file__).resolve().parent.parent / "entry.png"
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
