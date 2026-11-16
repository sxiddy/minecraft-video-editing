# REVIEW opus_3: Tides SMP V2 MASTER (59.25 s) vs RuneSpire reference (48.7 s)

Evidence is in analysis/v4/review/: ours_sheet.png and ref_sheet.png (2 fps contact sheets, 5 s per row), ours_hook.png (12 fps, 0-3 s), ours_drop.png (24 fps, 13-15 s), ours_39_48.png, ours_end.png and ref_hook.png.
**I cannot listen.** Every audio statement below comes from ebur128 and per-second astats, both full band and below 120 Hz. Text sizes are estimated from 320 px thumbnails, so they are accurate to about ±0.5% of frame height.

## Measurements
| | OURS | REF |
|---|---|---|
| Cuts at scene>0.3 | 11 (1.5, 1.68, 1.97, 13.88, 14.35, 39.75, 43.88, 44.35, 45.37, 45.75, 46.5) | 15, on a ~1.6 s grid |
| Cuts at scene>0.12 | 45 | 23 |
| Integrated loudness / LRA | -13.6 LUFS / **5.3 LU** (opus_2 measured 2.2) | -15.6 LUFS / **12.0 LU** |
| Per-second RMS | 0-13 s: -14 to -20. 13-56 s: flat at -12 to -18, with a periodic -17 dip every ~6 s. Outro fade 56-59 s. | Build at -18 to -35, a -41 hole at 20 s, a DROP at 22-42 s (-13 to -16), outro fade |
| Below 120 Hz RMS | -15 to -22 for the whole film. One -37 hole at 13 s (the pre-drop gap, which is good). | The build falls to **-49 to -56** (bass removed), then the drop comes in at -14 to -20 |

On mean level below 120 Hz, ours is -16.3 dB and the reference is -20.5 dB. Our bass is therefore present at all times. That is the problem: with no contrast, the drop has no weight. The reference strips its bass out completely in the build, which makes the drop feel huge.

## Did the opus_2 fixes land?
| opus_2 fix | Status |
|---|---|
| Bright, saturated frame 0 | **PARTIAL.** It now opens on a sunrise island instead of black, but the frame is still dark and tree-heavy on the left. |
| Logo flash and settle | LANDED (cuts at 1.5, 1.68, 1.97). The logo is still held about 4 s (2-6 s). |
| Cap shot length | **NOT LANDED.** 6-8.25 s is still an empty ocean. 14.4-27 s is about 12.6 s of the same grey storm sea with no cut above 0.3. |
| Dynamic arc / dip before drop | **PARTIAL.** The low-band hole at 13 s and the white flash at 13.9 s are real, but after the drop the RMS is as flat as before. LRA rose from 2.2 to 5.3; the reference is 12. |
| Grade variety | PARTIAL. Sunset gold (40-42 s) and underwater god rays now break up the grey. The storm block is still monochrome. |
| Shorten the menu sequence | **NOT LANDED.** 50-55 s is still about 5 s of server-list screen recording. |
| Bigger captions | **NOT LANDED.** "SURVIVE THE OPEN SEA", "BUILD ON THE WAVES" and "JAVA + BEDROCK" are about 3% of frame height. The reference's "CAUGHT!" and "OPEN ALPHA" are 8-10%. |
| Length under 60 s | LANDED (59.25 s). |

## Scores (OURS / REF)
| Category | Ours | Ref |
|---|---|---|
| Hook | 6 | 8 |
| Pacing / beat sync | 5.5 | 8 |
| Shot selection / variety / framing | 5 | 8.5 |
| Camera motion | 5 | 7 |
| Transitions | 6 | 7 |
| Typography | 6 | 8 |
| Text animation | 6 | 8 |
| Game-UI / pop-ups | 7 | 8.5 |
| Colour grade | 6 | 8 |
| Structure / arc | 6 | 7.5 |
| Energy vs music | 4.5 | 8 |
| Sound design / mix / bass | 4.5 | 7.5 |
| Info clarity | 8.5 | 6 |
| End card / CTA | 7 | 7 |
| Polish / artifacts | 6.5 | 8 |
| Premium feel | 5.5 | 8.5 |
| **OVERALL** | **5.8** | **7.8** |

**Verdict: still below the bar.** That is up 0.6 from 5.2, but still 2 points behind the reference.

## Category detail (worse or equal), including what 10/10 would take

**Hook (6 vs 8).**
- 0-1.5 s is a static island with a dark tree mass filling about 40% of the left of the frame. Nothing moves, and there is no question for the viewer to want answered.
- Fix: 0-1.5 s becomes an underwater god-ray shot, or a low raft shot at golden hour.
  - Push in from 100% to 110% with an ease-in.
  - Add a riser that ends on the logo hit at 1.5 s.
- 10/10: the first 12 frames alone should make someone stop scrolling. Show motion plus a hint of the premise: one tiny raft in a huge ocean.

