"""Synthesise placeholder narration per scene from script/narration.md with Piper.

Scene blocks are the markdown headers that name a scene class (CamelCase, e.g. "### PilingUp").
[pause] becomes a silence; [cue] records a timestamp for the scene's next self.cue() call;
*emphasis* markers are stripped. Each sentence is synthesised separately so its timing is known
exactly. Output: audio/placeholder/<Scene>.wav and <Scene>.json (cue times, sentence captions,
duration), plus a table comparing narration length with the rendered video length in renders/.

Usage: python3 tools/tts_narration.py [Scene ...]   (default: every scene with a render)

TTS_BACKEND=breeze uses a running Breeze TTS 2 server (python -m breeze_infer.api <weights> --port 7860)
and clones the reference clip audio/voices/breeze_ref.wav (+ breeze_ref.txt with its exact transcript)
for every sentence, so the voice stays the same across scenes. Output then goes to audio/final/, which
NarratedScene prefers over the Piper placeholders. Breeze weights and outputs are research and
non-commercial only: fine for personal study videos, not for monetised uploads.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NARRATION = ROOT / "script" / "narration.md"
# Male voice trained from scratch on public-domain LibriVox recordings, so the narration is safe to
# publish. Avoid voices whose data is non-commercial (ryan, hfc_*: CC BY-NC-SA) or that were fine-tuned
# from one (joe, from lessac). Public-domain alternatives: en_US-john-medium, en_US-ljspeech-high.
VOICE = ROOT / "audio" / "voices" / "en_US-norman-medium.onnx"
PIPER = [str(ROOT / ".venv-tts" / "bin" / "python"), "-m", "piper"]
BACKEND = os.environ.get("TTS_BACKEND", "piper")
BREEZE_URL = os.environ.get("BREEZE_URL", "http://127.0.0.1:7860")
BREEZE_REF = ROOT / "audio" / "voices" / "breeze_ref.wav"
BREEZE_SEED = 7
# Breeze check: transcribe every sentence and retry those that don't match the script
VERIFY = os.environ.get("TTS_VERIFY", "1") == "1"
# Python of an environment with faster-whisper installed
WHISPER_PYTHON = Path(os.environ.get("WHISPER_PYTHON", "python3"))
MIN_SIMILARITY = 0.9
RETRY_SEEDS = (11, 23, 31)
NUMBER_WORDS = set("""zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen
sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand
point half halves third thirds quarter quarters fifth sixths sevenths eighths ninths eighteenths""".split())
# Spoken spelling for words the voice tends to slur; captions keep the original text
PRONUNCIATION = {r"\bcovariance\b": "co-variance", r"\bCovariance\b": "Co-variance"}
OUT_DIR = ROOT / "audio" / ("final" if BACKEND == "breeze" else "placeholder")
RENDERS = ROOT / "renders"

# Pacing: silence after every sentence, extra silence between paragraphs and at [pause] marks,
# and a slightly slower speaking rate (Piper's length scale; 1.0 is the voice's default)
SENTENCE_SECONDS = 0.55
PAUSE_SECONDS = 1.2
PARAGRAPH_SECONDS = 0.9
LENGTH_SCALE = 1.1
SCENE_NAME = re.compile(r"\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b")


def parse_scenes(text):
    """Map scene name -> narration text, from headers that name a scene class"""
    scenes = {}
    current = None
    for line in text.splitlines():
        if line.startswith("#"):
            match = SCENE_NAME.search(line)
            current = match.group(1) if match and "TODO" not in line else None
            if current:
                scenes[current] = []
        elif current is not None:
            scenes[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in scenes.items()}


def clean(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)  # fact-check notes are not spoken
    text = re.sub(r"^\s*---+\s*$", "", text, flags=re.M)  # markdown rules between sections
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[(?!pause\]|cue\])[^\]]*\]\s*", "", text)  # stage directions like [reveal]
    return text


SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")


def tts_text(sentence):
    if BACKEND != "breeze":
        return sentence
    for pattern, spoken in PRONUNCIATION.items():
        sentence = re.sub(pattern, spoken, sentence)
    return sentence


def synthesize_breeze(sentence_text, path):
    """POST one sentence as multipart form data; the server streams 24 kHz mono 16-bit PCM"""
    import urllib.request
    boundary = "----narration-boundary"
    fields = {"text": sentence_text, "ref_text": BREEZE_REF.with_suffix(".txt").read_text().strip(), "seed": str(BREEZE_SEED)}
    body = b"".join(
        f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode()
        for key, value in fields.items()
    )
    body += (
        f'--{boundary}\r\nContent-Disposition: form-data; name="ref_audio"; filename="{BREEZE_REF.name}"\r\n'
        "Content-Type: audio/wav\r\n\r\n"
    ).encode() + BREEZE_REF.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    request = urllib.request.Request(
        f"{BREEZE_URL}/v1/audio/speech", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        pcm = response.read()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes(pcm)


def synthesize(sentence_text, path):
    if BACKEND == "breeze":
        return synthesize_breeze(sentence_text, path)
    subprocess.run(
        PIPER + ["-m", str(VOICE), "-f", str(path), "--length-scale", str(LENGTH_SCALE)],
        input=sentence_text.encode(), check=True, capture_output=True,
    )


def normalize_words(text):
    """Alphabetic words for comparing a transcript with the script; numbers are skipped (digits vs words)"""
    text = text.lower().replace("-", " ").replace("practise", "practice")
    text = re.sub(r"\b([a-z]) (?=[a-z]\b)", r"\1", text)  # spelled-out symbols: "x t" is heard as "xt"
    words = re.findall(r"[a-z]+", text)
    return [w for w in words if w not in NUMBER_WORDS]


def check_sentences(items):
    """Transcribe clips with Whisper on the CPU; return {path: similarity to the script, 0..1}"""
    import difflib
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump([str(path) for path, _ in items], f)
    result = subprocess.run([str(WHISPER_PYTHON), "-I", str(ROOT / "tools" / "check_sentences.py"), f.name],
                            capture_output=True, text=True, check=True)
    transcripts = json.loads(result.stdout.strip().splitlines()[-1])
    scores = {}
    for path, sentence in items:
        heard = normalize_words(transcripts[str(path)])
        said = normalize_words(sentence)
        scores[path] = difflib.SequenceMatcher(None, said, heard).ratio() if said or heard else 1.0
    return scores


def synthesize_checked(sentences, folder):
    """Synthesize every sentence; with Breeze, retry low-scoring ones with other seeds and keep the best"""
    paths = [folder / f"{i}.wav" for i in range(len(sentences))]
    for path, sentence in zip(paths, sentences):
        synthesize(tts_text(sentence), path)
    if BACKEND != "breeze" or not VERIFY:
        return paths
    best = check_sentences(list(zip(paths, sentences)))
    for seed in RETRY_SEEDS:
        bad = [i for i, path in enumerate(paths) if best[path] < MIN_SIMILARITY]
        if not bad:
            break
        global BREEZE_SEED
        default_seed, BREEZE_SEED = BREEZE_SEED, seed
        retries = []
        for i in bad:
            retry = folder / f"{i}_seed{seed}.wav"
            synthesize(tts_text(sentences[i]), retry)
            retries.append((retry, sentences[i]))
        BREEZE_SEED = default_seed
        scores = check_sentences(retries)
        for (retry, _), i in zip(retries, bad):
            if scores[retry] > best[paths[i]]:
                retry.replace(paths[i])
                best[paths[i]] = scores[retry]
    for path, sentence in zip(paths, sentences):
        if best[path] < MIN_SIMILARITY:
            print(f"    still unclear ({best[path]:.2f}): {sentence}")
    return paths


def build_scene_audio(name, text, out_path):
    paragraphs = [" ".join(p.split()) for p in clean(text).split("\n\n") if p.strip()]
    plan, sentences = [], []
    for paragraph in paragraphs:
        for chunk in re.split(r"(\[pause\]|\[cue\])", paragraph):
            chunk = chunk.strip()
            if chunk in ("[pause]", "[cue]"):
                plan.append(chunk)
                continue
            for sentence in SENTENCE_END.split(chunk):
                if sentence.strip():
                    plan.append(len(sentences))
                    sentences.append(sentence)
        plan.append("[paragraph]")
    with tempfile.TemporaryDirectory() as tmp:
        paths = synthesize_checked(sentences, Path(tmp))
        frames, params, cues, captions = [], None, [], []
        elapsed = 0.0
        for step in plan:
            if step == "[pause]":
                frames.append(("silence", PAUSE_SECONDS))
                elapsed += PAUSE_SECONDS
            elif step == "[cue]":
                cues.append(round(elapsed, 3))
            elif step == "[paragraph]":
                frames.append(("silence", PARAGRAPH_SECONDS))
                elapsed += PARAGRAPH_SECONDS
            else:
                with wave.open(str(paths[step])) as w:
                    params = w.getparams()
                    frames.append(("audio", w.readframes(w.getnframes())))
                    start = elapsed
                    elapsed += w.getnframes() / w.getframerate()
                captions.append([round(start, 3), round(elapsed, 3), sentences[step]])
                frames.append(("silence", SENTENCE_SECONDS))
                elapsed += SENTENCE_SECONDS
        with wave.open(str(out_path), "wb") as out:
            out.setparams(params)
            for kind, data in frames:
                if kind == "silence":
                    data = b"\x00" * (int(params.framerate * data) * params.sampwidth * params.nchannels)
                out.writeframes(data)
    with wave.open(str(out_path)) as w:
        duration = w.getnframes() / w.getframerate()
    timings = {"cues": cues, "duration": round(duration, 3), "captions": captions}
    out_path.with_suffix(".json").write_text(json.dumps(timings, indent=2))
    return duration


def video_duration(name):
    path = RENDERS / f"{name}.mp4"
    if not path.exists():
        return None
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scenes = parse_scenes(NARRATION.read_text())
    names = sys.argv[1:] or [n for n in scenes if (RENDERS / f"{n}.mp4").exists()]
    print(f"{'scene':28} {'voice':>7} {'video':>7} {'diff':>7}")
    for name in names:
        voice = build_scene_audio(name, scenes[name], OUT_DIR / f"{name}.wav")
        video = video_duration(name)
        diff = f"{voice - video:+7.1f}" if video else "    n/a"
        print(f"{name:28} {voice:7.1f} {video or 0:7.1f} {diff}")


if __name__ == "__main__":
    main()
