#!/usr/bin/env bash
# Frequency test ("F"): one AI/human pair where the ONLY intended difference is the frequency ceiling.
# AI = SONICS Suno v3.5 (source is 16 kHz, so nothing above 8 kHz); human = h03 at full bandwidth.
# Both: 30 s from 25% in, -16 LUFS, no fades, no low-pass, 44.1 kHz stereo, 192 kbps CBR MP3, no tags.
set -euo pipefail
CLIP=30; out=blind/F; rm -rf "$out"; mkdir -p "$out"
echo "track_id,label,source_file,generator,level" > private/key_F.csv
for spec in "ai,raw/ai_vocal/fake_54122_suno_0.mp3,suno-v3.5" "human,raw/human/h03.mp3,"; do
  IFS=, read -r label f gen <<< "$spec"
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  start=$(python -c "d=float('$dur'); print(max(0.0, min(d*0.25, d-$CLIP)))")
  id="trk_$(openssl rand -hex 4)"; dst="$out/$id.mp3"
  ffmpeg -nostdin -v error -y -ss "$start" -t "$CLIP" -i "$f" -map 0:a:0 -map_metadata -1 -map_chapters -1 \
    -fflags +bitexact -flags:a +bitexact -af "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100" \
    -ac 2 -c:a libmp3lame -b:a 192k -write_xing 0 -id3v2_version 0 -write_id3v1 0 "$dst"
  touch -t 202601010000 "$dst"
  echo "$id,$label,$(basename "$f"),$gen,F" >> private/key_F.csv
done
