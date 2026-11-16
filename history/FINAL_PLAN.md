# TIDES SMP — FINAL PLAN (locked)
Supersedes PLAN.md v1 and v2. Every decision is made here; the build follows this file exactly.

## 0. Basics
- **Runtime: 79.0 s** (picture 0.00–78.65, then 0.35 s black). Delivered at 1920×1080, 60 fps, H.264 High, CRF 14 (≈40–60 Mbps), AAC 320 kbps 48 kHz.
- **Story (four beats, timed to the music):**
  1. Tide in: 0–19 s.
  2. Open sea and storm: 19–38.25 s.
  3. Depths and building: 38.25–57.6 s.
  4. "Who you bring matters" and the info card: 57.6–79 s.
- **Motif:** one 1 px hairline, the "horizon". It draws across the horizon in s02, the TIDES title rises out of it, it sits between every caption's two lines, and it becomes the divider on the info card.

## 1. Music (client note: the last track was "too calm")
### How the candidates were analysed
Each track was decoded to mono and measured for RMS level in 4 s and 2 s windows (0.25 s around transitions) and for spectral-flux onset density.

| Track | Dur | Structure found | Verdict |
|---|---|---|---|
| almost-new | 202.6 s | flat −27 dB from start to end, no build | too calm |
| dreamer | 204.1 s | slowly decays −18 → −24 dB, loudest at 0 s | no swell |
| floating-cities | 184.1 s | very gentle rise −26 → −22 dB over 3 min | too calm (likely the old feel) |
| evening | 186.3 s | one small lift at 28–44 s (+4 dB) | weak |
| heartwarming | 72.0 s | loudest at the top, fades out | wrong shape |
| local-forecast (slower) | 199.5 s | flat −12 dB, dense all the way | busy, no arc |
| clean-soul | 306.7 s | sparse cinematic, −35 dB intro, peaks around −23 dB, very spiky | dynamics too uneven under text; quiet parts are almost silent |
| ascending-the-vale | 247.6 s | steady −21 dB, onset density builds at 56–80 s, peak density at 104–136 s | **backup** |
| **chill-wave** | 240.1 s | full groove −12 dB, then a **breakdown at 115.25 s (−26 dB)**, a **lift at 134.25 s (−19 dB)** and a **full return at 153.5 s (−12 dB)**. Pulse about 99 BPM (flux autocorrelation found 1.207 s per 2 beats); phrases ≈ 9.66 s | **PICK** |

### The pick: "Chill Wave" (Kevin MacLeod), CC BY 4.0
- **Track in point: 115.25 s.** This lands on the first frame of the breakdown, so the video opens on its soft, dreamy section. There are no edits and no loop; the track plays straight through.
- **Track out point: 194.25 s** (video 79.0 s).
- **Fades:** fade in 0.0–1.5 s (waves are heard first). Fade out from video 74.0 to 79.0 s, an equal-power curve (qsin).

Mapping: video time = track time − 115.25.

| Swell in the track | Video time | Visual beat locked to it |
|---|---|---|
| breakdown phrase 2 | 9.66 | TIDES rises out of the waterline |
| lift (+7 dB) | 19.00 | hard cut into the storm (s05, rain) |
| lift phrase 2 | 28.66 | SURVIVE THE OPEN SEA fully on |
| full return (+7 dB) | 38.25 | surface-break transition resolves into the reef (the dive) |
| phrase | 47.90 | BUILD ON THE WAVES fully on |
| phrase | 57.60 | "Who you bring matters." |
| phrase | 67.20 | info card rows land |
| phrase | 76.90 | everything fades out |

**Why this isn't "too calm".** The track rises about 14 dB in two clear steps (quiet breakdown, then a lift, then the full groove), and the edit's energy follows those steps. The texture is soft synth pads and a gentle pulse, so it stays dreamy and the edit never cuts on every beat. Only the two lift moments get a hard cut or a swell.

### Backup: "Ascending the Vale" (Kevin MacLeod)
Use it only if the client rejects the pick.
- In at 41.0 s, out at 120.0 s; fade in 2 s, fade out 5 s.
- It builds at about 56–80 s of the track (video ≈ 15–39 s) and is densest at 104–120 s (video 63–79 s).
- Keep the same scene table and shift only the text times by ±1 s to its phrases.

**Credit line** (in the YouTube description, and on screen 77.0–78.6 s in Inter 400, 16 px, 50 % white, bottom centre):
`Music: "Chill Wave" by Kevin MacLeod (incompetech.com) · Licensed under CC BY 4.0`

