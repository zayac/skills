#!/usr/bin/env bash
# One-time setup for a new video project made from this template (Arch Linux; adapt pacman lines elsewhere).
# Creates .venv (ManimGL) and .venv-tts (Piper), clones the reference repos, downloads the narrator
# voice, and renders a smoke-test frame.
set -euo pipefail
cd "$(dirname "$0")"

need() { command -v "$1" >/dev/null || { echo "missing: $1"; missing=1; }; }
missing=0
for tool in python3 git ffmpeg ffprobe latex dvisvgm pdftoppm; do need "$tool"; done
if [[ $missing == 1 ]]; then
    echo "Install system packages first, e.g.:"
    echo "  sudo pacman -S --needed python git ffmpeg poppler texlive-basic texlive-latex \\"
    echo "      texlive-latexrecommended texlive-latexextra texlive-fontsrecommended \\"
    echo "      texlive-mathscience texlive-binextra"
    exit 1
fi

[[ -d ref/manim ]] || git clone --depth 1 https://github.com/3b1b/manim ref/manim
# Parallel renders share latex_cache/working.tex upstream and swap formulas between scenes (then the
# wrong SVGs get cached for good); give each process its own working file
sed -i 's|tex_path = temp_dir / "working.tex"|tex_path = temp_dir / f"working_{os.getpid()}.tex"|' \
    ref/manim/manimlib/utils/tex_file_writing.py
grep -q 'working_{os.getpid()}' ref/manim/manimlib/utils/tex_file_writing.py \
    || echo "warning: ManimGL tex patch did not apply; don't render scenes in parallel"
[[ -d ref/videos ]] || git clone --depth 1 https://github.com/3b1b/videos ref/videos

[[ -d .venv ]] || python3 -m venv .venv
.venv/bin/pip install -q -e ref/manim av

[[ -d .venv-tts ]] || python3 -m venv .venv-tts
.venv-tts/bin/pip install -q piper-tts

# Narrator: trained from scratch on public-domain LibriVox audio, so safe to publish
[[ -f audio/voices/en_US-norman-medium.onnx ]] || \
    .venv-tts/bin/python -m piper.download_voices --download-dir audio/voices en_US-norman-medium

echo "smoke test: rendering the building-blocks gallery"
.venv/bin/manimgl scenes/style.py BuildingBlocksGallery -w -s -l 2>&1 | grep -E "File ready|Error" || true
ls renders/BuildingBlocksGallery.png && echo "setup ok"
