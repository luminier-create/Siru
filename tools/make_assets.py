#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공유 썸네일(og-image.png, 1200x630)과 앱 아이콘(icons/*)을 만든다.

그림이 크게 바뀌었을 때만 실행하면 된다 (build.py 는 이 파일이 없어도 동작).
필요: Pillow (pip install pillow), Pretendard 폰트(OTF) — 폰트 폴더를 인자로 줄 수 있다.

    python3 tools/make_assets.py [Pretendard OTF 폴더]
"""
import glob
import io
import re
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "site"))
from extract import extract  # noqa: E402

CREAM = (255, 248, 238)
INK = (29, 23, 20)
BEAN = (140, 47, 43)
LEMON = (255, 229, 138)
PASTELS = [(255, 215, 196), (255, 235, 166), (207, 236, 223), (214, 228, 251), (231, 221, 251)]


def find_font(weight, hint_dir=None):
    dirs = [hint_dir] if hint_dir else []
    dirs += [os.path.expanduser("~/.fonts"), os.path.expanduser("~/Library/Fonts"), "/Library/Fonts",
             "/usr/share/fonts", "/usr/local/share/fonts"]
    for d in dirs:
        if not d:
            continue
        hits = glob.glob(os.path.join(d, "**", "Pretendard-%s.otf" % weight), recursive=True)
        if hits:
            return hits[0]
    sys.exit("[!] Pretendard-%s.otf 를 찾지 못했습니다. 폰트 폴더를 인자로 주세요." % weight)


def load(img):
    return Image.open(io.BytesIO(img["bytes"])).convert("RGBA")


def trim(im, pad=8):
    box = im.getbbox()
    if not box:
        return im
    l, t, r, b = box
    return im.crop((max(0, l - pad), max(0, t - pad), min(im.width, r + pad), min(im.height, b + pad)))


def fit(im, size):
    im = trim(im)
    s = min(size / im.width, size / im.height)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


def sticker(im, size, radius=34, border=5, pad=0.1):
    """흰 둥근 사각 스티커 + 먹선 + 딱딱한 그림자."""
    card = Image.new("RGBA", (size + 10, size + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((8, 8, size + 8, size + 8), radius, fill=INK)  # hard shadow
    d.rounded_rectangle((0, 0, size, size), radius, fill=(255, 255, 255), outline=INK, width=border)
    art = fit(im, int(size * (1 - pad * 2)))
    card.alpha_composite(art, ((size - art.width) // 2, (size - art.height) // 2))
    return card


def paste_rot(base, im, xy, angle):
    r = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(r, (int(xy[0] - r.width / 2), int(xy[1] - r.height / 2)))


def orbs(w, h, spots):
    layer = Image.new("RGB", (w, h), CREAM)
    d = ImageDraw.Draw(layer)
    for (x, y, r, col) in spots:
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)
    return layer.filter(ImageFilter.GaussianBlur(110)).convert("RGBA")


def dots(w, h, step=26, col=(29, 23, 20, 22)):
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(step // 2, h, step):
        for x in range(step // 2, w, step):
            d.ellipse((x - 1.3, y - 1.3, x + 1.3, y + 1.3), fill=col)
    return layer


def mochi(hero, size):
    """떡 접시 위의 시루."""
    s = size
    m = Image.new("RGBA", (s + 40, s + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", m.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((s * 0.18 + 20, s - 6, s * 0.82 + 20, s + 34), fill=(120, 60, 20, 90))
    m.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    plate = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    for i in range(40):  # 부드러운 명암
        t = i / 39
        c = tuple(int(a + (b - a) * t) for a, b in zip((241, 216, 195), (255, 253, 248)))
        inset = int(t * s * 0.18)
        pd.ellipse((inset * 0.6, inset * 0.4, s - inset * 1.4, s - inset * 1.6), fill=c + (255,))
    pd.ellipse((3, 3, s - 3, s - 3), outline=INK + (255,), width=6)
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, s, s), fill=255)
    m.paste(plate, (20, 10), mask)
    art = fit(hero, int(s * 0.86))
    m.alpha_composite(art, (20 + (s - art.width) // 2, 10 + (s - art.height) // 2))
    return m


def og_image(c, fonts, out):
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), CREAM + (255,))
    img.alpha_composite(orbs(W, H, [(120, 80, 260, PASTELS[0]), (700, -40, 240, PASTELS[1]),
                                    (1080, 560, 280, PASTELS[2]), (360, 640, 220, PASTELS[3]),
                                    (1120, 120, 170, PASTELS[4])]))
    img.alpha_composite(dots(W, H))
    hero = load(c["hero"]["image"])
    items = c["gallery"]["items"]

    # 왼쪽: 떡 위의 시루
    m = mochi(hero, 400)
    img.alpha_composite(m, (78, 108))

    # 스티커 행
    picks = [items[i * len(items) // 5] for i in range(5)]
    for k, it in enumerate(picks):
        st = sticker(load(it), 118, radius=26, border=4)
        paste_rot(img, st, (618 + k * 118, 520 + (k % 2) * 10), [-8, 6, -4, 9, -6][k])

    d = ImageDraw.Draw(img)
    # 배지
    badge = c["hero"]["badge"].lstrip("🐾").strip()
    bf = ImageFont.truetype(fonts["bold"], 30)
    bw = d.textlength(badge, font=bf) + 56
    by = 104
    badge_im = Image.new("RGBA", (int(bw) + 10, 70), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge_im)
    bd.rounded_rectangle((6, 6, bw + 6, 64), 30, fill=INK)
    bd.rounded_rectangle((0, 0, bw, 58), 29, fill=(255, 255, 255), outline=INK, width=4)
    bd.text((28, 29), badge, font=bf, fill=INK, anchor="lm")
    paste_rot(img, badge_im, (560 + bw / 2, by + 30), 2)

    # 제목
    tf = ImageFont.truetype(fonts["black"], 210)
    title = c["hero"]["title"]
    d.text((548, 330), title, font=tf, fill=INK, anchor="ls")
    tw = d.textlength(title, font=tf)
    # SIRU 라벨
    lf = ImageFont.truetype(fonts["black"], 38)
    lab = c["brand"]
    lw = d.textlength(lab, font=lf) + 40
    lab_im = Image.new("RGBA", (int(lw) + 12, 78), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lab_im)
    ld.rounded_rectangle((7, 7, lw + 7, 70), 16, fill=INK)
    ld.rounded_rectangle((0, 0, lw, 63), 16, fill=LEMON, outline=INK, width=4)
    ld.text((lw / 2, 32), lab, font=lf, fill=INK, anchor="mm")
    paste_rot(img, lab_im, (548 + tw + 50, 180), -12)

    # 태그라인
    sf = ImageFont.truetype(fonts["semibold"], 31)
    lines = [re.sub(r"<[^>]+>", "", x).strip() for x in c["hero"]["tagline"].split("<br>")]
    lines = [x for x in lines if x and x.rstrip(".") not in badge] or lines
    d.multiline_text((552, 352), "\n".join(wrap(d, " ".join(lines), sf, 590)), font=sf, fill=(91, 81, 74), spacing=10)

    img.convert("RGB").save(out, "PNG", optimize=True)


def wrap(d, text, font, width):
    """폭에 맞춰 줄바꿈하되, 마지막 줄이 짧게 남지 않도록 균형을 맞춘다."""
    best = _wrap(d, text, font, width)
    w = width
    while w > width * 0.55:
        w -= 10
        cand = _wrap(d, text, font, w)
        if len(cand) > len(best):
            break
        best = cand
    return best


def _wrap(d, text, font, width):
    out, line = [], ""
    for word in text.split(" "):
        test = (line + " " + word).strip()
        if d.textlength(test, font=font) <= width or not line:
            line = test
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out[:3]


def icon(hero, size, bleed, bg=CREAM, ring=False):
    im = Image.new("RGBA", (size, size), bg + (255,))
    if ring:
        d = ImageDraw.Draw(im)
        w = max(2, size // 40)
        d.ellipse((w, w, size - w - 1, size - w - 1), outline=INK, width=w)
    art = fit(hero, int(size * bleed))
    im.alpha_composite(art, ((size - art.width) // 2, (size - art.height) // 2 + int(size * 0.02)))
    return im


def main():
    font_dir = sys.argv[1] if len(sys.argv) > 1 else None
    fonts = {"black": find_font("Black", font_dir), "bold": find_font("Bold", font_dir),
             "semibold": find_font("SemiBold", font_dir)}
    os.chdir(ROOT)
    c = extract(open(os.path.join("src", "siruhomepage.html"), encoding="utf-8").read())
    hero = load(c["hero"]["image"])
    og_image(c, fonts, "og-image.png")
    os.makedirs("icons", exist_ok=True)
    icon(hero, 512, 0.78).convert("RGB").save("icons/icon-512.png", optimize=True)
    icon(hero, 192, 0.78).convert("RGB").save("icons/icon-192.png", optimize=True)
    icon(hero, 512, 0.6).convert("RGB").save("icons/icon-maskable-512.png", optimize=True)
    icon(hero, 180, 0.8).convert("RGB").save("icons/apple-touch-icon.png", optimize=True)
    # 파비콘: 투명 배경 + 둥근 크림 원
    fav = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(fav)
    d.ellipse((1, 1, 62, 62), fill=CREAM + (255,), outline=INK, width=3)
    art = fit(hero, 58)
    fav.alpha_composite(art, ((64 - art.width) // 2, (64 - art.height) // 2 + 1))
    fav.resize((32, 32), Image.LANCZOS).save("icons/favicon-32.png", optimize=True)
    for p in ["og-image.png"] + sorted(glob.glob("icons/*.png")):
        print("  %-28s %6d bytes  %s" % (p, os.path.getsize(p), Image.open(p).size))


if __name__ == "__main__":
    main()