## 2. Segment prep changes (edit `tides-trailer/prep.sh`, then re-run it)
Grade, fps and CRF stay as they are. These changes buy the time needed so the beats land on the music anchors.

| id | clip | in–out | speed | result |
|---|---|---|---|---|
| s03 | 1 | 2.0–10.0 | **0.8** | 10.00 s |
| s05 | 3 | **2.0–5.0** | 1.0 | 3.00 s |
| s06 | 8 | 0.5–3.5 | **0.8** | 3.75 s |
| s07 | 11 | 3.0–8.0 | **0.8** | 6.25 s |
| s08 | 14 | 6.0–8.5 | **0.5** | 5.00 s (trimmed to 4.95 in the edit) |
| s16 | 29 | 0.0–9.5 | **0.5** | 19.00 s |
| **s17 (new)** | **2** | **1.0–4.0** | 1.0 | 3.00 s (rain swim that sinks below the surface) |

Other segments are unchanged: s01, s02, s04, s09–s15.

Slow-motion uses frame duplication, with no minterpolate (it smears pixel art). At 0.5× on 60 fps footage that gives 30 unique frames per second, which is acceptable at these calm speeds.

## 3. Scene table
Times are on the video timeline. The "In" of each shot overlaps the previous shot's tail by the transition length. Motion is applied in HyperFrames with a GSAP linear tween on the `<video>`: scale goes from 1.00 to the value shown, and the drift is translation over the whole shot.

| # | Video in–out | Asset (clip, source) | Speed | Motion | Text | Transition OUT |
|---|---|---|---|---|---|---|
| s01 | 0.00–4.50 | clip 30, 0.5–5.0 (underwater, looking up at the raft) | 1.0 | push 1.00→1.06 | L1 (§4) | **ripple-waves shader, 1.0 s** (3.50–4.50): the surface break, so the camera "breaks the surface" |
| s02 | 3.50–8.00 | clip 7, 1.0–5.5 (clear horizon, sun glints) | 1.0 | push 1.00→1.04, drift x −20 px | L2 + hairline draw | **light-leak shader, 1.2 s** (6.80–8.00): warm sun glints flow into the golden hour |
| s03 | 6.80–16.80 | clip 1, 2.0–10.0 (golden island) | 0.8 | push 1.00→1.10 toward the player | TIDES title | **CSS crossfade, 0.8 s** (16.00–16.80): calm and same-day, nothing to dramatise |
| s04 | 16.00–19.00 | clip 5, 3.0–6.0 (clear-sky swim) | 1.0 | push 1.00→1.05 | — | **hard cut at 19.00**: lands on the music lift; the jump from sun to rain is the point |
| s05 | 19.00–22.00 | clip 3, 2.0–5.0 (rainy open ocean) | 1.0 | push 1.00→1.04, drift y +12 px | — | **hard cut at 22.00**: rain to rain, so it reads as one storm |
| s17 | 22.00–25.00 | clip 2, 1.0–4.0 (rain swim, sinks under the surface) | 1.0 | push 1.00→1.05 | — | **CSS crossfade, 0.6 s** (24.40–25.00) |
| s06 | 24.40–28.15 | clip 8, 0.5–3.5 (rain swim) | 0.8 | push 1.00→1.05 | — | **CSS crossfade, 0.6 s** (27.55–28.15) |
| s07 | 27.55–33.80 | clip 11, 3.0–8.0 (reaching the pig island) | 0.8 | push 1.00→1.07, drift x +30 px | C1 SURVIVE | **CSS crossfade, 0.5 s** (33.30–33.80) |
| s08 | 33.30–38.25 | clip 14, 6.0–8.475 (pig close-up, a light beat) | 0.5 | push 1.00→1.04 | — | **ripple-waves shader, 1.0 s** (37.25–38.25): the dive and second surface break; it resolves fully underwater exactly on the drop at 38.25 |
| s09 | 37.25–40.25 | clip 8, 7.8–9.8 (sinking into the reef) | 0.67 | push 1.00→1.08 | — | **CSS crossfade, 0.8 s** (39.45–40.25) |
| s10 | 39.45–43.95 | clip 10, 2.0–6.5 (kelp and signposts, clouds above) | 1.0 | drift y −25 px (rising), scale 1.04 | — | **cross-warp-morph shader, 1.0 s** (42.95–43.95): fluid, like moving through water |
| s11 | 42.95–46.95 | clip 27, 1.0–5.0 (lantern pillar from below) | 1.0 | push 1.00→1.06 | — | **ripple-waves shader, 1.0 s** (45.95–46.95): surfacing again, up to the raft |
| s12 | 45.95–50.95 | clip 28, 2.0–7.0 (crane down onto the raft) | 1.0 | none (the camera already moves) | C2 BUILD | **light-leak shader, 0.8 s** (50.15–50.95): warm, leading into the firelight |
| s13 | 50.15–53.15 | clip 18, 0.0–3.0 (campfire, already lifted) | 1.0 | push 1.00→1.05 | — | **CSS crossfade, 1.0 s** (52.15–53.15) |
| s14 | 52.15–57.15 | clip 26, 0.0–5.0 (sunset tower) | 1.0 | push 1.00→1.06 | C3 CROSSPLAY | **domain-warp shader, 1.0 s** (56.15–57.15), intensity 0.25: dusk heat-haze melting into sea mist |
| s15 | 56.15–61.15 | clip 31, 1.0–6.0 (lone boat, moody clouds) | 1.0 | push 1.00→1.05, drift x −30 px | T1 "Who you bring matters." | **CSS crossfade, 1.5 s** (59.65–61.15): the longest, softest dissolve, into the ending |
| s16 | 59.65–78.65 | clip 29, 0.0–9.5 (mirror-calm raft and reflection) | 0.5 | push 1.00→1.03 (barely) | T2, lockup, info card | **dip to black, 1.65 s** (77.00–78.65), then 0.35 s black |

