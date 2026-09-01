#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시루 홈페이지 빌드 스크립트
================================================================
원본(src/siruhomepage.html)에 아래 개선사항을 입혀 배포본(index.html)을 만든다.

  · 모바일 최적화 — 노치 안전영역, 터치 보정, 나브 가로 스크롤,
                    반응형 여백, 소형화면(<=420px) 2열 갤러리
  · 문의 이메일   — 제목·본문이 채워진 mailto + 주소 복사 버튼
  · SEO          — 검색 메타 / Open Graph / 트위터 카드 / JSON-LD
  · 부속 파일     — robots.txt, sitemap.xml, og-image.png, favicon.png

사용법
------
    python3 build.py                      # src/siruhomepage.html 로 빌드
    python3 build.py ~/Downloads/새파일.html   # 새 원본을 src/ 에 넣고 빌드

원본이 바뀌어도 이 스크립트만 다시 돌리면 개선사항이 그대로 재적용된다.
갤러리 개수(예: 55종)는 원본에서 자동으로 세어 문구에 반영한다.
"""
import base64
import json
import os
import re
import shutil
import sys

# ------------------------------------------------------------------ 설정
SITE = "https://siru-4a476.web.app"
EMAIL = "luminier@gmail.com"
SRC = os.path.join("src", "siruhomepage.html")
OUT = "index.html"

ROOT = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------------ 유틸
class Build:
    def __init__(self, html):
        self.h = html
        self.done, self.skipped, self.failed = [], [], []

    def step(self, old, new, label):
        if old in self.h:
            self.h = self.h.replace(old, new, 1)
            self.done.append(label)
        elif new in self.h:
            self.skipped.append(label)
        else:
            self.failed.append(label)
        return self


def gallery_count(html):
    """원본의 갤러리 항목 수를 센다 (실패 시 None)."""
    m = re.search(r"const DATA = (\[.*?\]);", html, re.S)
    if not m:
        return None
    try:
        return len(json.loads(m.group(1)))
    except Exception:
        return html.count('"src": "data:image')


# ------------------------------------------------------------------ 조각
def seo_block(count):
    n = "%d종" % count if count else "다양한 표정"
    return '''
<!-- SEO -->
<meta name="description" content="루루 작가의 캐릭터 '시루(SIRU)' 공식 팬페이지. 강아지인 척하는 조랭이떡 시루의 표정 {n} 갤러리와 작가 소개, 이모티콘·캐릭터 협업·굿즈 제작 문의를 한곳에서 만나보세요.">
<meta name="keywords" content="시루, SIRU, 루루 작가, 캐릭터, 이모티콘, 조랭이떡, 캐릭터 팬페이지, 굿즈, 캐릭터 협업, 이모티콘 작가">
<meta name="author" content="루루 작가">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{site}/">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/favicon.png">

<!-- Open Graph (카카오톡·페이스북 등 공유 미리보기) -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="시루 SIRU">
<meta property="og:title" content="시루 SIRU — 루루 작가 캐릭터 팬페이지">
<meta property="og:description" content="강아지인 척하는 조랭이떡 '시루'의 표정 {n} 갤러리와 작가 소개, 협업·굿즈 문의까지 한곳에서.">
<meta property="og:url" content="{site}/">
<meta property="og:image" content="{site}/og-image.png">
<meta property="og:image:width" content="360">
<meta property="og:image:height" content="360">
<meta property="og:image:alt" content="캐릭터 시루 대표 이미지">
<meta property="og:locale" content="ko_KR">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="시루 SIRU — 루루 작가 캐릭터 팬페이지">
<meta name="twitter:description" content="강아지인 척하는 조랭이떡 '시루'의 표정 {n} 갤러리와 작가 소개, 협업·굿즈 문의까지 한곳에서.">
<meta name="twitter:image" content="{site}/og-image.png">

<!-- 구조화 데이터 (JSON-LD) -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "WebSite",
      "@id": "{site}/#website",
      "url": "{site}/",
      "name": "시루 SIRU",
      "description": "루루 작가의 캐릭터 '시루(SIRU)' 공식 팬페이지",
      "inLanguage": "ko-KR"
    }},
    {{
      "@type": "Person",
      "@id": "{site}/#artist",
      "name": "루루 작가",
      "jobTitle": "일러스트레이터",
      "email": "{email}"
    }},
    {{
      "@type": "CreativeWork",
      "name": "시루 (SIRU)",
      "alternateName": "SIRU",
      "description": "강아지인 척하는 조랭이떡 캐릭터",
      "image": "{site}/og-image.png",
      "inLanguage": "ko-KR",
      "creator": {{ "@id": "{site}/#artist" }},
      "isPartOf": {{ "@id": "{site}/#website" }}
    }}
  ]
}}
</script>'''.format(n=n, site=SITE, email=EMAIL)


MAILTO = (
    "mailto:" + EMAIL +
    "?subject=%5B%EC%8B%9C%EB%A3%A8%20SIRU%5D%20%EB%AC%B8%EC%9D%98%EB%93%9C%EB%A6%BD%EB%8B%88%EB%8B%A4"
    "&body=%EC%95%88%EB%85%95%ED%95%98%EC%84%B8%EC%9A%94%2C%20%EB%A3%A8%EB%A3%A8%20%EC%9E%91%EA%B0%80%EB%8B%98.%0A%0A"
    "%28%20%EB%AC%B8%EC%9D%98%20%EB%82%B4%EC%9A%A9%EC%9D%84%20%EC%A0%81%EC%96%B4%EC%A3%BC%EC%84%B8%EC%9A%94%20%29%0A%0A"
    "-%20%EB%AC%B8%EC%9D%98%20%EC%9C%A0%ED%98%95%28%EC%9D%B4%EB%AA%A8%ED%8B%B0%EC%BD%98/%ED%98%91%EC%97%85/%EA%B5%BF%EC%A6%88%20%EB%93%B1%29%3A%0A"
    "-%20%ED%9A%8C%EC%8B%A0%EB%B0%9B%EC%9D%84%20%EC%97%B0%EB%9D%BD%EC%B2%98%3A%0A"
)

COPY_JS = """  if(e.key==='ArrowRight') step(1);
});

