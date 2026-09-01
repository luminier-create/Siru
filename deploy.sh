#!/usr/bin/env bash
#
# 시루 홈페이지 배포 — 빌드부터 푸시까지 한 번에
#
#   ./deploy.sh                          현재 src/siruhomepage.html 로 빌드 후 배포
#   ./deploy.sh ~/Downloads/새파일.html   새 원본을 등록하고 빌드 후 배포
#
# 푸시가 끝나면 GitHub Actions 가 Firebase Hosting 에 자동 배포합니다.
#
set -euo pipefail

cd "$(dirname "$0")"

echo "=============================================="
echo " 시루 홈페이지 배포"
echo "=============================================="
echo

# 1) 빌드 (새 원본 경로가 있으면 함께 전달)
if [ $# -ge 1 ]; then
  python3 build.py "$1"
else
  python3 build.py
fi

echo
echo "----------------------------------------------"

# 2) 변경사항 확인
if [ -z "$(git status --porcelain)" ]; then
  echo "변경된 내용이 없습니다. 이미 최신 상태입니다."
  exit 0
fi

echo "변경된 파일:"
git status --short
echo

# 3) 커밋
git add -A
MSG="${DEPLOY_MSG:-Update homepage}"
git commit -m "$MSG"

# 4) 푸시 (일시적 네트워크 오류는 재시도)
echo
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
for i in 1 2 3 4; do
  if git push -u origin "$BRANCH"; then
    echo
    echo "=============================================="
    echo " 배포 요청 완료"
    echo "=============================================="
    echo " 1~2분 뒤 아래 주소에 반영됩니다:"
    echo "   https://siru-4a476.web.app"
    echo
    echo " 진행 상황:"
    echo "   https://github.com/luminier-create/Siru/actions"
    exit 0
  fi
  echo "푸시 실패 — ${i}회차, 잠시 후 재시도합니다..."
  sleep $((2 ** i))
done

echo
echo "[!] 푸시에 실패했습니다. 위 오류 메시지를 Claude에게 보여주세요."
exit 1
