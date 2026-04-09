#!/usr/bin/env bash
# Apply branch protection for main/stage with required CI check.

set -euo pipefail

REQUIRED_CONTEXT="quality-and-security"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required." >&2
  exit 1
fi

if [[ -z "${GITHUB_TOKEN:-}" && -z "${GH_TOKEN:-}" ]]; then
  echo "Set GITHUB_TOKEN or GH_TOKEN before running. For branch protection updates, use a classic PAT with repo scope and repository admin rights, or a fine-grained PAT with Administration: Read and write for this repository." >&2
  exit 1
fi

# Derive owner/repo from the current repository remote; allow overrides via OWNER/REPO env vars
_REPO_SLUG="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
OWNER="${OWNER:-${_REPO_SLUG%%/*}}"
REPO="${REPO:-${_REPO_SLUG#*/}}"

for BRANCH in main stage; do
  echo "Applying protection to ${BRANCH}..."
  gh api \
    --method PUT \
    "repos/${OWNER}/${REPO}/branches/${BRANCH}/protection" \
    --input - <<JSON
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "${REQUIRED_CONTEXT}"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
JSON

  gh api "repos/${OWNER}/${REPO}/branches/${BRANCH}" --jq '"- " + .name + " protected=" + (.protected|tostring)'
done

echo "Done. Confirm in GitHub settings: required status check '${REQUIRED_CONTEXT}'."
