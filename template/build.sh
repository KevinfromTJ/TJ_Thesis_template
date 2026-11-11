#!/usr/bin/env bash
# 同济大学论文模板 — 本地编译脚本
#
# 用法:
#   ./build.sh                    # 仅编译正式版（默认）
#   ./build.sh all                # 正式版 + 隐名版
#   ./build.sh anonymous          # 仅隐名版
#   ./build.sh clean              # 清理编译产物
#   ./build.sh open [thesis|anonymous|all]
#   ./build.sh watch              # latexmk 持续编译（输出到 .output/）
#   ./build.sh latexmk            # 单次 latexmk（输出到 .output/，与 VSCode 一致）
#
# 环境变量（可在命令前 export，或写入 .env 后 source）:
#   BUILD_ANONYMOUS=1   与 all 等效，默认 0
#   VERBOSE=1           打印完整 xelatex/biber 日志，默认 0
#   OPEN_PDF=1          编译成功后自动打开 PDF（macOS: open）
#   LATEX_PASSES=3      xelatex 总次数（含首次），默认 3；快速草稿可设 1
#   SKIP_BIBER=1        跳过 biber（仅改正文、不动参考文献时可加速）
#
# 示例:
#   BUILD_ANONYMOUS=1 ./build.sh
#   VERBOSE=1 ./build.sh anonymous
#   LATEX_PASSES=1 SKIP_BIBER=1 ./build.sh

set -uo pipefail
cd "$(dirname "$0")"

# ── 默认配置 ──────────────────────────────────────────────
BUILD_ANONYMOUS="${BUILD_ANONYMOUS:-0}"
VERBOSE="${VERBOSE:-0}"
OPEN_PDF="${OPEN_PDF:-0}"
LATEX_PASSES="${LATEX_PASSES:-3}"
SKIP_BIBER="${SKIP_BIBER:-0}"

OUTPUT_DIR="output"
THESIS_JOB="thesis"
THESIS_ENTRY="thesis.tex"
ANON_JOB="thesis_anonymous"
ANON_ENTRY="thesis_anonymous.tex"

# ── 终端样式（非 TTY 时自动关闭颜色）────────────────────
if [[ -t 1 ]]; then
  C_RESET='\033[0m'
  C_DIM='\033[2m'
  C_BOLD='\033[1m'
  C_GREEN='\033[32m'
  C_YELLOW='\033[33m'
  C_RED='\033[31m'
  C_CYAN='\033[36m'
else
  C_RESET='' C_DIM='' C_BOLD='' C_GREEN='' C_YELLOW='' C_RED='' C_CYAN=''
fi

log_info()  { printf "${C_CYAN}▸${C_RESET} %s\n" "$*"; }
log_ok()    { printf "${C_GREEN}✓${C_RESET} %s\n" "$*"; }
log_warn()  { printf "${C_YELLOW}!${C_RESET} %s\n" "$*"; }
log_err()   { printf "${C_RED}✗${C_RESET} %s\n" "$*"; }

usage() {
  cat <<'EOF'
同济大学论文模板 — build.sh

命令:
  build              编译正式版（默认）
  all                正式版 + 隐名版
  anonymous          仅隐名版
  clean              清理 output/ 与根目录临时文件
  open [target]      打开 PDF（target: thesis | anonymous | all，默认 thesis）
  watch              latexmk -pvc（.output/，与 VSCode 配置一致）
  latexmk            latexmk 单次完整编译（.output/）
  help               显示本帮助

选项（可写在命令前，如 VERBOSE=1 ./build.sh all）:
  BUILD_ANONYMOUS=1  编译时包含隐名版
  VERBOSE=1          显示完整 LaTeX 日志
  OPEN_PDF=1         成功后打开 PDF
  LATEX_PASSES=N     xelatex 运行次数（默认 3）
  SKIP_BIBER=1       跳过参考文献处理

标志:
  -a, --anonymous    等同 BUILD_ANONYMOUS=1
  -v, --verbose      等同 VERBOSE=1
  -o, --open         等同 OPEN_PDF=1
  -h, --help         显示帮助

输出:
  正式版   output/thesis/thesis.pdf
  隐名版   output/thesis_anonymous/thesis_anonymous.pdf
  详细日志 output/<job>/<job>.build.log（非 VERBOSE 模式）
EOF
}

