# REVIEW opus 4 (FINAL round): Tides SMP Trailer V2 MASTER

Method: ffmpeg 2 fps contact sheet of the full 89.25 s (`analysis/v5/review/ours_2fps.jpg`), 6 fps strip of 0-8 s (`ours_0-8s.jpg`), 2 fps strip of 76-89 s (`ours_end.jpg`), reference at 1 fps (`ref_1fps.jpg`), scene-change detection, EBU R128 and a <120 Hz band measurement. **I can't listen.** The audio notes below come from meters only.

## Measurements
- Loudness: -13.8 LUFS integrated, LRA 5.1 LU, true peak -1.5 dBTP. Reference: -15.6 LUFS, LRA 12.0.
- Low band (<120 Hz) mean per 15 s window: -15.5 / -15.9 / -18.0 / -15.4 / -15.4 / -15.8 dB. Reference over its full length: -20.1 dB. The bass is about 4.5 dB heavier than the reference, so the "heavier bass" request has been met. There is a 2.5 dB sag at 30-45 s.
- Scene-change spikes at 2.63, 3.10, 5.63, 6.10, 38.63, 39.10, 68.63, 69.10. These are **four full-white flash frames**, at 2.67, 5.67, 38.5 and 68.5 s.

## Scores (ours vs reference = 7)
| Area | Ours | Note |
|---|---|---|
| Hook / opening | 6 | Static Manrope words on black for 2.6 s; no kinetic motion |
| Typo: kinetic words (Manrope) | 6 | Clean but default: same size and position, cut-on, no tracking or motion |
| Typo: TIDES title (Cinzel) | 8 | Strong. The scramble glyph "ϟ/>>" frames at 6.1 s look like broken text |
| Typo: kicker / sublines | 5 | About 1.2% frame height, unreadable at 1080p on a phone |
| Typo: captions (Cinzel caps) | 7 | Sun glint sits on the first letter ("W_O YOU BRING", "A WORLD") |
| Typo: pop-ups (STORM SURVIVED / ISLAND DISCOVERED) | 3 | Orange blocky pixel font **over footage**, which breaks client note 2 |
| Typo: advancement toast | 8 | Correct use of in-game UI |
| Typo: end card | 6 | TIDES is good; the IP and Bedrock lines are about 1.5%/1% tall and the credit line is microscopic |
| Text animation | 6 | Mask wipes are fine; nothing at Apple-kinetic level |
| Transition smoothness | 4 | Four white flash frames are hard and harsh, the opposite of note 3 |
| Pacing | 7 | Good montage at 3-5.8 s; dead holds at 21-24, 44-50 and 57-60 s |
| Shot selection | 6 | The sunset-pillar shot repeats 3x (21, 60, 74 s) and the raft top-down 3x |
| Camera motion | 7 | Smooth, but many locked-off ocean plates |
| Grade | 7 | Consistent, slightly milky in the rain section |
| Structure | 8 | Clear arc: cold open > title > features > join > card |
| Energy vs music | 6 | 160 BPM track but 2-4 s static holds mid-film |
| Sound / bass | 8 | Bass is up. LRA 5.1 is over-compressed and the drop has no punch (unheard) |
| Info clarity | 7 | Server-list sequence is clever; garbled "Bedrock pl(*$=" text at 83.5 s |
| End card readability | 5 | Fully legible only about 85.6-88.0 s (2.4 s), then fades |
| Polish / artifacts | 5 | White flashes, garbled UI text, glyph-scramble junk, glint collisions |
| Premium feel | 6 | The Cinzel direction is right; the pixel pop-ups and flashes cheapen it |
| **Overall** | **6.3** | Beats the reference on bass, structure and info; loses on polish |

### Section scores
- Cold open, 0-2.7 s: 5
- Flash montage, 2.7-5.8 s: 7 (minus the flashes)
- Title reveal, 6-11.5 s: 8
- Features and captions, 12-50 s: 6
- Pop-ups, 51-57 s: 3
- Build / Java+Bedrock / Who you bring, 60-80 s: 6
- Server-list info, 80-84 s: 7
- End card, 84-89.25 s: 5

## PRIORITISED FIX LIST

