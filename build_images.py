#!/usr/bin/env python3
"""بوصلة UT — professional A5 PNG page designs (no PDF focus)."""

from __future__ import annotations

import math
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFilter, ImageFont, features

ROOT = Path(__file__).resolve().parent
FONTS = ROOT / "fonts"
OUT = ROOT / "pages"
ASSETS = ROOT / "_assets"
UT_LOGO = ASSETS / "ut-logo.png"
UT_LOGO_WHITE = ASSETS / "ut-logo-white.png"
HAS_RAQM = features.check("raqm")

GREEN = (0x3B, 0x52, 0x49)
CREAM = (0xED, 0xE7, 0xD4)
PURPLE = (0x74, 0x73, 0xB3)
GOLD = (0xF8, 0xB6, 0x24)
PASTEL = (0xB5, 0xC9, 0xE4)
MAGENTA = (0xFF, 0x5C, 0xB6)
CYAN = (0x51, 0x9C, 0xF2)
PLUM = (0x65, 0x18, 0x53)
LEAF = (0x5B, 0xB3, 0x4E)
CORAL = (0xE8, 0xA9, 0xA3)
CORAL_DEEP = (0xD4, 0x7F, 0x76)
SAGE = (0xB5, 0xCF, 0xA5)
SAGE_DEEP = (0x8F, 0xB0, 0x7C)
INK = (0x1F, 0x1F, 0x22)
MUTED = (0x4A, 0x45, 0x42)
WHITE = (255, 255, 255)
SOFT = (0xF7, 0xF5, 0xF0)

DPI = 300
W = int(148 / 25.4 * DPI)
H = int(210 / 25.4 * DPI)
M = int(1.4 / 25.4 * DPI)


def ar(t: str) -> str:
    if not t:
        return t
    return t if HAS_RAQM else get_display(arabic_reshaper.reshape(t))


def fnt(weight: str, size: float) -> ImageFont.FreeTypeFont:
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


def page(bg=WHITE) -> Image.Image:
    return Image.new("RGB", (W, H), bg)


def tsize(d, text, font):
    b = d.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]


def txt(d, xy, text, font, fill=INK, anchor="mm", rtl=True):
    d.text(xy, ar(text) if rtl else text, font=font, fill=fill, anchor=anchor)


