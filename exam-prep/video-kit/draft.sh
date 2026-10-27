#!/usr/bin/env bash
# Draft-render scenes and make contact sheets. Usage: tools/draft.sh <file-stem> <Scene> [step] [quality]
set -uo pipefail
cd "$(dirname "$0")/.."
file=$1; scene=$2; q=${3:--l}
out=$(.venv/bin/manimgl "scenes/$file.py" "$scene" -w $q 2>&1 | tr '\r' '\n')
echo "$out" | grep -aE "WARNING|Error|rror:|Exception|line [0-9]+, in construct" | grep -v "it/s\|Estimated size" | head -20
mkdir -p renders/sheets
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 renders/$scene.mp4); step=$(python3 -c "print(max(1.0, round($d/12, 1)))"); tools/contact_sheet.sh "renders/$scene.mp4" "renders/sheets/$scene.png" "$step" >/dev/null 2>&1 && echo "sheet: renders/sheets/$scene.png ($(ffprobe -v error -show_entries format=duration -of csv=p=0 renders/$scene.mp4)s)"
