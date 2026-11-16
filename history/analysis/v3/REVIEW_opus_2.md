# REVIEW opus_2: Tides SMP V2 MASTER vs RuneSpire reference

Evidence is in `analysis/v3/review/`: O_/R_contact.jpg (2 fps sheets), O_/R_cuts.txt, O_/R_rms.txt (RMS per second), O_logo_strip.jpg and the O_f*.jpg stills.
I could not listen to the audio. Everything said about sound comes from ebur128 and per-second RMS, not from hearing it.

## Measurements
| | OURS | REF |
|---|---|---|
| Length | 62.9 s, 1080p60 | 48.7 s, 2160p60 |
| Cuts at scene>0.3 | 10 (1.6, 2.07, 16.07, 16.72, 40.3, 44.85-46.68 flurry) | 15, on a ~1.6 s grid |
| Cuts at scene>0.12 | ~40, roughly every 0.98/1.97 s (on the 122 BPM grid) | n/a |
| Integrated loudness | -13.9 LUFS | -15.6 LUFS |
| LRA | **2.2 LU** | **12.0 LU** |
| RMS curve | flat at -15 to -18 dB from 0 to 58 s. No dip and no drop. | -19 to -35 build (0-21 s), a -41 dB hole at 20 s, then a DROP to -13 to -16 (22-42 s), then an outro fade |

Most of our cuts only register at the 0.12 threshold. That means consecutive shots look almost the same (grey ocean into grey ocean), so on screen the cuts read as one long shot. The reference's cuts change the image completely.

## Scores (OURS / REF)
| Category | Ours | Ref |
|---|---|---|
| Hook (0-3 s) | 6 | 8 |
| Pacing / beat sync | 5 | 8 |
| Shot selection / variety / framing | 4 | 8 |
| Camera motion | 5 | 7 |
| Transitions | 5 | 7 |
| Typography | 7 | 8 |
| Text animation | 6 | 8 |
| Game-UI / pop-ups | 7 | 8 |
| Colour grade / consistency | 5 | 8 |
| Structure / story arc | 5 | 7 |
| Energy curve vs music | 3 | 8 |
| Sound design / mix | 3 | 7 |
| Info clarity (IP, Java + Bedrock) | 8 | 6 |
| End card / CTA | 7 | 7 |
| Polish / artifacts | 6 | 8 |
| Premium feel | 5 | 8 |
| **OVERALL** | **5.2** | **7.7** |

**Verdict: V2 does not meet the client's minimum bar.** It is roughly 2.5 points short.

## Category detail (all categories where we are worse or equal)

**Hook (6 vs 8).**
- 0-1.5 s is a near-black, murky frame. Then a white flash at 1.6 s and the logo at 2.07 s over a dim, desaturated island shot.
- The logo frame is muddy brown, with heavy vignette over a dark tree mass on the left. The reference's tunnel opens into light, so its first frame is already a striking image.
- Fix:
  - Open at frame 0 on the brightest, most saturated shot available: sunrise raft or underwater god rays.
  - Push in from 100% to 108% over 1.5 s.
  - Logo hit at 1.5 s with a 3 f white flash, then settle from 104% to 100% over 8 f.
  - Lift exposure on the logo plate by about +0.4 EV and cut the vignette by half.

**Pacing (5 vs 8).**
- The cuts are on the grid, but 2.07-15.7 s is effectively three shots: logo plate held about 4 s, then an empty ocean pan of about 4 s carrying a small subtitle line.
- 16-29 s is grey ocean and island shots that all look the same.
- 48.2-57.8 s is about 9.6 s with no cuts at all, the multiplayer-menu screen recording.
- Fix:
  - Cap any shot at 2 beats (0.98 s) in the build and 4 beats (1.97 s) elsewhere.
  - Cut the menu sequence to 4 s.
  - Every cut must change at least two of: location, scale, brightness, subject.

**Shot selection (4 vs 8).**
- Many near-identical wide, low horizon shots of flat sea with a tiny player in the centre: 7-14 s and 16-29 s.
- There are no close-ups, no faces or nametags, and no builds of any scale.
- The reference shows a spawn hub, crates, VFX, PvP and a fishing UI, so every shot is a distinct "feature".
- Fix:
  - Record or pick a close-up of the player (FOV 30), a low-angle raft build, an underwater over-the-shoulder shot and a storm lightning shot.
  - Drop at least half of the wide empty-sea shots.
  - The player should fill at least 25% of frame height in at least half the shots.

**Camera motion (5 vs 7).** The ocean shots are slow, generic drifts. Fix: add 3-6% punch-in zooms on beats in the main section, plus one fast whip or roll between sections. Speed-ramp two shots: 100% to 30% around a hit, then back up.

**Transitions (5 vs 7).**
- One flash at 1.6 s and one at about 40 s, plus soft dissolves at 7-9 s (the subtitle fade).
- There is no signature transition. The reference has its kaleidoscope warp at 8.7-10.7 s.
- Fix: build one signature "tide wash" (water wipe or wavy mask, 10-14 f) and use it at 15.7 s and 40.3 s only. Everything else should be hard cuts.

