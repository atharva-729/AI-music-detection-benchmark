#!/usr/bin/env bash
# Usage: scripts/make_levels.sh [levels...]   (default: L0 L1 L2 L3 L4)
# Builds the difficulty ladder (LEVELS_PLAN.md) from the 10 pilot tracks listed in private/key_full.csv.
# Writes blind/<L>/<id>.<ext>, private/key_<L>.csv and private/truth_<L>.csv (ffprobe/loudnorm ground truth).
set -euo pipefail
LEVELS=("${@:-L0 L1 L2 L3 L4}"); [ $# -eq 0 ] && LEVELS=(L0 L1 L2 L3 L4)
CLIP=30
SRC=$(tail -n +2 private/key_full.csv | cut -d, -f2,3,4)   # label,source_file,generator

for L in "${LEVELS[@]}"; do
  out="blind/$L"; rm -rf "$out"; mkdir -p "$out"
  echo "track_id,label,source_file,generator,level" > "private/key_$L.csv"
  echo "track_id,duration_s,sample_rate_hz,bitrate_kbps,channels,codec,n_tags,suno_tag,integrated_lufs" > "private/truth_$L.csv"
  while IFS=, read -r label src gen <&3; do
    [ "$label" = ai ] && f="raw/ai/$src" || f="raw/human/$src"
    ext="${src##*.}"; id="trk_$(openssl rand -hex 4)"
    BASE=(-map 0:a:0 -map_metadata -1 -map_chapters -1 -fflags +bitexact -flags:a +bitexact)
    ENC=(-ac 2 -c:a libmp3lame -b:a 192k -write_xing 0 -id3v2_version 0 -write_id3v1 0)
    case "$L" in
      L0) dst="$out/$id.$ext"; cp "$f" "$dst" ;;
      L1) dst="$out/$id.$ext"; ffmpeg -nostdin -v error -y -i "$f" "${BASE[@]}" -c copy "$dst" ;;
      L2) dst="$out/$id.mp3";  ffmpeg -nostdin -v error -y -i "$f" "${BASE[@]}" -af aresample=44100 "${ENC[@]}" "$dst" ;;
      L3) dst="$out/$id.mp3";  ffmpeg -nostdin -v error -y -i "$f" "${BASE[@]}" \
            -af "aresample=44100,lowpass=f=15000:poles=2,lowpass=f=15000:poles=2" "${ENC[@]}" -cutoff 15500 "$dst" ;;
      L4) dst="$out/$id.mp3"
          dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
          start=$(python -c "d=float('$dur'); print(max(0.0, min(d*0.25, d-$CLIP)))")
          ffmpeg -nostdin -v error -y -ss "$start" -t "$CLIP" -i "$f" "${BASE[@]}" \
            -af "loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:d=0.5,afade=t=out:st=$((CLIP-1)):d=1,aresample=44100,lowpass=f=15000:poles=2,lowpass=f=15000:poles=2" \
            "${ENC[@]}" -cutoff 15500 "$dst" ;;
    esac
    touch -t 202601010000 "$dst"
    echo "$id,$label,$src,$gen,$L" >> "private/key_$L.csv"
    q() { ffprobe -v error -select_streams a:0 -show_entries "$1" -of default=nw=1:nk=1 "$dst" | head -1 | tr -d ","; }
    du=$(q format=duration); sr=$(q stream=sample_rate); br=$(q format=bit_rate); ch=$(q stream=channels); co=$(q stream=codec_name)
    nt=$(ffprobe -v error -show_entries format_tags -of flat "$dst" | wc -l)
    st=$(ffprobe -v error -show_entries format_tags -of flat "$dst" | grep -qi suno && echo yes || echo no)
    lu=$(ffmpeg -nostdin -nostats -i "$dst" -af loudnorm=print_format=summary -f null - 2>&1 | awk '/Input Integrated/{print $3}')
    printf "%s,%.1f,%s,%d,%s,%s,%s,%s,%s\n" "$id" "$du" "$sr" "$((br/1000))" "$ch" "$co" "$nt" "$st" "$lu" >> "private/truth_$L.csv"
    echo "$L: $src -> $dst"
  done 3<<< "$SRC"
done
