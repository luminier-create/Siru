# 시루 SIRU — 루루 작가 캐릭터 팬페이지

루루 작가의 캐릭터 "시루(SIRU)" 팬페이지입니다. 이미지가 모두 파일 안에 포함된 단일 HTML(`index.html`)로 되어 있어 별도 서버나 빌드 과정 없이 정적 호스팅만으로 바로 볼 수 있습니다.

## 온라인으로 보기 (GitHub Pages)

`index.html` 이 저장소 루트에 있어 GitHub Pages로 바로 배포할 수 있습니다.
**최초 1회만** 아래 설정을 해주면 이후에는 자동으로 갱신됩니다. (이 설정은 저장소 소유자만 할 수 있어 코드로 대신 처리할 수 없습니다.)

1. GitHub 저장소 → **Settings** → 왼쪽 메뉴 **Pages**
2. **Build and deployment** → **Source** 를 **Deploy from a branch** 로 선택
3. **Branch** 를 `claude/homepage-online-deployment-2m18ec`, 폴더는 **`/ (root)`** 로 선택 후 **Save**
   - (이 브랜치가 병합되면 `main` 브랜치로 바꿔주세요.)
4. 1~2분 뒤 아래 주소로 접속하면 페이지가 보입니다.

### 접속 주소

```
https://luminier-create.github.io/Siru/
```

## 로컬에서 미리 보기

별도 빌드 없이 브라우저로 파일을 바로 열면 됩니다.

```bash
# 파일 직접 열기
open index.html            # macOS
xdg-open index.html        # Linux

# 또는 간단한 로컬 서버로 확인
python3 -m http.server 8000
# 브라우저에서 http://localhost:8000 접속
```