**P1. Remove all four white flash frames** (2.667, 5.667, 38.5, 68.5 s).
- Replace each with the underwater ripple/displacement transition the client liked: 12-16 frames at 60 fps, displacement amplitude 0 > 2.5% > 0, easeInOutSine, plus a 6-frame luma dip to about 15% brightness. Never use pure white.
- At 2.667 s, if you want impact, use a 4-frame exposure bump to at most 70% grey plus a 1.02 > 1.00 scale push instead.

**P2. Rebuild the pop-ups at 51-57 s** so there is no pixel font over footage.
- Option A: render STORM SURVIVED and ISLAND DISCOVERED as Minecraft advancement toasts, like the 30.5 s one (top-right, about 9% frame height), which the client allows.
- Option B: set them in Cinzel 600 at 6% height, warm white #F3EBDD, tracking +80, with the Manrope 500 subline at 2.4% height.
- Never orange gradient pixel text.

**P3. Cold open hook (0-2.7 s)** to meet client note 1.
- Each word should land on the beat (160 BPM = 22.5 frames per beat at 60 fps). Per-letter rise: 8% height y-offset to 0, opacity 0 > 1, blur 12 px > 0, stagger 2 frames, expo-out over 14 frames.
- Grow size per line: ONE OCEAN 5%, NO MAP 6%, NO WAY BACK 7.5%, then JUST THE TIDE in Cinzel 9% with tracking that animates +300 > +120.
- Add slow push-in scale 1.00 > 1.06 across 0-2.6 s and a faint ocean caustic texture behind the text at 6% opacity (black stays dominant).
- Exit each word with a vertical mask wipe of 6 frames, not a cut.

**P4. Make the end card hold** (84-89.25 s).
- Hold it fully visible for at least 4.5 s: from 84.6 s to 89.1 s, with the fade only in the last 0.15 s. Or extend the film to 90 s; the client allows up to 1:30.
- Java IP: 3.2% height, Manrope 600.
- Bedrock line and port: 2.6% height.
- "Bedrock names start with a dot": 2.0% height at 75% opacity.
- Music credit: 1.6% height at 50% opacity.
- Reveal stagger of 6 frames per line, all lines in by 85.4 s.

**P5. Fix the sublines and kickers everywhere.** "A SURVIVAL SMP", "JAVA · BEDROCK · ONE OCEAN" and the caption sublines go to at least 2.2% frame height (about 24 px at 1080p), Manrope 600, tracking +250, 85% opacity, with a 40% black soft shadow (blur 8 px).

**P6. Fix the caption and glint collisions.**
- Move "A WORLD OF WATER" (16-20 s) and "WHO YOU BRING MATTERS." (75-80 s) to centre-lower-third, or shift them right so the specular sun streak doesn't cross the first letter.
- Alternatively, add a local 25% darken vignette behind the text block (feather 30% width).

**P7. Clean up the title reveal glitch at 6.1-6.4 s.** The scramble shows junk glyphs ("ϟ", ">>"). Replace it with a letter-by-letter tracking collapse: +600 > +140, blur 20 > 0, scale 1.15 > 1.0, over 24 frames with expo-out. Add a 2% subtle chromatic split for 6 frames only.

**P8. Fix the garbled UI text at 83.0-83.8 s.** Remove "Bedrock pl(*$=" and the stray "Steve" chat overlay, or make it typed text that is real and readable. Typing speed should be 2 frames per character, with the cursor blinking at 30 frames.

**P9. Cut the dead holds and repeats.**
- Trim the static sunset 21-24 s to 1.6 s.
- Trim the rain plate 44-50 s by 2 s and insert one new action shot (building, fishing or combat).
- Replace the second and third uses of the sunset-pillar shot (60 s, 74 s) and of the raft top-down (63 s, 71.5 s) with unique footage.
- Keep every caption up for at least 2.5 s after it is fully revealed.

**P10. Audio (I can't listen; this is based on meters only).**
- Lift 30-45 s by 2 dB in the low band to remove the sag.
- Open dynamics to LRA of about 7-8 LU: reduce limiter gain reduction by 2 dB and target -14 LUFS integrated with -1.0 dBTP.
- Add a 6-frame sub-drop (50 Hz sine, -6 dB) under the title hit at 6.1 s and under the end-card hit at 84.3 s.

**P11. Grade.** In the rain section (39-50 s), add contrast +8, black point down 3%, and a slight teal shadow (#0E2A33) to stop the milky look.

Doing P1-P4 alone takes this from about 6.3 to about 8.5. All of P1-P11 should land at 9+ and clearly beat the reference.