def wrap(d, box, text, font, fill=INK, spacing=1.45, align="right"):
    x0, y0, x1, y1 = box
    max_w = x1 - x0
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        tw, _ = tsize(d, ar(trial), font)
        if tw <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    step = int(font.size * spacing)
    y = y0
    for line in lines:
        if y > y1:
            break
        s = ar(line)
        if align == "right":
            d.text((x1, y), s, font=font, fill=fill, anchor="ra")
        elif align == "center":
            d.text(((x0 + x1) // 2, y), s, font=font, fill=fill, anchor="ma")
        else:
            d.text((x0, y), s, font=font, fill=fill, anchor="la")
        y += step
    return y


def shadow_rect(base, box, radius, fill, shadow=18, blur=12, offset=(0, 6)):
    """Soft drop-shadow rounded card."""
    x0, y0, x1, y1 = box
    pad = shadow + abs(offset[0]) + abs(offset[1]) + blur
    layer = Image.new("RGBA", (W + pad * 2, H + pad * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ox, oy = offset
    # shadow
    ld.rounded_rectangle(
        [x0 + pad + ox, y0 + pad + oy, x1 + pad + ox, y1 + pad + oy],
        radius=radius,
        fill=(0, 0, 0, 45),
    )
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    # card
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle(
        [x0 + pad, y0 + pad, x1 + pad, y1 + pad],
        radius=radius,
        fill=fill + ((255,) if len(fill) == 3 else ()),
    )
    base.paste(layer, (-pad, -pad), layer)


def paste(base, path, box):
    if not Path(path).exists():
        return
    im = Image.open(path).convert("RGBA")
    x0, y0, x1, y1 = [int(v) for v in box]
    bw, bh = max(1, x1 - x0), max(1, y1 - y0)
    scale = min(bw / im.width, bh / im.height)
    nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    base.paste(im, (x0 + (bw - nw) // 2, y0 + (bh - nh) // 2), im)


def make_icons():
    """High-res flat app icons."""
    s = 512
    ASSETS.mkdir(exist_ok=True)

    # Blackboard
    bb = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    for y in range(s):
        for x in range(s):
            t = (x * 0.6 + y * 0.4) / s
            r = int(20 + (40 - 20) * t)
            g = int(90 + (190 - 90) * t)
            b = int(210 + (70 - 210) * t)
            bb.putpixel((x, y), (r, g, b, 255))
    d = ImageDraw.Draw(bb)
    # rounded mask
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], radius=90, fill=255)
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    out.paste(bb, mask=mask)
    d = ImageDraw.Draw(out)
    d.polygon(
        [
            (s * 0.50, s * 0.26),
            (s * 0.74, s * 0.62),
            (s * 0.62, s * 0.62),
            (s * 0.50, s * 0.42),
            (s * 0.38, s * 0.62),
            (s * 0.26, s * 0.62),
        ],
        fill=(255, 255, 255, 255),
    )
    out.save(ASSETS / "app-blackboard.png")

    # Khata
    kh = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(kh)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=90, fill=(40, 42, 48, 255))
    for i, col in enumerate([(255, 255, 255), (110, 210, 120), (255, 255, 255)]):
        x0 = s * 0.26 + i * s * 0.17
        d.rounded_rectangle([x0, s * 0.22, x0 + s * 0.13, s * 0.78], radius=18, fill=col)
    kh.save(ASSETS / "app-khata.png")

    # Notion
    no = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(no)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=90, fill=(255, 255, 255, 255))
    d.rounded_rectangle([18, 18, s - 19, s - 19], radius=72, outline=(25, 25, 25), width=22)
    try:
        nf = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 280)
    except Exception:
        nf = ImageFont.load_default()
    d.text((s * 0.5, s * 0.48), "N", font=nf, fill=(25, 25, 25), anchor="mm")
    no.save(ASSETS / "app-notion.png")

    # Forest
    fo = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(fo)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=90, fill=(255, 255, 255, 255))
    d.rounded_rectangle([24, 24, s - 25, s - 25], radius=70, fill=(246, 250, 240), outline=(200, 210, 190), width=8)
    d.ellipse([s * 0.28, s * 0.60, s * 0.72, s * 0.84], fill=(130, 85, 45))
    d.line([(s * 0.5, s * 0.66), (s * 0.5, s * 0.36)], fill=(55, 140, 65), width=16)
    d.ellipse([s * 0.30, s * 0.26, s * 0.50, s * 0.48], fill=(85, 185, 75))
    d.ellipse([s * 0.50, s * 0.26, s * 0.70, s * 0.48], fill=(70, 170, 60))
    fo.save(ASSETS / "app-forest.png")

    # QR clean from reference if present, else keep existing
    src = ROOT / "project  2-2" / "5.png"
    if src.exists():
        import numpy as np

        im = Image.open(src).convert("RGB")
        a = np.array(im)
        r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
        black = (r < 55) & (g < 55) & (b < 55)
        ys, xs = np.where(black)
        if len(xs) > 100:
            qx0, qy0, qx1, qy1 = int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())
            side = max(qx1 - qx0, qy1 - qy0)
            cx, cy = (qx0 + qx1) // 2, (qy0 + qy1) // 2
            pad = 10
            box = (cx - side // 2 - pad, cy - side // 2 - pad, cx + side // 2 + pad, cy + side // 2 + pad)
            qr = np.array(im.crop(box))
            mask = (qr[:, :, 0] < 80) & (qr[:, :, 1] < 80) & (qr[:, :, 2] < 80)
            out = np.full_like(qr, 255)
            out[mask] = 0
            Image.fromarray(out).resize((512, 512), Image.Resampling.NEAREST).save(ASSETS / "qr-map.png")


# ─── Pages ───────────────────────────────────────────────────────────────────


def page_cover():
    img = page(SOFT)
    d = ImageDraw.Draw(img)

    # subtle top wash
    for i in range(mm(40)):
        a = int(255 * (1 - i / mm(40)))
        # cream gradient via lines
        c = tuple(int(SOFT[j] + (CREAM[j] - SOFT[j]) * (1 - i / mm(40)) * 0.5) for j in range(3))
        d.line([(0, i), (W, i)], fill=c)

    txt(d, (W - M, M + mm(4)), "الطبعة الأولى", fnt("regular", 26), MUTED, "rt")
    txt(d, (M, M + mm(4)), "Aug. 23, 2026", fnt("light", 24), MUTED, "lt", rtl=False)

    cy = mm(58)
    txt(d, (W // 2, cy), "بوصلة UT", fnt("black", 118), INK, "mm")
    txt(d, (W // 2, cy + mm(18)), "مذكرة مستجد", fnt("medium", 42), MUTED, "mm")

    # gold accent with soft ends
    rw = mm(32)
    ry = cy + mm(28)
    d.rounded_rectangle([W // 2 - rw // 2, ry, W // 2 + rw // 2, ry + mm(1.4)], radius=4, fill=GOLD)

    # decorative small sparkles
    for cx, cy2, sz in ((W // 2 - mm(40), ry + mm(20), mm(2.5)), (W // 2 + mm(40), ry + mm(20), mm(2))):
        pts = []
        for i in range(8):
            ang = math.radians(i * 45 - 90)
            r = sz if i % 2 == 0 else sz * 0.35
            pts.append((cx + r * math.cos(ang), cy2 + r * math.sin(ang)))
        d.polygon(pts, fill=GOLD)

    paste(img, UT_LOGO, (W // 2 - mm(22), H - M - mm(16), W // 2 + mm(22), H - M))
    return img


def page_apps():
    img = page(SOFT)
    d = ImageDraw.Draw(img)

    # Header bar
    header_h = mm(32)
    d.rectangle([0, 0, W, header_h], fill=WHITE)
    # highlight pill behind title
    title = "تطبيقات ستسهل عليك رحلتك الجامعية.."
    tf = fnt("bold", 30)
    tw, th = tsize(d, ar(title), tf)
    hx0 = (W - tw) // 2 - mm(4)
    hy0 = (header_h - th) // 2 - mm(2)
    d.rounded_rectangle([hx0, hy0, hx0 + tw + mm(8), hy0 + th + mm(4)], radius=mm(2), fill=CREAM)
    txt(d, (W // 2, header_h // 2), title, tf, INK, "mm")

    # soft section backgrounds
    mid = header_h + (H - header_h) // 2
    d.rectangle([0, header_h, W, mid], fill=CORAL)
    d.rectangle([0, mid, W, H], fill=SAGE)

    apps = [
        (ASSETS / "app-blackboard.png", "Blackboard", "بلاك بورد",
         "المنصة الأكاديمية الرسمية للجامعة؛ تمكنك من متابعة المحاضرات، تسليم الواجبات، واطلاعك على الإعلانات والدرجات أولاً بأول.",
         (M, header_h + mm(5), W // 2 - mm(2.5), mid - mm(5)), WHITE),
        (ASSETS / "app-khata.png", "Khata", "خطة",
         "حاسبتك ومنظمك الأكاديمي؛ يساعدك على حساب ومتابعة معدلك التراكمي (GPA)، تنظيم الجدول الدراسي، وتتبع الدرجات بسهولة.",
         (W // 2 + mm(2.5), header_h + mm(5), W - M, mid - mm(5)), WHITE),
        (ASSETS / "app-notion.png", "Notion", "نوشن",
         "المساحة الشاملة لتنظيم حياتك الدراسية؛ تُستخدم لتدوين الملاحظات، ترتيب المهام، وإدارة المشاريع بأسلوب عصري.",
         (M, mid + mm(5), W // 2 - mm(2.5), H - mm(5)), WHITE),
        (ASSETS / "app-forest.png", "Forest", "فوريست",
         "تطبيق مبتكر للتركيز والتخلص من تشتت الهاتف؛ ينمي لك شجرة افتراضية كلما ابتعدت عن جوالك وركزت في مذاكرتك.",
         (W // 2 + mm(2.5), mid + mm(5), W - M, H - mm(5)), WHITE),
    ]

    for icon, en, ar_name, body, box, fill in apps:
        shadow_rect(img, box, radius=mm(4), fill=fill, shadow=14, blur=10, offset=(0, 5))
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = box
        # bottom accent strip inside card
        accent = CORAL_DEEP if y0 < mid else SAGE_DEEP
        d.rounded_rectangle([x0 + mm(1), y1 - mm(4), x1 - mm(1), y1 - mm(1)], radius=mm(1.5), fill=accent)

        icon_s = mm(14)
        ix1, iy0 = x1 - mm(5), y0 + mm(6)
        paste(img, icon, (ix1 - icon_s, iy0, ix1, iy0 + icon_s))
        title = f"{en} ({ar_name})"
        txt(d, (ix1 - icon_s - mm(3), iy0 + icon_s // 2), title, fnt("bold", 24), INK, "rm")
        d.line(
            [(x0 + mm(5), iy0 + icon_s + mm(4)), (x1 - mm(5), iy0 + icon_s + mm(4))],
            fill=GOLD,
            width=3,
        )
        wrap(
            d,
            (x0 + mm(5), iy0 + icon_s + mm(8), x1 - mm(5), y1 - mm(8)),
            body,
            fnt("regular", 20),
            MUTED,
            spacing=1.45,
            align="right",
        )
    return img


def page_tips():
    img = page(WHITE)
    d = ImageDraw.Draw(img)

    # soft cream header band
    d.rectangle([0, 0, W, mm(28)], fill=SOFT)
    hx = W - M
    hy = mm(6)
    d.rectangle([hx - mm(1.3), hy, hx, hy + mm(14)], fill=PURPLE)
    txt(d, (hx - mm(4), hy + mm(1)), "البدايات لا تُكتب بالحظ... بل بالعادات", fnt("medium", 24), INK, "rt")
    txt(d, (hx - mm(4), hy + mm(8)), "الصغيرة التي نختارها كل يوم", fnt("medium", 24), MUTED, "rt")

    tips = [
        ("01", "لا تؤجل البداية", "قد يبدو الأسبوع الأول خفيفًا لكنه يرسم الفصل كاملاً. وكل مهمة تنجزها اليوم، هي عبء أقل تحمله غدًا."),
        ("02", "اسأل بثقة", "ليس السؤال دليلًا على الجهل، بل رغبة في الفهم. وكل إجابة تحصل عليها اليوم، تختصر عليك كثيرًا من التردد."),
        ("03", "اجعل للمراجعة موعدًا", "لا تجعل كتبك لا تعرفك إلا ليلة الاختبار. دقائق قليلة بعد كل محاضرة قد تغنيك عن ساعات طويلة من القلق."),
        ("04", "عش التجربة كاملة", "درجاتك جزء من رحلتك لكنها ليست الرحلة كلها. شارك، تعلّم، واصنع لنفسك ذكريات تستحق أن تُروى بعد التخرج."),
        ("05", "نظّم وقتك قبل أن ينظّمك الوقت", "المهام الجامعية لا تتراكم فجأة بل تتسلل بهدوء. وما تكتبه في جدولك اليوم، لن يطاردك غدًا."),
    ]

    top, bottom = mm(34), H - M
    mid = W // 2
    gap = mm(5)
    cell_h = (bottom - top) // 3

    def tip(box, num, title, body):
        x0, y0, x1, y1 = box
        # number badge
        badge = mm(7)
        d.rounded_rectangle([x1 - badge, y0, x1, y0 + badge], radius=mm(1.5), fill=PURPLE)
        txt(d, (x1 - badge // 2, y0 + badge // 2), num, fnt("bold", 16), WHITE, "mm", rtl=False)
        txt(d, (x1 - badge - mm(2), y0 + badge // 2), title, fnt("bold", 23), INK, "rm")
        wrap(d, (x0, y0 + badge + mm(3), x1, y1 - mm(2)), body, fnt("regular", 17), MUTED, 1.4, "right")

    for i, t in enumerate(tips[:3]):
        y0 = top + i * cell_h
        tip((mid + gap, y0, W - M, y0 + cell_h - mm(4)), *t)
    for i, t in enumerate(tips[3:]):
        y0 = top + i * cell_h
        tip((M, y0, mid - gap, y0 + cell_h - mm(4)), *t)

    # quote card
    qx0, qy0 = M, top + 2 * cell_h
    qx1, qy1 = mid - gap, bottom
    shadow_rect(img, (qx0, qy0, qx1, qy1), radius=mm(5), fill=SOFT, shadow=10, blur=8)
    d = ImageDraw.Draw(img)
    txt(d, (qx0 + mm(6), qy0 + mm(8)), "”", fnt("black", 96), PURPLE, "lt", rtl=False)
    wrap(
        d,
        (qx0 + mm(6), qy0 + mm(28), qx1 - mm(6), qy1 - mm(6)),
        "مساحة لاقتباسك أو ملاحظة شخصية تكتبها بيدك…",
        fnt("medium", 18),
        PURPLE,
        1.35,
        "right",
    )
    return img


def page_map():
    img = page(PASTEL)
    d = ImageDraw.Draw(img)

    strip = mm(12)
    panel = [M, M, W - strip, H - M]
    px0, py0, px1, py1 = panel
    d.rounded_rectangle(panel, radius=mm(3), fill=PURPLE)

    nr = mm(8)
    for cx, cy in ((px0, py0), (px1, py0), (px0, py1), (px1, py1)):
        d.ellipse([cx - nr, cy - nr, cx + nr, cy + nr], fill=PASTEL)

    # richer route graphic on left
    path_col = (0x9A, 0x99, 0xCE)
    pts = []
    for i in range(24):
        t = i / 23
        x = px0 + mm(16) + math.sin(t * math.pi * 2.5) * mm(8)
        y = py0 + mm(28) + t * (py1 - py0 - mm(55))
        pts.append((x, y))
    d.line(pts, fill=path_col, width=5)
    stops = [0, 6, 12, 18, 23]
    labels = ["بوابة", "كليات", "مكتبة", "عمادة", "وجهتك"]
    for idx, (si, lab) in enumerate(zip(stops, labels)):
        x, y = pts[si]
        col = GOLD if si == stops[-1] else WHITE
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=col)
        txt(d, (x + mm(5), y), lab, fnt("medium", 14), (0xE8, 0xE6, 0xF5), "lm")

    x, y = pts[-1]
    d.polygon([(x, y - mm(9)), (x - mm(4.5), y - mm(2)), (x + mm(4.5), y - mm(2))], fill=GOLD)

    tx1 = px1 - mm(10)
    tx0 = px0 + mm(36)
    ty = py0 + mm(18)

    txt(d, (tx1, ty), "أين وجهتك؟", fnt("black", 56), WHITE, "rt")
    y2 = wrap(
        d,
        (tx0, ty + mm(16), tx1, ty + mm(52)),
        "سواء كنت متجهًا إلى عمادة شؤون الطلاب، أو تبحث عن المكتبة المركزية أو كليتك، ستساعدك الخريطة التفاعلية على الوصول بسهولة.",
        fnt("regular", 25),
        (0xF2, 0xF0, 0xFA),
        1.48,
        "right",
    )

    # secondary tip card mid-page
    tip_box = [tx0, y2 + mm(8), tx1, y2 + mm(28)]
    d.rounded_rectangle(tip_box, radius=mm(3), fill=(0x67, 0x66, 0xA8))
    wrap(
        d,
        (tip_box[0] + mm(4), tip_box[1] + mm(4), tip_box[2] - mm(4), tip_box[3] - mm(3)),
        "الخريطة التفاعلية ترشدك لأهم المعالم داخل المدينة الجامعية بضغطة واحدة.",
        fnt("medium", 18),
        WHITE,
        1.35,
        "right",
    )

    # CTA near QR
    cta = "امسح الرمز وابدأ رحلتك !"
    cf = fnt("bold", 24)
    cw, ch = tsize(d, ar(cta), cf)
    qr_s = mm(38)
    qx1, qy1 = W - mm(4), H - mm(10)
    qx0, qy0 = qx1 - qr_s, qy1 - qr_s

    cy = qy0 - mm(12)
    pill = [tx1 - cw - mm(8), cy - mm(3), tx1, cy + ch + mm(3)]
    d.rounded_rectangle(pill, radius=mm(3), fill=GOLD)
    txt(d, (tx1 - mm(4), cy + ch // 2), cta, cf, INK, "rm")

    shadow_rect(img, (qx0 - mm(3), qy0 - mm(3), qx1 + mm(3), qy1 + mm(3)), radius=mm(3), fill=WHITE)
    paste(img, ASSETS / "qr-map.png", (qx0, qy0, qx1, qy1))
    return img


def page_essay():
    img = page(SOFT)
    d = ImageDraw.Draw(img)

    # white content card
    card = [M, M, W - M, H - mm(22)]
    shadow_rect(img, card, radius=mm(4), fill=WHITE, shadow=16, blur=12)
    d = ImageDraw.Draw(img)

    # accent bar
    d.rectangle([card[2] - mm(1.5), card[1] + mm(10), card[2], card[3] - mm(10)], fill=PURPLE)

    paragraphs = [
        "قالوا إن الجامعة مرحلة صعبة، مليئة بالعقبات، ولم يقولوا إنها رحلة يتعاقب فيها العسر واليسر، وتُصنع فيها الحكايات بينهما.",
        "وقالوا: لا تصدّق أحدًا، فالكل سيستغلك؛ ولم يقولوا إنك ستجد فيها أناسًا يحبون العطاء، ويبذلون من وقتهم وجهدهم ما يجعل أيامك أيسر وأجمل.",
        "وقالوا إن الجامعة ليست إلا آيبادًا وقهوةً وروتينًا مملًا، ولم يذكروا أنها مساحة واسعة لاكتشاف ذاتك، وصقل مهاراتك، وبناء شخصيتك بعيدًا عن مقاعد الدراسة.",
        "قالوا الكثير، فلا تجعل ما قيل لك يرسم تجربتك قبل أن تعيشها. لا تكن معلّقًا في مهبّ الأقوال، بل خض تجربتك بنفسك، واصنع قصتك بطريقتك، وكن أنت من يمسك بدفّة سفينته، ويوجهها نحو المرفأ الذي ينشده.",
    ]
    closing = "فالجامعة لا تُروى كما قيلت لك... بل كما عشتها أنت"

    y = card[1] + mm(12)
    x0, x1 = card[0] + mm(8), card[2] - mm(8)
    for p in paragraphs:
        y = wrap(d, (x0, y, x1, card[3] - mm(30)), p, fnt("regular", 22), MUTED, 1.5, "right")
        y += mm(4)

    d.line([(x1 - mm(28), y + mm(2)), (x1, y + mm(2))], fill=GOLD, width=3)
    wrap(d, (x0, y + mm(6), x1, card[3] - mm(8)), closing, fnt("bold", 24), GREEN, 1.45, "right")

    paste(img, UT_LOGO, (W // 2 - mm(18), H - mm(18), W // 2 + mm(18), H - mm(6)))
    return img


def page_palette():
    img = page(WHITE)
    d = ImageDraw.Draw(img)

    txt(d, (W - M, M + mm(6)), "توزيع الألوان", fnt("black", 44), GREEN, "rt")
    d.rounded_rectangle([W - M - mm(26), M + mm(16), W - M, M + mm(17.4)], radius=3, fill=GOLD)

    txt(d, (W - M, M + mm(28)), "أساسي", fnt("bold", 26), INK, "rt")
    primaries = [(GREEN, "#3B5249", "أخضر"), (CREAM, "#EDE7D4", "كريمي"), (PURPLE, "#7473B3", "بنفسجي"), (GOLD, "#F8B624", "ذهبي")]
    gap, y, h = mm(4), M + mm(36), mm(32)
    cw = (W - 2 * M - 3 * gap) // 4
    for i, (col, hx, label) in enumerate(primaries):
        x1 = W - M - i * (cw + gap)
        x0 = x1 - cw
        shadow_rect(img, (x0, y, x1, y + h), radius=mm(3), fill=col, shadow=8, blur=6, offset=(0, 3))
        d = ImageDraw.Draw(img)
        tc = GREEN if col in (CREAM, GOLD) else WHITE
        txt(d, ((x0 + x1) // 2, y + h // 2 - mm(3)), label, fnt("bold", 18), tc, "mm")
        txt(d, ((x0 + x1) // 2, y + h // 2 + mm(5)), hx, fnt("light", 14), tc, "mm", rtl=False)

    dy = y + h + mm(14)
    d.line([(M, dy), (W - M, dy)], fill=(220, 220, 220), width=2)
    txt(d, (W - M, dy + mm(8)), "فرعي", fnt("bold", 26), INK, "rt")

    secs = [
        (PASTEL, "#B5C9E4", "سماوي"),
        (MAGENTA, "#FF5CB6", "وردي"),
        (CYAN, "#519CF2", "أزرق"),
        (PLUM, "#651853", "برقوقي"),
        (LEAF, "#5BB34E", "أخضر"),
    ]
    y2 = dy + mm(18)
    h2 = mm(26)
    cw2 = (W - 2 * M - 4 * gap) // 5
    for i, (col, hx, label) in enumerate(secs):
        x1 = W - M - i * (cw2 + gap)
        x0 = x1 - cw2
        shadow_rect(img, (x0, y2, x1, y2 + h2), radius=mm(3), fill=col, shadow=6, blur=5)
        d = ImageDraw.Draw(img)
        tc = GREEN if col == PASTEL else WHITE
        txt(d, ((x0 + x1) // 2, y2 + h2 // 2 - mm(2)), label, fnt("bold", 15), tc, "mm")
        txt(d, ((x0 + x1) // 2, y2 + h2 // 2 + mm(4)), hx, fnt("light", 12), tc, "mm", rtl=False)

    # brand footer strip
    band = mm(18)
    d.rectangle([0, H - band, W, H], fill=PURPLE)
    paste(img, UT_LOGO_WHITE, (W // 2 - mm(20), H - band + mm(2), W // 2 + mm(20), H - mm(2)))
    return img


def main():
    make_icons()
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.png"):
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
        path = OUT / f"{name}.png"
        img.save(path, "PNG", dpi=(DPI, DPI), optimize=True)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
