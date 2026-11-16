# Tides SMP trailer: V5 plan (deadline 8:30 PM, 2026-11-02)

## Every client/user note so far (latest wins)
1. Length about 50 s ("40 s-1:30 would be MORE than enough"; they asked for 50 s).
2. Use FEWER clips, LONG clips, and never reuse a clip ("for the 5th time").
3. Keep it calm: the only thing V3 got right.
4. No overlays on their footage. The bubbles over an underwater shader clip were the worst offender; no rays, flares, leaks or fake rain either.
5. No cartoonish look and no "condom ad" / kindergarten-advertisement feel.
6. It must not look AI-made or like "Claude with GitHub skills". No template transitions (whip, zoom-blur, light-leak, ripple, dip, shake).
7. KEEP the end part: the Minecraft multiplayer screen where the server is added/joined, then the end card. "Last part is awesome." (V4 dropped it, so it must come back.)
8. Thumbnail watermark: ONE mark is enough. The full tiling made it look like "a thumbnail in our watermark".
9. Video watermark: full-frame and see-through, so the video can't be uploaded to YouTube, but not extreme.
10. Thumbnail note from Leon: "the sky feels fake". That belongs to the thumbnail session.
11. Earlier notes still stand:
    - Fonts are judged first: no Montserrat, no Lilita, no glossy cartoon logo, no pixel type over footage.
    - The swim -> dive underwater moment is the favourite.
    - Music is Neon Laser Horizon.
    - Server facts: Java `pm-twirl.gl.joinmc.link`; Bedrock `listed-completing.gl.at.ply.gg`, port 35634; Bedrock names start with "." (.Steve).
    - The music credit is required.

## Why V4 still reads as AI-made (diagnosis)
- Text treatment is the giveaway:
  - glowing Cinzel with a light sweep, plus a centred, wide-tracked caps subline under every caption, plus a dark scrim. That is the stock "AI trailer" look.
  - Captions like "A WORLD OF WATER" are also generic.
- The advancement toast lands on a calm underwater shot as a gimmick.
- The music runs on a flat loudness curve, with no breath and no real ending hit.
- The shots are cut to a fixed grid rather than to the action inside each clip, which makes it feel generated.

## V5 plan
- **Footage:**
  - About 10 shots, 4-7 s each, each clip used once, picked from the best moments (analysis/v7/clip_stats.txt).
  - Proposed order: c31 sun glare -> c1 golden island -> c28 raft -> c5 sailing -> c8 swim -> dive (whole) -> c13 shader light -> c10 reef -> c29 raft at sea -> c26 sunset -> multiplayer screen -> end card.
  - Cut on the motion inside the clip (a turn, a jump, the dive), not only on the bar line.
- **No added effects:** no overlays and no grade. The only transitions are straight cuts, with one slow dissolve into the end.
- **Text, kept minimal and human:**
  - The TIDES title once, plain: no glow, no sweep, no scrim.
  - No mid-video captions, or at most one short line.
  - No toast.
- **End:**
  - Bring back the V2/V3 multiplayer server-join sequence (overlay_v2.info_screen, about 6-8 s), then the end card. The end card keeps the big addresses and the credit.
  - Total about 52-55 s.
- **Music:** Neon Laser Horizon. Start on a quiet bar, swell into the dive, and end on a real hit at the end card. Gentler loudnorm, so the loudness range (LRA) is at least 7.
- **Watermark:**
  - Video: the current full-frame light tiling plus the drifting mark (watermark.py, video mode).
  - Thumbnail: a single centred "MediaSynx" mark only.
- **Verify before sending:**
  - ffprobe;
  - ebur128;
  - a 2 fps sheet;
  - a scdet check that no clip repeats;
  - a still of the end sequence.

## Files
- Scripts are in `tides-trailer/`: `timeline_v2.py` (currently V4), `overlay_v2.py`, `render_v2.py`, `audio_v4.py`, `watermark.py`, and the render scripts `C:/Users/Siddharth D/tides-work/render_v4.sh`.
- Backups: `*_V2backup.py` and `*_V3backup.py`. The V3 timeline has the info-screen timing (INFO, INFO_REF=8.6).
- Renders: launch them detached with PowerShell `Start-Process`. Background shells die when a session ends.
