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