**Pacing (5.5 vs 8).**
- 6.0-8.25 s: an empty ocean held for 2.25 s.
- 14.35-27 s: about 12.6 s where only 0.12-level cuts register. Every shot is the same grey rain sea, so on screen it reads as one shot.
- 50-55 s: menu recording.
- Fix:
  - Cut 6-8.25 s down to 0.75 s.
  - Rebuild 14.35-27 s as 8 shots of about 1 s each, every one a different subject or angle: wave level, aerial, close-up of the raft, lightning, a hand placing a block, a drowned mob, a mast cam and the island ahead.
  - Speed-ramp the menu to 2.5 s.
- 10/10: no two adjacent shots share both framing and colour, and every cut lands on a kick or a snare.

**Shot variety (5 vs 8.5).**
- About 60% of the runtime is a horizon line through the middle of the frame with a small player in it. The player is under 5% of frame height at 8-13 s and 17-27 s.
- The reference alternates wide, close, macro and UI in every 1.6 s block.
- Fix: the player is at 25% or more of frame height in at least half the shots. Add over-the-shoulder, low-angle and drone-orbit shots.
- 10/10: about 20 distinct setups across 60 s.

**Camera motion (5 vs 7).**
- Mostly slow pans or locked-off shots.
- Fix:
  - Give every shot a 3-8% push or drift.
  - At the drop (13.9-16 s), add handheld shake of ±6 px for 12 f.
  - Use ReplayMod or Flashback orbit shots.
- 10/10: motion-matching across cuts, so the pan direction carries from one shot into the next.

**Transitions (6 vs 7).**
- The whiteout flashes at 13.6 s and 45.5 s work.
- Everywhere else is a hard cut between near-identical shots, which is why 34 of our cuts only register at the 0.12 threshold.
- Fix: add 2-3 designed transitions.
  - A water-surface wipe on the dive (~28 s).
  - A match-cut on the surfacing at ~37 s.
  - A 4 f zoom-blur into the flurry at 45 s.

**Typography (6 vs 8).**
- Lilita One is the right choice. At about 3% of frame height, though, the captions are illegible on a phone.
- The Montserrat subline is about 1.2% and unreadable.
- Fix:
  - Main captions at 7-8% of frame height.
  - Sublines at 2.6% or more, in SemiBold with tracking +40.
  - Drop shadow: 0 4 px 12 px, 60% black.
  - Centre the captions at 72% of frame height, not on the horizon line.

**Text animation (6 vs 8).**
- The captions appear and sit there.
- The scramble on "WHO YOU BRING MATTERS." at 47.5 s is good, but at that size nobody will notice it.
- Fix:
  - Scale pop from 115% to 100% over 6 f on the kick, overshoot to 98% and back to 100% (3 f), with a 1 f letter stagger.
  - Blur or slide out over 4 f on the next downbeat.

**Game-UI / pop-ups (7 vs 8.5).**
- The "Advancement Made" toast (31-35 s) is tiny: about 4% of frame height, top right.
- "ISLAND DISCOVERED!" (37-38.5 s) is the best text moment in the film.
- The reference's "CAUGHT! LEGENDARY" is huge, centred and paired with a minigame bar.
- Fix:
  - Toast at 7% of frame height, with a 6 f slide-in and a chime.
  - Add a second big centre pop, for example "STORM SURVIVED" at about 27 s.

**Colour grade (6 vs 8).**
- 14-27 s is one desaturated grey-teal block.
- The logo plate (2-6 s) is muddy brown with a heavy vignette.
- Fix:
  - Storm: lift the midtones by +0.3 EV and add lightning frames with cyan highlights.
  - Logo plate: halve the vignette and add +15 warm saturation.
- 10/10: one palette per act (gold → steel → emerald → gold) and no muddy frames.

**Structure (6 vs 7.5).**
- The arc reads: calm → storm → dive → discover → build → community → join.
- The storm act runs about 13 s, and the climax is only 2.5 s.
- Fix: storm 8 s, climax 5 s, menu 2.5 s.

**Energy vs music (4.5 vs 8).**
- After the drop, the picture energy stays flat for 30 s, and visual intensity never peaks again between 14 and 45 s.
- Fix:
  - Make 40-44 s a second build: strip the music to pad plus riser.
  - Hit the flurry at 44 s with cuts every 1.5 s, then 0.375 s.
  - Use 8 f cuts on the final bar.

**Sound design / bass (4.5 vs 7.5).**
- Below 120 Hz the level sits at -15 to -22 dB through the whole film. The only hole is at 13 s.
- The reference's build sits at -50 to -56 dB in that band, which is why its drop hits.
- No SFX transients are measurable: there are no RMS spikes on the pop-ups.
- Fix:
  - High-pass the music at 150 Hz from 6 to 13.4 s and from 41 to 44 s.
  - Slam the full band back with an 808 sub boom at 13.9 s and at 44 s.
  - Add SFX: a logo impact, dive splashes, whooshes on the whiteouts, a toast chime and menu UI clicks.
  - Target an LRA of 9-12 LU.

**End card / CTA (7 vs 7).**
- Clear, but the IP line is about 1.5% of frame height.
- Fix: IP at 3.5% in aqua, a 6 f type-on with a blinking cursor, and a 3 s hold.

