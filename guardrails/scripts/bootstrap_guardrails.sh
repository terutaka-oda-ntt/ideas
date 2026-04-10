#!/usr/bin/env bash
# Bootstrap guardrails files into an existing repository.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./guardrails/scripts/bootstrap_guardrails.sh --template-dir <path> [--target-dir <path>] [--with-docs] [--force] [--dry-run]

Options:
  --template-dir <path>  Path to the template repository (required)
  --target-dir <path>    Path to target repository (default: current directory)
  --with-docs            Also copy guardrails/docs into target
  --force                Overwrite existing files
  --dry-run              Print planned actions without modifying files
  -h, --help             Show this help

Examples:
  ./guardrails/scripts/bootstrap_guardrails.sh --template-dir /path/to/ideas --target-dir .
  ./guardrails/scripts/bootstrap_guardrails.sh --template-dir /path/to/ideas --target-dir . --with-docs --force
  ./guardrails/scripts/bootstrap_guardrails.sh --template-dir /path/to/ideas --target-dir . --dry-run
EOF
}

TEMPLATE_DIR=""
TARGET_DIR="$(pwd)"
WITH_DOCS=0
FORCE=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --template-dir)
      TEMPLATE_DIR="${2:-}"
      shift 2
      ;;
    --target-dir)
      TARGET_DIR="${2:-}"
      shift 2
      ;;
    --with-docs)
      WITH_DOCS=1
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

run_cmd() {
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "Dry-run: $*"
  else
    "$@"
  fi
}

if [[ -z "$TEMPLATE_DIR" ]]; then
  echo "--template-dir is required." >&2
  usage
  exit 1
fi

if [[ ! -d "$TEMPLATE_DIR" ]]; then
  echo "Template directory not found: $TEMPLATE_DIR" >&2
  exit 1
fi

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Target directory not found: $TARGET_DIR" >&2
  exit 1
fi

TEMPLATE_DIR="$(cd "$TEMPLATE_DIR" && pwd)"
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

required_template_files=(
  ".pre-commit-config.yaml"
  ".secrets.baseline"
  ".guardrails-config.yaml"
  "requirements-ci.txt"
  ".github/workflows/ci.yml"
  "guardrails/scripts/apply_branch_protection.sh"
  "guardrails/test/run_tests.sh"
)

for src in "${required_template_files[@]}"; do
  if [[ ! -e "$TEMPLATE_DIR/$src" ]]; then
    echo "Missing required file in template: $src" >&2
    exit 1
  fi
done

copy_file() {
  local rel="$1"
  local src="$TEMPLATE_DIR/$rel"
  local dst="$TARGET_DIR/$rel"

  run_cmd mkdir -p "$(dirname "$dst")"

  if [[ -e "$dst" && $FORCE -ne 1 ]]; then
    echo "Skip (exists): $rel"
    return
  fi

  run_cmd cp "$src" "$dst"
  echo "Copied: $rel"
}

copy_tree_contents() {
  local rel="$1"
  local src_dir="$TEMPLATE_DIR/$rel"
  local dst_dir="$TARGET_DIR/$rel"

  run_cmd mkdir -p "$dst_dir"

  if [[ -d "$dst_dir" && $FORCE -ne 1 ]]; then
    # Copy files one-by-one to preserve non-conflicting existing files.
    while IFS= read -r -d '' src; do
      local rel_path
      rel_path="${src#$src_dir/}"
      local dst="$dst_dir/$rel_path"
      run_cmd mkdir -p "$(dirname "$dst")"
      if [[ -e "$dst" ]]; then
        echo "Skip (exists): $rel/$rel_path"
      else
        run_cmd cp "$src" "$dst"
        echo "Copied: $rel/$rel_path"
      fi
    done < <(find "$src_dir" -type f -print0)
  else
    run_cmd cp -r "$src_dir/." "$dst_dir/"
    echo "Copied directory contents: $rel"
  fi
}

echo "Template : $TEMPLATE_DIR"
echo "Target   : $TARGET_DIR"
if [[ $DRY_RUN -eq 1 ]]; then
  echo "Mode     : dry-run"
fi

copy_file ".pre-commit-config.yaml"
copy_file ".secrets.baseline"
copy_file ".guardrails-config.yaml"
copy_file "requirements-ci.txt"
copy_file ".github/workflows/ci.yml"
copy_file "guardrails/scripts/apply_branch_protection.sh"

# Also copy this bootstrap script for future updates if available.
if [[ -f "$TEMPLATE_DIR/guardrails/scripts/bootstrap_guardrails.sh" ]]; then
  copy_file "guardrails/scripts/bootstrap_guardrails.sh"
fi

copy_tree_contents "guardrails/test"

if [[ $WITH_DOCS -eq 1 ]]; then
  if [[ -d "$TEMPLATE_DIR/guardrails/docs" ]]; then
    copy_tree_contents "guardrails/docs"
  else
    echo "Skip docs copy: template does not have guardrails/docs"
  fi
fi

if [[ -f "$TARGET_DIR/guardrails/scripts/apply_branch_protection.sh" ]]; then
  run_cmd chmod +x "$TARGET_DIR/guardrails/scripts/apply_branch_protection.sh"
fi
if [[ -f "$TARGET_DIR/guardrails/scripts/bootstrap_guardrails.sh" ]]; then
  run_cmd chmod +x "$TARGET_DIR/guardrails/scripts/bootstrap_guardrails.sh"
fi
if [[ -f "$TARGET_DIR/guardrails/test/run_tests.sh" ]]; then
  run_cmd chmod +x "$TARGET_DIR/guardrails/test/run_tests.sh"
fi

echo
if [[ $DRY_RUN -eq 1 ]]; then
  echo "Dry-run completed. No files were modified."
  echo "Next steps after actual run:"
else
  echo "Bootstrap completed. Next steps:"
fi
echo "1) python3 -m venv guardrails/.venv && source guardrails/.venv/bin/activate"
echo "2) pip install -r requirements-ci.txt"
echo "3) pre-commit install"
echo "4) detect-secrets scan --baseline .secrets.baseline"
echo "5) pre-commit run --all-files"
echo "6) ./guardrails/test/run_tests.sh"
