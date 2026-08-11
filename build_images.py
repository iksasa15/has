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
ASSETS = ROOT / "_assets"
UT_LOGO = ASSETS / "ut-logo.png"
UT_LOGO_WHITE = ASSETS / "ut-logo-white.png"
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
CORAL = (0xE2, 0x96, 0x8F)
SAGE = (0xAB, 0xC7, 0x97)
BROWN = (0x5C, 0x3D, 0x2E)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK = (0x2A, 0x2A, 0x2A)

DPI = 300
W = int(148 / 25.4 * DPI)  # 1748
H = int(210 / 25.4 * DPI)  # 2480
MARGIN = int(1.5 / 25.4 * DPI)


def ar(text: str) -> str:
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
    return ImageFont.truetype(str(FONTS / files[weight]), int(size))


def mm(v: float) -> int:
    return int(v / 25.4 * DPI)


def new_page(bg=WHITE) -> Image.Image:
    return Image.new("RGB", (W, H), bg)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_text(draw, xy, text, fnt, fill=BLACK, anchor="mm", arabic=True):
    t = ar(text) if arabic else text
    draw.text(xy, t, font=fnt, fill=fill, anchor=anchor)


def draw_multiline_rtl(
    draw,
    box,
    text,
    fnt,
    fill=BLACK,
    line_spacing=1.4,
    align="right",
):
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

    step = int(fnt.size * line_spacing)
    y = y0
    for line in lines:
        if y + step > y1 + step:
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


def paste_fit(base: Image.Image, path: Path, box, bg_round=False):
    if not path.exists():
        return
    logo = Image.open(path).convert("RGBA")
    x0, y0, x1, y1 = box
    bw, bh = max(1, x1 - x0), max(1, y1 - y0)
    lw, lh = logo.size
    scale = min(bw / lw, bh / lh)
    nw, nh = max(1, int(lw * scale)), max(1, int(lh * scale))
    logo = logo.resize((nw, nh), Image.Resampling.LANCZOS)
    px = x0 + (bw - nw) // 2
    py = y0 + (bh - nh) // 2
    base.paste(logo, (px, py), logo)


