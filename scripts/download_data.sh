#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$ROOT/data"
mkdir -p "$DATA" "$DATA/repo_zips" "$DATA/acl_zips"

download_zip_repo() {
  local name="$1"
  local url="$2"
  local zip="$DATA/repo_zips/${name}.zip"
  if [ -d "$DATA/$name" ] && find "$DATA/$name" -type f | grep -q .; then
    echo "[ok] $name already exists"
    return
  fi
  echo "[download] $name"
  curl -L --max-time 180 --retry 3 --fail --show-error "$url" -o "$zip"
  rm -rf "$DATA/$name" "$DATA/${name}-main" "$DATA/${name}-master"
  (cd "$DATA" && unzip -q "$zip")
  local extracted
  extracted="$(find "$DATA" -maxdepth 1 -type d \( -name '*-main' -o -name '*-master' \) | head -1)"
  if [ -n "$extracted" ]; then
    mv "$extracted" "$DATA/$name"
  fi
}

download_zip_repo "MuSR" "https://github.com/Zayne-sprague/MuSR/archive/refs/heads/main.zip"
download_zip_repo "DetectiveQA" "https://github.com/Phospheneser/DetectiveQA/archive/refs/heads/main.zip"
download_zip_repo "TurnaboutLLM" "https://github.com/zharry29/turnabout_llm/archive/refs/heads/main.zip"
download_zip_repo "DetectBench" "https://github.com/MikeGu721/DetectBench/archive/refs/heads/main.zip"
download_zip_repo "llm-mysteries" "https://github.com/metareflection/llm-mysteries/archive/refs/heads/main.zip"

if [ ! -s "$DATA/acl_zips/2024.findings-emnlp.11.data.zip" ]; then
  echo "[download] DetectBench ACL data zip"
  curl -L --max-time 180 --retry 3 --fail --show-error \
    "https://aclanthology.org/2024.findings-emnlp.11.data.zip" \
    -o "$DATA/acl_zips/2024.findings-emnlp.11.data.zip"
fi

echo "[done] data download attempts complete"