**Polish (6.5 vs 8).**
- A ghosted whiteout frame at 13.6 s.
- The mouse cursor is visible at 50-55 s.
- Text collides with the horizon line.
- Fix: hide the cursor, clean up the whiteout frame, and reposition the text.

**Premium feel (5.5 vs 8.5).**
- It looks like survival POV footage, not cinematic camerawork.
- Fix: ReplayMod/Flashback camera paths, volumetric shaders and depth of field on close-ups.

## Genuinely better than the reference
- Info clarity: Java + Bedrock, the IP and the port are all shown, and the server-list demo teaches the viewer how to join.
- The raft-survival story arc is more coherent than the reference's feature montage.
- "ISLAND DISCOVERED!" works as a pop, and the underwater god-ray reef (31-37 s) is the best footage in the film.
- The loudness target is sensible at -13.6 LUFS.

## Fonts (individual ratings)
| Font | Attract. | Read. | Fit | Size | Anim. | Score | To reach 10 |
|---|---|---|---|---|---|---|---|
| Lilita One captions | 8 | 5 | 8 | 3 | 5 | **6** | 7-8% of frame height, drop shadow, scale-pop in and blur out on the beat, a subtle teal-to-white gradient |
| Montserrat subtitle | 6 | 3 | 7 | 2 | 4 | **4.5** | 2.6% or more in SemiBold, tracking +40, 85% white, fading in 4 f after the caption |
| Pixel logo | 8 | 8 | 9 | 7 | 6 | **7.5** | 14-16% of frame height, stroke plus bevel, a shimmer sweep, a 3 f chromatic split on the hit |
| End-card pixel type | 7 | 5 | 9 | 4 | 6 | **6.5** | IP at 3.5% in aqua, a type-on, more line spacing |
| Toast / pop-up type | 7 | 5 | 10 | 4 | 6 | **6.5** | Toasts at 7%, centre pops at 9%, a pop SFX on each |

## Section-by-section
| Section | Time | Score | Issue → what 10/10 takes |
|---|---|---|---|
| Hook | 0-1.5 | 5.5 | Static dark island → a bright moving hero shot with a push-in and a riser |
| Logo | 1.5-6 | 6.5 | Held 4 s on a muddy plate → 2 s hold, lifted grade, shimmer, cut on the downbeat |
| Intro | 6-13.5 | 5 | 2.25 s of empty ocean and a tiny swimmer → 5 shots of 1.5 s each with the player large, music high-passed |
| Storm drop | 13.5-14.4 | 7 | The whiteout plus the low-band hole works → add an 808 boom, a 12 f camera shake and a lightning frame |
| Storm | 14.4-27 | 4 | 12.6 s of the same grey shot with tiny captions → 8 s across 6 or more varied shots, captions at 7% |
| Dive | 27-30 | 6.5 | A water-surface wipe, a splash SFX, and a 50% slow-mo ramp for 0.5 s |
| Reef | 30-37 | 7 | Bigger toast, a chime, and one macro shot of the coral |
| Surfacing / pop | 37-39.7 | 7.5 | Match-cut on the surface and a bass hit under "ISLAND DISCOVERED!" |
| Build | 39.7-45 | 6 | Static shots and small captions → building time-lapses, captions at 7% |
| Climax flurry | 45-47.5 | 5.5 | Too short and repeats earlier shots → 5 s of new action cut at 6-12 f, on 1/8 notes |
| "Who you bring matters" | 47.5-50 | 6 | Text at 3% and no players on screen → text at 8% over a group shot of 3 or more players |
| Multiplayer screen | 50-55 | 5.5 | Slow, with the cursor visible → 2.5 s speed-ramp, zoom on the IP, key-click SFX |
| End card | 55-59.25 | 7 | IP at 3.5% in aqua, a type-on, a 3 s hold |

## Prioritised fix list
1. Rebuild the storm act (14.4-27 s → 8 s) with 6 or more distinct shots, the player at 25% or more of frame height.
2. Bass contrast: high-pass the music at 150 Hz from 6 to 13.4 s and from 41 to 44 s, with an 808 boom plus the full band back at 13.9 s and at 44 s. Target LRA 9-12.
3. Captions at 7-8% of frame height, sublines at 2.6% or more, drop shadows, placed at 72% of frame height.
4. Text animation: a 6 f scale pop on the kick, a 1 f letter stagger, a blur out on the downbeat.
5. Climax flurry extended to 5 s with new footage cut at 6-12 f.
6. Hook: a bright moving shot with a push-in. Logo hold cut to 2 s with a lifted grade.
7. Multiplayer screen speed-ramped to 2.5 s, cursor hidden, zoom on the IP.
8. Toast at 7% with a chime, plus a second centre pop at about 27 s.
9. SFX pass: impacts, splashes, whooshes, UI clicks.
10. End card: IP at 3.5% in aqua with a type-on and a 3 s hold. Cut 6-8.25 s down to 0.75 s.
