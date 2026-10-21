#!/usr/bin/env bash
# Rebuilds prompts from data/issues.csv, recomputes all numbers from runs/
# and compares them with expected.txt. Exit code 1 on any mismatch.
set -euo pipefail
cd "$(dirname "$0")"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

python3 scripts/make_prompts.py data/issues.csv "$tmp" > /dev/null
for p in A B; do
  if ! cmp -s "$tmp/prompt_$p.txt" "prompts/prompt_$p.txt"; then
    echo "FAIL: prompts/prompt_$p.txt differs from the one built from data/issues.csv"
    exit 1
  fi
done
echo "OK: prompts match data/issues.csv"

python3 analyze.py . > "$tmp/actual.txt"
cat "$tmp/actual.txt"
echo
if diff -u expected.txt "$tmp/actual.txt"; then
  echo "OK: output matches expected.txt"
else
  echo "FAIL: output differs from expected.txt"
  exit 1
fi
