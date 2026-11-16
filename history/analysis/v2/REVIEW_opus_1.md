# V2 review (opus_1): why MUSICTEST_voxel-revolution (0-20 s) loses to RuneSpire

## Evidence
- Frame sheets (4 fps, 0-20 s): `analysis/v2/review/cur_sheet.jpg` (current) and `ref_sheet20.jpg` (reference).
- Scene-cut detection (scene > 0.25):
  - **Reference, 0-20 s:** cuts at 3.9, 5.5, 7.1, 8.7, 10.75, 11.85, 13.5, 15.1, 16.7, 18.4, 19.97. That is 11 hard cuts, about one every 1.6 s, and each one changes the subject.
  - **Current, 0-20 s:** cuts at 7.0, 7.47, 17.67. Only 3 register.
  - The EDL does cut every 2 beats (1.2 s). But almost every edit carries a whip, zoom, leak, fade or ripple, and the shots look alike, so most cuts don't register as cuts.
- Audio level (RMS in 0.25 s windows):
  - -38 dB at 0 s, rising in a straight line to -18 dB at about 11 s, then flat at -17 dB with no dips.
  - So the music is an 11 s fade-in with no drop.
  - No SFX transients line up with the cuts.

## Every way it is worse, most damaging first

1. **There's no content. It's 20 s of ocean with a tiny player (every shot).**
   - The reference shows a new idea on every cut: spawn, crate wall, fishing-minigame UI, "CAUGHT! LEGENDARY", combat VFX, an armour-set card, a build.
   - V2 shows horizon, horizon, raft, horizon, then grey horizon in rain. A viewer reads that as one shot, and it's the root of the "no edit" complaint.
   - **Fix:** structure the edit around features: sail, fish, dive the reef, discover islands, survive the storm, build. Each 1.2-2.4 s shot answers "what do I do on this server?"
   - Pull the 8-10 most distinct clips from `index.txt`: reef close-ups, raft with the player doing something, island arrival, rain.
   - Remove every horizon-only shot that has no subject in the middle third.
   - Where the footage has no gameplay, build the gameplay as graphics (see #4).

2. **The hook is dead (0.0-2.5 s).**
   - It's black, then murky underwater footage. The typewriter text "The world is shared..." is about 2% of frame height, and the music is at -38 dB.
   - The reference has a lit tunnel with god rays building to the logo by 4 s.
   - **Fix:** frame 0 must already be bright, moving and audible.
     - Open on the brightest reef shot at 1.3x, pushing in from scale 1.0 to 1.15 over 1.2 s with ease-out.
     - At t=0 add a sub "whoomp" and a foreground bubble burst. First hard cut by 0.8 s.
     - Remove the typewriter line, or set it at 7-9% of frame height, centred, in the heavy title font, popping in word by word on beats.
     - Start the music on a loud downbeat (move `MUSIC_IN`), never inside a fade.

3. **The music has no build and no drop, so the cuts have nothing to land on (0-11 s fade, flat after).**
   - The swells the EDL is designed around (B15, B31) don't exist as audio events in the render.
   - **Fix: music shape.**
     - No global fade-in longer than 0.3 s.
     - Add a 2-bar riser (noise sweep or reverse cymbal) that ends on the title frame.
     - Put a 1-beat dip before the drop (lowpass at 400 Hz, or silence).
     - On the drop frame, add an impact (sub boom plus crash).
   - **Fix: SFX.**
     - Whoosh on every whip, splash or "bloop" on water cuts, thunder on storm cuts, a UI tick on every text pop.
     - Mix SFX about 6 dB under music peaks.
   - **Check:** audio onsets should fall within 1 frame of each cut.

4. **There are no gameplay UI graphics, and the text is weak.** The title at 6-9.5 s is the only graphic.
   - The reference sells features with Minecraft-style pop-ups: CAUGHT! LEGENDARY with sparkles, item-name cards, minigame bars.
   - **Fix:** in `overlay_v2.py`, build 4-5 widgets in the same pixel font as the title:
     - "NEW ISLAND DISCOVERED" toast sliding in from the top
     - "CAUGHT! RARE FISH" with a fish sprite and sparkles
     - "DEPTH 32m" gauge on underwater shots
     - red "STORM INCOMING" warning with a flash
     - compass/speed HUD on the raft
   - **Animation:** 6-frame overshoot pop (scale 0 to 1.15 to 1.0), 2-frame white flash on the text, hold 1.2 s, then a 4-frame scale-out on the next cut. One widget per feature shot.

5. **Transition soup (every edit).**
   - Examples: a full white-out at 7.3-7.8 s, a blurry grey leak at 8.0 s, a ripple at 2.5 s.
   - A whip, zoom, leak, ripple or fade on almost every cut is exactly the "AI slop" look. The reference hard-cuts almost everything and saves one big kaleidoscope effect for a section change.
   - **Fix:** make 80% of transitions "cut". Allow only 3 specials in 20 s:
     - (a) a title impact: 6 frames of white at 60% opacity, not about 30 frames of full white;
     - (b) one underwater-to-surface splash wipe, using a displacement map that travels up the frame;
     - (c) one lightning-flash cut into the storm.
   - Remove "leak" and "fade" from section A.

6. **The title holds 3.5 s over a blurred mess (6.0-9.5 s).**
   - It drifts slowly over a flashing gradient with no picture behind it.
   - **Fix:** 1.2 s total.
     - Slam in on the drop: scale 1.6 to 1.0 over 5 frames, 3 px chromatic split, 8 px camera shake decaying over 10 frames.
     - Hold 0.6 s over a sharp, moving hero shot (raft at golden hour, 1x speed).
     - Hard-cut out on the beat. Reuse the logo in the end card.

7. **Every shot has the same framing.**
   - The player is a few pixels at frame centre, with the horizon on the middle line.
   - **Fix:** punch in 1.5-2.5x on the player (Lanczos resize plus a light unsharp mask). Alternate wide, medium and close on every cut. Put the horizon on a third, and tilt 3-6 degrees on handheld-style shots.

8. **The camera feels frozen.**
   - **Fix:** give every shot a planned eased move:
     - push 6-12% over the shot;
     - lateral slide 3-5% on raft shots;
     - 2-degree roll on the reef.
   - Add a 2-frame +3% scale bump on accent beats.

9. **The storm section is grey and flat (12.5-20 s).**
   - It's low contrast and desaturated, the player can't be read, and nothing happens.
   - **Fix:**
     - Grade it dark teal-blue: crushed blacks, lift -0.05, gamma 0.9.
     - Add lightning: +2 stops for 2 frames, then +0.5 stops for 4 frames, synced to thunder and snare.
     - Add a 2-depth screen-space rain layer with motion blur, plus spray.
     - Cap the section at 4 s in this 20 s cut.

10. **The colour is flat and doesn't match.**
    - Underwater shots are dull green, sky shots milky, golden shots orange-pink. The reference is punchy and saturated.
    - **Fix:** one grade over the whole cut:
      - S-curve contrast;
      - vibrance +20;
      - teal shadows, warm highlights;
      - matched black point (1st-percentile luma about 0.03 on every shot);
      - highlight bloom above 0.85;
      - 15% vignette;
      - 2% grain.

11. **Shot lengths ignore the musical phrasing.** The underwater opener sits 2.5 s with nothing happening.
    - **Fix:**
      - no shot over 2.4 s before the title;
      - 1.2 s cuts (2 beats) through the build;
      - a double-time run of 0.6 s cuts (4-6 shots) in the bar before the drop;
      - one 2.4 s hero shot after the drop.

12. **Speed-ramp artefacts and no motion blur (around 9.8 s and 17.6 s).** The ramps show ghosting from frame blending.
    - **Fix:** for slow-motion, use optical-flow interpolation (ffmpeg `minterpolate=mi_mode=mci`, or RIFE). For fast parts, simulate a 180-degree shutter by averaging 3-4 subframes. Never ramp below 0.5x without interpolation.

13. **The overlays (rays, bubbles, flare) barely read and only soften the image.**
    - **Fix:** make them motivated and strong, e.g. foreground bubbles crossing the lens at 2-3 sizes, with the near ones sharp. Otherwise remove them. No lens flare on overcast shots.

14. **The intro text reads like subtitles, not a trailer.**
    - **Fix:** heavy pixel font, 2-4 words per card, centred, kinetic.

15. **The final cut has no ending or call to action.** It needs a logo sting, the server IP in large text, and a "JOIN NOW" pop on the last downbeat.

## How to clearly BEAT the reference with this footage

- **Signature "tide" transition built in Blender.**
  - A voxel water wall made of cube particles rises and washes across the frame. Render it with alpha and composite it, with a big splash SFX.
  - Use it twice, at section changes only. The reference has no equivalent.
- **Voxel logo reveal.**
  - TIDES SMP built from water blocks rising out of the ocean, or draining away, with god rays from below.
  - It does what the RuneSpire tunnel-logo reveal does, but on-theme.
- **Split-level shot.**
  - A wavy animated waterline mask with the raft above and the reef below. It instantly says "two worlds".
- **Drum-fill montage.**
  - 0.3 s per cut: player, raft, fish, island, lightning, then the logo.
- **Minecraft advancement toasts** ("Advancement Made: Sea Legs"), with the real-style toast sound. Players read these instantly.
- **Underwater sound design.**
  - Lowpass the whole mix on reef shots, then snap to full band at the surface break.
  - This is the biggest single "felt" upgrade.
- **Calm-to-storm story arc as the energy curve.**
  1. Serene opening, still with punchy cuts (0-4 s).
  2. Build (4-8 s).
  3. Logo drop.
  4. Storm at maximum cut rate.
  5. Sunrise hero shot.
  6. Logo and IP.
  - This gives the trailer a narrative; the reference doesn't have one.
