#!/usr/bin/env bash
# Cut + grade the source clips into the segments listed in ../PLAN.md (v2).
# usage: bash prep.sh   (writes assets/sNN.mp4, 1920x1080 60fps, no audio)
set -e
cd "$(dirname "$0")"
SRC="../raw/clips/vid2"
mkdir -p assets
clip() { sed -n "${1}p" ../analysis/index.txt | sed 's#clips/vid2/##'; }

# Shared look: teal shadows, warm highlights, lifted blacks, gentle contrast.
GRADE="curves=all='0/0.035 0.5/0.5 1/0.97',colorbalance=rs=-0.04:gs=0.0:bs=0.05:rh=0.05:gh=0.01:bh=-0.04,eq=contrast=1.05:saturation=1.08"

# id  clip  in   out   speed  extra
ONLY="${ONLY:-}"
SEGS="
s01 30 0.5 5.0 1.0 -
s02 7 1.0 5.5 1.0 -
s03 1 2.0 10.0 0.8 -
s04 5 3.0 6.0 1.0 -
s05 3 2.0 5.0 1.0 -
s06 8 0.5 3.5 0.8 -
s07 11 3.0 8.0 0.8 -
s08 14 6.0 8.5 0.5 -
s09 8 7.8 9.8 0.67 -
s10 10 2.0 6.5 1.0 -
s11 27 1.0 5.0 1.0 -
s12 28 2.0 7.0 1.0 -
s13 18 0.0 3.0 1.0 eq=brightness=0.05:gamma=1.25
s14 26 0.0 5.0 1.0 -
s15 31 1.0 6.0 1.0 -
s16 29 0.0 9.5 0.5 -
s17 2 1.0 4.0 1.0 -
"
echo "$SEGS" | while read -r id c in out sp extra; do
  [ -z "$id" ] && continue
  [ -n "$ONLY" ] && ! echo " $ONLY " | grep -q " $id " && continue
  f="$SRC/$(clip "$c")"
  vf="setpts=PTS/${sp}"
  [ "$extra" != "-" ] && vf="$vf,$extra"
  vf="$vf,$GRADE,fps=60,format=yuv420p"
  ffmpeg -v error -y -ss "$in" -to "$out" -i "$f" -an -vf "$vf" \
    -c:v libx264 -preset slow -crf 14 -g 30 "assets/$id.mp4" < /dev/null
  echo "$id $(ffprobe -v error -show_entries format=duration -of csv=p=0 assets/$id.mp4)"
done
