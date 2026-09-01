# 시루 SIRU — 루루 작가 캐릭터 팬페이지

<https://siru-4a476.web.app>

이미지가 모두 파일 안에 포함된 단일 HTML(`index.html`)입니다. 별도 서버·빌드 과정 없이 정적 호스팅으로 동작하며, 모바일 최적화·문의 이메일·SEO가 적용되어 있습니다.

---

## 새 버전 올리기

브랜치에 푸시하면 **GitHub Actions가 Firebase Hosting에 자동 배포**합니다.
새로 뽑은 홈페이지 HTML이 있다면, 터미널에서 한 줄이면 됩니다.

```bash
cd ~/Siru && ./deploy.sh ~/Downloads/siruhomepage.html
```

이 한 줄이 다음을 처리합니다.

1. 새 HTML을 원본(`src/siruhomepage.html`)으로 등록
2. **모바일 최적화 · 문의 이메일 · SEO** 를 자동으로 다시 적용
3. `robots.txt` · `sitemap.xml` · `og-image.png` · `favicon.png` 재생성
4. 커밋 + 푸시 → 1~2분 뒤 사이트에 반영

> **핵심:** 새로 뽑은 HTML에는 모바일·이메일·SEO가 없어도 됩니다.
> 원본은 `src/` 에 그대로 두고 개선사항은 빌드할 때마다 다시 입히므로,
> 새 버전을 올려도 그동안의 작업이 사라지지 않습니다.

### 배포 없이 결과만 확인

```bash
python3 build.py ~/Downloads/siruhomepage.html   # index.html 생성
open index.html                                   # 브라우저 확인
./deploy.sh                                       # 확인 후 배포
```

### 커밋 메시지 지정

```bash
DEPLOY_MSG="갤러리 60종으로 확대" ./deploy.sh ~/Downloads/siruhomepage.html
```

---

## 폴더 구조

| 경로 | 설명 |
|---|---|
| `src/siruhomepage.html` | **원본.** 새 버전을 넣는 유일한 파일 |
| `build.py` | 원본 → 배포본 변환 (모바일·이메일·SEO 적용) |
| `deploy.sh` | 빌드 + 커밋 + 푸시 |
| `index.html` | **자동 생성물.** 직접 수정하지 마세요 |
| `robots.txt`, `sitemap.xml`, `og-image.png`, `favicon.png` | 자동 생성물 |
| `firebase.json`, `.firebaserc` | Firebase Hosting 설정 (프로젝트 `siru-4a476`) |
| `.github/workflows/` | 푸시 시 자동 배포 |

---

## 빌드가 자동으로 입히는 것

**모바일 최적화**
- `viewport-fit=cover` + safe-area — 노치/홈 인디케이터 영역 대응
- iOS 글자 크기 자동확대 방지, 탭 하이라이트 제거, 터치 반응 개선
- 상단 메뉴를 모바일에서 숨기지 않고 **가로 스크롤**로 유지
- 모바일 여백 축소, CTA 버튼 풀폭, 좁은 화면(≤420px) 갤러리 2열
- `theme-color` 로 브라우저 상단바 색상 통일

**문의 이메일**
- "이메일 보내기" → 제목·본문이 미리 채워진 메일 작성 화면
- 메일 앱이 없는 기기를 위해 **주소 표시 + 복사 버튼**

**SEO**
- 검색 메타(description/keywords/robots) + canonical
- Open Graph · 트위터 카드 → 카카오톡·SNS 공유 시 썸네일 미리보기
- JSON-LD 구조화 데이터 (WebSite / Person / CreativeWork)
- 갤러리 개수를 **원본에서 자동으로 세어** 문구에 반영
- `robots.txt` + `sitemap.xml`, 파비콘·홈화면 아이콘

---

## 문제가 생기면

`build.py` 는 원본 구조가 바뀌어 적용에 실패하면 조용히 넘어가지 않고 명확히 알려줍니다:

```
[!] 적용 실패 — 원본 구조가 바뀐 것 같습니다:
  ! 이메일 주소 + 복사 버튼
```

이 출력을 그대로 Claude에게 보여주면 원본 구조에 맞춰 `build.py` 를 고칠 수 있습니다.
여러 번 실행해도 안전합니다 — 이미 적용된 항목은 건너뜁니다.

---

## 로컬 미리보기

```bash
open index.html                  # 파일 직접 열기
python3 -m http.server 8000      # http://localhost:8000
```

## 수동 배포 (자동 배포가 안 될 때)

```bash
npx firebase-tools deploy --only hosting --account luminier@gmail.com
```
