#!/usr/bin/env bash
# Combine renders/full_video.mp4 with its subtitles and, if present, background music.
# Output: renders/final.mp4 (subtitles as a selectable track; upload renders/full_video.srt too).
#
# Music: put one file at audio/music.{mp3,m4a,wav,flac}. It loops to the video's length, sits
# well below the voice, ducks further whenever the narrator speaks, and fades out at the end.
# Usage: tools/finalize.sh [music volume, default 0.18]
set -euo pipefail
cd "$(dirname "$0")/.."

video=renders/full_video.mp4
subs=renders/full_video.srt
out=renders/final.mp4
volume="${1:-0.18}"
music=$(ls audio/music.{mp3,m4a,wav,flac} 2>/dev/null | head -1 || true)
length=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$video")
fade_start=$(python3 -c "print(max(0, $length - 4))")

if [[ -n "$music" ]]; then
    echo "mixing music from $music at volume $volume"
    ffmpeg -loglevel error -y -i "$video" -stream_loop -1 -i "$music" -i "$subs" \
        -filter_complex "\
[0:a]asplit=2[voice][key];\
[1:a]volume=$volume,afade=t=out:st=$fade_start:d=4[bed];\
[bed][key]sidechaincompress=threshold=0.02:ratio=6:attack=40:release=700[ducked];\
[voice][ducked]amix=inputs=2:duration=first:normalize=0[mix]" \
        -map 0:v -map "[mix]" -map 2 -t "$length" \
        -c:v copy -c:a aac -b:a 192k -c:s mov_text -metadata:s:s:0 language=eng "$out"
else
    echo "no audio/music.* found: narration only"
    ffmpeg -loglevel error -y -i "$video" -i "$subs" \
        -map 0:v -map 0:a -map 1 -c:v copy -c:a copy -c:s mov_text -metadata:s:s:0 language=eng "$out"
fi
echo "$out: $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out")s"