parse_flags() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -a|--anonymous) BUILD_ANONYMOUS=1 ;;
      -v|--verbose)   VERBOSE=1 ;;
      -o|--open)      OPEN_PDF=1 ;;
      -h|--help)      usage; exit 0 ;;
      --) shift; break ;;
      -*) log_err "未知选项: $1"; usage; exit 1 ;;
      *)  break ;;
    esac
    shift
  done
  REMAINING_ARGS=("$@")
}

# 从 .log 提取错误摘要
show_log_errors() {
  local log="$1"
  [[ -f "$log" ]] || return 0
  local lines
  lines=$(grep -E '^(! |l\.[0-9]+ |Emergency stop|Fatal error)' "$log" 2>/dev/null | tail -20 || true)
  if [[ -n "$lines" ]]; then
    log_err "日志中的错误摘要 (${log}):"
    printf '%s\n' "$lines" | sed "s/^/    /"
  fi
}

has_log_errors() {
  local log="$1"
  [[ -f "$log" ]] || return 1
  grep -qE '^! |Emergency stop|Fatal error' "$log" 2>/dev/null
}

run_step() {
  local label="$1"
  shift
  if [[ "$VERBOSE" == "1" ]]; then
    log_info "$label"
    "$@"
    return $?
  fi
  printf "  ${C_DIM}→${C_RESET} %-28s " "$label"
  if "$@" >>"$BUILD_LOG" 2>&1; then
    printf "${C_GREEN}ok${C_RESET}\n"
    return 0
  else
    printf "${C_RED}warn${C_RESET} (退出码 $?，见 build.log)\n"
    return 0  # xelatex 常因警告非零退出，不中断后续 pass
  fi
}

build_thesis() {
  local jobname="$1"
  local entry="$2"
  local out="${OUTPUT_DIR}/${jobname}"
  local pdf="${out}/${jobname}.pdf"
  local log="${out}/${jobname}.log"
  BUILD_LOG="${out}/${jobname}.build.log"

  : >"$BUILD_LOG"
  local t0=$SECONDS

  printf "\n${C_BOLD}编译 ${entry}${C_RESET} ${C_DIM}→${C_RESET} ${pdf}\n"
  mkdir -p "$out"

  local passes="${LATEX_PASSES}"
  if [[ "$passes" -lt 1 ]]; then passes=1; fi

  run_step "xelatex (1/${passes})" \
    xelatex -interaction=nonstopmode -file-line-error \
      -output-directory="$out" "$entry"

  if [[ "$SKIP_BIBER" != "1" ]]; then
    run_step "biber" biber "${out}/${jobname}"
  else
    log_warn "已跳过 biber（SKIP_BIBER=1）"
  fi

  local i
  for ((i = 2; i <= passes; i++)); do
    run_step "xelatex (${i}/${passes})" \
      xelatex -interaction=nonstopmode -file-line-error \
        -output-directory="$out" "$entry"
  done

  local elapsed=$((SECONDS - t0))
  local status=0

  if [[ ! -f "$pdf" ]]; then
    log_err "未生成 PDF: ${pdf}"
    status=1
  elif has_log_errors "$log"; then
    log_warn "PDF 已生成，但日志含错误（${elapsed}s）"
    show_log_errors "$log"
    status=1
  else
    local size
    size=$(du -h "$pdf" 2>/dev/null | cut -f1 || echo "?")
    log_ok "完成 ${pdf} (${size}, ${elapsed}s)"
  fi

  if [[ "$VERBOSE" != "1" && -f "$BUILD_LOG" ]]; then
    printf "  ${C_DIM}详细输出: ${BUILD_LOG}${C_RESET}\n"
  fi

  return $status
}

do_build() {
  local mode="${1:-thesis}"
  local failed=0

  case "$mode" in
    thesis)
      build_thesis "$THESIS_JOB" "$THESIS_ENTRY" || failed=1
      ;;
    anonymous)
      build_thesis "$ANON_JOB" "$ANON_ENTRY" || failed=1
      ;;
    all)
      build_thesis "$THESIS_JOB" "$THESIS_ENTRY" || failed=1
      build_thesis "$ANON_JOB" "$ANON_ENTRY" || failed=1
      ;;
    *)
      log_err "未知编译目标: $mode"
      exit 1
      ;;
  esac

  if [[ "$failed" -eq 0 && "$OPEN_PDF" == "1" ]]; then
    case "$mode" in
      thesis)    open_pdf thesis ;;
      anonymous) open_pdf anonymous ;;
      all)       open_pdf all ;;
    esac
  fi

  return $failed
}

