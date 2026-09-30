# -*- coding: utf-8 -*-
"""
원본 HTML(시루 홈페이지 export)에서 콘텐츠만 뽑아낸다.

디자인은 site/ 의 템플릿이 담당하고, 원본에서는 글과 그림만 가져온다.
그래서 새 export 를 넣어도 새 디자인이 그대로 유지된다.

표준 라이브러리만 사용한다 (사용자 Mac 에서도 추가 설치 없이 동작).
"""
import base64
import html
import json
import re


class ExtractError(Exception):
    """원본 구조가 예상과 달라 필요한 콘텐츠를 찾지 못했을 때."""


# ------------------------------------------------------------------ 유틸
_ALLOWED = {"b", "strong", "em", "i", "br"}
_TAG = re.compile(r"<(/?)([a-zA-Z0-9]+)[^>]*?(/?)>")


def clean_inline(fragment):
    """허용 태그(b/strong/em/i/br)만 남기고 나머지는 벗겨낸 안전한 HTML."""
    out, pos = [], 0
    for m in _TAG.finditer(fragment):
        out.append(html.escape(html.unescape(fragment[pos:m.start()]), quote=False))
        closing, name = m.group(1), m.group(2).lower()
        if name in _ALLOWED:
            out.append("<br>" if name == "br" else "<%s%s>" % (closing, name))
        pos = m.end()
    out.append(html.escape(html.unescape(fragment[pos:]), quote=False))
    return re.sub(r"\s+", " ", "".join(out)).strip()


