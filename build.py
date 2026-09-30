#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시루 홈페이지 빌드
================================================================
원본 HTML(src/siruhomepage.html)에서 글과 그림만 뽑아
새 디자인 템플릿(site/)에 입혀 배포본을 만든다.

    python3 build.py                         # src/siruhomepage.html 로 빌드
    python3 build.py ~/Downloads/새파일.html  # 새 원본 등록 후 빌드

만드는 것
  index.html            배포 페이지 (디자인 + 콘텐츠)
  assets/img/*.png      원본에 들어 있던 그림을 파일로 분리 (내용 해시 이름)
  manifest.webmanifest  앱 설치(PWA) 정보
  sw.js                 오프라인 지원 서비스 워커
  robots.txt, sitemap.xml (이미지 사이트맵 포함)

디자인을 바꾸려면 site/ 안의 파일을, 문구를 바꾸려면 site/config.json 을 고친다.
표준 라이브러리만 사용한다.
"""
import hashlib
import html
import json
import os
import re
import shutil
import struct
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "site"))
from extract import ExtractError, extract  # noqa: E402

SRC = os.path.join("src", "siruhomepage.html")
IMG_DIR = os.path.join("assets", "img")

TAB_ICONS = {"#about": "i-t-about", "#gallery": "i-t-gallery", "#artist": "i-t-artist", "#contact": "i-t-contact"}
FLOAT_POS = [  # x, y, size(% of stage), rotate, depth, bob-duration, delay
    ("-4%", "8%", "21%", "-10deg", 1.4, "6.2s", "0s"),
    ("80%", "30%", "19%", "9deg", 0.8, "7s", "-1.4s"),
    ("75%", "70%", "20%", "12deg", 1.2, "5.6s", "-2.6s"),
    ("-2%", "60%", "22%", "-7deg", 0.9, "6.6s", "-.8s"),
    ("16%", "-5%", "15%", "-4deg", 1.6, "7.4s", "-3.2s"),
    ("40%", "88%", "14%", "6deg", 1.1, "5.9s", "-2s"),
]
DECO_POS = [("-4%", "-6%", "clamp(80px,16vw,140px)", "-12deg", "0s"),
            ("84%", "4%", "clamp(70px,13vw,120px)", "10deg", "-2s"),
            ("78%", "74%", "clamp(76px,14vw,128px)", "-6deg", "-4s")]

SQUIGGLE = ('<svg class="squiggle" viewBox="0 0 300 24" preserveAspectRatio="none" aria-hidden="true">'
            '<path d="M4 14C38 4 62 22 104 12s74-10 106 0 62 12 86-2" fill="none" stroke="currentColor" '
            'stroke-width="4.5" stroke-linecap="round" pathLength="1"/></svg>')


def e(s):
    return html.escape(str(s), quote=True)


def png_size(data):
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    return (360, 360)


class Assets:
    """이미지를 내용 해시 이름으로 저장하고 참조를 모은다."""

    def __init__(self):
        self.used = set()
        os.makedirs(IMG_DIR, exist_ok=True)

    def put(self, img):
        data, ext = img["bytes"], img.get("ext", "png")
        name = hashlib.sha1(data).hexdigest()[:12] + "." + ext
        path = os.path.join(IMG_DIR, name)
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(data)
        self.used.add(name)
        w, h = png_size(data)
        return {"src": "/" + IMG_DIR.replace(os.sep, "/") + "/" + name, "w": w, "h": h}

    def prune(self):
        removed = 0
        for f in os.listdir(IMG_DIR):
            if f not in self.used:
                os.remove(os.path.join(IMG_DIR, f))
                removed += 1
        return removed


def render(template, values):
    missing = []

    def raw(m):
        k = m.group(1)
        if k not in values:
            missing.append(k)
            return ""
        return str(values[k])

    def esc(m):
        k = m.group(1)
        if k not in values:
            missing.append(k)
            return ""
        return e(values[k])

    out = re.sub(r"\{\{\{\s*(\w+)\s*\}\}\}", raw, template)
    out = re.sub(r"\{\{\s*(\w+)\s*\}\}", esc, out)
    if missing:
        raise ExtractError("템플릿 값 누락: " + ", ".join(sorted(set(missing))))
    return out


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s*\n\s*", "\n", css)
    return css.strip()


def build(src_html, cfg):
    c = extract(src_html)
    A = Assets()
    site = cfg["site_url"].rstrip("/")

    logo = A.put(c["logo"])
    hero = A.put(c["hero"]["image"])
    about = A.put(c["about"]["image"])
    artist = A.put(c["artist"]["image"])

    # ---------------- 갤러리
    g = c["gallery"]
    labels = {f["key"]: f["label"] for f in g["filters"]}
    items = []
    for i, it in enumerate(g["items"]):
        a = A.put(it)
        items.append(dict(it, **a, i=i, label=labels.get(it["cat"], it["cat"])))
    by_title = {it["title"]: it for it in items}
    count = len(items)

    def pick(titles, n, avoid=()):
        out = [by_title[t] for t in titles if t in by_title and by_title[t] not in avoid]
        step = max(1, count // (n + 1))
        k = 0
        while len(out) < n and k < count:
            cand = items[(k * step + 3) % count]
            if cand not in out and cand not in avoid:
                out.append(cand)
            k += 1
        return out[:n]

    cards = []
    for it in items:
        r = ((it["i"] * 37) % 11 - 5) * 0.34
        cards.append(
            '<li class="card" data-cat="{cat}" data-cat-label="{lab}" data-title="{t}" data-sub="{s}">'
            '<a href="{src}" style="--r:{r:.2f}deg">'
            '<span class="pic"><img src="{src}" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async"></span>'
            '<span class="t">{t}</span><span class="s">{s}</span></a></li>'.format(
                cat=e(it["cat"]), lab=e(it["label"]), t=e(it["title"]), s=e(it["sub"]), src=e(it["src"]),
                r=r, w=it["w"], h=it["h"], alt=e("%s 이모티콘 — %s" % (c["hero"]["title"], it["title"]))))

    counts = {}
    for it in items:
        counts[it["cat"]] = counts.get(it["cat"], 0) + 1
    chips = ['<button class="chip" type="button" data-f="all" aria-pressed="true">%s <small>%d</small></button>'
             % (e(g["all_label"]), count)]
    for f in g["filters"]:
        if counts.get(f["key"]):
            chips.append('<button class="chip" type="button" data-f="%s" aria-pressed="false">%s <small>%d</small></button>'
                         % (e(f["key"]), e(f["label"]), counts[f["key"]]))

    # ---------------- 히어로
    floaters = []
    for it, (x, y, s, r, z, t, d) in zip(pick(cfg["floaters"], 6), FLOAT_POS):
        floaters.append('<span class="floater" data-k="%d" aria-hidden="true" style="--x:%s;--y:%s;--s:%s;--r:%s;--z:%s;--t:%s;--d:%s">'
                        '<span><img src="%s" alt="" width="%d" height="%d" loading="lazy" decoding="async"></span></span>'
                        % (len(floaters), x, y, s, r, z, t, d, e(it["src"]), it["w"], it["h"]))
    title_chars = "".join('<span class="ch" style="--i:%d" aria-hidden="true">%s</span>' % (i, e(ch))
                          for i, ch in enumerate(c["hero"]["title"]))
    hero_ctas = []
    for cta in c["hero"]["ctas"]:
        if cta["primary"]:
            hero_ctas.append('<a class="btn primary" href="%s">%s<svg aria-hidden="true"><use href="#i-arrow"/></svg></a>'
                             % (e(cta["href"]), e(cta["label"])))
        else:
            hero_ctas.append('<a class="btn" href="%s">%s</a>' % (e(cta["href"]), e(cta["label"])))

    star = '<svg aria-hidden="true" viewBox="0 0 24 24"><use href="#i-star"/></svg>'
    half = (count + 1) // 2
    tape_a = "".join("<span>%s%s</span>" % (e(it["title"]), star) for it in items[:half])
    tape_b = "".join("<span>%s%s</span>" % (e(it["title"]), star) for it in items[half:] or items)

    # ---------------- 채팅
    ch = cfg["chat"]
    used = set()
    chat = []
    for m in ch["script"]:
        if "text" in m:
            chat.append({"from": m["from"], "text": m["text"]})
            continue
        it = by_title.get(m.get("sticker"))
        if not it or it["title"] in used:
            it = next((x for x in items if x["cat"] == m.get("fallback") and x["title"] not in used), items[0])
        used.add(it["title"])
        chat.append({"from": m["from"], "src": it["src"]})
    stats = [(count, ch["stat_labels"][0]), (len(counts), ch["stat_labels"][1]), (1, ch["stat_labels"][2])]
    stats_html = "".join('<div class="stat"><b data-count="%d">%d</b><span>%s</span></div>' % (n, n, e(l)) for n, l in stats)

    # ---------------- 소개 · 신분증
    spec = c["about"]["spec"]

    def spec_val(pred):
        return next((s["value"] for s in spec if pred(s["label"])), None)

    idc = cfg["idcard"]
    fl = idc["front_labels"]
    front = [(fl["name"], spec_val(lambda l: l.upper() == "NAME" or "이름" in l) or c["brand"]),
             (fl["kind"], spec_val(lambda l: "위장" in l)),
             (fl["feature"], spec_val(lambda l: "귀" in l))]
    id_front_rows = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(k), e(v)) for k, v in front if v)
    id_back_rows = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(s["label"]), e(s["value"])) for s in spec)

    paras = lambda ps: "\n        ".join("<p>%s</p>" % p for p in ps)  # noqa: E731  (clean_inline 로 이미 정제됨)

    # ---------------- 문의
    ct = c["contact"]
    mail_cta = next((x for x in ct["ctas"] if x["href"].startswith("mailto:")), {"label": "이메일 보내기"})
    other_cta = next((x for x in ct["ctas"] if not x["href"].startswith("mailto:")), {"href": "#gallery", "label": "작품 다시 보기"})
    mailto = "mailto:%s?subject=%s&body=%s" % (
        ct["email"], urllib.parse.quote(cfg["mail_subject"]), urllib.parse.quote(cfg["mail_body"]))
    deco = "".join('<span class="deco" data-k="%d" aria-hidden="true" style="--x:%s;--y:%s;--s:%s;--r:%s;--d:%s">'
                   '<img src="%s" alt="" width="%d" height="%d" loading="lazy"></span>'
                   % (k, x, y, s, r, d, e(it["src"]), it["w"], it["h"])
                   for k, (it, (x, y, s, r, d)) in enumerate(zip(pick(cfg["contact_deco"], 3), DECO_POS)))

    # ---------------- 내비
    top_links = "".join('<a href="%s">%s</a>' % (e(n["href"]), e(n["label"])) for n in c["nav"])
    tabs = "".join('<a href="%s"><svg aria-hidden="true"><use href="#%s"/></svg><span>%s</span></a>'
                   % (e(n["href"]), TAB_ICONS.get(n["href"], "i-t-dot"), e(n["label"].split()[0]))
                   for n in c["nav"])

    # ---------------- SEO
    h1, brand, artist_name = c["hero"]["title"], c["brand"], c["artist"]["name"]
    badge_text = re.sub(r"^[^\w가-힣]+", "", c["hero"]["badge"]).strip()
    description = ("%s의 캐릭터 '%s(%s)' 공식 팬페이지. %s %s의 표정 %d종 갤러리와 작가 소개, "
                   "이모티콘·캐릭터 협업·굿즈 제작 문의를 한곳에서 만나보세요." % (artist_name, h1, brand, badge_text, h1, count))
    og_description = "%s '%s'의 표정 %d종 갤러리와 작가 소개, 협업·굿즈 문의까지 한곳에서." % (badge_text, h1, count)
    keywords = ", ".join(dict.fromkeys([h1, brand, artist_name, "캐릭터", "이모티콘", "캐릭터 팬페이지", "굿즈", "캐릭터 협업"]
                                       + [f["label"] + " 이모티콘" for f in g["filters"]]))
    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": site + "/#website", "url": site + "/", "name": "%s %s" % (h1, brand),
             "description": description, "inLanguage": "ko-KR"},
            {"@type": "Person", "@id": site + "/#artist", "name": artist_name, "jobTitle": c["artist"]["role"],
             "email": "mailto:" + ct["email"], "image": site + artist["src"]},
            {"@type": "CreativeWork", "@id": site + "/#character", "name": "%s (%s)" % (h1, brand),
             "alternateName": brand, "description": badge_text, "image": site + hero["src"],
             "creator": {"@id": site + "/#artist"}, "inLanguage": "ko-KR"},
            {"@type": "ImageGallery", "@id": site + "/#gallery", "name": "%s %s" % (h1, g["heading"]),
             "about": {"@id": site + "/#character"}, "isPartOf": {"@id": site + "/#website"},
             "associatedMedia": [{"@type": "ImageObject", "contentUrl": site + it["src"], "name": "%s — %s" % (h1, it["title"]),
                                  "caption": it["sub"], "width": it["w"], "height": it["h"],
                                  "creator": {"@id": site + "/#artist"}} for it in items]},
        ],
    }

    empty_it = by_title.get(cfg["gallery"]["empty_sticker"], items[0])
    vw = cfg["viewer"]
    js_cfg = {
        "lines": cfg["hero_lines"], "secret": cfg["hero_secret_line"], "secretAfter": cfg["hero_secret_after"],
        "idFront": idc["hint"], "idBack": idc["hint_back"],
        "themeLight": cfg["theme_color"], "themeDark": cfg["theme_color_dark"],
        "linkCopied": "링크를 복사했어요", "copied": cfg["contact_copied"], "copiedShort": "복사됨",
        "copy": cfg["contact_copy"], "copyPrompt": "아래 주소를 복사하세요",
    }
    safe_json = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")  # noqa: E731

    values = {
        "title": c["title"], "description": description, "keywords": keywords, "site_url": site,
        "og_site_name": "%s %s" % (h1, brand), "og_description": og_description,
        "og_image_alt": "%s — %s" % (h1, badge_text), "brand": brand,
        "theme_color": cfg["theme_color"], "theme_color_dark": cfg["theme_color_dark"],
        "jsonld": safe_json(jsonld),
        "logo_src": logo["src"], "logo_w": logo["w"], "logo_h": logo["h"],
        "top_links": top_links, "tabs": tabs, "tab_count": len(c["nav"]),
        "hero_badge": c["hero"]["badge"], "hero_title": h1, "hero_title_chars": title_chars,
        "hero_tagline": c["hero"]["tagline"], "hero_ctas": "".join(hero_ctas),
        "hero_src": hero["src"], "hero_w": hero["w"], "hero_h": hero["h"], "hero_alt": c["hero"]["image"]["alt"],
        "hero_hint": cfg["hero_hint"], "floaters": "\n      ".join(floaters),
        "tape_a": tape_a, "tape_b": tape_b, "squiggle": SQUIGGLE,
        "chat_tag": ch["tag"], "chat_heading": ch["heading"], "chat_text": ch["text"], "chat_room": ch["room"],
        "chat_replay": ch["replay"], "chat_sr": "친구와의 대화에서 %s 이모티콘을 쓰는 예시 애니메이션" % h1,
        "chat_json": safe_json(chat), "stats": stats_html,
        "about_tag": c["about"]["tag"], "about_heading": c["about"]["heading"], "about_title": c["about"]["title"],
        "about_src": about["src"], "about_w": about["w"], "about_h": about["h"], "about_alt": c["about"]["image"]["alt"],
        "about_paras": paras(c["about"]["paragraphs"]),
        "id_front_title": idc["front_title"], "id_front_stamp": idc["front_stamp"], "id_no": "%s-%04d" % (brand, count),
        "id_front_rows": id_front_rows, "id_back_title": idc["back_title"], "id_back_badge": idc["back_badge"],
        "id_back_stamp": idc["back_stamp"], "id_back_rows": id_back_rows, "id_hint": idc["hint"],
        "id_toggle_label": "%s 신분증 뒤집기" % h1,
        "gallery_tag": g["tag"], "gallery_heading": g["heading"], "gallery_count": count,
        "gallery_count_suffix": cfg["gallery"]["count_suffix"], "search_label": "표정 검색",
        "search_placeholder": cfg["gallery"]["search_placeholder"], "gacha_label": cfg["gallery"]["gacha"],
        "gacha_ribbon": cfg["gallery"]["gacha_ribbon"], "chips": "".join(chips), "cards": "\n".join(cards),
        "empty_src": empty_it["src"], "empty_title": cfg["gallery"]["empty_title"], "empty_text": cfg["gallery"]["empty_text"],
        "artist_tag": c["artist"]["tag"], "artist_heading": c["artist"]["heading"], "artist_role": c["artist"]["role"],
        "artist_name": artist_name, "artist_paras": paras(c["artist"]["paragraphs"]),
        "artist_src": artist["src"], "artist_w": artist["w"], "artist_h": artist["h"], "artist_alt": c["artist"]["image"]["alt"],
        "artist_cta": cfg["artist_cta"],
        "contact_tag": ct["tag"], "contact_heading": ct["heading"], "contact_text": ct["text"],
        "mailto": mailto, "email": ct["email"], "contact_cta_mail": mail_cta["label"],
        "contact_cta2_href": other_cta["href"], "contact_cta2_label": other_cta["label"],
        "contact_or": cfg["contact_or"], "copy_label": cfg["contact_copy"], "contact_deco": deco,
        "footer": c["footer"], "back_to_top": cfg["back_to_top"],
        "v_close": vw["close"], "v_prev": vw["prev"], "v_next": vw["next"], "v_share": vw["share"],
        "v_save": vw["save"], "v_hint": vw["swipe_hint"],
        "cfg_json": safe_json(js_cfg),
        "styles": minify_css(open(os.path.join("site", "styles.css"), encoding="utf-8").read()),
        "script": open(os.path.join("site", "app.js"), encoding="utf-8").read().replace("</script", "<\\/script"),
    }
    page = render(open(os.path.join("site", "template.html"), encoding="utf-8").read(), values)
    return page, c, items, hero, logo, A


def write_if_changed(path, text):
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    if old != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    return False


def main():
    os.chdir(ROOT)
    if len(sys.argv) > 1:
        given = os.path.expanduser(sys.argv[1])
        if not os.path.exists(given):
            sys.exit("[!] 파일을 찾을 수 없습니다: %s" % given)
        os.makedirs("src", exist_ok=True)
        if os.path.abspath(given) != os.path.abspath(SRC):
            shutil.copyfile(given, SRC)
        print("새 원본 등록: %s -> %s" % (given, SRC))
    if not os.path.exists(SRC):
        sys.exit("[!] 원본이 없습니다: %s\n    python3 build.py ~/Downloads/siruhomepage.html 처럼 경로를 주세요." % SRC)

    cfg = json.load(open(os.path.join("site", "config.json"), encoding="utf-8"))
    raw = open(SRC, encoding="utf-8").read()
    print("빌드 시작  원본 %s bytes" % format(len(raw.encode()), ","))
    try:
        page, c, items, hero, logo, A = build(raw, cfg)
    except ExtractError as err:
        print("\n[!] 원본에서 필요한 내용을 찾지 못했습니다: %s" % err)
        print("    원본 HTML 구조가 바뀐 것 같습니다. 이 메시지를 Claude에게 보여주세요.")
        sys.exit(1)

    site = cfg["site_url"].rstrip("/")
    version = hashlib.sha1(page.encode()).hexdigest()[:10]
    changed = []
    if write_if_changed("index.html", page):
        changed.append("index.html")

    manifest = {
        "name": c["title"], "short_name": c["brand"], "description": c["hero"]["badge"],
        "lang": "ko", "dir": "ltr", "start_url": "/", "scope": "/", "id": "/",
        "display": "standalone", "background_color": cfg["theme_color"], "theme_color": cfg["theme_color"],
        "icons": [
            {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "shortcuts": [{"name": n["label"], "url": "/" + n["href"]} for n in c["nav"]],
    }
    if write_if_changed("manifest.webmanifest", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"):
        changed.append("manifest.webmanifest")

    # Cache.addAll 은 중복 URL 이 있으면 설치 자체가 실패하므로 중복 제거 (로고와 대표 그림이 같을 수 있음)
    core = list(dict.fromkeys(["/", "/manifest.webmanifest", "/assets/fonts/pretendard/pretendard.css",
                               hero["src"], logo["src"], "/icons/icon-192.png"]))
    assets = sorted("/" + IMG_DIR.replace(os.sep, "/") + "/" + n for n in A.used)
    sw = open(os.path.join("site", "sw.js"), encoding="utf-8").read()
    sw = sw.replace("__VERSION__", version).replace("__CORE__", json.dumps(core)).replace("__ASSETS__", json.dumps(assets))
    if write_if_changed("sw.js", sw):
        changed.append("sw.js")

    if write_if_changed("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % site):
        changed.append("robots.txt")
    imgs = [hero["src"]] + [it["src"] for it in items]
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
               'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
               '  <url>\n    <loc>%s/</loc>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n%s  </url>\n'
               '</urlset>\n') % (site, "".join("    <image:image><image:loc>%s%s</image:loc></image:image>\n" % (site, s)
                                               for s in dict.fromkeys(imgs)))
    if write_if_changed("sitemap.xml", sitemap):
        changed.append("sitemap.xml")

    # 공유 썸네일·아이콘이 없으면(최초) 대표 그림으로 임시 생성 — 정식 이미지는 tools/make_assets.py
    os.makedirs("icons", exist_ok=True)
    hero_path = os.path.join(ROOT, hero["src"].lstrip("/"))
    for p in ["og-image.png", "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png",
              "icons/apple-touch-icon.png", "icons/favicon-32.png"]:
        if not os.path.exists(p):
            shutil.copyfile(hero_path, p)
            changed.append(p + " (임시)")

    removed = A.prune()

    # ---------------- 검증
    checks = {
        "갤러리 %d종" % len(items): page.count('class="card"') == len(items),
        "SEO": all(k in page for k in ('property="og:title"', "application/ld+json", 'rel="canonical"')),
        "모바일": 'viewport-fit=cover' in page and "@media (max-width" in page,
        "이메일": 'id="copyEmail"' in page and "mailto:" in page,
        "치환 누락 없음": "{{" not in page,
    }
    print("\n갤러리 %d종 · 이미지 %d개 · index.html %s bytes" % (
        len(items), len(A.used), format(len(page.encode()), ",")))
    if changed:
        print("변경: " + ", ".join(changed))
    if removed:
        print("안 쓰는 이미지 %d개 정리" % removed)
    print("검증  " + "  ".join("%s:%s" % (k, "OK" if v else "실패") for k, v in checks.items()))
    if not all(checks.values()):
        sys.exit("\n[!] 검증 실패. 이 출력을 Claude에게 보여주세요.")
    print("\n빌드 성공. 배포하려면:  ./deploy.sh")


if __name__ == "__main__":
    main()
