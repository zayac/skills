"""Render one day's video from a playlist of scenes: concat, encode, subtitles, chapters, metadata.

Usage: python3 -I tools/build_video.py <playlist> [--no-render] [--quality FLAG]

Playlists live in script/playlists.json:
{
  "out_dir": "../prep",                      # relative to the project root
  "language": "eng",                         # subtitle track language (ISO 639-2)
  "playlists": {
    "day01a": {
      "file": "day01/Day 1A - Topic - theory",
      "title": "Course Exam Prep · Day 1A: Topic — Theory",
      "description": "script/descriptions/day01a.md",
      "scenes": [["s01_intro", "TheoryIntro", "Intro"], ...]   # file stem, scene class, chapter
    }
  }
}
The description file may contain {chapters}; it is replaced by the computed chapter list
(otherwise the list is appended). Output: <out_dir>/<file>.mp4 with embedded subtitles, title,
description and chapters, plus <file>.srt and <file>.info.md (paste-ready title/description).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RENDERS = ROOT / "renders"
AUDIO = ROOT / "audio"
CONFIG = json.loads((ROOT / "script" / "playlists.json").read_text())
OUT_DIR = (ROOT / CONFIG.get("out_dir", "../prep")).resolve()


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def wrap(text, width=42):
    lines, current = [], ""
    for word in text.split():
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    return lines + [current]


def get_captions(scene):
    for folder in ("final", "placeholder"):
        path = AUDIO / folder / f"{scene}.json"
        if path.exists():
            return json.loads(path.read_text())["captions"]
    return []


def build_srt(scenes, path):
    entries, offset = [], 0.0
    for _, scene, _ in scenes:
        for start, end, text in get_captions(scene):
            lines = wrap(text)
            chunks = [lines[i:i + 2] for i in range(0, len(lines), 2)]
            total = sum(len(" ".join(c)) for c in chunks)
            t = start
            for chunk in chunks:
                share = (end - start) * len(" ".join(chunk)) / total
                entries.append((offset + t, offset + t + share, "\n".join(chunk)))
                t += share
        offset += duration(RENDERS / f"{scene}.mp4")
    path.write_text("\n".join(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{text}\n" for i, (a, b, text) in enumerate(entries, 1)))


def get_chapters(scenes):
    """[(start seconds, chapter name)]; consecutive scenes with the same name form one chapter"""
    chapters, offset = [], 0.0
    for _, scene, name in scenes:
        if not chapters or chapters[-1][1] != name:
            chapters.append((offset, name))
        offset += duration(RENDERS / f"{scene}.mp4")
    return chapters


def chapter_list(chapters):
    return "\n".join(f"{int(t // 60):02}:{int(t % 60):02} {name}" for t, name in chapters)


def ffmetadata(title, description, chapters, total):
    def escape(s):
        return "".join("\\" + c if c in "=;#\\\n" else c for c in s)
    text = f";FFMETADATA1\ntitle={escape(title)}\ndescription={escape(description)}\ncomment={escape(description)}\n"
    for i, (start, name) in enumerate(chapters):
        end = chapters[i + 1][0] if i + 1 < len(chapters) else total
        text += f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(start * 1000)}\nEND={int(end * 1000)}\ntitle={escape(name)}\n"
    return text


def main():
    name = sys.argv[1]
    render = "--no-render" not in sys.argv
    quality = sys.argv[sys.argv.index("--quality") + 1] if "--quality" in sys.argv else None
    playlist = CONFIG["playlists"][name]
    scenes = playlist["scenes"]
    out = OUT_DIR / f"{playlist['file']}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    if render:
        for file, scene, _ in scenes:
            print(f"rendering {scene}", flush=True)
            cmd = [str(ROOT / ".venv/bin/manimgl"), f"scenes/{file}.py", scene, "-w"] + ([quality] if quality else [])
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            for line in (result.stdout + result.stderr).replace("\r", "\n").splitlines():
                if ("WARNING" in line and "Estimated size" not in line) or "Error" in line:
                    print("   ", line.strip())
            if result.returncode != 0:
                sys.exit(f"render of {scene} failed; run: .venv/bin/manimgl scenes/{file}.py {scene} -w -l")
    chapters = get_chapters(scenes)
    title = playlist.get("title", out.stem)
    description = ""
    if playlist.get("description"):
        description = (ROOT / playlist["description"]).read_text().strip()
    if "{chapters}" in description:
        description = description.replace("{chapters}", chapter_list(chapters))
    else:
        description = f"{description}\n\nChapters:\n{chapter_list(chapters)}".strip()
    with tempfile.TemporaryDirectory() as tmp:
        listing = Path(tmp) / "list.txt"
        listing.write_text("".join(f"file '{RENDERS / (scene + '.mp4')}'\n" for _, scene, _ in scenes))
        video = Path(tmp) / "video.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                        "-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-crf", "16", "-g", "60",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", str(video)],
                       check=True)
        srt = out.with_suffix(".srt")
        build_srt(scenes, srt)
        meta = Path(tmp) / "meta.txt"
        meta.write_text(ffmetadata(title, description, chapters, duration(video)))
        has_subtitles = srt.stat().st_size > 0
        inputs = ["-i", str(video), "-i", str(meta)] + (["-i", str(srt)] if has_subtitles else [])
        maps = ["-map", "0:v", "-map", "0:a?"] + (["-map", "2", "-c:s", "mov_text",
                "-metadata:s:s:0", f"language={CONFIG.get('language', 'eng')}"] if has_subtitles else [])
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *inputs, *maps, "-map_metadata", "1", "-map_chapters", "1",
                        "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart", str(out)], check=True)
        if not has_subtitles:
            srt.unlink()
            print("no narration captions found: video has no subtitle track")
    info = out.with_suffix(".info.md")
    info.write_text(f"# {title}\n\n**Title:** {title}\n\n**Description:**\n\n{description}\n")
    print(f"{out}: {duration(out) / 60:.1f} min")
    print(chapter_list(chapters))
    print(f"info: {info}")


if __name__ == "__main__":
    main()
