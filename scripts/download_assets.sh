#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TAG="${RELEASE_TAG:-paper1-qrtchr-sanitized-20261013-v1}"
DEST="${ASSET_DIR:-$ROOT/frozen_assets_download}"
ARCHIVE="paper1-qrtchr-sanitized-20261013-v1.tar.zst"
mkdir -p "$DEST"
if [[ -z "${REPO:-}" ]]; then
  echo "ERROR: set REPO=owner/QRTC-HR-Paper1"
  exit 2
fi
command -v gh >/dev/null
gh release download "$TAG" --repo "$REPO" --dir "$DEST" --pattern "${ARCHIVE}*"
cd "$DEST"
sha256sum -c CHECKSUMS.sha256
mkdir -p "$ROOT/frozen_assets"
tar --use-compress-program=zstd -xf "$ARCHIVE" -C "$ROOT/frozen_assets"
echo "OK: $ROOT/frozen_assets"
