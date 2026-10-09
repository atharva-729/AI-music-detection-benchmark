#!/usr/bin/env bash
# Prints one line per blind clip. Every column except the id should look the same across files.
cd blind
printf "%-14s %8s %7s %6s %5s %6s %9s\n" id bitrate dur_s sr ch tags enc_str
for f in *.mp3; do
  br=$(ffprobe -v error -show_entries format=bit_rate -of csv=p=0 "$f")
  du=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" | cut -c1-6)
  sr=$(ffprobe -v error -show_entries stream=sample_rate -of csv=p=0 "$f")
  ch=$(ffprobe -v error -show_entries stream=channels -of csv=p=0 "$f")
  tg=$(ffprobe -v error -show_entries format_tags -of csv=p=0 "$f" | wc -c)
  en=$(strings -n 4 "$f" | grep -oE "LAME[0-9.]+|Lavf[0-9.]+|Lavc[0-9.]+|Xing|Info" | sort -u | tr '\n' ' ')
  printf "%-14s %8s %7s %6s %5s %6s %9s\n" "${f%.mp3}" "$br" "$du" "$sr" "$ch" "$tg" "$en"
done
