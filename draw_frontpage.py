#!/usr/bin/env python3
"""Build-time tool: compose the front page for 20 November 2026.

Reads the three generated illustrations from assets/ and lays them out
as a newspaper front page, writing entry.png (1024x1024) next to this
script. Deterministic: no randomness, no timestamps, no network.
Run:  python3 draw_frontpage.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 28
CONTENT_W = PAGE_W - 2 * MARGIN

PAPER = (246, 241, 231)      # newsprint cream
INK = (22, 22, 22)           # near-black text
NAVY = (20, 34, 58)          # nameplate and footer band
CREAM = (246, 241, 231)      # text on navy
GOLD = (201, 162, 82)        # thin rule under the nameplate
RED = (163, 22, 33)          # kickers and accents
GREY = (90, 86, 78)          # captions

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def fit_font(draw, text, path, start_size, max_width, min_size=12):
    """Largest font size (down from start_size) at which text fits."""
    size = start_size
    while size > min_size:
        fnt = font(path, size)
        if draw.textlength(text, font=fnt) <= max_width:
            return fnt
        size -= 1
    return font(path, min_size)


def draw_text_block(draw, x, y, text, fnt, fill, max_width, line_height):
    """Draw wrapped text; returns the y just below the last line."""
    for line in wrap(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def cover_crop(img, target_w, target_h):
    """Centre-crop the image to the target aspect, then resize."""
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    else:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))
    return img.resize((target_w, target_h), Image.LANCZOS)


def rule(draw, y, weight=2, fill=INK, x0=MARGIN, x1=PAGE_W - MARGIN):
    draw.line([(x0, y), (x1, y)], fill=fill, width=weight)


def build():
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(page)

    # ---- Nameplate -------------------------------------------------
    draw.rectangle([0, 0, PAGE_W, 104], fill=NAVY)
    title_font = fit_font(draw, "THE WORLD TODAY", SERIF_BOLD, 58,
                          CONTENT_W)
    title_w = draw.textlength("THE WORLD TODAY", font=title_font)
    draw.text(((PAGE_W - title_w) / 2, 10), "THE WORLD TODAY",
              font=title_font, fill=CREAM)
    date_font = font(SANS_BOLD, 25)
    date_text = "FRIDAY, 20 NOVEMBER 2026"
    date_w = draw.textlength(date_text, font=date_font)
    draw.text(((PAGE_W - date_w) / 2, 68), date_text,
              font=date_font, fill=GOLD)
    draw.line([(0, 104), (PAGE_W, 104)], fill=GOLD, width=3)

    # ---- Lead story: Cyclone Akvan --------------------------------
    y = 116
    kicker_font = font(SANS_BOLD, 21)
    draw.text((MARGIN, y), "CYCLONE AKVAN  •  ODISHA, INDIA",
              font=kicker_font, fill=RED)
    y += 28
    headline_font = fit_font(draw, "AKVAN SLAMS INDIA'S EAST COAST",
                             SERIF_BOLD, 46, CONTENT_W)
    draw.text((MARGIN, y), "AKVAN SLAMS INDIA'S EAST COAST",
              font=headline_font, fill=INK)
    y += 52

    cyclone = Image.open(os.path.join(ASSETS, "cyclone.png")).convert("RGB")
    cyclone = cover_crop(cyclone, CONTENT_W, 220)
    page.paste(cyclone, (MARGIN, y))
    draw.rectangle([MARGIN, y, MARGIN + CONTENT_W, y + 220],
                   outline=INK, width=2)
    y += 230

    deck_font = font(SERIF, 24)
    y = draw_text_block(
        draw, MARGIN, y,
        "More than 120,000 people evacuated as the severe storm "
        "comes ashore between Puri and Gopalpur. 300+ rescue teams "
        "deployed; about 60 trains cancelled.",
        deck_font, INK, CONTENT_W, 28)
    y += 4
    rule(draw, y)
    y += 10

    # ---- Second row: summit and GTA VI ----------------------------
    col_w = (CONTENT_W - 24) // 2
    col_x = [MARGIN, MARGIN + col_w + 24]

    stories = [
        {
            "image": "summit.png",
            "kicker": "SHENZHEN SUMMIT",
            "headline": "Trump, Xi and Putin meet in Shenzhen",
            "deck": "'Declaration Towards Peace' calls for UN reform "
                    "and nuclear-risk talks. No Ukraine breakthrough.",
        },
        {
            "image": "gta6.png",
            "kicker": "GAMES",
            "headline": "GTA VI breaks records on launch day",
            "deck": "99 on Metacritic; ~19m copies, $1.84bn on day "
                    "one. 6m watched live; 1 in 5 US workers took "
                    "the day off.",
        },
    ]

    top = y
    bottoms = []
    for i, story in enumerate(stories):
        x = col_x[i]
        cy = top
        draw.text((x, cy), story["kicker"], font=kicker_font, fill=RED)
        cy += 26
        head_font = font(SERIF_BOLD, 27)
        head_lines = wrap(draw, story["headline"], head_font, col_w)
        for line in head_lines:
            draw.text((x, cy), line, font=head_font, fill=INK)
            cy += 30
        cy += 4
        img = Image.open(os.path.join(ASSETS, story["image"])).convert("RGB")
        img = cover_crop(img, col_w, 150)
        page.paste(img, (x, cy))
        draw.rectangle([x, cy, x + col_w, cy + 150], outline=INK, width=2)
        cy += 160
        deck2_font = font(SANS, 18)
        cy = draw_text_block(draw, x, cy, story["deck"], deck2_font,
                             INK, col_w, 22)
        bottoms.append(cy)

    y = max(bottoms) + 8
    rule(draw, y)
    y += 10

    # ---- The Hague --------------------------------------------------
    hague_font = font(SERIF_BOLD, 23)
    y = draw_text_block(
        draw, MARGIN, y,
        "THE HAGUE \u2014 The world court ruled Myanmar committed "
        "genocide against the Rohingya in its 2017 crackdown.",
        hague_font, INK, CONTENT_W, 26)
    y += 6
    rule(draw, y)
    y += 10

    # ---- Also today -------------------------------------------------
    strip_label = font(SANS_BOLD, 18)
    strip_font = font(SANS, 17)
    label = "ALSO TODAY  \u2014  "
    draw.text((MARGIN, y), label, font=strip_label, fill=RED)
    label_w = draw.textlength(label, font=strip_label)
    y = draw_text_block(
        draw, MARGIN + label_w, y,
        "Anthropic's ~$2tn Nasdaq debut \u2022 Meta rethinks its "
        "2030 net-zero goal \u2022 First US deep-sea mining leases "
        "\u2022 Somalia expels UAE envoy \u2022 S. Korea court clears "
        "ex-PM Han \u2022 Fiji drought disaster \u2022 Voyager 1 one "
        "light-day out.",
        strip_font, INK, CONTENT_W - label_w, 20)

    # ---- Footer: the date, again ------------------------------------
    draw.rectangle([0, PAGE_H - 36, PAGE_W, PAGE_H], fill=NAVY)
    foot_font = font(SANS_BOLD, 17)
    foot_text = "Friday, 20 November 2026  \u2022  The World Today"
    foot_w = draw.textlength(foot_text, font=foot_font)
    draw.text(((PAGE_W - foot_w) / 2, PAGE_H - 28), foot_text,
              font=foot_font, fill=CREAM)

    out_path = os.path.join(HERE, "entry.png")
    page.save(out_path, format="PNG", optimize=True)
    print("wrote", out_path, page.size,
          os.path.getsize(out_path), "bytes")


if __name__ == "__main__":
    build()
