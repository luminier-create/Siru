# 시루 SIRU — 루루 작가 캐릭터 팬페이지

루루 작가의 캐릭터 "시루(SIRU)" 팬페이지입니다. 이미지가 모두 파일 안에 포함된 단일 HTML(`index.html`)로, 별도 서버·빌드 과정 없이 정적 호스팅으로 바로 볼 수 있으며 **모바일에 최적화**되어 있습니다.

## Firebase Hosting으로 온라인 배포하기

이 저장소는 Firebase Hosting 설정(`firebase.json`)이 되어 있습니다. 아래 순서대로 하면 됩니다.
(Firebase는 Google 계정 로그인이 필요해 배포 실행은 본인 PC에서 진행합니다.)

### 1. Firebase CLI 설치

```bash
npm install -g firebase-tools
```

### 2. Google 계정 로그인

```bash
firebase login
```

### 3. Firebase 프로젝트 만들기 (아직 없다면)

브라우저에서 <https://console.firebase.google.com> 접속 → **프로젝트 추가** → 이름 입력(예: `siru-homepage`) → 생성.
또는 CLI로 바로 생성:

```bash
firebase projects:create siru-homepage --display-name "SIRU"
```

> 생성된 **프로젝트 ID**(예: `siru-homepage` 또는 `siru-homepage-1a2b3`)를 확인해 두세요.

### 4. 이 저장소에 프로젝트 연결

저장소 폴더에서 아래를 실행하면 `.firebaserc` 가 자동으로 채워집니다.
(`YOUR_PROJECT_ID` 를 3단계에서 만든 실제 ID로 바꿔주세요.)

```bash
firebase use --add
# 목록에서 프로젝트 선택, 별칭(alias)은 default 로 지정
# 또는 한 줄로:
firebase use YOUR_PROJECT_ID
```

### 5. 배포

```bash
firebase deploy --only hosting
```

배포가 끝나면 아래 형식의 주소가 출력됩니다. 이 주소로 어디서든(모바일 포함) 접속할 수 있습니다.

```
https://YOUR_PROJECT_ID.web.app
https://YOUR_PROJECT_ID.firebaseapp.com
```

> 이후 내용을 수정하면 `firebase deploy --only hosting` 만 다시 실행하면 갱신됩니다.

## 홈페이지 전체 내용을 담은 단일 HTML 뽑기

`index.html` 하나에 이미 **모든 내용이 들어 있습니다.** 표정 이미지 53종을 포함한 그림 57장이 전부
base64로 파일 안에 박혀 있고, CSS와 JavaScript도 인라인이라 외부에서 불러오는 파일이 없습니다.
즉, 이 파일 하나만 복사해 가면 인터넷이 끊긴 상태에서도 홈페이지 전체가 그대로 보입니다.

### 방법 1 — 저장소 파일을 그대로 쓰기 (가장 간단)

```bash
git clone https://github.com/luminier-create/Siru.git
# Siru/index.html 을 원하는 곳으로 복사해서 더블클릭하면 끝
```

브라우저에서 <https://github.com/luminier-create/Siru/raw/main/index.html> 를 열어
**다른 이름으로 저장**해도 동일한 파일을 받을 수 있습니다.

### 방법 2 — 배포된 사이트에서 내려받기

```bash
curl -L https://siru-4a476.web.app/ -o siru.html
```

브라우저에서는 페이지를 열고 `Ctrl+S`(macOS는 `Cmd+S`) → **웹 페이지, HTML만** 으로 저장하면 됩니다.
이미지가 파일 안에 들어 있으므로 "전체 저장"을 고를 필요가 없습니다.

### 방법 3 — 100% 독립 파일로 내보내기 (권장)

`index.html` 은 파비콘(`/favicon.png`)만 바깥 파일을 참조합니다. 아래 스크립트를 쓰면 그것까지
파일 안에 넣어 **참조가 하나도 남지 않은 단일 HTML** 을 만듭니다.

```bash
python3 tools/export-standalone.py
# → dist/siru-standalone.html (약 1.9MB)

# 경로를 직접 지정할 수도 있습니다
python3 tools/export-standalone.py ~/Desktop/시루.html
```

실행하면 인라인 처리한 파일과 남은 외부 참조를 함께 출력하므로, 결과가
`남은 로컬 참조: 없음 (완전 독립 파일)` 이면 그 파일만 메일·USB·카톡으로 보내도 그대로 열립니다.

> 참고: `og:image`(SNS 미리보기용)와 `canonical` 주소는 절대 URL이라 그대로 둡니다.
> 오프라인에서 페이지를 보는 데는 영향이 없고, 링크 공유 시 미리보기가 정상 동작하려면 필요합니다.

## 모바일 최적화 포함 사항

- `viewport-fit=cover` + safe-area 대응(노치/홈 인디케이터 영역 여백 처리)
- iOS 자동 글자 크기 변경 방지, 탭 하이라이트 제거, 터치 지연 최소화
- 상단 내비게이션을 모바일에서 숨기지 않고 **가로 스크롤 바**로 유지 (이동 가능)
- 모바일 화면에서 히어로/블롭/섹션 여백 축소, CTA 버튼 풀폭(full-width)
- 좁은 화면(≤420px)에서 갤러리 2열 고정, 스펙 2열 등 소형 폰 튜닝
- `theme-color` 지정으로 모바일 브라우저 상단 바 색상 일치

## 로컬에서 미리 보기

```bash
# 파일 직접 열기
open index.html            # macOS
xdg-open index.html        # Linux

# 또는 로컬 서버
python3 -m http.server 8000     # http://localhost:8000
# Firebase 미리보기 서버(설치 후)
firebase serve --only hosting   # http://localhost:5000
```
