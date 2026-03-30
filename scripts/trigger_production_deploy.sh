#!/usr/bin/env bash
set -euo pipefail

repo="blackbirdzzzz365-gif/social-listening-v3"
gh workflow run deploy-production.yml --repo "$repo" --ref main
