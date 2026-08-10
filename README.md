# 시루 SIRU — 루루 작가 캐릭터 팬페이지

루루 작가의 캐릭터 "시루(SIRU)" 팬페이지입니다. 이미지가 모두 파일 안에 포함된 단일 HTML(`index.html`)로 되어 있어 별도 서버 없이 정적 호스팅만으로 바로 볼 수 있습니다.

## 온라인으로 보기 (GitHub Pages)

이 저장소는 GitHub Pages로 배포되도록 설정되어 있습니다.

- 배포 워크플로: [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml)
- 배포 후 접속 주소: **https://luminier-create.github.io/Siru/**

### 배포가 자동으로 안 될 경우 (최초 1회 설정)

GitHub Actions로 Pages를 자동 활성화하도록 되어 있지만, 조직/계정 정책에 따라 수동 활성화가 필요할 수 있습니다.

1. GitHub 저장소 → **Settings** → **Pages**
2. **Build and deployment** → **Source** 를 **GitHub Actions** 로 선택
3. 저장 후 Actions 탭에서 "Deploy to GitHub Pages" 워크플로가 성공하면 위 주소로 접속

## 로컬에서 미리 보기

별도 빌드 과정 없이 브라우저로 파일을 바로 열면 됩니다.

```bash
# 파일 직접 열기
open index.html            # macOS
xdg-open index.html        # Linux

# 또는 간단한 로컬 서버로 확인
python3 -m http.server 8000
# 브라우저에서 http://localhost:8000 접속
```
