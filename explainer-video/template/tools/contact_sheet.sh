#!/usr/bin/env bash
# Usage: tools/contact_sheet.sh renders/Scene.mp4 out.png [seconds_between_frames]
# Tiles frames sampled every N seconds into one image for quick visual review.
set -euo pipefail
video="$1"; out="$2"; step="${3:-2}"
ffmpeg -loglevel error -y -i "$video" -vf "fps=1/$step,scale=640:-1,tile=4x3:padding=4:color=white" -frames:v 1 "$out"
