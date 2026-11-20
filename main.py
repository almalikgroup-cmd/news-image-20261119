#!/usr/bin/env python3
"""Sum up the world news of Thursday 19 November 2026 in one image.

The program draws a one-page newspaper front page -- a dated masthead, a
lead story, four story cards and an "also today" strip -- and writes it as
a PNG to /output/entry.png (or to $MAKEFUN_OUTPUT_DIR/entry.png when that
variable is set, for local runs).

Pure Python 3.13 standard library: the picture is rasterised by hand into
an RGB buffer and encoded as a PNG with zlib.  No network, no files read,
no randomness and no clock: every run writes exactly the same bytes.

The stories are the day's wire news of 19 November 2026: the first
Trump-Xi-Putin three-way summit at APEC in Shenzhen and its joint peace
declaration; the ICJ ruling that Myanmar committed genocide of the
Rohingya; Anthropic's record $81bn IPO; the Iran war threats and Israeli
tanks in central Gaza; Ukraine's third strike on the Crimean Bridge in a
week and the Russian plane crash that killed 19; plus COP31, the
Denmark-Greenland pact, IMF inflation, children in conflict zones and
Fiji's El Nino drought disaster in the briefs strip.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- palette
PAPER = (243, 239, 229)
CARD = (255, 255, 255)
SHADOW = (216, 210, 196)
INK = (17, 21, 31)
NAVY = (13, 27, 62)
GOLD = (203, 152, 46)
PALE = (168, 182, 214)
RULE = (198, 192, 176)
BLUE = (21, 101, 192)
PURPLE = (84, 52, 150)
TEAL = (0, 117, 104)
BURNT = (176, 58, 20)
STEEL = (52, 92, 138)
WHITE = (255, 255, 255)
RED = (178, 34, 52)

# ------------------------------------------------------------------- font
# A 5x7 bitmap font, one entry per character: seven row values, each a
# 5-bit mask, bit 4 the leftmost pixel.  Uppercase only; the text helper
# uppercases everything it draws.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "+": (0x00, 0x04, 0x04, 0x0E, 0x04, 0x04, 0x00),
    "·": (0x00, 0x00, 0x00, 0x0C, 0x0C, 0x00, 0x00),
}


# ----------------------------------------------------------------- canvas
class Canvas:
    """A minimal RGB raster with the primitives the page needs."""

    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(bytes(colour) * (width * height))

    def set_px(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            at = (y * self.width + x) * 3
            self.pixels[at:at + 3] = bytes(colour)

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            at = (yy * self.width + x0) * 3
            self.pixels[at:at + len(row)] = row

    def frame_rect(self, x, y, w, h, colour, thick=3):
        self.fill_rect(x, y, w, thick, colour)
        self.fill_rect(x, y + h - thick, w, thick, colour)
        self.fill_rect(x, y, thick, h, colour)
        self.fill_rect(x + w - thick, y, thick, h, colour)

    def line(self, x0, y0, x1, y1, colour, thick=2):
        # Bresenham, stamped with a small square brush for thickness.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.fill_rect(x0 - half, y0 - half, thick, thick, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, radius, colour, fill=False, thick=2):
        if fill:
            for yy in range(cy - radius, cy + radius + 1):
                span = int((radius * radius - (yy - cy) ** 2) ** 0.5)
                self.fill_rect(cx - span, yy, 2 * span + 1, 1, colour)
            return
        # Midpoint circle outline, stamped thick.
        x = radius
        y = 0
        err = 1 - radius
        half = thick // 2
        while x >= y:
            for px, py in ((x, y), (y, x), (-y, x), (-x, y),
                           (-x, -y), (-y, -x), (y, -x), (x, -y)):
                self.fill_rect(cx + px - half, cy + py - half,
                               thick, thick, colour)
            y += 1
            if err < 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x) + 1

    def text(self, x, y, string, scale, colour, bold=False):
        """Draw uppercase bitmap text; returns the x just past the text."""
        cursor = x
        for char in string.upper():
            glyph = FONT.get(char, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (0x10 >> col):
                        self.fill_rect(cursor + col * scale,
                                       y + row * scale, scale, scale, colour)
                        if bold:
                            self.fill_rect(cursor + col * scale + scale // 2,
                                           y + row * scale, scale, scale,
                                           colour)
            cursor += 6 * scale
        return cursor - scale

    def text_centred(self, y, string, scale, colour, bold=False):
        width = text_width(string, scale)
        return self.text((self.width - width) // 2, y, string, scale,
                         colour, bold)


def text_width(string, scale):
    if not string:
        return 0
    return len(string) * 6 * scale - scale


# ------------------------------------------------------------------ icons
def icon_scales(cv, cx, cy, colour):
    """Scales of justice, drawn in a 44px box centred on (cx, cy)."""
    cv.line(cx, cy - 20, cx, cy + 14, colour, 3)
    cv.line(cx - 20, cy - 14, cx + 20, cy - 14, colour, 3)
    cv.circle(cx, cy - 20, 3, colour, fill=True)
    for side in (-20, 20):
        cv.line(cx + side, cy - 14, cx + side - 7, cy + 6, colour, 2)
        cv.line(cx + side, cy - 14, cx + side + 7, cy + 6, colour, 2)
        cv.line(cx + side - 9, cy + 6, cx + side + 9, cy + 6, colour, 3)
    cv.fill_rect(cx - 12, cy + 16, 24, 4, colour)


def icon_chip(cv, cx, cy, colour):
    """A microchip: square body, inner square, pins on every side."""
    cv.frame_rect(cx - 13, cy - 13, 26, 26, colour, 3)
    cv.frame_rect(cx - 6, cy - 6, 12, 12, colour, 2)
    for off in (-9, 0, 9):
        cv.fill_rect(cx + off - 1, cy - 19, 3, 6, colour)
        cv.fill_rect(cx + off - 1, cy + 13, 3, 6, colour)
        cv.fill_rect(cx - 19, cy + off - 1, 6, 3, colour)
        cv.fill_rect(cx + 13, cy + off - 1, 6, 3, colour)


def icon_burst(cv, cx, cy, colour):
    """A starburst of radiating lines -- an explosion, kept abstract."""
    import math
    for step in range(12):
        angle = step * math.pi / 6
        reach = 20 if step % 2 == 0 else 12
        x1 = cx + int(reach * math.cos(angle))
        y1 = cy + int(reach * math.sin(angle))
        cv.line(cx, cy, x1, y1, colour, 3)
    cv.circle(cx, cy, 5, colour, fill=True)


def icon_bridge(cv, cx, cy, colour):
    """An arch bridge over water, sized to sit inside a tag band."""
    cv.fill_rect(cx - 24, cy - 6, 48, 4, colour)
    for xx in range(cx - 20, cx + 21, 8):
        # Arch: posts rise from a shallow curve under the deck.
        depth = 11 - abs(xx - cx) // 4
        cv.fill_rect(xx, cy - 2, 3, depth, colour)
    for wave in range(3):
        x0 = cx - 22 + wave * 16
        cv.line(x0, cy + 17, x0 + 5, cy + 13, colour, 2)
        cv.line(x0 + 5, cy + 13, x0 + 10, cy + 17, colour, 2)


def icon_flags(cv, x, y):
    """Three summit flags on poles: United States, China, Russia."""
    flags = []
    # United States: blue canton with star dots over red stripes.
    us = []
    for stripe in range(4):
        us.append(("rect", 0, stripe * 8, 48, 4, RED))
    us.append(("rect", 0, 0, 22, 16, BLUE))
    for r in range(3):
        for c in range(4):
            us.append(("rect", 3 + c * 5, 3 + r * 5, 2, 2, WHITE))
    flags.append(us)
    # China: red field, one gold star suggested by a burst of dots.
    cn = [("rect", 0, 0, 48, 32, RED),
          ("rect", 6, 5, 6, 6, GOLD),
          ("rect", 15, 3, 3, 3, GOLD), ("rect", 17, 9, 3, 3, GOLD),
          ("rect", 17, 15, 3, 3, GOLD), ("rect", 15, 21, 3, 3, GOLD)]
    flags.append(cn)
    # Russia: white, blue and red horizontal thirds.
    ru = [("rect", 0, 0, 48, 11, WHITE), ("rect", 0, 11, 48, 11, BLUE),
          ("rect", 0, 22, 48, 10, RED),
          ("frame", 0, 0, 48, 32, INK)]
    flags.append(ru)
    for index, flag in enumerate(flags):
        fx = x + index * 58
        cv.fill_rect(fx - 3, y, 3, 96, INK)
        for item in flag:
            if item[0] == "rect":
                _, ox, oy, w, h, colour = item
                cv.fill_rect(fx + ox, y + oy, w, h, colour)
            else:
                _, ox, oy, w, h, colour = item
                cv.frame_rect(fx + ox, y + oy, w, h, colour, 1)


ICONS = {
    "scales": icon_scales,
    "chip": icon_chip,
    "burst": icon_burst,
    "bridge": icon_bridge,
}


# ------------------------------------------------------------------ cards
def card(cv, x, y, w, h, tag, tag_colour, headline, body, icon=None,
         headline_scale=4):
    """One story card: shadow, white body, coloured tag band, text."""
    cv.fill_rect(x + 6, y + 6, w, h, SHADOW)
    cv.fill_rect(x, y, w, h, CARD)
    cv.frame_rect(x, y, w, h, INK, 3)
    cv.fill_rect(x + 3, y + 3, w - 6, 41, tag_colour)
    cv.text(x + 18, y + 13, tag, 3, WHITE, bold=True)
    if icon is not None:
        ICONS[icon](cv, x + w - 30, y + 23, WHITE)
    ty = y + 58
    for line in headline:
        cv.text(x + 18, ty, line, headline_scale, INK, bold=True)
        ty += headline_scale * 7 + 6
    cv.fill_rect(x + 18, ty + 2, w - 36, 2, RULE)
    ty += 12
    for line in body:
        cv.text(x + 18, ty, line, 3, INK)
        ty += 25


# ------------------------------------------------------------------- page
def build_page():
    cv = Canvas(WIDTH, HEIGHT, PAPER)

    # Masthead.
    cv.fill_rect(0, 0, WIDTH, 150, NAVY)
    cv.fill_rect(0, 150, WIDTH, 5, GOLD)
    cv.text_centred(16, "THE WORLD'S NEWS · SUMMED UP IN ONE IMAGE", 2, GOLD)
    cv.text_centred(42, "19 NOVEMBER 2026", 10, WHITE, bold=True)
    cv.text_centred(124, "THURSDAY · ONE DAY OF WORLD NEWS", 3, PALE)

    # Lead story: the Shenzhen three-way summit.
    x, y, w, h = 36, 166, 952, 282
    cv.fill_rect(x + 6, y + 6, w, h, SHADOW)
    cv.fill_rect(x, y, w, h, CARD)
    cv.frame_rect(x, y, w, h, INK, 3)
    cv.fill_rect(x + 3, y + 3, w - 6, 41, BLUE)
    cv.text(x + 18, y + 13, "DIPLOMACY · SHENZHEN, CHINA", 3, WHITE, bold=True)
    cv.text(x + 18, y + 60, "TRUMP, XI & PUTIN", 5, INK, bold=True)
    cv.text(x + 18, y + 110, "MEET FACE TO FACE", 5, INK, bold=True)
    icon_flags(cv, 742, y + 56)
    cv.fill_rect(x + 18, y + 158, w - 36, 2, RULE)
    lead_body = [
        "First three-way summit, held at APEC.",
        "Joint peace declaration: talks on",
        "nuclear risks, Ukraine and the Iran",
        "war, and keeping oil flowing.",
    ]
    ty = y + 170
    for line in lead_body:
        cv.text(x + 18, ty, line, 3, INK)
        ty += 27

    # Second row: the ICJ ruling and the Anthropic IPO.
    card(cv, 36, 462, 468, 242, "WORLD COURT · HAGUE", PURPLE,
         ["UN COURT RULES:", "MYANMAR GENOCIDE"],
         ["The ICJ finds Myanmar",
          "committed genocide of",
          "the Rohingya - a first",
          "ruling of its kind."],
         icon="scales")
    card(cv, 520, 462, 468, 242, "TECHNOLOGY · USA", TEAL,
         ["ANTHROPIC SETS", "RECORD $81BN IPO"],
         ["AI firm prices shares",
          "at $83 before its Nasdaq",
          "debut - a $1.5 trillion",
          "value, an IPO record."],
         icon="chip")

    # Third row: the Middle East and the Ukraine war.
    card(cv, 36, 720, 468, 228, "MIDDLE EAST", BURNT,
         ["REGION ON EDGE"],
         ["Trump vows to wipe out",
          "Iran over dirty-bomb",
          "claims; Israeli tanks",
          "push into central Gaza."],
         icon="burst")
    card(cv, 520, 720, 468, 228, "EUROPE · UKRAINE WAR", STEEL,
         ["CRIMEAN BRIDGE HIT"],
         ["Kyiv strikes the bridge",
          "a third time this week;",
          "Russian plane crash",
          "kills all 19 aboard."],
         icon="bridge")

    # Also today: the briefs strip.
    cv.fill_rect(0, 962, WIDTH, 62, INK)
    briefs = [
        ("ALSO TODAY · ", "COP31 CLIMATE TALKS GO TO THE WIRE OVER FOSSIL FUELS"),
        ("", "DENMARK BACKS GREENLAND DEFENCE PACT 109-0 · IMF: WORLD INFLATION AT 4.7%"),
        ("", "589M CHILDREN NOW LIVE IN CONFLICT ZONES · FIJI DECLARES EL NINO DROUGHT DISASTER"),
    ]
    ty = 968
    for label, line in briefs:
        x_end = cv.text(20, ty, label, 2, GOLD, bold=True) if label else 20
        cv.text(x_end + (12 if label else 0), ty, line, 2, WHITE)
        ty += 18
    return cv


# -------------------------------------------------------------- PNG write
def png_bytes(cv):
    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))

    raw = bytearray()
    stride = cv.width * 3
    for yy in range(cv.height):
        raw.append(0)
        raw += cv.pixels[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.width, cv.height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build_page())
    with open(os.path.join(out_dir, "entry.png"), "wb") as handle:
        handle.write(data)


if __name__ == "__main__":
    main()
