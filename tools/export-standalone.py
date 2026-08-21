#!/usr/bin/env python3
"""index.html + 외부 리소스를 하나로 합쳐 완전 독립 HTML을 만든다.

사용법:
    python3 tools/export-standalone.py [출력경로]
기본 출력: dist/siru-standalone.html
"""
import base64
import mimetypes
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def inline_local_assets(html: str) -> tuple[str, list[str]]:
    """src/href 가 가리키는 저장소 내 파일을 data URI 로 치환한다."""
    inlined: list[str] = []

    def repl(m: re.Match) -> str:
        attr, quote, ref = m.group(1), m.group(2), m.group(3)
        if ref.startswith(("data:", "#", "mailto:", "tel:", "http://", "https://", "//")):
            return m.group(0)
        asset = ROOT / ref.lstrip("/")
        if not asset.is_file():
            return m.group(0)
        inlined.append(ref)
        return f"{attr}={quote}{data_uri(asset)}{quote}"

    pattern = re.compile(r'\b(src|href)=(["\'])([^"\']+)\2')
    return pattern.sub(repl, html), inlined


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "siru-standalone.html"
    html = SRC.read_text(encoding="utf-8")
    html, inlined = inline_local_assets(html)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    # 남은 외부 참조 확인 (og:image 등 절대 URL은 SNS 미리보기용이라 그대로 둔다)
    leftovers = sorted(
        set(
            ref
            for ref in re.findall(r'\b(?:src|href)=["\']([^"\']+)["\']', html)
            if not ref.startswith(("data:", "#", "mailto:", "tel:", "http"))
        )
    )

    size_mb = out.stat().st_size / 1024 / 1024
    print(f"생성: {out}  ({size_mb:.2f} MB)")
    print(f"인라인 처리한 로컬 파일: {', '.join(inlined) if inlined else '없음'}")
    print(f"남은 로컬 참조: {', '.join(leftovers) if leftovers else '없음 (완전 독립 파일)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
