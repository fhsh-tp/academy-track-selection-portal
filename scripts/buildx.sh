#!/bin/bash

# ==========================================
# 用法: ./buildx.sh [OPTIONS] [TAG]
#
# Options:
#   -t, --target <target>  建構目標: app | nginx | all  (預設: all)
#   -h, --help             顯示此說明
#
# Tag 拆解規則 (SemVer):
#   1.0.1  →  latest, 1, 1.0, 1.0.1
#   0.1.0  →  latest, 0.1, 0.1.0
#   1.0.0  →  latest, 1
#   (省略) →  latest only
#
# 範例:
#   ./buildx.sh 1.0.1              # 建構 all，tag: latest, 1, 1.0, 1.0.1
#   ./buildx.sh -t app 0.1.0       # 只建構 app
#   ./buildx.sh --target nginx     # 只建構 nginx，tag: latest
# ==========================================

# ==========================================
# 變數設定 (請根據你的專案修改)
# ==========================================
APP_IMAGE="ghcr.io/fhsh-tp/atsp"
NGINX_IMAGE="ghcr.io/fhsh-tp/atsp-webserver"
PLATFORMS="linux/amd64,linux/arm64"
BUILDER_NAME="cross-platform-builder"

# ==========================================
# Help
# ==========================================
show_help() {
  cat <<EOF
用法: $(basename "$0") [OPTIONS] [TAG]

OPTIONS:
  -t, --target <target>  建構目標 (預設: all)
                           app    只建構後端 (Dockerfile)
                           nginx  只建構 nginx/frontend (nginx/Dockerfile)
                           all    兩個都建構
  -h, --help             顯示此說明

TAG (SemVer，選填):
  省略      → latest
  1.0.0     → latest, 1
  0.1.0     → latest, 0.1, 0.1.0
  1.0.1     → latest, 1, 1.0, 1.0.1
  v 開頭會自動去除 (e.g. v1.0.1 → 1.0.1)

範例:
  $(basename "$0") 1.0.1
  $(basename "$0") -t app 0.1.0
  $(basename "$0") --target nginx 1.0.0
EOF
}

# ==========================================
# 解析參數
# ==========================================
TARGET="all"
INPUT_TAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      show_help
      exit 0
      ;;
    -t|--target)
      if [[ -z "${2:-}" ]]; then
        echo "錯誤：--target 需要指定值 (app | nginx | all)" >&2
        exit 1
      fi
      TARGET="$2"
      shift 2
      ;;
    -*)
      echo "錯誤：未知選項 '$1'" >&2
      show_help >&2
      exit 1
      ;;
    *)
      INPUT_TAG="$1"
      shift
      ;;
  esac
done

if [[ "$TARGET" != "app" && "$TARGET" != "nginx" && "$TARGET" != "all" ]]; then
  echo "錯誤：--target 必須是 app、nginx 或 all，收到: '$TARGET'" >&2
  exit 1
fi

# ==========================================
# SemVer tag 拆解
# 規則：major(>0), major.minor, major.minor.patch
#       若 major == 0，跳過 major-only tag
#       若 minor == 0 且 patch == 0，只保留 major
# ==========================================
VERSION="${INPUT_TAG#v}"   # 移除開頭的 'v'（如 v1.0.0 → 1.0.0）

TAG_SUFFIXES=("latest")

