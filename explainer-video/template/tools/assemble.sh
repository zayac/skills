#!/usr/bin/env bash
# Concatenate rendered scenes, in story order, into renders/full_video.mp4.
# Usage: tools/assemble.sh [--render [quality flag, default -l]]
#   --render re-renders every scene first (e.g. tools/assemble.sh --render --uhd)
set -euo pipefail
cd "$(dirname "$0")/.."

SCENES=(
    # "<file in scenes/ without .py> <SceneClass>", in story order
    "s01_example ExampleIntro"
)

if [[ "${1:-}" == "--render" ]]; then
    quality="${2:--l}"
    for entry in "${SCENES[@]}"; do
        read -r file scene <<< "$entry"
        echo "rendering $scene"
        .venv/bin/manimgl "scenes/$file.py" "$scene" -w "$quality" 2>&1 | grep -E "WARNING|Error" || true
    done
fi

list=$(mktemp)
for entry in "${SCENES[@]}"; do
    read -r _ scene <<< "$entry"
    echo "file '$PWD/renders/$scene.mp4'" >> "$list"
done
# One delivery encode for the whole video: constant quality, tuned for flat animation, a keyframe
# every 2 s (what YouTube recommends; also keeps seeking clean), and moov atom up front for streaming
ffmpeg -loglevel error -stats -y -f concat -safe 0 -i "$list" \
    -c:v libx264 -preset slow -tune animation -crf 12 -g 60 -keyint_min 30 -bf 2 \
    -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart renders/full_video.mp4
rm "$list"
echo "renders/full_video.mp4: $(ffprobe -v error -show_entries format=duration -of csv=p=0 renders/full_video.mp4)s"