def sparkle(draw, cx, cy, size, color=GOLD):
    pts = []
    for i in range(8):
        ang = math.radians(i * 45 - 90)
        r = size if i % 2 == 0 else size * 0.38
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=color)
    w = max(2, size // 7)
    draw.rectangle([cx - w, cy - size, cx + w, cy + size], fill=color)
    draw.rectangle([cx - size, cy - w, cx + size, cy + w], fill=color)


def draw_footer_band(img: Image.Image):
    d = ImageDraw.Draw(img)
    band_h = mm(20)
    y0 = H - band_h
    d.rectangle([0, y0, W, H], fill=PURPLE)
    cy = y0 + band_h // 2
    pad = mm(2)

    sparkle(d, mm(7), cy - mm(1), mm(2.4))
    sparkle(d, mm(13), cy + mm(2.5), mm(1.6))

    draw_text(d, (mm(20), cy - mm(2.5)), "عمادة شؤون الطلاب", font("bold", 15), WHITE, "lm")
    draw_text(
        d,
        (mm(20), cy + mm(3.5)),
        "Deanship of Students' Affairs",
        font("light", 10),
        WHITE,
        "lm",
        arabic=False,
    )

    logo_h = band_h - mm(5)
    logo_w = min(int(logo_h * 3.0), mm(44))
    lx0 = W // 2 - logo_w // 2
    paste_fit(img, UT_LOGO_WHITE, (lx0, y0 + pad, lx0 + logo_w, H - pad))

    div_x = lx0 + logo_w + mm(2.5)
    d.line([(div_x, cy - mm(5)), (div_x, cy + mm(5))], fill=WHITE, width=1)
    draw_text(d, (div_x + mm(3), cy - mm(2.5)), "كتيب أرشدني", font("bold", 18), WHITE, "lm")
    draw_text(d, (div_x + mm(3), cy + mm(4)), "نسخة 48", font("light", 14), WHITE, "lm")

    sparkle(d, W - mm(7), cy - mm(1.5), mm(1.8))
    sparkle(d, W - mm(13), cy + mm(2), mm(2.4))
    sparkle(d, W - mm(19), cy - mm(2.5), mm(1.4))


# ─── Pages ───────────────────────────────────────────────────────────────────


def page_cover() -> Image.Image:
    img = new_page(WHITE)
    d = ImageDraw.Draw(img)

    # RTL meta: Arabic edition on the right, date on the left
    draw_text(d, (W - MARGIN, MARGIN + mm(3)), "الطبعة الأولى", font("regular", 28), BLACK, "rt")
    draw_text(
        d, (MARGIN, MARGIN + mm(3)), "Aug. 23, 2026", font("light", 26), BLACK, "lt", arabic=False
    )

    cy = mm(52)
    draw_text(d, (W // 2, cy), "بوصلة UT", font("black", 108), BLACK, "mm")
    draw_text(d, (W // 2, cy + mm(16)), "مذكرة مستجد", font("medium", 40), BLACK, "mm")

    rw = mm(28)
    ry = cy + mm(24)
    d.rectangle([W // 2 - rw // 2, ry, W // 2 + rw // 2, ry + mm(1.1)], fill=GOLD)

    logo_h = mm(14)
    logo_w = mm(42)
    paste_fit(
        img,
        UT_LOGO,
        (W // 2 - logo_w // 2, H - MARGIN - logo_h, W // 2 + logo_w // 2, H - MARGIN),
    )
    return img


def page_apps() -> Image.Image:
    img = new_page(WHITE)
    d = ImageDraw.Draw(img)

    header_h = mm(28)
    d.rectangle([0, 0, W, header_h], fill=CREAM)
    draw_text(
        d,
        (W // 2, header_h // 2),
        "تطبيقات ستسهل عليك رحلتك الجامعية..",
        font("bold", 34),
        BLACK,
        "mm",
    )

    # 2x2 grid
    gap = mm(0)
    top = header_h
    mid_y = top + (H - top) // 2
    mid_x = W // 2

    # backgrounds
    d.rectangle([0, top, mid_x, mid_y], fill=CORAL)
    d.rectangle([mid_x, top, W, mid_y], fill=CORAL)
    d.rectangle([0, mid_y, mid_x, H], fill=SAGE)
    d.rectangle([mid_x, mid_y, W, H], fill=SAGE)

    apps = [
        # (box, icon, title_en, title_ar, body) — visual: left-top Blackboard, right-top Khata
        (
            (0, top, mid_x, mid_y),
            ASSETS / "app-blackboard.png",
            "Blackboard",
            "بلاك بورد",
            "المنصة الأكاديمية الرسمية للجامعة؛ تمكنك من متابعة المحاضرات، تسليم الواجبات، واطلاعك على الإعلانات والدرجات أولاً بأول.",
        ),
        (
            (mid_x, top, W, mid_y),
            ASSETS / "app-khata.png",
            "Khata",
            "خطة",
            "حاسبتك ومنظمك الأكاديمي؛ يساعدك على حساب ومتابعة معدلك التراكمي (GPA)، تنظيم الجدول الدراسي، وتتبع الدرجات بسهولة.",
        ),
        (
            (0, mid_y, mid_x, H),
            ASSETS / "app-notion.png",
            "Notion",
            "نوشن",
            "المساحة الشاملة لتنظيم حياتك الدراسية؛ تُستخدم لتدوين الملاحظات، ترتيب المهام، وإدارة المشاريع بأسلوب عصري.",
        ),
        (
            (mid_x, mid_y, W, H),
            ASSETS / "app-forest.png",
            "Forest",
            "فوريست",
            "تطبيق مبتكر للتركيز والتخلص من تشتت الهاتف؛ ينمي لك شجرة افتراضية كلما ابتعدت عن جوالك وركزت في مذاكرتك.",
        ),
    ]

    pad = mm(5)
    icon_s = mm(14)
    for box, icon, en, ar_name, body in apps:
        x0, y0, x1, y1 = box
        # icon on the right
        ix1 = x1 - pad
        iy0 = y0 + pad
        paste_fit(img, icon, (ix1 - icon_s, iy0, ix1, iy0 + icon_s))

        title = f"{en} ({ar_name}):"
        title_x = ix1 - icon_s - mm(2)
        draw_text(d, (title_x, iy0 + icon_s // 2), title, font("bold", 22), BROWN, "rm")

        body_top = iy0 + icon_s + mm(3)
        draw_multiline_rtl(
            d,
            (x0 + pad, body_top, x1 - pad, y1 - pad),
            body,
            font("regular", 18),
            DARK,
            line_spacing=1.35,
            align="right",
        )

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
            "لا تجعل كتبك لا تعرفك إلا ليلة الاختبار. دقائق قليلة بعد كل محاضرة قد تغنيك عن ساعات طويلة من القلق.",
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

    gap = mm(6)
    top = hy + mm(24)
    bottom = H - MARGIN
    mid_x = W // 2
    cell_h = (bottom - top) // 3

    def tip_cell(box, num, title, body):
        x0, y0, x1, y1 = box
        draw_text(d, (x1, y0), f"{num}  {title}", font("bold", 27), BLACK, "rt")
        draw_multiline_rtl(
            d,
            (x0, y0 + mm(9), x1, y1 - mm(2)),
            body,
            font("regular", 19),
            DARK,
            line_spacing=1.4,
            align="right",
        )

    # Right column 01-03, left 04-05 + quote
    for i, tip in enumerate(tips[:3]):
        y0 = top + i * cell_h
        tip_cell((mid_x + gap // 2, y0, W - MARGIN, y0 + cell_h - mm(3)), *tip)
    for i, tip in enumerate(tips[3:]):
        y0 = top + i * cell_h
        tip_cell((MARGIN, y0, mid_x - gap // 2, y0 + cell_h - mm(3)), *tip)

    # Quote box bottom-left
    qx0, qy0 = MARGIN, top + 2 * cell_h
    qx1, qy1 = mid_x - gap // 2, bottom
    d.rounded_rectangle(
        [qx0 + mm(1), qy0 + mm(2), qx1 - mm(1), qy1 - mm(2)],
        radius=mm(5),
        outline=GRAY,
        width=2,
    )
    draw_text(
        d,
        (qx0 + mm(7), qy0 + mm(10)),
        "”",
        font("black", 88),
        PURPLE,
        "lt",
        arabic=False,
    )
    return img


def page_map() -> Image.Image:
    """أين وجهتك؟ — purple frame with blue strip + QR."""
    img = new_page(PASTEL_BLUE)
    d = ImageDraw.Draw(img)

    # Purple panel with concave corners (notches)
    panel = [MARGIN, MARGIN, W - mm(18), H - MARGIN]
    px0, py0, px1, py1 = panel
    d.rounded_rectangle(panel, radius=mm(4), fill=PURPLE)

    # Concave notches at corners via blue circles
    notch_r = mm(7)
    for cx, cy in (
        (px0, py0),
        (px1, py0),
        (px0, py1),
        (px1, py1),
    ):
        d.ellipse([cx - notch_r, cy - notch_r, cx + notch_r, cy + notch_r], fill=PASTEL_BLUE)

    # Text inside panel (right aligned)
    tx1 = px1 - mm(10)
    tx0 = px0 + mm(10)
    ty = py0 + mm(18)
    draw_text(d, (tx1, ty), "أين وجهتك؟", font("black", 52), WHITE, "rt")

    body = (
        "سواء كنت متجهًا إلى عمادة شؤون الطلاب، أو تبحث عن المكتبة المركزية أو كليتك، "
        "ستساعدك الخريطة التفاعلية على الوصول بسهولة."
    )
    draw_multiline_rtl(
        d,
        (tx0, ty + mm(16), tx1, ty + mm(55)),
        body,
        font("regular", 26),
        WHITE,
        line_spacing=1.45,
        align="right",
    )

    draw_text(
        d,
        (tx1, ty + mm(62)),
        "امسح الرمز وابدأ رحلتك داخل المدينة الجامعية !",
        font("bold", 24),
        CORAL,
        "rt",
    )

    # QR bottom-right of panel, overlapping blue strip
    qr_s = mm(38)
    qx1 = W - mm(8)
    qy1 = H - mm(14)
    qx0 = qx1 - qr_s
    qy0 = qy1 - qr_s
    # white pad
    d.rounded_rectangle([qx0 - mm(2), qy0 - mm(2), qx1 + mm(2), qy1 + mm(2)], radius=mm(2), fill=WHITE)
    paste_fit(img, ASSETS / "qr-map.png", (qx0, qy0, qx1, qy1))
    return img


def page_essay() -> Image.Image:
    img = new_page(WHITE)
    d = ImageDraw.Draw(img)

    paragraphs = [
        "قالوا إن الجامعة مرحلة صعبة، مليئة بالعقبات، ولم يقولوا إنها رحلة يتعاقب فيها العسر واليسر، وتُصنع فيها الحكايات بينهما.",
        "وقالوا: لا تصدّق أحدًا، فالكل سيستغلك؛ ولم يقولوا إنك ستجد فيها أناسًا يحبون العطاء، ويبذلون من وقتهم وجهدهم ما يجعل أيامك أيسر وأجمل.",
        "وقالوا إن الجامعة ليست إلا آيبادًا وقهوةً وروتينًا مملًا، ولم يذكروا أنها مساحة واسعة لاكتشاف ذاتك، وصقل مهاراتك، وبناء شخصيتك بعيدًا عن مقاعد الدراسة.",
        "قالوا الكثير، فلا تجعل ما قيل لك يرسم تجربتك قبل أن تعيشها. لا تكن معلّقًا في مهبّ الأقوال، بل خض تجربتك بنفسك، واصنع قصتك بطريقتك، وكن أنت من يمسك بدفّة سفينته، ويوجهها نحو المرفأ الذي ينشده.",
        "فالجامعة لا تُروى كما قيلت لك... بل كما عشتها أنت",
    ]

    y = MARGIN + mm(10)
    body_f = font("regular", 24)
    last_f = font("bold", 26)
    for i, para in enumerate(paragraphs):
        fnt = last_f if i == len(paragraphs) - 1 else body_f
        y = draw_multiline_rtl(
            d,
            (MARGIN, y, W - MARGIN, H - mm(28)),
            para,
            fnt,
            DARK if i < len(paragraphs) - 1 else GREEN,
            line_spacing=1.55,
            align="right",
        )
        y += mm(5)

    # small logo bottom
    logo_h = mm(10)
    logo_w = mm(32)
    paste_fit(
        img,
        UT_LOGO,
        (W // 2 - logo_w // 2, H - MARGIN - logo_h, W // 2 + logo_w // 2, H - MARGIN // 2),
    )
    return img


def page_palette() -> Image.Image:
    img = new_page(WHITE)
    d = ImageDraw.Draw(img)

    draw_text(d, (W - MARGIN, MARGIN + mm(6)), "توزيع الألوان", font("black", 42), GREEN, "rt")
    d.rectangle([W - MARGIN - mm(24), MARGIN + mm(16), W - MARGIN, MARGIN + mm(17.2)], fill=GOLD)

    draw_text(d, (W - MARGIN, MARGIN + mm(28)), "أساسي", font("bold", 28), BLACK, "rt")

    primaries = [
        (GREEN, "#3B5249"),
        (CREAM, "#EDE7D4"),
        (PURPLE, "#7473B3"),
        (GOLD, "#F8B624"),
    ]
    gap = mm(3)
    chip_h = mm(28)
    y = MARGIN + mm(36)
    chip_w = (W - 2 * MARGIN - 3 * gap) // 4
    for i, (col, hexcode) in enumerate(primaries):
        x1 = W - MARGIN - i * (chip_w + gap)
        x0 = x1 - chip_w
        d.rounded_rectangle([x0, y, x1, y + chip_h], radius=mm(2), fill=col)
        tc = GREEN if col in (CREAM, GOLD) else WHITE
        draw_text(d, ((x0 + x1) // 2, y + chip_h // 2), hexcode, font("bold", 18), tc, "mm", arabic=False)

    # divider
    dy = y + chip_h + mm(14)
    d.line([(MARGIN, dy), (W - MARGIN, dy)], fill=BLACK, width=2)
    draw_text(d, (W - MARGIN, dy + mm(8)), "فرعي", font("bold", 28), BLACK, "rt")

    secondaries = [
        (PASTEL_BLUE, "#B5C9E4"),
        (MAGENTA, "#FF5CB6"),
        (CYAN, "#519CF2"),
        (PLUM, "#651853"),
        (LEAF, "#5BB34E"),
    ]
    y2 = dy + mm(18)
    chip_w2 = (W - 2 * MARGIN - 4 * gap) // 5
    chip_h2 = mm(22)
    for i, (col, hexcode) in enumerate(secondaries):
        x1 = W - MARGIN - i * (chip_w2 + gap)
        x0 = x1 - chip_w2
        d.rounded_rectangle([x0, y2, x1, y2 + chip_h2], radius=mm(2), fill=col)
        tc = GREEN if col == PASTEL_BLUE else WHITE
        draw_text(
            d, ((x0 + x1) // 2, y2 + chip_h2 // 2), hexcode, font("bold", 14), tc, "mm", arabic=False
        )

    draw_footer_band(img)
    return img


def export_pdf(pages: list[Image.Image], path: Path):
    rgb = [p.convert("RGB") for p in pages]
    rgb[0].save(path, "PDF", resolution=DPI, save_all=True, append_images=rgb[1:])


def main():
    OUT_DIR.mkdir(exist_ok=True)
    # remove old pages that no longer apply
    for old in OUT_DIR.glob("*.png"):
        old.unlink()

    pages = [
        ("01-غلاف", page_cover()),
        ("02-تطبيقات", page_apps()),
        ("03-نصائح", page_tips()),
        ("04-أين-وجهتك", page_map()),
        ("05-قالوا", page_essay()),
        ("06-ألوان", page_palette()),
    ]
    for name, img in pages:
        out = OUT_DIR / f"{name}.png"
        img.save(out, "PNG", dpi=(DPI, DPI))
        print(f"Wrote {out}")

    export_pdf([p for _, p in pages], PDF_OUT)
    print(f"Wrote {PDF_OUT}")


if __name__ == "__main__":
    main()
