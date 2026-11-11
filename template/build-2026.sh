#!/usr/bin/env bash
# Use the independently installed TeX Live without changing the user's shell.
set -euo pipefail
cd "$(dirname "$0")"
tex_bin="${TONGJI_TEX_BIN:-/data1_temp/chenjuntao/texlive/2026/bin/x86_64-linux}"
for tool in xelatex latexmk biber; do
  [[ -x "$tex_bin/$tool" ]] || { printf '未找到编译工具：%s/%s\n' "$tex_bin" "$tool" >&2; exit 1; }
done
export PATH="$tex_bin:$PATH"
case "${1:-build}" in
  build) exec latexmk -outdir=output/texlive2026 thesis.tex ;;
  anonymous) exec latexmk -outdir=output/texlive2026 thesis_anonymous.tex ;;
  spine) exec latexmk -outdir=output/texlive2026 spine.tex ;;
  test) exec latexmk -outdir=output/texlive2026/tests tests/layout.tex ;;
  all) latexmk -outdir=output/texlive2026 thesis.tex thesis_anonymous.tex spine.tex ;;
  *) printf '用法：%s [build|anonymous|spine|test|all]\n' "$0" >&2; exit 2 ;;
esac
