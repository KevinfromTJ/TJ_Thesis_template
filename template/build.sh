#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
case "${1:-build}" in
  build) latexmk thesis.tex ;;
  anonymous) latexmk thesis_anonymous.tex ;;
  all) latexmk thesis.tex; latexmk thesis_anonymous.tex ;;
  spine) latexmk spine.tex ;;
  watch) latexmk -pvc thesis.tex ;;
  clean) latexmk -c thesis.tex thesis_anonymous.tex ;;
  help|-h|--help) printf '%s\n' './build.sh [build|anonymous|all|spine|watch|clean]' 'PDF 输出到 output/；clean 保留 PDF。' ;;
  *) printf '未知目标：%s\n' "$1" >&2; exit 2 ;;
esac
