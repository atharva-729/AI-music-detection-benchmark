#!/usr/bin/env bash
# Round 3b ("V2"): 5 SONICS "half fake" songs (Suno v3.5, AI music, human-written lyrics),
# built exactly like the AI side of make_vocal_round.sh. Human side reuses round 3's clips and answers.
set -euo pipefail
CLIP=30; out=blind/V2; rm -rf "$out"; mkdir -p "$out"
echo "track_id,label,source_file,generator,level,pair" > private/key_V2.csv
PAIRS="1,raw/ai_vocal_hf/fake_52380_suno_0.mp3
2,raw/ai_vocal_hf/fake_21854_suno_1.mp3
3,raw/ai_vocal_hf/fake_05008_suno_0.mp3
4,raw/ai_vocal_hf/fake_12470_suno_1.mp3
5,raw/ai_vocal_hf/fake_40682_suno_1.mp3"
while IFS=, read -r pair f <&3; do
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  start=$(python -c "d=float('$dur'); print(max(0.0, min(d*0.25, d-$CLIP)))")
  id="trk_$(openssl rand -hex 4)"; dst="$out/$id.mp3"
  ffmpeg -nostdin -v error -y -ss "$start" -t "$CLIP" -i "$f" -map 0:a:0 -map_metadata -1 -map_chapters -1 \
    -fflags +bitexact -flags:a +bitexact -af "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=16000" \
    -ac 1 -c:a libmp3lame -b:a 64k -write_xing 0 -id3v2_version 0 -write_id3v1 0 "$dst"
  touch -t 202601010000 "$dst"
  echo "$id,ai,$(basename "$f"),suno-v3.5-halffake,V2,$pair" >> private/key_V2.csv
done 3<<< "$PAIRS"
