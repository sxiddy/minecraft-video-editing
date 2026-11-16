# Tides SMP Trailer V3 MASTER: strict review (opus_5)

Evidence is in `analysis/v6/`: contact sheets `v_0..v_75.jpg` (V3) and `r_0..r_45.jpg` (reference), all at 4 fps, plus stills `s_*.jpg`.

## Measurements

| Metric | V3 (90.0 s) | Reference (48.7 s) |
|---|---|---|
| Hard cuts (scdet > 0.3) | 13 (3.0, 16.5, 18.8, 22.1, 28.3, 54.4, 57.8, 58.9, 61.1, 64.5, 65.6, 67.9, 76.5) | 15 in the first 41 s, regular about 1.6 s grid (3.9, 5.5, 7.1, 8.7 ...) |
| Cuts per 15 s window | 1 / 4 / 0 / 3 / 4 / 1 / 0 | 6 / 7 / 2 (then logo and outro) |
| Average shot length (visual, counting dissolves) | about 3.0-3.5 s | about 1.6 s |
| Integrated loudness / LRA | -13.8 LUFS / **4.9 LU** | -15.6 LUFS / **12.0 LU** |
| Black (blackdetect) | none flagged | logo fade only |

Most V3 transitions are dissolves or soft ripples, so scdet under-counts them. Even so, the contact sheets confirm the problem: holds of 3-4 s at most positions. The reference cuts on a strict beat grid, so its rhythm is legible. V3's isn't.

Fixed since REVIEW_opus_4:
- White flashes are gone.
- The orange pixel pop-ups are now Minecraft toasts.
- The garbled "Bedrock pl(*$=" is replaced by a real server-list UI sequence.
- The end card now holds about 5 s.
- The cold open now escalates from sans to serif.

## Scores (reference is about 8 for each category unless noted)

**1. Hook / opening (0-3 s): 5.** Small sans words ("ONE OCEAN.", "NO MAP.", "NO WAY BACK.") sit at about 2% height over near-black, low-contrast plates. On a phone they are unreadable, and the first meaningful image (the gold "JUST THE TIDE.") only arrives at about 2.3 s. The reference opens with a light-burst push into a lit gate, so there is motion and light from frame 1.
Fix: size the lines 5% / 6% / 7.5% of frame height, with JUST THE TIDE at 9%. Lift the plates' exposure +0.5 EV and add a 1.00 > 1.06 push across 0-2.7 s. Land each line on the beat (160 BPM = 22.5 frames).

**2. Pacing & rhythm: 4.** This is still the biggest failure. The "slideshow" note is not solved.
- The TIDES title sits for **about 8 s (6-14 s)** on two shots.
- "A WORLD OF WATER" holds 16-21 s over 4 shots, with the caption static the whole time.
- The underwater section, 30-45 s, is 15 s of one look.
- "SURVIVE THE OPEN SEA" holds 39-45 s on rain plates.
- 45-50 s are dark storm shots.

The reference never holds a shot more than about 2 s except on the logo.
Fix: grid cuts every 2 beats (0.75 s) in the 12-30 s and 54-72 s sections, and every 4 beats (1.5 s) elsewhere. Title hold max 3.5 s (6.0-9.5 s). Caption holds 2.5 s after fully revealed, then out.

**3. Beat sync: 4.** The cuts at 54-68 s look roughly on a grid, but 30-54 s has zero hard cuts across 24 s of music, so the beat isn't visible at all. Fix: put a cut or punch-in (1.00 > 1.08 over 4 frames) on every downbeat from 30-54 s.

**4. Shot selection & variety: 4.** The palette is narrow (open water, raft, sunset pillar, rain, kelp) with heavy reuse:
- Sunset pillar / raft-in-orange: 20-21 s, 23 s, 47 s (57 s grid), 62-63 s, 77-78 s. That's 4-5 uses.
- Raft top-down with sparkle: 18-19 s, 63-64 s, 66-67 s, 76-77 s. That's 4 uses.
- Island-with-trees golden: 6-11 s, 58-60 s, 60-61 s, 64-65 s.
- Kelp-plus-pillar underwater: 31-35 s, 40-44 s, 70 s.
- Flat open-ocean horizon: 12 s, 16 s, 26 s, 49 s, 61 s, 64 s, 72 s.

