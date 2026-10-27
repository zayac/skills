"""Transcribe synthesized sentence clips so tts_narration.py can catch mispronunciations.

Run with the whisper tool's Python: <whisper>/.venv/bin/python -I tools/check_sentences.py files.json
Reads a JSON list of wav paths and prints a JSON object {path: transcript}. Runs on the CPU so it can
share the machine with the TTS server on the GPU.
"""
import json
import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel


def load_audio(path):
    """16 kHz mono float32 via ffmpeg (faster-whisper's own decoder breaks with this PyAV version)"""
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def main():
    paths = json.loads(open(sys.argv[1]).read())
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    result = {}
    for path in paths:
        segments, _ = model.transcribe(load_audio(path), language="en", beam_size=5)
        result[path] = " ".join(segment.text.strip() for segment in segments)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