**Transitions not used, and why:** whip-pan, glitch, chromatic-split, swirl-vortex, thermal-distortion, flash-through-white, cinematic-zoom, gravitational-lens, sdf-iris and ridged-burn are all hype or stylised effects that break the calm brief.

**Opening:** fade from black 0.00–1.20 (CSS opacity on the full stack).

**Shader settings:**
- ripple-waves: amplitude 0.015, frequency 18, centre (0.5, 0.45).
- light-leak: warm amber `#FFB36B`, maximum opacity 0.55.
- cross-warp-morph: strength 0.3.

## 4. On-screen text (exact)
Shared style:
- Colour `#F4F1EA` with text-shadow `0 2px 18px rgba(0,20,30,.45)`.
- Everything is centred horizontally.
- Captions sit inside the letterbox area, with their baseline at y = 600.
- Every element enters with opacity 0→1, y +14→0 and letter-spacing +0.04em→its final value, over 0.9 s (power2.out). It exits with opacity 1→0 and y 0→−8 over 0.7 s (power2.in).
- No more than two lines are on screen at once (the info card is the only exception).

| id | Text | Font | Size / tracking | On (fully in) → off (fully out) | Animation |
|---|---|---|---|---|---|
| L1 | *The world is shaped…* | EB Garamond Italic 400 | 44 px / 0.02em | 1.30 (in from 1.3) → 3.80 | letter-by-letter opacity, 0.035 s stagger; blur 6→0 px (seen through water) |
| L2 | *…by the players who sail into it.* | EB Garamond Italic 400 | 44 px / 0.02em | 4.90 → 7.80 | same as L1, with no blur |
| H | hairline | 1 px `#F4F1EA` 70 % | 0→1200 px wide, centred on y = 540 | draws 4.60–6.20, sits on the sea horizon of s02, then stays as the TIDES waterline until 15.6 | scaleX from the centre, power3.inOut |
| TT | **TIDES** | EB Garamond 500 | 168 px / 0.38em | rises 9.66–11.10, holds, fades 15.0–15.8 | clip-path sine-wave mask (GSAP-animated SVG path, 2 waves across) reveals from under the hairline; mirrored copy below the line at 14 % opacity with blur 2 px and scaleY −1; displacement-filter ripple scale 8→0 over 1.4 s |
| TS | a water-world survival server | Inter 400 | 22 px / 0.32em, uppercase, 75 % | 11.0 → 15.6 | standard entry, below the hairline at y = 600 |
| C1 | **SURVIVE THE OPEN SEA** / *every island is earned* | Montserrat 600 / EB Garamond Italic | 34 px / 0.18em ; 28 px | 27.76 → 32.60 | standard; 160 px hairline between the lines draws first (0.4 s) |
| C2 | **BUILD ON THE WAVES** / *a home the tide can't take* | same | same | 47.00 → 50.40 | same |
| C3 | **JAVA + BEDROCK** / *one ocean, any device* | same | same | 53.00 → 56.20 | same |
| T1 | *Who you bring matters.* | EB Garamond Italic 400 | 64 px / 0.01em | 57.60 → 61.60 | word by word, 0.18 s stagger, slow (1.2 s per word, sine.out) |
| T2 | Invite friends · earn rewards | Inter 400 | 24 px / 0.30em, uppercase, 80 % | 61.90 → 64.40 | standard |
| LK | **TIDES SMP** / a NightClub Network server | EB Garamond 500 100 px, 0.30em ; Inter 400 18 px, 0.32em uppercase, 70 % | — | 64.40 in at centre (y = 470); at 66.40–67.20 it moves to y = 230 and scales to 0.62 | same waterline mask as TT; it stays as the info header |

