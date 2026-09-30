# 시루 SIRU — 루루 작가 캐릭터 팬페이지

<https://siru-4a476.web.app>

---

## 새 버전 올리기

새로 뽑은 홈페이지 HTML 파일 하나면 됩니다. 터미널에서 한 줄:

```bash
cd ~/Siru && ./deploy.sh ~/Downloads/siruhomepage.html
```

이 한 줄이 원본 등록 → 새 디자인으로 빌드 → 커밋·푸시까지 하고,
GitHub Actions 가 1~2분 뒤 Firebase Hosting 에 배포합니다.

> **디자인은 새 HTML 과 분리되어 있습니다.**
> 원본에서는 글과 그림(캐릭터 소개, 표정 목록, 작가 소개, 문의 이메일 등)만 가져오고,
> 화면 디자인은 `site/` 의 템플릿이 담당합니다. 그래서 새 버전을 넣어도 디자인이 유지됩니다.

배포 없이 결과만 보려면:

```bash
python3 build.py ~/Downloads/siruhomepage.html   # index.html 생성
python3 -m http.server 8000                       # http://localhost:8000 에서 확인
./deploy.sh                                       # 확인 후 배포
```

---

## 폴더 구조

| 경로 | 설명 |
|---|---|
| `src/siruhomepage.html` | **원본.** 새 버전을 넣는 유일한 파일 |
| `site/template.html` | 페이지 뼈대 (새 디자인) |
| `site/styles.css` | 디자인 시스템 — 색, 글꼴, 모션 |
| `site/app.js` | 인터랙션 |
| `site/config.json` | **디자인 문구** — 말풍선 대사, 채팅 데모 대본, 신분증 문구, 메일 제목 등 |
| `site/extract.py` | 원본에서 글·그림을 뽑는 부분 |
| `site/sw.js` | 오프라인 지원 서비스 워커 원본 |
| `build.py` | 원본 → 배포본 빌드 (표준 라이브러리만 사용, 추가 설치 불필요) |
| `deploy.sh` | 빌드 + 커밋 + 푸시 |
| `tools/make_assets.py` | 공유 썸네일·앱 아이콘 생성 (그림이 크게 바뀔 때만, Pillow 필요) |
| `index.html`, `assets/img/`, `sw.js`, `manifest.webmanifest`, `sitemap.xml`, `robots.txt` | **자동 생성물.** 직접 고치지 마세요 |
| `assets/fonts/pretendard/` | 셀프 호스팅 Pretendard 폰트 (SIL OFL) |
| `og-image.png`, `icons/`, `favicon.ico` | 공유 썸네일·아이콘 |

### 자주 하는 수정

- **말풍선 대사, 채팅 데모 대본, 신분증 문구** → `site/config.json` 수정 후 `./deploy.sh`
- **색·여백·모션** → `site/styles.css` 수정 후 `./deploy.sh`
- **대표 그림이 바뀌어 공유 썸네일도 바꾸고 싶을 때** → `pip3 install pillow` 후 `python3 tools/make_assets.py`

---

## 디자인 · 기술 요약

**콘셉트 "쫀득"** — 떡의 물성(눌리면 찌그러졌다 튕기는 스프링 모션)과 손그림 노트 질감(두들 밑줄·스티커·마스킹테이프). 팥색을 브랜드 액센트로 사용.

**인터랙션**
- 떡 위의 시루를 누르면 스퀴시 모션 + 팥알 파티클 + 말풍선 (7번째엔 비밀 대사)
- 채팅 데모: 대화 속에서 이모티콘이 어떻게 쓰이는지 자동 재생
- 반려견 등록증 ↔ 정체 확인서 3D 뒤집기
- 갤러리: 감정 필터·검색 (View Transitions 로 부드럽게 재배치), 오늘의 표정 뽑기
- 전체 화면 뷰어: 좌우 스와이프, 아래로 내려 닫기, 이미지 파일 그대로 공유(Web Share), 저장, 표정별 공유 링크 (`#e=꿀잠`)
- 원형으로 번지는 다크 모드 전환 — 다크에서도 그림은 밝은 스티커 위에 유지

**성능 · 모바일**
- 페이지 1.9MB → 약 140KB. 그림은 파일로 분리해 보일 때만 로드, 내용 해시 이름으로 장기 캐시
- Pretendard 가변 폰트를 필요한 글자 묶음만 받도록 셀프 호스팅
- 모바일 하단 탭 바, 노치 안전영역, 스크롤 시 숨는 상단 바
- 앱처럼 설치 가능(PWA) + 오프라인에서도 열림

**검색 · 공유**
- 메타·Open Graph·트위터 카드, 1200×630 공유 썸네일
- JSON-LD 구조화 데이터 (웹사이트·작가·캐릭터·표정 갤러리 53종 각각)
- 이미지 사이트맵 — 표정 그림 하나하나가 이미지 검색에 노출되도록

**접근성**
- 모든 그림 대체 텍스트, 키보드 조작, 포커스 표시, 동작 줄이기 설정 존중
- JavaScript 가 꺼져 있어도 모든 내용과 그림이 보임

---

## 문제가 생기면

`build.py` 는 원본 구조가 바뀌어 필요한 내용을 못 찾으면 조용히 넘어가지 않고 알려줍니다:

```
[!] 원본에서 필요한 내용을 찾지 못했습니다: 섹션 #gallery
```

이 메시지를 Claude 에게 보여주면 `site/extract.py` 를 원본 구조에 맞게 고칠 수 있습니다.

수동 배포 (자동 배포가 안 될 때):

```bash
npx firebase-tools deploy --only hosting --account luminier@gmail.com
```
