#!/usr/bin/env python3
"""Generate بوصلة UT booklet as print-ready A5 image pages (+ PDF)."""

from __future__ import annotations

import math
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont, features

ROOT = Path(__file__).resolve().parent
FONTS = ROOT / "fonts"
OUT_DIR = ROOT / "pages"
PDF_OUT = ROOT / "بوصلة-UT-كتيب.pdf"
UT_LOGO = ROOT / "_assets" / "ut-logo.png"
UT_LOGO_WHITE = ROOT / "_assets" / "ut-logo-white.png"
HAS_RAQM = features.check("raqm")

# Brand
GREEN = (0x3B, 0x52, 0x49)
CREAM = (0xED, 0xE7, 0xD4)
PURPLE = (0x74, 0x73, 0xB3)
GOLD = (0xF8, 0xB6, 0x24)
PASTEL_BLUE = (0xB5, 0xC9, 0xE4)
MAGENTA = (0xFF, 0x5C, 0xB6)
CYAN = (0x51, 0x9C, 0xF2)
PLUM = (0x65, 0x18, 0x53)
LEAF = (0x5B, 0xB3, 0x4E)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
CREAM_LINE = (0xC5, 0xBF, 0xA8)

# A5 @ 300 DPI
DPI = 300
W = int(148 / 25.4 * DPI)  # 1748
H = int(210 / 25.4 * DPI)  # 2480
MARGIN = int(1.6 / 25.4 * DPI)


def ar(text: str) -> str:
    """Shape Arabic for Pillow. With raqm/HarfBuzz, pass text through unchanged
    — reshape+bidi would reverse glyphs a second time."""
    if not text:
        return text
    if HAS_RAQM:
        return text
    return get_display(arabic_reshaper.reshape(text))


def font(weight: str, size: float) -> ImageFont.FreeTypeFont:
    files = {
        "light": "thmanyahsans-Light.otf",
        "regular": "thmanyahsans-Regular.otf",
        "medium": "thmanyahsans-Medium.otf",
        "bold": "thmanyahsans-Bold.otf",
        "black": "thmanyahsans-Black.otf",
    }
    path = FONTS / files[weight]
    return ImageFont.truetype(str(path), int(size))


def mm(v: float) -> int:
    return int(v / 25.4 * DPI)


def new_page(bg=WHITE) -> Image.Image:
    return Image.new("RGB", (W, H), bg)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    fnt,
    fill=BLACK,
    anchor: str = "mm",
    arabic: bool = True,
):
    t = ar(text) if arabic else text
    draw.text(xy, t, font=fnt, fill=fill, anchor=anchor)