/* 이메일 주소 복사 */
(function(){
  const btn=document.getElementById('copyEmail');
  const addr=document.getElementById('emailAddr');
  if(!btn||!addr) return;
  const email=addr.dataset.email;
  btn.addEventListener('click',async()=>{
    try{
      if(navigator.clipboard&&navigator.clipboard.writeText){
        await navigator.clipboard.writeText(email);
      }else{
        const t=document.createElement('textarea');
        t.value=email; t.style.position='fixed'; t.style.opacity='0';
        document.body.appendChild(t); t.focus(); t.select();
        document.execCommand('copy'); document.body.removeChild(t);
      }
      const prev=btn.textContent;
      btn.textContent='복사됨'; btn.classList.add('done');
      setTimeout(()=>{ btn.textContent=prev; btn.classList.remove('done'); },1600);
    }catch(e){
      window.prompt('아래 주소를 복사하세요', email);
    }
  });
})();"""

MEDIA_OLD = """@media(max-width:760px){
  .about,.artist{grid-template-columns:1fr;text-align:center;padding:28px}
  .artist img{max-width:180px;margin:0 auto}
  .about img{max-width:220px;margin:0 auto}
  .nav-links{display:none}
  .grid{grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px}
}"""

MEDIA_NEW = """@media(max-width:760px){
  .about,.artist{grid-template-columns:1fr;text-align:center;padding:28px}
  .artist img{max-width:180px;margin:0 auto}
  .about img{max-width:220px;margin:0 auto}
  /* 내비 링크를 숨기지 않고 가로 스크롤 바로 유지 — 모바일에서도 이동 가능 */
  .nav-links{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;max-width:60%;justify-content:flex-end}
  .nav-links::-webkit-scrollbar{display:none}
  .nav-links a{flex:0 0 auto;background:var(--paper);border:2px solid var(--line)}
  .grid{grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px}
  section{padding:44px 0}
  header{padding:40px 0 40px}
  .hero-img{width:170px;height:170px}
  .b1{width:150px;height:150px;left:-50px}
  .b2{width:130px;height:130px}
  .b3{width:90px;height:90px;right:20px}
  .contact{padding:36px 22px}
  .cta{flex-direction:column;align-items:stretch}
  .cta .btn{width:100%;padding:14px 20px}
  footer{padding:32px 20px calc(40px + env(safe-area-inset-bottom))}
}
@media(max-width:420px){
  .wrap{padding:0 16px}
  .grid{grid-template-columns:repeat(2,1fr);gap:10px}
  .logo{font-size:17px}
  .logo img{width:34px;height:34px}
  h1{letter-spacing:-2px}
  .spec{grid-template-columns:1fr 1fr}
  .lb{padding:16px}
  .lb-close{top:-12px;right:-12px}
}"""

ROBOTS = "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE

SITEMAP_TMPL = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>%s/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
""" % SITE