def text(fragment):
    """태그를 모두 벗긴 순수 텍스트."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _one(pattern, src, what, flags=re.S):
    m = re.search(pattern, src, flags)
    if not m:
        raise ExtractError(what)
    return m


def _section(src, sid):
    return _one(r'<section[^>]*id="%s"[^>]*>(.*?)</section>' % sid, src, "섹션 #%s" % sid).group(1)


def _img(fragment, what):
    """fragment 안 첫 번째 data-URI 이미지 → (bytes, alt)."""
    m = _one(r'<img[^>]*?src="data:image/(png|jpe?g|webp|gif);base64,([A-Za-z0-9+/=\s]+)"([^>]*)>',
             fragment, what)
    alt = re.search(r'alt="([^"]*)"', m.group(0))
    return {
        "bytes": base64.b64decode(re.sub(r"\s", "", m.group(2))),
        "ext": "jpg" if m.group(1).startswith("jp") else m.group(1),
        "alt": html.unescape(alt.group(1)) if alt else "",
    }


def _paragraphs(fragment, skip_class=None):
    out = []
    for m in re.finditer(r"<p([^>]*)>(.*?)</p>", fragment, re.S):
        if skip_class and skip_class in m.group(1):
            continue
        body = clean_inline(m.group(2))
        if body:
            out.append(body)
    return out


# ------------------------------------------------------------------ 추출
def extract(src):
    c = {}

    c["title"] = text(_one(r"<title>(.*?)</title>", src, "<title>").group(1))

    # 로고
    logo = _one(r'<div class="logo">(.*?)</div>', src, "로고(.logo)").group(1)
    c["logo"] = _img(logo, "로고 이미지")
    c["brand"] = text(re.sub(r"<img[^>]*>", "", logo)) or "SIRU"

    # 내비
    links = _one(r'<div class="nav-links">(.*?)</div>', src, "내비(.nav-links)").group(1)
    c["nav"] = [{"href": h, "label": text(l)}
                for h, l in re.findall(r'<a href="(#[^"]+)"[^>]*>(.*?)</a>', links, re.S)]

    # 히어로
    header = _one(r"<header[^>]*>(.*?)</header>", src, "<header>").group(1)
    c["hero"] = {
        "badge": text(_one(r'class="badge"[^>]*>(.*?)</div>', header, "배지(.badge)").group(1)),
        "image": _img(header, "대표 이미지(.hero-img)"),
        "title": text(_one(r"<h1[^>]*>(.*?)</h1>", header, "<h1>").group(1)),
        "tagline": clean_inline(_one(r'class="tagline"[^>]*>(.*?)</div>', header, "태그라인(.tagline)").group(1)),
        "ctas": [{"href": h, "label": text(l), "primary": "fill" in cls}
                 for cls, h, l in re.findall(r'<a class="btn([^"]*)" href="([^"]+)"[^>]*>(.*?)</a>', header, re.S)],
    }

    # 캐릭터 소개
    about = _section(src, "about")
    c["about"] = {
        "tag": text(_one(r'class="sec-tag"[^>]*>(.*?)</div>', about, "about 태그").group(1)),
        "heading": text(_one(r"<h2[^>]*>(.*?)</h2>", about, "about 제목").group(1)),
        "image": _img(about, "캐릭터 소개 이미지"),
        "title": text(_one(r"<h3[^>]*>(.*?)</h3>", about, "about 소제목").group(1)),
        "paragraphs": _paragraphs(about),
        "spec": [{"label": text(k), "value": text(v)}
                 for k, v in re.findall(r"<div><b>(.*?)</b><span>(.*?)</span></div>", about, re.S)],
    }

    # 갤러리
    gallery = _section(src, "gallery")
    filters = [{"key": k, "label": text(l)}
               for k, l in re.findall(r'data-f="([^"]+)"[^>]*>(.*?)</button>', gallery, re.S)]
    c["gallery"] = {
        "tag": text(_one(r'class="sec-tag"[^>]*>(.*?)</div>', gallery, "gallery 태그").group(1)),
        "heading": text(_one(r"<h2[^>]*>(.*?)</h2>", gallery, "gallery 제목").group(1)),
        "all_label": next((f["label"] for f in filters if f["key"] == "all"), "전체"),
        "filters": [f for f in filters if f["key"] != "all"],
    }
    raw = _one(r"const DATA\s*=\s*(\[.*?\]);", src, "갤러리 데이터(const DATA)").group(1)
    try:
        data = json.loads(raw)
    except ValueError as e:
        raise ExtractError("갤러리 데이터 JSON 파싱 실패: %s" % e)
    items = []
    for d in data:
        m = re.match(r"data:image/(png|jpe?g|webp|gif);base64,(.+)$", d.get("src", ""), re.S)
        if not m:
            raise ExtractError("갤러리 항목 이미지(data URI) 형식")
        items.append({
            "bytes": base64.b64decode(m.group(2)),
            "ext": "jpg" if m.group(1).startswith("jp") else m.group(1),
            "title": d.get("title", "").strip(),
            "sub": d.get("sub", "").strip(),
            "cat": d.get("cat", "").strip(),
        })
    if not items:
        raise ExtractError("갤러리 항목이 비어 있음")
    c["gallery"]["items"] = items

    # 작가
    artist = _section(src, "artist")
    c["artist"] = {
        "tag": text(_one(r'class="sec-tag"[^>]*>(.*?)</div>', artist, "artist 태그").group(1)),
        "heading": text(_one(r"<h2[^>]*>(.*?)</h2>", artist, "artist 제목").group(1)),
        "role": text(_one(r'class="role"[^>]*>(.*?)</div>', artist, "작가 역할(.role)").group(1)),
        "name": text(_one(r"<h3[^>]*>(.*?)</h3>", artist, "작가 이름").group(1)),
        "paragraphs": _paragraphs(artist),
        "image": _img(artist, "작가 이미지"),
    }

    # 문의
    contact = _section(src, "contact")
    mail = _one(r'href="mailto:([^"?]+)', contact, "문의 이메일(mailto)").group(1)
    c["contact"] = {
        "tag": text(_one(r'class="sec-tag"[^>]*>(.*?)</div>', contact, "contact 태그").group(1)),
        "heading": text(_one(r"<h2[^>]*>(.*?)</h2>", contact, "contact 제목").group(1)),
        "text": (_paragraphs(contact, skip_class="email-line") or [""])[0],
        "email": html.unescape(mail),
        "ctas": [{"href": h, "label": text(l), "primary": "fill" in cls}
                 for cls, h, l in re.findall(r'<a class="btn([^"]*)" href="([^"]+)"[^>]*>(.*?)</a>', contact, re.S)],
    }

    footer = re.search(r"<footer[^>]*>(.*?)</footer>", src, re.S)
    c["footer"] = text(footer.group(1)) if footer else ""
    return c