def draw_multiline_rtl(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    fnt,
    fill=BLACK,
    line_spacing: float = 1.35,
    align: str = "right",
):
    """Word-wrap Arabic paragraph inside box (x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    max_w = x1 - x0
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        tw, _ = text_size(draw, ar(trial), fnt)
        if tw <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    ascent = fnt.size
    step = int(ascent * line_spacing)
    y = y0
    for line in lines:
        if y + step > y1:
            break
        shaped = ar(line)
        if align == "right":
            draw.text((x1, y), shaped, font=fnt, fill=fill, anchor="ra")
        elif align == "center":
            draw.text(((x0 + x1) // 2, y), shaped, font=fnt, fill=fill, anchor="ma")
        else:
            draw.text((x0, y), shaped, font=fnt, fill=fill, anchor="la")
        y += step
    return y


def rounded_rect(draw, box, radius, outline=GRAY, width=2, fill=None):
    draw.rounded_rectangle(box, radius=radius, outline=outline, width=width, fill=fill)


def sparkle(draw, cx, cy, size, color=GOLD):
    """8-point sparkle."""
    pts = []
    for i in range(8):
        ang = math.radians(i * 45 - 90)
        r = size if i % 2 == 0 else size * 0.38
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=color)
    w = max(2, size // 7)
    draw.rectangle([cx - w, cy - size, cx + w, cy + size], fill=color)
    draw.rectangle([cx - size, cy - w, cx + size, cy + w], fill=color)


def logo_placeholder(draw, box, color=WHITE):
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline=color, width=3)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + (y1 - y0) * 0.05
    r = (x1 - x0) * 0.28
    # arch via arc
    draw.arc([cx - r, cy - r * 0.3, cx + r, cy + r * 1.2], 200, 340, fill=color, width=3)
    for i in range(-4, 5):
        ang = math.radians(-90 + i * 12)
        x2 = cx + math.cos(ang) * r * 1.15
        y2 = cy - 8 + math.sin(ang) * r * 1.15
        draw.line([(cx, cy - 6), (x2, y2)], fill=color, width=2)


# ─── Pages ───────────────────────────────────────────────────────────────────


def page_cover() -> Image.Image:
    img = new_page(WHITE)
    d = ImageDraw.Draw(img)

    # Top meta
    draw_text(d, (MARGIN, MARGIN + mm(2)), "الطبعة الأولى", font("regular", 28), BLACK, "lt")
    draw_text(d, (W - MARGIN, MARGIN + mm(2)), "Aug. 23, 2026", font("light", 26), BLACK, "rt", arabic=False)

    # Title block upper-center
    cy = mm(55)
    draw_text(d, (W // 2, cy), "بوصلة UT", font("black", 110), BLACK, "mm")
    draw_text(d, (W // 2, cy + mm(16)), "مذكرة مستجد", font("medium", 42), BLACK, "mm")

    # Gold accent rule
    rw = mm(28)
    ry = cy + mm(24)
    d.rectangle([W // 2 - rw // 2, ry, W // 2 + rw // 2, ry + mm(1.1)], fill=GOLD)

    # University of Tabuk logo — bottom center
    logo_h = mm(14)
    logo_w = mm(42)
    paste_logo(
        img,
        UT_LOGO,
        (W // 2 - logo_w // 2, H - MARGIN - logo_h, W // 2 + logo_w // 2, H - MARGIN),
    )

    return img


def page_name() -> Image.Image:
    img = new_page(PURPLE)
    d = ImageDraw.Draw(img)

    # Name field near top
    y = mm(40)
    label = ar("اسمك الكريم")
    lf = font("medium", 32)
    lw, _ = text_size(d, label, lf)
    # line then label on the right (RTL): label at right, line extends left
    right = W - MARGIN
    d.text((right, y), label, font=lf, fill=WHITE, anchor="rm")
    line_x1 = right - lw - mm(4)
    line_x0 = MARGIN + mm(10)
    d.line([(line_x0, y + mm(1)), (line_x1, y + mm(1))], fill=WHITE, width=2)

    # Center message
    mid = H // 2 - mm(5)
    draw_text(
        d,
        (W // 2, mid),
        "صممنا هذي النسخة الاستثنائية لك .. حتى",
        font("bold", 36),
        WHITE,
        "mm",
    )
    draw_text(d, (W // 2, mid + mm(12)), "تكون دليلك الأول", font("bold", 36), WHITE, "mm")

    # Signature + date
    by = H - mm(45)
    col_w = (W - 2 * MARGIN) // 2
    # left: توقيعك
    cx1 = MARGIN + col_w // 2
    cx2 = MARGIN + col_w + col_w // 2
    draw_text(d, (cx1, by), "توقيعك", font("light", 28), WHITE, "mm")
    d.line([(cx1 - mm(22), by + mm(10)), (cx1 + mm(22), by + mm(10))], fill=WHITE, width=2)
    draw_text(d, (cx2, by), "التاريخ", font("light", 28), WHITE, "mm")
    d.line([(cx2 - mm(22), by + mm(10)), (cx2 + mm(22), by + mm(10))], fill=WHITE, width=2)

    return img


def page_tips() -> Image.Image:
    img = new_page(WHITE)
    d = ImageDraw.Draw(img)

    # Header with vertical bar on the right
    hx = W - MARGIN
    hy = MARGIN + mm(4)
    d.rectangle([hx - mm(1.2), hy, hx, hy + mm(16)], fill=BLACK)
    draw_text(
        d,
        (hx - mm(4), hy + mm(2)),
        "البدايات لا تُكتب بالحظ... بل بالعادات",
        font("medium", 26),
        BLACK,
        "rt",
    )
    draw_text(
        d,
        (hx - mm(4), hy + mm(9)),
        "الصغيرة التي نختارها كل يوم",
        font("medium", 26),
        BLACK,
        "rt",
    )

    tips = [
        (
            "01",
            "لا تؤجل البداية",
            "قد يبدو الأسبوع الأول خفيفًا لكنه يرسم الفصل كاملاً. وكل مهمة تنجزها اليوم، هي عبء أقل تحمله غدًا.",
        ),
        (
            "02",
            "اسأل بثقة",
            "ليس السؤال دليلًا على الجهل، بل رغبة في الفهم. وكل إجابة تحصل عليها اليوم، تختصر عليك كثيرًا من التردد.",
        ),
        (
            "03",
            "اجعل للمراجعة موعدًا",
            "لا تجعل كتبك لا تعرفك إلا ليلة الاختبار.. دقائق قليلة بعد كل محاضرة قد تغنيك عن ساعات طويلة من القلق.",
        ),
        (
            "04",
            "عش التجربة كاملة",
            "درجاتك جزء من رحلتك لكنها ليست الرحلة كلها. شارك، تعلّم، واصنع لنفسك ذكريات تستحق أن تُروى بعد التخرج.",
        ),
        (
            "05",
            "نظّم وقتك قبل أن ينظّمك الوقت",
            "المهام الجامعية لا تتراكم فجأة بل تتسلل بهدوء. وما تكتبه في جدولك اليوم، لن يطاردك غدًا.",
        ),
    ]

    # Grid: right col = 01,02,03 | left col = 04,05,quote
    gap = mm(6)
    top = hy + mm(24)
    bottom = H - MARGIN - mm(4)
    mid_x = W // 2
    col_r = (mid_x + gap // 2, top, W - MARGIN, bottom)
    col_l = (MARGIN, top, mid_x - gap // 2, bottom)

    cell_h = (bottom - top) // 3

    def tip_cell(box, num, title, body):
        x0, y0, x1, y1 = box
        draw_text(d, (x1, y0), f"{num}  {title}", font("bold", 28), BLACK, "rt")
        draw_multiline_rtl(
            d,
            (x0, y0 + mm(9), x1, y1 - mm(2)),
            body,
            font("regular", 20),
            BLACK,
            line_spacing=1.45,
            align="right",
        )

    # Right column tips 01-03
    for i, tip in enumerate(tips[:3]):
        y0 = top + i * cell_h
        tip_cell((col_r[0], y0, col_r[2], y0 + cell_h - mm(3)), *tip)

    # Left column tips 04-05
    for i, tip in enumerate(tips[3:]):
        y0 = top + i * cell_h
        tip_cell((col_l[0], y0, col_l[2], y0 + cell_h - mm(3)), *tip)

    # Quote box bottom-left
    qx0, qy0 = col_l[0], top + 2 * cell_h
    qx1, qy1 = col_l[2], bottom
    rounded_rect(d, [qx0 + mm(2), qy0 + mm(2), qx1 - mm(2), qy1 - mm(2)], radius=mm(6), outline=GRAY, width=2)
    # big quote mark
    draw_text(
        d,
        (qx0 + mm(8), qy0 + mm(10)),
        "”",
        font("black", 90),
        PURPLE,
        "lt",
        arabic=False,
    )
    draw_multiline_rtl(
        d,
        (qx0 + mm(8), qy0 + mm(28), qx1 - mm(8), qy1 - mm(6)),
        "مساحة لاقتباسك المفضّل أو ملاحظة شخصية…",
        font("medium", 22),
        PURPLE,
        align="right",
    )

    return img


def paste_logo(base: Image.Image, logo_path: Path, box: tuple[int, int, int, int]):
    """Paste logo scaled to fit inside box (x0,y0,x1,y1), centered, keep aspect."""
    if not logo_path.exists():
        d = ImageDraw.Draw(base)
        logo_placeholder(d, list(box), WHITE)
        return
    logo = Image.open(logo_path).convert("RGBA")
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    lw, lh = logo.size
    scale = min(bw / lw, bh / lh)
    nw, nh = max(1, int(lw * scale)), max(1, int(lh * scale))
    logo = logo.resize((nw, nh), Image.Resampling.LANCZOS)
    px = x0 + (bw - nw) // 2
    py = y0 + (bh - nh) // 2
    base.paste(logo, (px, py), logo)


def draw_footer_band(img: Image.Image):
    d = ImageDraw.Draw(img)
    band_h = mm(22)
    y0 = H - band_h
    d.rectangle([0, y0, W, H], fill=PURPLE)

    cy = y0 + band_h // 2
    pad = mm(2.5)

    # Left sparkles
    sparkle(d, mm(8), cy - mm(2), mm(2.8))
    sparkle(d, mm(15), cy + mm(3), mm(1.8))

    # Deanship text
    draw_text(d, (mm(22), cy - mm(3)), "عمادة شؤون الطلاب", font("bold", 16), WHITE, "lm")
    draw_text(
        d,
        (mm(22), cy + mm(4)),
        "Deanship of Students' Affairs",
        font("light", 11),
        WHITE,
        "lm",
        arabic=False,
    )

    # University of Tabuk logo (official white lockup)
    logo_h = band_h - mm(6)
    logo_w = int(logo_h * (800 / 261))  # approx aspect of ut-logo-white
    logo_w = min(logo_w, mm(48))
    lx0 = W // 2 - logo_w // 2
    paste_logo(img, UT_LOGO_WHITE, (lx0, y0 + pad, lx0 + logo_w, H - pad))

    # Divider
    div_x = lx0 + logo_w + mm(3)
    d.line([(div_x, cy - mm(6)), (div_x, cy + mm(6))], fill=WHITE, width=1)

    # Booklet title
    draw_text(d, (div_x + mm(4), cy - mm(3)), "كتيب أرشدني", font("bold", 20), WHITE, "lm")
    draw_text(d, (div_x + mm(4), cy + mm(5)), "نسخة 48", font("light", 15), WHITE, "lm")

    # Right sparkles
    sparkle(d, W - mm(8), cy - mm(2), mm(2.0))
    sparkle(d, W - mm(15), cy + mm(2), mm(2.8))
    sparkle(d, W - mm(22), cy - mm(3), mm(1.6))


def page_content() -> Image.Image:
    img = new_page(CREAM)
    d = ImageDraw.Draw(img)

    draw_text(d, (W - MARGIN, MARGIN + mm(8)), "محتوى القسم", font("black", 52), GREEN, "rt")
    # gold rule under title (right aligned short)
    d.rectangle([W - MARGIN - mm(26), MARGIN + mm(20), W - MARGIN, MARGIN + mm(21.2)], fill=GOLD)

    draw_multiline_rtl(
        d,
        (MARGIN, MARGIN + mm(28), W - MARGIN, MARGIN + mm(55)),
        "هذه صفحة محتوى داخلية جاهزة للتعديل. ضع هنا فقرات القسم، جداول التعريف، أو أي محتوى تحتاجه. الخلفية الكريمية والفوتر البنفسجي يعكسان هوية كتيب أرشدني.",
        font("regular", 26),
        GREEN,
        line_spacing=1.5,
        align="right",
    )

    # Color chips
    draw_text(d, (W - MARGIN, MARGIN + mm(62)), "توزيع الألوان", font("medium", 24), GREEN, "rt")

    primaries = [
        (GREEN, "أخضر", WHITE),
        (CREAM, "كريمي", GREEN),
        (PURPLE, "بنفسجي", WHITE),
        (GOLD, "ذهبي", GREEN),
    ]
    secondaries = [
        (PASTEL_BLUE, "سماوي", GREEN),
        (MAGENTA, "وردي", WHITE),
        (CYAN, "أزرق", WHITE),
        (PLUM, "برقوقي", WHITE),
        (LEAF, "أخضر فاتح", WHITE),
    ]

    chip_h = mm(16)
    gap = mm(3)
    y = MARGIN + mm(70)
    # primary row — RTL so first chip on the right
    chip_w = (W - 2 * MARGIN - 3 * gap) // 4
    for i, (col, label, tc) in enumerate(primaries):
        x1 = W - MARGIN - i * (chip_w + gap)
        x0 = x1 - chip_w
        d.rounded_rectangle([x0, y, x1, y + chip_h], radius=mm(2), fill=col)
        draw_text(d, ((x0 + x1) // 2, y + chip_h // 2), label, font("bold", 20), tc, "mm")
        # hex small
        hex_c = "#{:02X}{:02X}{:02X}".format(*col)
        draw_text(
            d,
            ((x0 + x1) // 2, y + chip_h + mm(4)),
            hex_c,
            font("light", 14),
            GREEN,
            "mm",
            arabic=False,
        )

    y2 = y + chip_h + mm(12)
    chip_w2 = (W - 2 * MARGIN - 4 * gap) // 5
    for i, (col, label, tc) in enumerate(secondaries):
        x1 = W - MARGIN - i * (chip_w2 + gap)
        x0 = x1 - chip_w2
        d.rounded_rectangle([x0, y2, x1, y2 + chip_h], radius=mm(2), fill=col)
        draw_text(d, ((x0 + x1) // 2, y2 + chip_h // 2), label, font("bold", 16), tc, "mm")

    draw_footer_band(img)
    return img


def page_notes() -> Image.Image:
    img = new_page(CREAM)
    d = ImageDraw.Draw(img)

    draw_text(d, (W - MARGIN, MARGIN + mm(8)), "ملاحظاتي", font("black", 48), GREEN, "rt")
    d.rectangle([W - MARGIN - mm(22), MARGIN + mm(18), W - MARGIN, MARGIN + mm(19.2)], fill=GOLD)

    # Lined area
    top = MARGIN + mm(28)
    bottom = H - mm(28)
    line_gap = mm(10)
    y = top
    while y < bottom:
        d.line([(MARGIN, y), (W - MARGIN, y)], fill=CREAM_LINE, width=2)
        y += line_gap

    draw_footer_band(img)
    return img


def page_palette_ref() -> Image.Image:
    """Bonus creative divider / palette splash page."""
    img = new_page(WHITE)
    d = ImageDraw.Draw(img)

    # Split layout: purple left band, cream right — but RTL so purple on right
    split = int(W * 0.42)
    d.rectangle([W - split, 0, W, H], fill=PURPLE)
    d.rectangle([0, 0, W - split, H], fill=CREAM)

    draw_text(d, (W - split // 2, mm(40)), "بوصلة", font("black", 72), WHITE, "mm")
    draw_text(d, (W - split // 2, mm(55)), "UT", font("black", 64), GOLD, "mm", arabic=False)

    draw_text(d, ((W - split) // 2, mm(50)), "هويّة بصرية", font("bold", 40), GREEN, "mm")
    draw_text(
        d,
        ((W - split) // 2, mm(65)),
        "قالب بصري جاهز للطباعة",
        font("regular", 24),
        GREEN,
        "mm",
    )

    # accent dots
    colors = [GOLD, PURPLE, GREEN, MAGENTA, CYAN]
    for i, c in enumerate(colors):
        cx = (W - split) // 2 - mm(20) + i * mm(10)
        d.ellipse([cx - mm(3), mm(80), cx + mm(3), mm(86)], fill=c)

    sparkle(d, W - split // 2, H - mm(40), mm(6), GOLD)
    sparkle(d, W - split // 2 - mm(14), H - mm(32), mm(3.5), GOLD)

    return img


def export_pdf(pages: list[Image.Image], path: Path):
    rgb_pages = [p.convert("RGB") for p in pages]
    rgb_pages[0].save(
        path,
        "PDF",
        resolution=DPI,
        save_all=True,
        append_images=rgb_pages[1:],
    )


def main():
    OUT_DIR.mkdir(exist_ok=True)

    pages = [
        ("01-غلاف", page_cover()),
        ("02-الاسم", page_name()),
        ("03-نصائح", page_tips()),
        ("04-هوية", page_palette_ref()),
        ("05-محتوى", page_content()),
        ("06-ملاحظات", page_notes()),
    ]

    for name, img in pages:
        out = OUT_DIR / f"{name}.png"
        img.save(out, "PNG", dpi=(DPI, DPI))
        print(f"Wrote {out}")

    export_pdf([p for _, p in pages], PDF_OUT)
    print(f"Wrote {PDF_OUT}")


if __name__ == "__main__":
    main()
