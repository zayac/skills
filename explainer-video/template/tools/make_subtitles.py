"""Build renders/full_video.srt from the narration's per-sentence caption timings.

Scene order comes from tools/assemble.sh; each scene's offset is the summed length of the rendered
scenes before it, so run this after rendering. Captions come from audio/final/<Scene>.json when it
exists, else audio/placeholder/<Scene>.json.

Usage: python3 tools/make_subtitles.py
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RENDERS = ROOT / "renders"
AUDIO = ROOT / "audio"
LINE_LENGTH = 42  # characters per subtitle line, two lines per caption at most


def scene_order():
    text = (ROOT / "tools" / "assemble.sh").read_text()
    return re.findall(r'"s\d+_\w+ (\w+)"', text)


def video_duration(scene):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
         str(RENDERS / f"{scene}.mp4")],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout)


def load_captions(scene):
    for folder in ("final", "placeholder"):
        path = AUDIO / folder / f"{scene}.json"
        if path.exists():
            return json.loads(path.read_text()).get("captions", [])
    return []


def wrap(words):
    """Greedy-wrap words into lines of at most LINE_LENGTH characters"""
    lines, current = [], ""
    for word in words:
        if current and len(current) + 1 + len(word) > LINE_LENGTH:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    return lines + [current]


def split_caption(start, end, text):
    """Split long sentences into two-line captions, sharing time in proportion to their length"""
    lines = wrap(text.split())
    pieces = [" ".join(lines[i:i + 2]) for i in range(0, len(lines), 2)]
    pieces_lines = [lines[i:i + 2] for i in range(0, len(lines), 2)]
    total = sum(len(p) for p in pieces)
    t = start
    for piece, piece_lines in zip(pieces, pieces_lines):
        duration = (end - start) * len(piece) / total
        yield t, t + duration, "\n".join(piece_lines)
        t += duration


def timestamp(seconds):
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    entries = []
    offset = 0.0
    for scene in scene_order():
        for start, end, text in load_captions(scene):
            entries.extend(split_caption(offset + start, offset + end, text))
        offset += video_duration(scene)
    out = RENDERS / "full_video.srt"
    out.write_text("\n".join(
        f"{i}\n{timestamp(start)} --> {timestamp(end)}\n{text}\n"
        for i, (start, end, text) in enumerate(entries, 1)
    ))
    print(f"{out}: {len(entries)} captions, video length {offset:.1f}s")


if __name__ == "__main__":
    main()