## 5. Info segment (67.20 → 77.00, readable for 9.8 s)
The letterbox opens 63.60–65.10 to full 16:9 (bars slide out, power2.inOut), so the info gets the whole frame.

The background is s16, the mirror-calm raft, with a 30 % vertical gradient of `rgba(4,22,30,.0→.55)` from y = 380 to the bottom for legibility. There is no panel. Layout on 1920×1080, everything centred:

```
y=230   TIDES SMP          (lockup, from LK)
y=290   A NIGHTCLUB NETWORK SERVER
y=380   ───────────── 900 px hairline (60 %) ─────────────
y=450   JAVA                       Inter 600 18 px, 0.34em, 65 %
y=500   pm-twirl.gl.joinmc.link    JetBrains Mono 500 46 px, 100 %
y=590   BEDROCK                    Inter 600 18 px, 0.34em, 65 %
y=640   listed-completing.gl.at.ply.gg   port 35634
        (address JetBrains Mono 500 46 px; "port" Inter 400 22 px 60 %; "35634" JetBrains Mono 500 46 px)
y=760   ·  .Steve                  JetBrains Mono 400 34 px
y=810   Bedrock players: your name begins with a drop.   EB Garamond Italic 30 px, 85 %
```

Timing:
- 66.80: the hairline draws.
- 67.20: JAVA rows fade up.
- 67.80: BEDROCK rows fade up (stagger 0.6 s, power2.out).
- 69.00: **the droplet.** A 14 px teardrop (SVG, white with a 2 px teal `#7FD6D2` glow) falls from y = −20 to y = 760 over 0.7 s (power2.in). It lands where the period sits, in front of the pre-placed `Steve`, at 69.70. Two concentric rings (stroke 1.5 px, radius 0→60 px, opacity 0.6→0, 0.9 s, the second 0.15 s later) expand from that point. The drop shrinks into a "." that stays in the text colour.
- 70.00: the note line fades in.
- Everything holds until 77.00, then fades with the dip to black (77.00–78.65). The addresses are on screen and still for 9.8 s.

## 6. Sound

| Layer | Source | Where | Level (relative to music at 0 dB) |
|---|---|---|---|
| Music | Chill Wave 115.25–194.25 | 0–79 | 0 dB. Low-pass 900 Hz from 0–4.0, sweeping open to 20 kHz over 3.5–4.5 (the surface break). Ducks −3 dB over 67.0–77.0 under the info card |
| Ocean waves (synth: pink noise → LP 1.2 kHz, LFO amplitude 0.12 Hz) | local synthesis | 0–79; muted under water 0.0–4.0 and 38.25–46.0 | −20 dB; first 1.0 s solo before the music fades in |
| Underwater bed (brown noise LP 350 Hz + sparse bubbles) | local synthesis | 0.0–4.2 and 37.6–46.6 | −22 dB; fades 0.4 s |
| Rain (white noise HP 2 kHz, crackle-modulated) | local synthesis | 18.9–33.8 (fade in 0.2 s, fade out 1.0 s from 32.8) | −21 dB |
| Campfire crackle | local synthesis | 50.2–53.4 | −24 dB |
| Transition swells (reverse-swept noise, 0.8–1.2 s, LP 3 kHz) | local synthesis | 3.5, 37.25, 45.95 (ripples); 6.8, 50.15 (light leaks) | −24 dB |
| Surface splash / bubble burst | local synthesis | 4.45 and 38.2 | −22 dB |
| Droplet "plip" (sine 1.8 kHz → 900 Hz over 60 ms + 300 ms reverb tail) | local synthesis | 69.70 | −14 dB (the only spot effect that stands out) |

**Master:** −14 LUFS integrated, −1.0 dBTP, with a gentle glue compressor at 2:1. Earshot critiques the mix before sign-off.

## 7. Grade and finishing (ffmpeg, after compositing)
- The base grade is already baked into the segments by prep.sh (teal shadows, warm highlights, lifted blacks).
- **Bloom:** split → `gblur=sigma=18` → blend `screen` at opacity 0.10.
- **Grain:** `noise=alls=5:allf=t` (fine, temporal).
- **Vignette:** `vignette=angle=PI/5`.
- **Letterbox:** 2.39:1 bars, black, 139 px top and bottom, from 0.00. They slide open 63.60–65.10 and stay fully open to the end.
- Text is composited before the grain, so the grain sits over the text as well.