# ------------------------------------------------------------------ 빌드
def build(html):
    b = Build(html)
    count = gallery_count(html)

    # 1) 모바일 메타
    b.step('<meta name="viewport" content="width=device-width, initial-scale=1.0">',
           '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">\n'
           '<meta name="theme-color" content="#FFF9F0">\n'
           '<meta name="mobile-web-app-capable" content="yes">\n'
           '<meta name="apple-mobile-web-app-capable" content="yes">\n'
           '<meta name="apple-mobile-web-app-status-bar-style" content="default">\n'
           '<meta name="format-detection" content="telephone=no">',
           "모바일 메타 (viewport-fit / theme-color)")

    # 2) SEO
    if "og:title" in b.h:
        b.skipped.append("SEO 태그")
    elif "</title>\n" in b.h:
        b.h = b.h.replace("</title>\n", "</title>\n" + seo_block(count) + "\n", 1)
        b.done.append("SEO 태그 (메타 / OG / 트위터 / JSON-LD)")
    else:
        b.failed.append("SEO 태그")

    # 3) 터치·스크롤 보정
    b.step("html{scroll-behavior:smooth}",
           "html{scroll-behavior:smooth;-webkit-text-size-adjust:100%;text-size-adjust:100%}",
           "글자 크기 자동확대 방지")
    b.step("  background-size:22px 22px;\n}",
           "  background-size:22px 22px;\n"
           "  -webkit-tap-highlight-color:transparent;\n"
           "  -webkit-font-smoothing:antialiased;\n"
           "  overflow-x:hidden;\n}\n"
           "img{max-width:100%}\n"
           "a,button{touch-action:manipulation}",
           "터치 하이라이트 / 가로 스크롤 방지")

    # 4) 노치 대응
    b.step("nav{position:sticky;top:0;z-index:50;background:rgba(255,249,240,.92);backdrop-filter:blur(8px);border-bottom:2px solid var(--line)}",
           "nav{position:sticky;top:0;z-index:50;background:rgba(255,249,240,.92);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border-bottom:2px solid var(--line);padding-top:env(safe-area-inset-top)}",
           "상단바 노치 여백")
    b.step(".nav-in{max-width:1080px;margin:0 auto;padding:12px 20px;",
           ".nav-in{max-width:1080px;margin:0 auto;padding:12px max(20px,env(safe-area-inset-left)) 12px max(20px,env(safe-area-inset-right));",
           "상단바 좌우 안전영역")

    # 5) 버튼 터치 반응
    b.step(".btn:hover{transform:translate(2px,2px);box-shadow:2px 2px 0 var(--line)}",
           ".btn:hover{transform:translate(2px,2px);box-shadow:2px 2px 0 var(--line)}\n"
           ".btn:active{transform:translate(4px,4px);box-shadow:0 0 0 var(--line)}",
           "버튼 터치 반응")

    # 6) 이메일 영역 스타일
    b.step(".contact p{color:var(--sub);font-weight:600;margin-bottom:26px}",
           ".contact p{color:var(--sub);font-weight:600;margin-bottom:26px}\n"
           ".email-line{margin-top:22px;margin-bottom:0;font-size:14px;line-height:1.9}\n"
           ".email-line a{font-size:17px;font-weight:900;color:var(--ink);text-decoration:none;border-bottom:2px solid var(--peach);word-break:break-all}\n"
           ".copy-btn{font-family:inherit;font-weight:800;font-size:12px;padding:4px 12px;margin-left:8px;border:2px solid var(--line);border-radius:999px;background:var(--lemon);cursor:pointer;vertical-align:middle}\n"
           ".copy-btn:active{transform:translateY(1px)}\n"
           ".copy-btn.done{background:var(--mint)}",
           "이메일 영역 스타일")

    # 7) 반응형
    b.step(MEDIA_OLD, MEDIA_NEW, "반응형 (모바일 여백 / 소형화면 2열)")

    # 8) 이메일 버튼 + 주소/복사
    b.step('<a class="btn fill" href="mailto:%s">이메일 보내기</a>' % EMAIL,
           '<a class="btn fill" href="' + MAILTO + '">이메일 보내기</a>',
           "이메일 제목·본문 자동 입력")
    b.step('        <a class="btn" href="#gallery">작품 다시 보기</a>\n      </div>\n    </div>',
           '        <a class="btn" href="#gallery">작품 다시 보기</a>\n      </div>\n'
           '      <p class="email-line">또는 직접 메일 주소로 보내주세요<br>\n'
           '        <a id="emailAddr" href="mailto:{e}" data-email="{e}">{e}</a>\n'
           '        <button type="button" class="copy-btn" id="copyEmail" aria-label="이메일 주소 복사">복사</button>\n'
           '      </p>\n    </div>'.format(e=EMAIL),
           "이메일 주소 + 복사 버튼")

    # 9) 이미지 대체텍스트
    b.step("function render(){ const d=DATA[cur]; lbImg.src=d.src; lbT.textContent",
           "function render(){ const d=DATA[cur]; lbImg.src=d.src; lbImg.alt=d.title; lbT.textContent",
           "이미지 대체텍스트(alt)")

    # 10) 복사 스크립트
    b.step("  if(e.key==='ArrowRight') step(1);\n});", COPY_JS, "복사 버튼 동작 스크립트")

    return b, count