There's no people interaction, no building in progress, no combat, and no fishing. The reference shows hub, bosses, crates, fishing minigame, combat and builds, a new subject in every shot.
Fix: no clip used more than twice. Capture 8-10 new action shots (placing blocks on the raft, fishing catch, drowned fight, two players swimming, trident throw, building a dock) and slot them at 22-28 s, 45-50 s and 64-72 s.

**5. Transitions: 6.** The ripple and wave-warp transitions (about 21.5 s, 57.5 s, 59.5 s) are good and on-brief, and the swim > dive at about 27-30 s is still the best moment. Weaknesses:
- The horizontal wipe at 21 s (orange > teal, visible hard seam) looks like a default preset.
- The fades to dark at 46-48 s kill momentum.

Fix: replace the 21 s wipe with the ripple (12-16 frames). Replace the 46-48 s dark dips with a hard cut plus a lightning flash at 60% grey max, 3 frames.

**6. Typography, element by element.**
- **Cold open words: 4.** Manrope-like sans at about 2% height is too small, too thin, and grey on grey. The serif switch at "JUST THE TIDE." is good (gold Cinzel). Fix per the hook item above, and set the sans lines in Manrope 700, tracking +150.
- **TIDES title: 7.** The Cinzel-style serif with gold rule is clean and premium. It's let down by the A SURVIVAL SMP / JAVA · BEDROCK · ONE OCEAN lines at about 2.2%, which are fine on desktop and weak on a phone. It's also on screen too long (8 s) and sits over a motion-blurred plate that reads as smeared. Fix: 3.5 s hold; sublines at 2.6% height, weight 600; use a sharp, slow-moving plate.
- **Captions (A WORLD OF WATER, SURVIVE THE OPEN SEA, BUILD ON THE WAVES, JAVA + BEDROCK, WHO YOU BRING MATTERS.): 6.** The serif caps are consistent but always lower-third, always the same size (about 3.3%) and the same fade. Five identical slides is the "slideshow" feeling. Sun glints still collide with the first letters (16-20 s "A", 60-63 s "BUILD", 75-77 s "WHO"). Fix: vary placement (left third, centre, right third), scale the key word to 6%, and add a local 25% darken vignette behind the text.
- **Sublines (EVERY ISLAND IS EARNED etc.): 3.** About 1.1% height, unreadable on a phone. Fix: 2.2% minimum, Manrope 600, +200 tracking, 85% opacity, soft shadow.
- **Toasts: 7.** Authentic Minecraft advancement style, good. But six of them (Set Sail, Hold Your Breath, Into the Deep, Weather the Storm, Storm Survived, Island Discovered, Home on the Waves, One Ocean) each stay up 4-6 s, so the top-right is occupied about 50% of the runtime and it gets wallpapered. Fix: 2.5 s each (slide in 8 frames, hold, slide out 8 frames), keep max 4 toasts total, add the toast "ding" SFX.
- **End card: 6.** Hierarchy is good; JAVA IP in cyan at about 4.5% is readable on a phone. Problems:
  - The BEDROCK line runs nearly full width (308-1610 px) and is cramped.
  - "Bedrock names start with a dot" at about 2.5% grey is borderline.
  - The music credit at about 1.3% in a pixel/mono font is illegible and mixes a third typeface.
  - The black background is flat. The reference ends on a branded logo over imagery.

  Fix: split Bedrock into two lines (`BEDROCK  listed-completing.gl.at.ply.gg` / `PORT 35634`), credit in Manrope 1.8% at 55%, and a subtle slow ocean plate behind it at 20% opacity.

