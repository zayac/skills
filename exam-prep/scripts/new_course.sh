#!/usr/bin/env bash
# Create the video project for a course and add the exam-prep layer on top of the explainer template.
# Usage: new_course.sh <course>/prep-videos
# Needs the explainer-video skill next to this one (or in $SKILLS_DIR).
set -euo pipefail
target="$(realpath -m "${1:?usage: new_course.sh <course>/prep-videos}")"
skill="$(cd "$(dirname "$0")/.." && pwd)"
explainer="$skill/../explainer-video"
[[ -d "$explainer" ]] || explainer="${SKILLS_DIR:?set SKILLS_DIR to the folder that holds explainer-video}/explainer-video"
[[ -x "$explainer/scripts/new_project.sh" ]] || { echo "error: explainer-video skill not found" >&2; exit 1; }

"$explainer/scripts/new_project.sh" "$target"
cd "$target"
cp "$skill/video-kit/kit.py" "$skill/video-kit/s00_day_patterns.py" scenes/
cp "$skill/video-kit/build_video.py" "$skill/video-kit/draft.sh" tools/
chmod +x tools/draft.sh
mkdir -p script/descriptions
cp "$skill/video-kit/playlists.json" script/
cp "$skill/templates/frequencies.md" script/
cp "$skill/templates/description.md" script/descriptions/day01a.md
mkdir -p ../prep/templates
cp "$skill/templates/"{practice.tex,cheatsheet.tex,plan.md,day-README.md} ../prep/templates/
git add -A
git commit -qm "Add exam-prep layer (kit, playlist build, templates) from exam-prep skill ($(git -C "$skill" rev-parse --short HEAD 2>/dev/null || echo local))"
echo "video project: $target"
echo "sheet templates: $(realpath ../prep/templates)"
