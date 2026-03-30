#!/usr/bin/env bash
set -euo pipefail

repo="blackbirdzzzz365-gif/social-listening-v3"
rollback_sha="${1:-}"

if [ -n "$rollback_sha" ]; then
  gh workflow run rollback-production.yml --repo "$repo" -f rollback_sha="$rollback_sha"
else
  gh workflow run rollback-production.yml --repo "$repo"
fi
