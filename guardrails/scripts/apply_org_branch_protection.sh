#!/usr/bin/env bash
# Apply organization-standard branch protection profiles.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./guardrails/scripts/apply_org_branch_protection.sh [options]

Options:
  --profile <name>          Profile name: security-only | full-guardrails
                            default: security-only
  --branches <csv>          Protected branches (default: main)
  --required-contexts <csv> Override status checks explicitly
  --reviews <n>             Required approving review count (default: 0)
  --dry-run                 Print resolved settings without applying
  -h, --help                Show this help

Examples:
  ./guardrails/scripts/apply_org_branch_protection.sh
  ./guardrails/scripts/apply_org_branch_protection.sh --profile full-guardrails --reviews 1
  ./guardrails/scripts/apply_org_branch_protection.sh --branches main,release --profile security-only
  ./guardrails/scripts/apply_org_branch_protection.sh --required-contexts gitleaks-pr-scan,quality-and-security
EOF
}

PROFILE="security-only"
PROTECTED_BRANCHES="main"
REQUIRED_CONTEXTS=""
REQUIRED_APPROVING_REVIEW_COUNT="0"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      PROFILE="${2:-}"
      shift 2
      ;;
    --branches)
      PROTECTED_BRANCHES="${2:-}"
      shift 2
      ;;
    --required-contexts)
      REQUIRED_CONTEXTS="${2:-}"
      shift 2
      ;;
    --reviews)
      REQUIRED_APPROVING_REVIEW_COUNT="${2:-}"
      shift 2
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

if [[ ! "${PROFILE}" =~ ^(security-only|full-guardrails)$ ]]; then
  echo "--profile must be one of: security-only, full-guardrails" >&2
  exit 1
fi

if [[ ! "${REQUIRED_APPROVING_REVIEW_COUNT}" =~ ^[0-9]+$ ]]; then
  echo "--reviews must be a non-negative integer" >&2
  exit 1
fi

if [[ -n "${REQUIRED_CONTEXTS}" ]]; then
  resolved_contexts="${REQUIRED_CONTEXTS}"
else
  case "${PROFILE}" in
    security-only)
      resolved_contexts="gitleaks-pr-scan"
      ;;
    full-guardrails)
      resolved_contexts="gitleaks-pr-scan,quality-and-security"
      ;;
  esac
fi

echo "Profile                        : ${PROFILE}"
echo "Protected branches             : ${PROTECTED_BRANCHES}"
echo "Required status checks         : ${resolved_contexts}"
echo "Required approving review count: ${REQUIRED_APPROVING_REVIEW_COUNT}"

if [[ ${DRY_RUN} -eq 1 ]]; then
  echo "Dry-run: no changes were applied."
  exit 0
fi

CHECK_PROFILE="${PROFILE}" \
PROTECTED_BRANCHES="${PROTECTED_BRANCHES}" \
REQUIRED_CONTEXTS="${resolved_contexts}" \
REQUIRED_APPROVING_REVIEW_COUNT="${REQUIRED_APPROVING_REVIEW_COUNT}" \
  ./guardrails/scripts/apply_branch_protection.sh