## 8. What is borrowed from the references
- **Kelvin trailers:**
  - Small centred two-line feature captions (bold uppercase sans plus a light line).
  - Cinematic letterbox.
  - Constant slow camera motion.
  - The logo and IP at the end, held long enough to screenshot.
- **Insta calm reel:**
  - The mood: soft lowercase-feeling serif lines appearing one at a time (L1/L2, T1), unhurried pacing, and rain and night as atmosphere rather than action.
  - Text that lets the footage breathe.
- **YouTube thumbnail sheet:** one big word centred over a beautiful frame (the Kelvin style, e.g. "Weekly Events"), not the cluttered face-cam style.

## 9. Clip usage (all 31 accounted for)
- **Used (16 clips):** 1, 2, 3, 5, 7, 8 (twice: rain half and reef half), 10, 11, 14, 18, 26, 27, 28, 29, 30, 31.
- **Left out on purpose:**
  - 4: duplicates 11 and 14 (the same pig island in rain).
  - 13 and 25: duplicate 27.
  - 22 and 24: night boats, near-black; lifting them shows noise.
  - 6, 9, 12, 15, 16, 17, 19, 20, 21, 23: too dark or empty.

## 10. Thumbnail (1920×1080, plus a 1280×720 downscale)
- **Source frame:** clip 1 at 9.5 s (the golden island: player by the crafting table, sun on the sea at left), with the same grade plus +0.15 exposure.
- **Layout:**
  - **TIDES** in EB Garamond 600, 300 px, 0.22em, `#FFF6E6`, centred at y = 470, with an outer glow of 40 px `rgba(255,190,110,.55)`.
  - A 2 px hairline at y = 590, 700 px wide.
  - **SMP** in Montserrat 700, 72 px, 0.6em, centred at y = 660.
  - A top-left tag at (80, 80): `JAVA + BEDROCK`, Montserrat 700 32 px, white text on a `rgba(4,40,50,.75)` rounded pill (r 999, padding 14/28).
  - A soft dark radial vignette behind the text for contrast at small size.
- No cut-out is needed: the player is already in the frame at right. rembg is not used.
- Rendered from HTML with playwright-cli. Check that it is legible at 320×180.

## 11. Deliverables and Google Drive
- `TidesSMP_Trailer_MASTER_1080p60.mp4`: clean.
- `TidesSMP_Trailer_PREVIEW_watermarked.mp4`: watermark treatment, applied as an ffmpeg overlay after the master:
  1. A tiled "MediaSynx" pattern: a PNG made with Python, Inter 600 40 px, white at **7 %** opacity, rotated −20°, on a 420×240 grid across the full frame.
  2. One drifting "MediaSynx" mark: Inter 700 72 px, white at **18 %**, moved with `x=(W-w)/2+560*sin(t/7)`, `y=(H-h)/2+300*sin(t/11)`, so it can't be cropped out.
- `TidesSMP_Thumbnail_1920.png`, `_1280.png`, plus watermarked copies (same tile at 10 %).
- **Drive** (uploaded with the Google Workspace skill):
  - "Tides SMP – Client Preview": the watermarked trailer and the watermarked thumbnails. This is the link that goes to the client.
  - "Tides SMP – Final (private)": the clean master and the clean thumbnails, released after payment.
- Put the credit line in the description text file that is uploaded with both.

## 12. Score and risks
**Score: 8.5/10.** The structure is locked to measured music swells, every cut is specified, the info is elegant and readable for 9.8 s, and the period note is memorable.

Risks and mitigations:
1. **Chill Wave has a steady synth pulse.** It could read as "lo-fi" more than "cinematic". Mitigation: render a 25 s test (video 0–25 s) and send it to the client first. Switch to the backup if needed; only the text times move.
2. **0.5× slow-mo on s08 and s16 shows 30 fps cadence.** Mitigation: both shots are near-static; if judder shows, use s16 at 0.6 and end at 75.5 s (info 67.2–75.0, which is still more than 7.8 s; raise the info start to 66.6).
3. **Shader transitions in HyperFrames need both clips decoded in the overlap.** Snapshot every transition midpoint with `npx hyperframes snapshot --at 4,7.4,37.75,43.45,46.45,50.55,56.65` before the full render.
4. **Clip 18 (campfire) is the darkest shot.** If it still looks muddy after the lift, cut it and extend s12 and s14 by 1.5 s each; the timeline is otherwise unchanged.
5. **Beat anchors assume the decoder start offset is accurate.** Verify by laying the music under the 38.25 surface break and checking the waveform in the render.