**7. Text animation: 5.** Typewriter reveal on the cold open and blur-fade on captions, both serviceable. Every caption uses the same fade in and out, and nothing reacts to the beat. The reference text slams in with scale and glow. Fix: caption in = tracking collapse +400 > +120 with blur 16 > 0 over 18 frames on the downbeat; out = 6-frame vertical mask wipe.

**8. Color grade per section.**
- Cold open: 5 (muddy, crushed).
- Title/golden: 7.
- Open water 12-30 s: 6. The orange sunset clips don't match the teal clips around them, so it reads as two shows.
- Underwater: 8, the best section.
- Storm 39-54 s: 4. Milky grey and low contrast, and 46-48 s is nearly black mush.
- UI and end: 7.

Fix: storm gets contrast +10, blacks -3%, teal shadows #0E2A33, lift mids at 46-48 s by 0.7 EV. Sunset clips get 20% desaturation toward teal-orange to blend.

**9. Game-UI popups (server list 79-84 s): 7.** This is a big improvement: real typing, real server entries, readable. It's a little long (5 s) and the UI is tiny on a phone. Fix: scale the UI 1.4x and punch in on the address field while typing. Trim to 3.5 s.

**10. Audio mix (meters only): 5.** At -13.8 LUFS integrated the level is fine for YouTube, but the LRA of 4.9 LU is heavily squashed against the reference's 12 LU. There's no dynamic drop before the title or the dive. Fix: limiter gain reduction -3 dB. Dip the music by 6 dB for 0.5 s before the 6.0 s title hit and the 27.5 s dive. Add whoosh and impact SFX on title, caption and toast hits. Target -14 LUFS / -1 dBTP / LRA 8+.

**11. End card readability on phone: 6.** See the end card item above.

**12. Overall: 5.5 / 10 (reference 8).** It's clean, on-brand and error-free, a real step up from V2. But it's still a slow, caption-driven slideshow with one shot palette, and it's nearly twice the reference's length with less content in it.

## Prioritised fix list

- **P1. Recut to a beat grid.** At 160 BPM: cuts every 0.75 s in 12-30 s and 54-72 s, and every 1.5 s elsewhere. No shot over 2.0 s except the title (3.5 s) and the end card. Target 45+ hard cuts (currently 13). Consider trimming the total to 60-70 s.
- **P2. Kill the repeats and add new footage.** Max 2 uses per clip (sunset pillar, raft top-down, golden island, flat horizon are all at 4+). Record 8-10 action shots (building, fishing, drowned combat, multiple players, trident) and place them at 22-28 s, 45-50 s and 64-72 s.
- **P3. Title.** Cut the hold from 6-14 s to 6.0-9.5 s. Use a sharp plate in place of the motion-blurred one. Sublines to 2.6% height.
- **P4. Cold open.** Lines at 5 / 6 / 7.5 / 9% height, Manrope 700. Exposure +0.5 EV. Push-in 1.00 > 1.06. Each line on a beat (22.5 frames).
- **P5. Captions.** Vary position and scale per caption. Animate in with a tracking collapse on the downbeat and out with a mask wipe. Sublines 2.2% minimum. Local darken behind the text to fix the glint collisions at 16-20, 60-63 and 75-77 s.
- **P6. Toasts.** 2.5 s each, max 4 total, with SFX.
- **P7. Storm section 39-54 s.** Regrade (contrast +10, teal shadows). Remove the dark dips at 46-48 s and cut on every downbeat with lightning flashes (max 60% grey).
- **P8. Audio.** LRA 8+ (back the limiter off by 3 dB). Pre-hit music dips at 6.0 s and 27.5 s. Add whoosh and impact SFX.
- **P9. Transitions.** Replace the 21 s hard-seam wipe with the ripple. Keep the swim > dive untouched.
- **P10. End card.** Split the Bedrock line into two. Credit in Manrope 1.8%. Add a 20% ocean plate behind. Trim the server-list UI to 3.5 s and scale it 1.4x.