open_pdf() {
  local target="${1:-thesis}"
  case "$target" in
    thesis)
      open "${OUTPUT_DIR}/${THESIS_JOB}/${THESIS_JOB}.pdf" 2>/dev/null \
        || xdg-open "${OUTPUT_DIR}/${THESIS_JOB}/${THESIS_JOB}.pdf" 2>/dev/null \
        || log_warn "请手动打开 ${OUTPUT_DIR}/${THESIS_JOB}/${THESIS_JOB}.pdf"
      ;;
    anonymous)
      open "${OUTPUT_DIR}/${ANON_JOB}/${ANON_JOB}.pdf" 2>/dev/null \
        || xdg-open "${OUTPUT_DIR}/${ANON_JOB}/${ANON_JOB}.pdf" 2>/dev/null \
        || log_warn "请手动打开 ${OUTPUT_DIR}/${ANON_JOB}/${ANON_JOB}.pdf"
      ;;
    all)
      open_pdf thesis
      open_pdf anonymous
      ;;
    *)
      log_err "open 目标应为 thesis | anonymous | all"
      exit 1
      ;;
  esac
}

do_clean() {
  log_info "清理 ${OUTPUT_DIR}/ 与根目录 LaTeX 临时文件 …"
  rm -rf "${OUTPUT_DIR:?}/${THESIS_JOB:?}"/* "${OUTPUT_DIR}/${ANON_JOB}"/* 2>/dev/null || true
  rm -rf .output/* 2>/dev/null || true
  latexmk -norc -c -outdir=.output "$THESIS_ENTRY" 2>/dev/null || true

  local patterns=(
    '*.aux' '*.bbl' '*.bcf' '*.blg' '*.fdb_latexmk' '*.fls'
    '*.loa' '*.loe' '*.lof' '*.log' '*.lot' '*.out' '*.run.xml'
    '*.synctex.gz' '*.toc' '*.xdv'
  )
  local f
  for f in "${patterns[@]}"; do
    rm -f $f 2>/dev/null || true
  done
  rm -f thesis.log thesis.pdf 2>/dev/null || true
  log_ok "清理完成"
}

do_latexmk() {
  local extra=()
  [[ "$VERBOSE" == "1" ]] && extra+=(-interaction=nonstopmode) || extra+=(-silent)
  log_info "latexmk → .output/（与 VSCode latex-workshop 一致）"
  mkdir -p .output
  latexmk -norc -xelatex -bibtex -bibfudge \
    -latex='xelatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S' \
    -outdir=.output "${extra[@]}" "$THESIS_ENTRY"
}

do_watch() {
  log_info "latexmk -pvc → .output/（Ctrl+C 退出）"
  mkdir -p .output
  latexmk -norc -pvc -xelatex -bibtex -bibfudge \
    -latex='xelatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S' \
    -outdir=.output "$THESIS_ENTRY"
}

# ── 入口 ──────────────────────────────────────────────────
main() {
  parse_flags "$@"
  set -- "${REMAINING_ARGS[@]:-}"

  local cmd="${1:-build}"
  [[ $# -gt 0 ]] && shift

  local build_mode="thesis"
  case "$cmd" in
    build|"")
      if [[ "$BUILD_ANONYMOUS" == "1" ]]; then
        build_mode="all"
      else
        build_mode="thesis"
      fi
      ;;
    all)        build_mode="all" ;;
    anonymous)  build_mode="anonymous" ;;
    clean)      do_clean; exit 0 ;;
    open)       open_pdf "${1:-thesis}"; exit 0 ;;
    watch)      do_watch; exit 0 ;;
    latexmk|mk) do_latexmk; exit $? ;;
    help|-h|--help) usage; exit 0 ;;
    *)
      log_err "未知命令: $cmd"
      usage
      exit 1
      ;;
  esac

  log_info "开始编译（模式: ${build_mode}）"
  do_build "$build_mode"
}

main "$@"
