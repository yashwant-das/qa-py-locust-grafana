#!/usr/bin/env bash
# Check generated requirements without changing the committed files.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export_dir=$(mktemp -d)
trap 'rm -rf "$export_dir"' EXIT
uv export --locked --no-dev --no-emit-project --no-header \
  -o "$export_dir/runtime.txt" >/dev/null
uv export --locked --all-groups --no-emit-project --no-header \
  -o "$export_dir/development.txt" >/dev/null
diff -u target-app/requirements.txt "$export_dir/runtime.txt"
diff -u requirements-dev.txt "$export_dir/development.txt"