**Typography (7 vs 8).**
- The logo is good: pixel font with a blue gradient and gold outline, about 11% FH.
- The captions ("SURVIVE THE OPEN SEA", "BUILD ON THE WAVES") are a thin spaced sans at about 2% FH in the lower third. They are too small for a title tier and hard to read over busy water.
- The 7-14 s subtitle ("Shaped by the players who sail into it") is about 1.5% FH sentence case and reads as subtitles. This was flagged in review 1 and is still not fixed.
- Fix:
  - Section titles in the pixel font at 5% FH, centred, with a soft shadow and a 1.8% FH subline lagging 5 f.
  - Delete the sentence-case tagline or make it 2-4 words.

**Text animation (6 vs 8).** The captions fade in and out. The reference uses a per-letter decode and pop with sparkles. Fix: apply a 10 f random-order decode to every section title, sync a 3 f brightness pop to the beat, and exit with a hard cut.

**Game-UI (7 vs 8).**
- "ISLAND DISCOVERED!" at about 40.5 s and the "Advancement Made! Into the Deep" toast at about 33 s are good ideas.
- The toast is small, about 7% FH, top-right, and partly clipped by the letterbox edge.
- The pop has no sparkles, scale bounce or sound you can see in the frames.
- Fix:
  - Move the toast 2% down so it clears the letterbox.
  - Give the pop a scale of 60% to 110% to 100% over 8 f, plus sparkle particles.
  - Hold it 1.5 s.

**Grade (5 vs 8).** 16-29 s (storm and rain) is flat grey-blue with low contrast, next to warm sunset at 44 s and a teal underwater section. It looks like three different videos. Fix: unify with teal-orange, raise contrast by about 15% and saturation by about 10% on the storm. Add bloom on highlights and a consistent 15% vignette.

**Structure (5 vs 7).** The arc of calm, storm, deep, island, sunset and join exists on paper. On screen, the storm doesn't feel bigger than the calm section, and the menu sequence kills momentum right before the end. Fix: compress to 45-50 s. Storm becomes the max-energy section; the menu shrinks to 4 s, or goes in as a 2 s insert.

**Energy curve vs music (3 vs 8). The biggest gap.**
- Our RMS is flat from start to finish (LRA 2.2 LU). There is no build, no pre-drop silence and no drop.
- The reference falls to -41 dB at 20 s and then slams in at -15.
- Fix:
  - Start the music section 0-15 s about 6 dB lower, or lowpassed.
  - Put 0.5 s of near-silence (a riser tail) before the storm hit at about 15.7 s.
  - Land the drop on the downbeat with a boom and white flash.
  - Re-edit the music so the loudest section sits under the storm and montage.
  - Target LRA of at least 8 LU.

**Sound design (3 vs 7).** I can't hear it, but the flat RMS shows there are no audible impacts, whooshes or underwater lowpass dips. Fix:
- Whoosh on each section transition.
- Sub boom on the logo and the drop.
- Lowpass at 800 Hz under the underwater shots at 29-37 s.
- Toast "ding" and pop sparkle SFX.
- Rain and thunder under the storm.

**End card (7 vs 7).**
- Clean: logo, "JOIN THE TIDE", both IPs, and the music credit (O_f61.5).
- Static apart from the fade, with no per-letter decode.
- The Bedrock line is wider than the logo and looks crowded.
- Fix:
  - Decode the IPs letter by letter over 12 f.
  - Put Bedrock on two lines (address, then "port 35634").
  - Hold 3.5 s, then a 1 s fade.

**Polish (6 vs 8).** 1080p against 4K. Some flurry cuts at 44.85-46.7 s are only 0.4 s and land on similar frames. The 2 fps sheet also shows a small "blue block" overlay artifact at about 23 s and about 35 s (purple square at 1170,358 in O_f33.5). Check it and remove it if it isn't an intended particle.

**Premium (5 vs 8).** This follows from all of the above.

## Where ours is genuinely better
- Info clarity: both Java and Bedrock IPs, with the port, are legible on the end card. The reference shows only a tiny play.runespiremc.com.
- The multiplayer-screen "how to join" is a useful idea. It is too long, though.
- The logo design is on par with the reference.
- The diegetic toast and the "ISLAND DISCOVERED!" pop show the right instincts.

## Prioritised fix list
1. Rebuild the audio energy curve: quiet build, 0.5 s silence, drop at ~15.7 s, LRA of at least 8 LU.
2. Add the SFX layer: booms, whooshes, underwater lowpass, toast ding, thunder.
3. Cut the multiplayer-menu sequence from 9.6 s to 4 s or less.
4. Replace half of the identical wide-sea shots with close-ups, builds and storm or lightning. Every cut must visibly change the image.
5. New hook: bright, saturated frame 0, logo by 1.5 s, flash plus settle.
6. Grade the storm section up to match: contrast +15%, teal-orange, bloom.
7. Section titles in the pixel font at 5% FH, centred, 10 f decode in. Delete the sentence-case subtitle.
8. One signature tide-wash transition at the two section breaks. Everything else becomes hard cuts.
9. Pop and toast animation: scale bounce, sparkles, toast clear of the letterbox.
10. End card: per-letter IP decode, Bedrock on two lines, 3.5 s hold. Trim the total to about 50 s.