if [[ "$VERSION" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
  MAJOR="${BASH_REMATCH[1]}"
  MINOR="${BASH_REMATCH[2]}"
  PATCH="${BASH_REMATCH[3]}"

  # major（僅當 major > 0）
  if [[ $MAJOR -gt 0 ]]; then
    TAG_SUFFIXES+=("${MAJOR}")
  fi

  # major.minor 與完整版號（當 minor > 0 或 patch > 0）
  if [[ $MINOR -gt 0 || $PATCH -gt 0 ]]; then
    TAG_SUFFIXES+=("${MAJOR}.${MINOR}")
    TAG_SUFFIXES+=("${MAJOR}.${MINOR}.${PATCH}")
  fi
elif [[ -n "$VERSION" && "$VERSION" != "latest" ]]; then
  # 非 SemVer 格式，直接使用原始 tag
  TAG_SUFFIXES+=("${VERSION}")
fi

# ==========================================
# 建構函式
# ==========================================
build_image() {
  local image_name="$1"
  local dockerfile="$2"
  local context="${3:-.}"

  local tag_flags=()
  local tags_display=()
  for suffix in "${TAG_SUFFIXES[@]}"; do
    tag_flags+=("--tag" "${image_name}:${suffix}")
    tags_display+=("${image_name}:${suffix}")
  done

  echo ""
  echo "📦 建構: $image_name"
  echo "🏷️  Tags: ${tags_display[*]}"

  docker buildx build \
    --platform "$PLATFORMS" \
    "${tag_flags[@]}" \
    --file "$dockerfile" \
    --push \
    "$context"

  if [[ $? -ne 0 ]]; then
    echo "❌ 建構失敗: $image_name"
    return 1
  fi
  echo "✅ 建構成功: $image_name"
}

# ==========================================
# 1. 初始化與環境準備
# ==========================================
echo "🚀 準備跨平台建構環境 (target: $TARGET)..."

# Linux 才需要手動設定 QEMU；macOS (OrbStack/Docker Desktop) 已內建
if [[ "$OSTYPE" == "linux"* ]]; then
  echo "🐳 設定 QEMU (multiarch/qemu-user-static)..."
  docker run --rm --privileged multiarch/qemu-user-static --reset -p yes > /dev/null 2>&1
fi

# ==========================================
# 2. 設定 Buildx Builder
# ==========================================
# containerd snapshotter 已啟用，docker driver 可直接支援 multi-platform + push
# 優先使用當前 Docker context 的 builder（OrbStack → orbstack，Docker Desktop → desktop-linux）
CURRENT_CONTEXT=$(docker context show 2>/dev/null || echo "default")
CONTEXT_BUILDER=$(docker buildx ls | awk -v ctx="$CURRENT_CONTEXT" '
  /^[^ ]/ && NR>1 { gsub(/\*/, "", $1); name=$1; driver=$2 }
  /^ / && driver=="docker" && $0 ~ ctx { print name; exit }
')

if [[ -n "$CONTEXT_BUILDER" ]]; then
  echo "✅ 使用 '$CONTEXT_BUILDER' builder (driver: docker, context: $CURRENT_CONTEXT)..."
  docker buildx use "$CONTEXT_BUILDER"
else
  # fallback：找任意 docker driver builder
  FALLBACK=$(docker buildx ls | awk '/^[^ ]/ && NR>1 { gsub(/\*/, "", $1); if ($2=="docker") {print $1; exit} }')
  if [[ -n "$FALLBACK" ]]; then
    echo "✅ 使用 '$FALLBACK' builder (driver: docker)..."
    docker buildx use "$FALLBACK"
  else
    echo "❌ 找不到可用的 docker driver builder"
    echo "   請確認 OrbStack/Docker Desktop 正在執行"
    exit 1
  fi
fi

echo "⚙️ 確認 builder 狀態..."
docker buildx inspect

# ==========================================
# 3. 執行建構與推送
# 請確保你已經執行過 docker login ghcr.io
# ==========================================
BUILD_FAILED=0

case "$TARGET" in
  app)
    build_image "$APP_IMAGE" "Dockerfile" "." || BUILD_FAILED=1
    ;;
  nginx)
    build_image "$NGINX_IMAGE" "nginx/Dockerfile" "." || BUILD_FAILED=1
    ;;
  all)
    build_image "$APP_IMAGE" "Dockerfile" "." || BUILD_FAILED=1
    build_image "$NGINX_IMAGE" "nginx/Dockerfile" "." || BUILD_FAILED=1
    ;;
esac

echo ""
if [[ $BUILD_FAILED -eq 0 ]]; then
  echo "🎉 所有映像檔建構並推送成功！"
else
  echo "❌ 部分或全部建構失敗，請檢查以上錯誤訊息。"
  exit 1
fi

# ==========================================
# 4. (選擇性) 清理環境
# ==========================================
# 如果你不想保留這個 builder，可以取消註解下一行
# docker buildx rm "$BUILDER_NAME"