def write_assets(html):
    """robots.txt / sitemap.xml / og-image.png / favicon.png 생성."""
    out = []
    for name, content in (("robots.txt", ROBOTS), ("sitemap.xml", SITEMAP_TMPL)):
        old = open(name, encoding="utf-8").read() if os.path.exists(name) else None
        if old != content:
            open(name, "w", encoding="utf-8").write(content)
            out.append(name)
    pats = (("og-image.png", r'<img class="hero-img" src="data:image/png;base64,([A-Za-z0-9+/=]+)"'),
            ("favicon.png", r'<div class="logo"><img src="data:image/png;base64,([A-Za-z0-9+/=]+)"'))
    missing = []
    for name, pat in pats:
        m = re.search(pat, html)
        if not m:
            missing.append(name)
            continue
        raw = base64.b64decode(m.group(1))
        old = open(name, "rb").read() if os.path.exists(name) else None
        if old != raw:
            open(name, "wb").write(raw)
            out.append("%s (%s bytes)" % (name, format(len(raw), ",")))
    return out, missing


def main():
    os.chdir(ROOT)

    # 새 원본을 인자로 받으면 src/ 에 넣는다
    if len(sys.argv) > 1:
        given = os.path.expanduser(sys.argv[1])
        if not os.path.exists(given):
            print("[!] 파일을 찾을 수 없습니다: %s" % given)
            sys.exit(1)
        os.makedirs("src", exist_ok=True)
        if os.path.abspath(given) != os.path.abspath(SRC):
            shutil.copyfile(given, SRC)
        print("새 원본을 등록했습니다: %s  ->  %s" % (given, SRC))

    if not os.path.exists(SRC):
        print("[!] 원본이 없습니다: %s" % SRC)
        print("    새 HTML 경로를 인자로 주세요:")
        print("      python3 build.py ~/Downloads/siruhomepage.html")
        sys.exit(1)

    raw = open(SRC, encoding="utf-8").read()
    print("빌드 시작  원본 %s bytes" % format(len(raw.encode()), ","))

    b, count = build(raw)
    open(OUT, "w", encoding="utf-8").write(b.h)
    assets, missing = write_assets(b.h)

    # ---------------- 결과
    if b.done:
        print("\n적용:")
        for d in b.done:
            print("  o " + d)
    if b.skipped:
        print("건너뜀(원본에 이미 있음):")
        for s in b.skipped:
            print("  - " + s)
    if b.failed:
        print("\n[!] 적용 실패 — 원본 구조가 바뀐 것 같습니다:")
        for f in b.failed:
            print("  ! " + f)
    if assets:
        print("\n부속 파일:")
        for a in assets:
            print("  o " + a)
    for m in missing:
        b.failed.append(m + " 추출")

    txt = b.h
    checks = {
        "SEO": ("og:title" in txt) and ("application/ld+json" in txt),
        "모바일": ("viewport-fit=cover" in txt) and ("@media(max-width:420px)" in txt),
        "이메일": "copyEmail" in txt,
        "부속파일": all(os.path.exists(f) for f in ("robots.txt", "sitemap.xml", "og-image.png", "favicon.png")),
    }
    print("\n갤러리 %s개  ->  index.html %s bytes" % (
        count if count else "?", format(os.path.getsize(OUT), ",")))
    print("검증  " + "  ".join("%s:%s" % (k, "OK" if v else "실패") for k, v in checks.items()))

    if all(checks.values()) and not b.failed:
        print("\n빌드 성공. 배포하려면:  ./deploy.sh")
    else:
        print("\n[!] 문제가 있습니다. 이 출력 전체를 Claude에게 보여주세요.")
        sys.exit(1)


if __name__ == "__main__":
    main()
