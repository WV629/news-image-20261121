#!/usr/bin/env python3
"""Render entry.png: a one-page newspaper front page summing up
Saturday 21 November 2026 in 36 stories, drawn entirely with Pillow.

Format: date-first serif masthead, red stat strip, region chips,
3 feature stories with drawn banner art, 10 smaller stories with
mini art, a dark world map with numbered pins, 23 one-line briefs,
a markets strip, and a DATE CHECK strip naming the big Friday 20 Nov
and Thursday 19 Nov stories so they are never shown as Saturday news.

Date discipline: every story here happened, or was first reported,
on Saturday 21 November 2026 in at least one time zone, as reported
live on 21 Nov 2026 (AP/AFP/Dawn/The Hindu/Manila Times/Reuters/
One Turn). Claims are attributed in the decks, not stated as fact.

Deterministic: fixed layout, fixed palette, no network, no random
numbers, no timestamps. Run: python3 generate.py writes entry.png
(1024x1024) next to this file. It prints a warning for any headline,
deck or brief that overflows its box.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (247, 242, 232)
PAPER_LT = (252, 250, 244)
INK = (24, 24, 24)
NAVY = (18, 42, 68)
NAVY_DK = (12, 28, 50)
RED = (178, 38, 38)
RED_DK = (140, 26, 26)
GOLD = (198, 148, 52)
GREY = (108, 105, 96)
LINE = (196, 189, 172)
SEA = (13, 30, 54)
LAND = (222, 206, 172)
LAND_LN = (150, 138, 110)
TEAL = (24, 120, 116)
BLUE = (36, 80, 164)
ORANGE = (198, 110, 30)
PURPLE = (110, 60, 140)
GREEN = (60, 130, 60)

FD = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FD, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FD, "DejaVuSans.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")

WARN = []


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    out, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def para(d, x, y, text, f, max_w, leading, fill=INK, max_lines=None):
    lines = wrap(d, text, f, max_w)
    if max_lines is not None and len(lines) > max_lines:
        WARN.append("TRUNCATED %r to %d lines" % (text[:48], max_lines))
        lines = lines[:max_lines]
    for line in lines:
        d.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def fit_one_line(d, text, f, max_w, warn_label):
    """Shrink-free single line: warn if it does not fit."""
    if d.textlength(text, font=f) > max_w:
        WARN.append("OVERFLOW %s: %r" % (warn_label, text[:60]))
    return text


def hline(d, x0, x1, y, w=2, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)


def vgrad(d, x0, y0, x1, y1, top, bot):
    n = max(1, y1 - y0)
    for i in range(n):
        t = i / n
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def stars(d, x0, y0, x1, y1, pts):
    for (sx, sy, r) in pts:
        d.ellipse([x0 + sx - r, y0 + sy - r, x0 + sx + r, y0 + sy + r],
                  fill=(235, 235, 220))


# ---------------------------------------------------------------- data

STATS = [
    ("2", "missiles down in Poland"),
    ("\u22123.7%", "S&P 500 on Friday"),
    ("\u20ac7.9bn", "EU payout to Ukraine"),
    ("235 mo", "Gupta sentence"),
    ("3", "UK\u2013EU deals signed"),
    ("1st", "Trump\u2013Xi\u2013Putin summit"),
]

CHIPS = [
    ("EUROPE 11", BLUE),
    ("AMERICAS 7", TEAL),
    ("ASIA-PACIFIC 9", ORANGE),
    ("MIDEAST 4", PURPLE),
    ("AFRICA 2", GREEN),
    ("WORLD 3", RED),
]

# (num, city, topic, headline, deck, art)
FEATURES = [
    ("01", "POLAND", "MISSILES",
     "Russian missiles hit Poland",
     "Two missiles and a suspected drone come down; Warsaw calls it "
     "a deliberate provocation, NATO a grave violation of its airspace. "
     "(AFP, Reuters)",
     "poland"),
    ("02", "SHENZHEN, CHINA", "SUMMIT",
     "Trump, Xi and Putin leave first summit with little to show",
     "Trilateral talks end with a \u201chollow\u201d peace promise and few "
     "concrete results; India says it has \u201ctaken note\u201d. "
     "(Dawn, The Hindu)",
     "summit"),
    ("03", "NEW YORK", "MARKETS",
     "S&P 500 slides into correction as AI shares plunge",
     "US stocks fall about 3.7% on Friday as the AI sell-off spreads; "
     "the Dow joins the S&P in correction territory. (One Turn)",
     "markets"),
]

# (num, city, topic, headline, deck, art)
SMALLS = [
    ("04", "BRUSSELS", "EUROPE",
     "Burnham signs three UK\u2013EU deals",
     "Food trade, carbon and youth mobility agreed. (Reuters)", "eu"),
    ("05", "RIYADH", "CONFLICT",
     "Houthi missiles intercepted over Riyadh",
     "Three missiles fired at Riyadh destroyed. (Dawn)", "missile"),
    ("06", "SAN FRANCISCO", "SCIENCE",
     "Claude \u201cproves\u201d Riemann Hypothesis",
     "Anthropic: Claude proved maths\u2019 greatest riddle. (The Hindu)", "math"),
    ("07", "NEW YORK", "JUSTICE",
     "Gupta gets 235 months in Pannun plot",
     "Plot to kill Sikh separatist leader in New York. (The Hindu)", "gavel"),
    ("08", "WORLD", "CLIMATE",
     "COP31 crunch time, no deal in sight",
     "No deal as the summit hits its crunch point. (Manila Times)", "climate"),
    ("09", "LOS ANGELES", "FIRE",
     "Jury convicts man who started Palisades Fire",
     "Rinderknecht found guilty of starting the blaze. (One Turn)", "fire"),
    ("10", "DHAKA", "UNREST",
     "Fresh arson attacks erupt in Bangladesh",
     "Violence flares before Hasina\u2019s return. (Dawn, The Hindu)",
     "unrest"),
    ("11", "COPENHAGEN", "ESPIONAGE",
     "Denmark accuses Russia of murder plot",
     "Russia accused of murder plot in Denmark. (Manila Times)", "spy"),
    ("12", "BRAS\u00cdLIA", "POLITICS",
     "Bolsonaro hospitalised for abdominal pain",
     "Former president taken to hospital. (AFP)", "flagbr"),
    ("13", "ULAANBAATAR", "POLITICS",
     "Mongolia\u2019s president resigns",
     "President quits; snap election ahead. (supportyourbusiness.eu)", "flagmn"),
]

# (num, one-line brief) — numbers continue from the 13 features
BRIEFS = [
    ("14", "THE HAGUE \u2014 ICJ ruling echoes in Gaza."),
    ("15", "BRUSSELS \u2014 \u20ac1bn EU military aid for Kyiv."),
    ("16", "BAGHDAD \u2014 Forces retake Jurf al-Sakhar."),
    ("17", "WASHINGTON \u2014 Trump eyes aide, 2028."),
    ("18", "NEW DELHI \u2014 Modi urges SCO dialogue."),
    ("19", "JOHANNESBURG \u2014 60 murders a day."),
    ("20", "DEEP SPACE \u2014 Voyager 1 calls from afar."),
    ("21", "PARIS \u2014 EU may visit Moscow on Ukraine."),
    ("22", "ROME \u2014 Crowds march against Meloni."),
    ("23", "MADRID \u2014 Amnesty: force at strike."),
    ("24", "BERLIN \u2014 Defence chief open to Moscow."),
    ("25", "CAIRO \u2014 Egypt eyes AI rivalry."),
    ("26", "KUALA LUMPUR \u2014 Rohingya to Turkey."),
    ("27", "JAKARTA \u2014 Prabowo, Xi eye sea ties."),
    ("28", "SEOUL \u2014 Move to impeach top judge."),
    ("29", "DOHA \u2014 Pakistan Shaheens rout UAE."),
    ("30", "SYDNEY \u2014 Cummins camp hits \u201chysteria\u201d."),
    ("31", "GENEVA \u2014 UN: Hodeidah raids hit aid line."),
    ("32", "SANA\u2019A \u2014 Houthis warn Saudi airspace."),
    ("33", "KYIV \u2014 Russia pounds Ukraine anew."),
    ("34", "TOKYO \u2014 China snub may lift Japan PM."),
    ("35", "MOSCOW \u2014 Russia ships fuel to Brazil."),
    ("36", "BRAS\u00cdLIA \u2014 Lula shields Indigenous land."),
]

DATE_CHECK = (
    "First reported Friday 20 Nov, NOT shown as Saturday\u2019s news: Cyclone Akvan "
    "landfall \u00b7 ~30 missiles at Kyiv \u00b7 BepiColombo reaches Mercury \u00b7 Phillips 118 "
    "\u00b7 Pancreatic-cancer pill \u00b7 ICJ Myanmar verdict (Thu 19) \u00b7 Anthropic\u2019s $83 IPO "
    "pricing \u00b7 GTA VI launch \u00b7 Riyadh tower attack (Thu) \u00b7 Khasab tanker strike (Thu)."
)

FOOTER = (
    "Every story here happened, or was first reported, on Saturday 21 November 2026. "
    "Claims are attributed. "
    "Sources: AFP \u00b7 Dawn \u00b7 The Hindu \u00b7 Manila Times \u00b7 Reuters \u00b7 One Turn"
)

# ---------------------------------------------------------------- art

def art_poland(d, x, y, w, h):
    """Night sky over Poland: missile trails, impact glow, rooftops."""
    vgrad(d, x, y, x + w, y + h, (16, 24, 48), (52, 40, 66))
    stars(d, x, y, x + w, y + h,
          [(20, 14, 1), (60, 26, 1), (120, 10, 2), (180, 22, 1),
           (240, 12, 1), (280, 30, 2), (150, 34, 1), (95, 12, 1)])
    # moon
    d.ellipse([x + w - 52, y + 10, x + w - 24, y + 38], fill=(232, 228, 200))
    d.ellipse([x + w - 46, y + 14, x + w - 26, y + 34], fill=(52, 40, 66))
    # two missile trails arcing down to an impact glow
    for (x0, y0, x1, y1) in [(30, 8, 120, 78), (150, 4, 210, 84)]:
        d.line([x + x0, y + y0, x + x1, y + y1], fill=(255, 176, 66), width=3)
        d.line([x + x0, y + y0, x + x1, y + y1], fill=(255, 226, 160), width=1)
        d.ellipse([x + x1 - 5, y + y1 - 5, x + x1 + 5, y + y1 + 5],
                  fill=(255, 200, 90))
    # impact glow
    for r, col in [(26, (255, 120, 40)), (16, (255, 170, 60)),
                   (9, (255, 220, 130))]:
        d.ellipse([x + 165 - r, y + h - 26 - r, x + 165 + r, y + h - 26 + r],
                  fill=col)
    # rooftops + lit windows
    d.polygon([(x, y + h), (x, y + h - 26), (x + 46, y + h - 40),
               (x + 92, y + h - 24), (x + 140, y + h - 34),
               (x + 200, y + h - 22), (x + w, y + h - 30), (x + w, y + h)],
              fill=(10, 14, 26))
    for wx in (18, 62, 108, 232, 268):
        d.rectangle([x + wx, y + h - 20, x + wx + 7, y + h - 12],
                    fill=(255, 214, 130))
    # Polish flag strip
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(255, 255, 255))
    d.rectangle([x, y + h - 3, x + w, y + h], fill=(220, 20, 60))


def art_summit(d, x, y, w, h):
    """Shenzhen dusk: skyline, three flags, round table."""
    vgrad(d, x, y, x + w, y + h, (214, 164, 92), (126, 84, 96))
    d.ellipse([x + w - 66, y + 12, x + w - 26, y + 52], fill=(255, 214, 140))
    # skyline
    d.rectangle([x + 8, y + 58, x + 34, y + h], fill=(52, 44, 66))
    d.rectangle([x + 44, y + 40, x + 66, y + h], fill=(44, 38, 58))
    d.rectangle([x + 76, y + 66, x + 104, y + h], fill=(56, 48, 70))
    d.rectangle([x + 220, y + 52, x + 248, y + h], fill=(48, 40, 62))
    d.rectangle([x + 258, y + 64, x + 288, y + h], fill=(58, 50, 72))
    for wx, wy in [(16, 66), (52, 48), (86, 74), (228, 60), (266, 72),
                   (24, 82), (58, 64), (236, 76)]:
        d.rectangle([x + wx, y + wy, x + wx + 6, y + wy + 8],
                    fill=(255, 214, 130))
    # three flags on poles
    poles = [(120, (178, 34, 34)), (155, (222, 30, 30)), (190, (36, 80, 164))]
    for (px, col) in poles:
        d.line([x + px, y + 34, x + px, y + 92], fill=(240, 238, 230), width=3)
        d.rectangle([x + px, y + 34, x + px + 26, y + 52], fill=col)
    d.rectangle([x + 120, y + 34, x + 146, y + 40], fill=(255, 255, 255))
    d.rectangle([x + 120, y + 46, x + 146, y + 52], fill=(255, 255, 255))
    d.rectangle([x + 155, y + 34, x + 181, y + 52], fill=(222, 30, 30))
    d.ellipse([x + 158, y + 37, x + 166, y + 45], fill=(255, 220, 60))
    d.rectangle([x + 190, y + 34, x + 216, y + 40], fill=(255, 255, 255))
    d.rectangle([x + 190, y + 40, x + 216, y + 46], fill=(36, 80, 164))
    d.rectangle([x + 190, y + 46, x + 216, y + 52], fill=(178, 34, 34))
    # round table
    d.ellipse([x + 96, y + 92, x + 214, y + 112], fill=(96, 62, 44))
    d.ellipse([x + 104, y + 94, x + 206, y + 106], fill=(140, 96, 66))


def art_markets(d, x, y, w, h):
    """Falling chart: red line over bars, closing low."""
    d.rectangle([x, y, x + w, y + h], fill=(250, 244, 232))
    # grid
    for gy in range(1, 4):
        yy = y + h * gy // 4
        d.line([x + 8, yy, x + w - 8, yy], fill=(226, 220, 204), width=1)
    # bars, falling
    tops = [18, 30, 26, 44, 40, 56, 52, 68, 64, 82]
    bw = (w - 32) // len(tops)
    for i, t in enumerate(tops):
        bx = x + 16 + i * bw
        d.rectangle([bx, y + t, bx + bw - 6, y + h - 22],
                    fill=(198, 60, 52) if i % 2 else (222, 96, 84))
    # falling line
    pts = [(x + 16 + i * bw + bw // 2, y + tops[i] - 6) for i in range(len(tops))]
    d.line(pts, fill=(140, 26, 26), width=3)
    d.ellipse([pts[-1][0] - 5, pts[-1][1] - 5, pts[-1][0] + 5, pts[-1][1] + 5],
              fill=(140, 26, 26))
    d.text((x + 10, y + h - 20), "\u22123.7%  S&P 500",
           font=F(SANS_B, 15), fill=RED_DK)


def mini_art(d, x, y, w, h, kind):
    """48px banner motif for a small story card."""
    if kind == "eu":
        d.rectangle([x, y, x + w, y + h], fill=(36, 80, 164))
        for k in range(8):
            import math as _m
            a = _m.pi * 2 * k / 8
            sx = x + w // 2 + int(13 * _m.cos(a))
            sy = y + h // 2 + int(11 * _m.sin(a))
            d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 220, 60))
        d.rectangle([x, y + h - 4, x + w, y + h], fill=(255, 220, 60))
    elif kind == "missile":
        vgrad(d, x, y, x + w, y + h, (20, 26, 48), (70, 52, 60))
        d.line([x + 20, y + 6, x + 90, y + h - 10], fill=(255, 176, 66), width=3)
        d.line([x + 80, y + 4, x + 150, y + h - 14], fill=(255, 200, 90), width=2)
        d.ellipse([x + 148, y + h - 18, x + 158, y + h - 8], fill=(255, 220, 130))
        d.rectangle([x, y + h - 8, x + w, y + h], fill=(10, 14, 26))
    elif kind == "math":
        d.rectangle([x, y, x + w, y + h], fill=(18, 42, 68))
        d.text((x + 8, y + 2), "\u03b6(s) = 0", font=F(SERIF_B, 22),
               fill=(255, 220, 130))
        d.line([x + 120, y + 10, x + 150, y + 34, x + 178, y + 12],
               fill=(120, 200, 190), width=2)
        d.ellipse([x + 168, y + 30, x + 180, y + 42], fill=(255, 255, 255))
    elif kind == "gavel":
        d.rectangle([x, y, x + w, y + h], fill=(96, 62, 44))
        d.rectangle([x + 30, y + 12, x + 90, y + 26], fill=(140, 96, 66))
        d.rectangle([x + 108, y + 14, x + 116, y + 40], fill=(60, 38, 26))
        d.rectangle([x + 20, y + 36, x + 150, y + 42], fill=(60, 38, 26))
        d.rectangle([x, y + h - 5, x + w, y + h], fill=(60, 38, 26))
    elif kind == "climate":
        vgrad(d, x, y, x + w, y + h, (120, 190, 150), (40, 110, 80))
        d.ellipse([x + w // 2 - 16, y + 6, x + w // 2 + 16, y + 38],
                  fill=(30, 90, 140))
        d.arc([x + w // 2 - 16, y + 6, x + w // 2 + 16, y + 38], 200, 340,
              fill=(120, 200, 140), width=3)
        d.line([x + 14, y + 40, x + w - 14, y + 40], fill=(255, 220, 130), width=2)
    elif kind == "fire":
        vgrad(d, x, y, x + w, y + h, (60, 20, 16), (140, 50, 20))
        for (fx, fh, col) in [(30, 26, (255, 140, 40)), (70, 34, (255, 90, 20)),
                              (110, 24, (255, 170, 60)), (145, 30, (255, 110, 30))]:
            d.polygon([(x + fx - 10, y + h - 4), (x + fx, y + h - 4 - fh),
                       (x + fx + 10, y + h - 4)], fill=col)
        d.rectangle([x, y + h - 4, x + w, y + h], fill=(20, 12, 10))
    elif kind == "unrest":
        d.rectangle([x, y, x + w, y + h], fill=(52, 44, 40))
        d.polygon([(x + 60, y + h - 4), (x + 70, y + 12), (x + 80, y + h - 4)],
                  fill=(255, 120, 40))
        d.polygon([(x + 100, y + h - 4), (x + 112, y + 18), (x + 124, y + h - 4)],
                  fill=(255, 170, 60))
        d.rectangle([x, y + h - 6, x + w, y + h], fill=(178, 38, 38))
    elif kind == "spy":
        d.rectangle([x, y, x + w, y + h], fill=(24, 24, 30))
        d.ellipse([x + w // 2 - 34, y + 10, x + w // 2 + 34, y + 38],
                  outline=(220, 220, 210), width=2)
        d.ellipse([x + w // 2 - 9, y + 15, x + w // 2 + 9, y + 33],
                  fill=(178, 38, 38))
        d.ellipse([x + w // 2 - 3, y + 21, x + w // 2 + 3, y + 27],
                  fill=(10, 10, 12))
    elif kind == "flagbr":
        d.rectangle([x, y, x + w, y + h], fill=(0, 140, 60))
        d.polygon([(x + w // 2, y + 4), (x + w - 12, y + h // 2),
                   (x + w // 2, y + h - 4), (x + 12, y + h // 2)],
                  fill=(255, 220, 40))
        d.ellipse([x + w // 2 - 13, y + h // 2 - 12, x + w // 2 + 13,
                   y + h // 2 + 12], fill=(36, 80, 164))
    elif kind == "flagmn":
        d.rectangle([x, y, x + w // 2, y + h], fill=(36, 80, 164))
        d.rectangle([x + w // 2, y, x + w, y + h], fill=(178, 38, 38))
        d.ellipse([x + w // 2 - 10, y + 10, x + w // 2 + 10, y + 30],
                  fill=(255, 220, 60))
        d.rectangle([x, y + h - 4, x + w, y + h], fill=(255, 220, 60))


FEATURE_ART = {"poland": art_poland, "summit": art_summit,
               "markets": art_markets}


# ---------------------------------------------------------------- layout

def draw_masthead(d):
    d.text((28, 14), "THE WORLD IN ONE DAY", font=F(SANS_B, 15), fill=RED)
    right = "SATURDAY\u2019S NEWS \u00b7 ONE PAGE \u00b7 36 STORIES \u00b7 6 CONTINENTS"
    d.text((W - 28 - d.textlength(right, font=F(SANS, 13)), 15), right,
           font=F(SANS, 13), fill=GREY)
    title = "Saturday 21 November 2026"
    d.text((28, 32), title, font=F(SERIF_B, 60), fill=INK)
    kicker = ("Russian missiles hit Poland \u00b7 Trump\u2013Xi\u2013Putin summit ends hollow "
              "\u00b7 Wall Street slides \u00b7 UK\u2013EU sign new deals")
    d.text((28, 104), kicker, font=F(SERIF, 15), fill=RED)
    hline(d, 28, W - 28, 128, w=4)


def draw_stats(d):
    y0 = 136
    cw = (W - 56) // 6
    for i, (big, label) in enumerate(STATS):
        cx = 28 + i * cw
        d.text((cx + 8, y0), big, font=F(SERIF_B, 27), fill=RED)
        d.text((cx + 8, y0 + 32), label, font=F(SANS, 11), fill=GREY)
        if i:
            d.line([(cx, y0 + 4), (cx, y0 + 44)], fill=LINE, width=1)
    hline(d, 28, W - 28, 186, w=1, fill=LINE)


def draw_chips(d):
    x = 28
    y = 194
    for label, col in CHIPS:
        wch = d.textlength(label, font=F(SANS_B, 12)) + 18
        d.rounded_rectangle([x, y, x + wch, y + 20], radius=10, fill=col)
        d.text((x + 9, y + 3), label, font=F(SANS_B, 12), fill=(255, 255, 255))
        x += wch + 8
    note = "ALL STORIES: SAT 21 NOV 2026, ANY TIME ZONE"
    d.text((W - 28 - d.textlength(note, font=F(SANS, 11)), y + 4), note,
           font=F(SANS, 11), fill=GREY)


def feature_card(d, x, y, w, h, feat):
    num, city, topic, headline, deck, art = feat
    d.rectangle([x, y, x + w, y + h], outline=LINE, width=1, fill=PAPER_LT)
    FEATURE_ART[art](d, x + 1, y + 1, w - 2, 110)
    ty = y + 118
    d.text((x + 10, ty), "%s \u00b7 %s \u00b7 %s" % (num, city, topic),
           font=F(SANS_B, 11), fill=RED)
    hy = ty + 18
    para(d, x + 10, hy, headline, F(SERIF_B, 22), w - 20, 26,
         max_lines=3)
    dy = hy + 3 * 26 + 4
    para(d, x + 10, dy, deck, F(SANS, 12), w - 20, 15, fill=(60, 58, 52),
         max_lines=3)


def small_card(d, x, y, w, h, item):
    num, city, topic, headline, deck, art = item
    d.rectangle([x, y, x + w, y + h], outline=LINE, width=1, fill=PAPER_LT)
    mini_art(d, x + 1, y + 1, w - 2, 46, art)
    ty = y + 50
    d.text((x + 8, ty), "%s \u00b7 %s \u00b7 %s" % (num, city, topic),
           font=F(SANS_B, 10), fill=RED)
    hy = ty + 14
    para(d, x + 8, hy, headline, F(SERIF_B, 14), w - 16, 16, max_lines=3)
    dy = hy + 3 * 16 + 2
    para(d, x + 8, dy, deck, F(SANS, 10), w - 16, 12, fill=(60, 58, 52),
         max_lines=2)


# simplified world map: rough continent polygons in a 332x174 box
CONTINENTS = [
    [(18, 28), (45, 12), (80, 16), (105, 26), (120, 40), (108, 58),
     (88, 72), (70, 88), (48, 84), (30, 66), (14, 48)],
    [(108, 10), (124, 8), (128, 18), (112, 20)],
    [(92, 96), (112, 92), (128, 100), (132, 124), (120, 152), (104, 150),
     (94, 122)],
    [(168, 30), (186, 22), (202, 28), (206, 40), (196, 52), (180, 50),
     (168, 42)],
    [(162, 28), (168, 26), (170, 34), (164, 36)],
    [(170, 62), (196, 58), (212, 68), (210, 92), (196, 118), (180, 112),
     (168, 88), (164, 72)],
    [(208, 26), (250, 14), (300, 20), (322, 34), (318, 58), (296, 72),
     (268, 78), (240, 66), (216, 52), (206, 38)],
    [(272, 84), (292, 86), (296, 96), (276, 96)],
    [(272, 122), (306, 118), (318, 130), (300, 146), (276, 142)],
]
# (pin number, map x, map y)
PINS = [("1", 200, 32), ("2", 296, 58), ("3", 78, 44), ("4", 172, 38),
        ("5", 222, 72), ("6", 38, 52), ("7", 92, 54), ("9", 52, 62),
        ("10", 272, 60), ("11", 182, 22), ("12", 118, 124),
        ("13", 282, 34)]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    for poly in CONTINENTS:
        pts = [(x + px, y + py) for (px, py) in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LN)
    d.text((x + 8, y + 8), "ATLANTIC", font=F(SANS_B, 10), fill=(140, 160, 190))
    d.text((x + 8, y + h - 20), "PACIFIC", font=F(SANS_B, 10),
           fill=(140, 160, 190))
    d.text((x + w - 52, y + 8), "ASIA", font=F(SANS_B, 10),
           fill=(140, 160, 190))
    for num, px, py in PINS:
        cx, cy = x + px, y + py
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED,
                  outline=(255, 255, 255), width=1)
        tw = d.textlength(num, font=F(SANS_B, 9))
        d.text((cx - tw / 2, cy - 6), num, font=F(SANS_B, 9),
               fill=(255, 255, 255))


def draw_briefs(d, x, y, w, h):
    cols = [[], [], []]
    for i, (num, text) in enumerate(BRIEFS):
        cols[i % 3].append((num, text))
    cw = (w - 24) // 3
    f = F(SANS, 9)
    for ci, col in enumerate(cols):
        cx = x + ci * (cw + 12)
        by = y
        for num, text in col:
            line = "%s  %s" % (num, text)
            if d.textlength(line, font=f) > cw:
                WARN.append("BRIEF OVERFLOW %s" % line[:50])
                while d.textlength(line + "\u2026", font=f) > cw and len(line) > 8:
                    line = line[:-1]
                line += "\u2026"
            d.text((cx, by), line, font=f, fill=INK)
            by += 19
    return y


def draw_markets(d, y):
    d.text((28, y + 2), "MARKETS AT CLOSE", font=F(SANS_B, 12), fill=RED)
    # S&P 500 bar: -3.7% of a 100px scale
    bx = 190
    d.rectangle([bx, y + 4, bx + 220, y + 16], outline=LINE, width=1)
    d.rectangle([bx, y + 4, bx + 220, y + 10], fill=(232, 226, 212))
    d.rectangle([bx, y + 10, bx + 220, y + 16], fill=RED)
    d.text((bx + 228, y + 2), "S&P 500  \u22123.7%  \u2014  correction territory",
           font=F(SANS_B, 12), fill=INK)
    d.text((W - 28 - d.textlength("Dow also in correction \u00b7 AI shares lead the sell-off",
                                  font=F(SANS, 12)), y + 2),
           "Dow also in correction \u00b7 AI shares lead the sell-off",
           font=F(SANS, 12), fill=GREY)


def draw_date_check(d, y):
    d.rounded_rectangle([28, y, W - 28, y + 34], radius=3, outline=RED, width=2)
    d.text((38, y + 4), "DATE CHECK", font=F(SANS_B, 11), fill=RED)
    para(d, 128, y + 4, DATE_CHECK, F(SANS, 11), W - 28 - 128 - 10, 13,
         fill=INK, max_lines=2)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_stats(d)
    draw_chips(d)
    # features: 3 cards, y 212..458
    fw = (W - 56 - 24) // 3
    for i, feat in enumerate(FEATURES):
        fx = 28 + i * (fw + 12)
        feature_card(d, fx, 212, fw, 246, feat)
    # smalls: 2 rows of 5, 132 tall
    sw = (W - 56 - 36) // 5
    for row in range(2):
        for i in range(5):
            item = SMALLS[row * 5 + i]
            sx = 28 + i * (sw + 9)
            small_card(d, sx, 464 + row * 150, sw, 142, item)
    # bottom: map + briefs
    d.text((28, 762), "WHERE IT HAPPENED", font=F(SANS_B, 13), fill=RED)
    d.text((340, 762), "ALSO ON SATURDAY 21 NOVEMBER \u2014 23 MORE STORIES",
           font=F(SANS_B, 13), fill=RED)
    hline(d, 28, W - 28, 780, w=1, fill=LINE)
    draw_map(d, 28, 786, 300, 154)
    draw_briefs(d, 340, 786, W - 28 - 340, 154)
    draw_markets(d, 946)
    draw_date_check(d, 970)
    if d.textlength(FOOTER, font=F(SANS, 11)) > W - 56:
        WARN.append("FOOTER OVERFLOW")
    d.text((28, 1008), FOOTER, font=F(SANS, 11), fill=GREY)
    return img


def main():
    img = build()
    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    print("wrote %s %dx%d %d bytes" % (out, W, H, size))
    if size > 1048576:
        print("WARNING: over 1 MiB cap")
    for w in WARN:
        print("WARN:", w)
    print("warnings:", len(WARN))


if __name__ == "__main__":
    main()
