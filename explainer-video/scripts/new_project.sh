#!/usr/bin/env bash
# Start a new explainer-video project from the bundled template.
# Usage: new_project.sh [target-dir]   (default: ./video in the current folder)
# Exports the committed template/ (no build artefacts) into a fresh git repo, then runs setup.sh
# (Python envs, ManimGL, reference repos, narrator voice, smoke test).
set -euo pipefail
target="$(realpath -m "${1:-video}")"
skill="$(cd "$(dirname "$0")/.." && pwd)"

if [[ -e "$target" ]]; then
    echo "error: $target already exists" >&2
    exit 1
fi
if [[ -n "$(git -C "$skill" status --porcelain -- template)" ]]; then
    echo "warning: template/ has uncommitted changes; they are NOT included (commit them first)" >&2
fi

mkdir -p "$target"
# The skill may live in a subfolder of a larger repo, so address the tree by its repo-relative path
# and run git from the repo root: from a subfolder, git archive silently filters the tree to that subfolder
prefix="$(git -C "$skill" rev-parse --show-prefix)"
root="$(git -C "$skill" rev-parse --show-toplevel)"
git -C "$root" archive "HEAD:${prefix}template" | tar -x -C "$target"
cd "$target"
git init -q
git add -A
git commit -qm "Start from explainer template ($(git -C "$skill" rev-parse --short HEAD))"
./setup.sh
