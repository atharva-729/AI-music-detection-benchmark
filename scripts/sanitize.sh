#!/usr/bin/env bash
# Usage: scripts/sanitize.sh <raw_dir> <label: ai|human> [level: A|B]
# Writes anonymised clips to blind/ and appends the answer key to private/key.csv
set -euo pipefail
RAW="$1"; LABEL="$2"; LEVEL="${3:-B}"
CLIP=30            # seconds per clip (level B)
mkdir -p blind private
[ -f private/key.csv ] || echo "track_id,label,source_file,generator,level" > private/key.csv

shopt -s nullglob
for f in "$RAW"/*.{mp3,wav,flac,m4a,ogg,opus,aac,webm}; do
  id="trk_$(openssl rand -hex 4)"
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")

  if [ "$LEVEL" = "B" ]; then
    # fixed 30 s window starting 25% into the track + loudness normalisation
    start=$(python3 -c "d=float('$dur'); print(max(0.0, min(d*0.25, d-$CLIP)))")
    TRIM=(-ss "$start" -t "$CLIP")
    LOUD="loudnorm=I=-16:TP=-1.5:LRA=11,"
    FADE="afade=t=in:d=0.5,afade=t=out:st=$((CLIP-1)):d=1,"
  else
    TRIM=(); LOUD=""; FADE=""
  fi

  ffmpeg -v error -y "${TRIM[@]}" -i "$f" -map 0:a:0 -map_metadata -1 -map_chapters -1 \
    -fflags +bitexact -flags:a +bitexact \
    -af "${LOUD}${FADE}aresample=44100,lowpass=f=15000:poles=2,lowpass=f=15000:poles=2" \
    -ac 2 -c:a libmp3lame -b:a 192k -cutoff 15500 \
    -write_xing 0 -id3v2_version 0 -write_id3v1 0 "blind/$id.mp3"

  touch -t 202601010000 "blind/$id.mp3"        # identical file timestamps
  echo "$id,$LABEL,$(basename "$f"),${GENERATOR:-},$LEVEL" >> private/key.csv
  echo "$f -> blind/$id.mp3"
done
