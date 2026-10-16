#!/usr/bin/env bash
# Vocal round ("V"): 5 SONICS AI vocal tracks (Suno v3.5 / Udio) vs 5 human CC vocal tracks.
# SONICS ships 16 kHz mono ~35 kbps MP3, so every file is brought to the same quality:
#   human only: one 16 kHz mono 32 kbps MP3 pass (matches the AI files' generation loss)
#   all: 30 s from 25% in, 16 kHz mono, -16 LUFS, NO fades, NO extra low-pass, 64 kbps CBR MP3, no tags.
# Writes blind/V/, private/key_V.csv, private/truth_V.csv.
set -euo pipefail
CLIP=30; out=blind/V; tmp=$(mktemp -d)
rm -rf "$out"; mkdir -p "$out"
echo "track_id,label,source_file,generator,level,pair" > private/key_V.csv
echo "track_id,duration_s,sample_rate_hz,bitrate_kbps,channels,integrated_lufs" > private/truth_V.csv
PAIRS="1,ai,raw/ai_vocal/fake_54122_suno_0.mp3,suno-v3.5
1,human,raw/human/h03.mp3,
2,ai,raw/ai_vocal/fake_53263_udio_1.mp3,udio-120s
2,human,raw/human/h11.mp3,
3,ai,raw/ai_vocal/fake_53742_suno_1.mp3,suno-v3.5
3,human,raw/human/h12.mp3,
4,ai,raw/ai_vocal/fake_53772_suno_0.mp3,suno-v3.5
4,human,raw/human/h16.mp3,
5,ai,raw/ai_vocal/fake_53651_udio_1.mp3,udio-120s
5,human,raw/human/h20.mp3,"
while IFS=, read -r pair label f gen <&3; do
  src="$f"
  if [ "$label" = human ]; then
    src="$tmp/$(basename "$f").lo.mp3"
    ffmpeg -nostdin -v error -y -i "$f" -map 0:a:0 -ac 1 -ar 16000 -c:a libmp3lame -b:a 32k "$src"
  fi
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$src")
  start=$(python -c "d=float('$dur'); print(max(0.0, min(d*0.25, d-$CLIP)))")
  id="trk_$(openssl rand -hex 4)"; dst="$out/$id.mp3"
  ffmpeg -nostdin -v error -y -ss "$start" -t "$CLIP" -i "$src" -map 0:a:0 -map_metadata -1 -map_chapters -1 \
    -fflags +bitexact -flags:a +bitexact -af "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=16000" \
    -ac 1 -c:a libmp3lame -b:a 64k -write_xing 0 -id3v2_version 0 -write_id3v1 0 "$dst"
  touch -t 202601010000 "$dst"
  echo "$id,$label,$(basename "$f"),$gen,V,$pair" >> private/key_V.csv
  q() { ffprobe -v error -select_streams a:0 -show_entries "$1" -of default=nw=1:nk=1 "$dst" | head -1 | tr -d ","; }
  lu=$(ffmpeg -nostdin -nostats -i "$dst" -af loudnorm=print_format=summary -f null - 2>&1 | awk '/Input Integrated/{print $3}')
  printf "%s,%.1f,%s,%d,%s,%s\n" "$id" "$(q format=duration)" "$(q stream=sample_rate)" "$(( $(q format=bit_rate)/1000 ))" "$(q stream=channels)" "$lu" >> private/truth_V.csv
done 3<<< "$PAIRS"
rm -rf "$tmp"
