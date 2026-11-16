# Tides SMP trailer — V6 final plan (for review)

This merges the Opus review with Antigravity's V6. It keeps V5.1's shots and order and adds real edit craft:
cut-on-motion, one ramp, sound design and one designed title. Music is 160 BPM, beat 0.375 s, drop at 22.5.

## Timeline
| Time (s) | Clip, source in→out | Cut / transition | Type | Sound |
|---|---|---|---|---|
| 0–3 | c31 1.5→4.5 | open, slow 108% punch-in over the hold | none | wind + water bed fades up; intro synths, drums stem out |
| 3–9 | c1 4.5→10.5 | hard cut on the beat; ends on the pan's 10.5 s motion peak | **TIDES** behind the island horizon (sky luma matte, so land occludes the letter bottoms). One letter per beat 3.0→4.5, tracking 12→24 over the hold, flat white ~90%. Fallback: plain tracked fade | — |
| 9–12 | c5 2.0→5.0 | hard cut matching c1's left→right drift | none | drums stem in full |
| 12–15 | c28 4.0→7.0 | lands on its 7 s motion peak; one hard 115% crop punch-in at 13.5 (cut, not an animated zoom) | none | song breakdown begins at 12.44 (drums drop naturally) |
| 15–22.5 | c8 0.0→7.5 | head goes under exactly at 22.5; optional 0.6x on the last 0.4 s | none | riser; low-pass on the music from 21.75 (2-beat breath) |
| **22.5** | c8 → c13 | **hard match-cut on the submersion = the drop** | none | splash SFX + drums/bass at 100%; underwater muffle on |
| 22.5–27 | c13 0.5→5.0 | — | none | muffle on |
| 27–31.5 | c10 5.0→9.5 | cut lands on the reef's 9.5 s motion spike (largest in the footage) | none | muffle off at 31.5 |
| 31.5–36 | c29 1.5→6.0 | hard cut | optional single line "JAVA + BEDROCK" (Inter Tight Medium 40 px, plain fade). Default: none | surfacing breath / splash at 31.5 |
| 36–41.25 | c26 2.2→7.5 | ends on the 7.5 s sunset spike | none | — |
| 41.25–54.75 | c14 blurred | 0.75 s dissolve | multiplayer join screen (unchanged, approved) → IP card snaps on the final hit at **50.25** → Kevin MacLeod CC BY credit | final hit at 50.25; tail |

Rhythm: 3 / 6 / 3 / 3 / 7.5 into the drop, then 4.5 / 4.5 / 4.5 / 5.25. The energy comes from cut-on-motion,
the punch-in, the match-cut and the sound, not from more cuts.

## Font
Inter Tight SemiBold (or Neue Haas Grotesk Display), all caps, wide tracking, flat white. No glow, no serif,
no sweep, no Black weight at huge sizes.

## Sound
- Stems (demucs, already split): drums stem out for 0–9, in at 9.
- Low-pass at 21.75–22.5, splash on 22.5, muffle 22.5–31.5, breath at 31.5, final hit at 50.25.
- -14 LUFS, true peak ≤ -1 dBTP. Static gain + limiter (no loudnorm).

## Banned (client feedback)
- slogans: NO MAINLAND, THE DEEP, EXPLORE…, BUILD/SURVIVE/CONQUER, THE OCEAN AWAITS
- the COORDINATES HUD; BREATHE pulses; elastic slams; beat pops
- bubbles, god-rays, flares, light leaks; whip/zoom/ripple transitions
- scrims; advancement toasts; reused clips; colour grade
- Montserrat / Lilita / Cinzel glow / pixel fonts

## Kept
- the multiplayer join ending + IP end card (Bedrock "." note)
- the full-frame preview watermark; the single centred thumbnail mark

## Tools
- HyperFrames (TIDES title, alpha render)
- sam2 or a luma key for the horizon matte
- pedalboard / ffmpeg for the muffle
- the existing numpy/ffmpeg compositor
