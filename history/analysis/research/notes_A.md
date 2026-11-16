# Notes A: Minecraft server trailer reference study

Sources: metrics_all.json, the 1 fps and 4 fps sheets, and new 8-12 fps crops I pulled with ffmpeg:
RUNESPIRE_ref/{logo_12fps, openalpha_12fps, endcard_12fps}.jpg and V0YxndnF0hg/{textcard_12fps, endcard_12fps}.jpg.
Sizes are estimated from the frames, as % of frame height (H). Frame counts assume the 12 fps sampling, so treat them as +/-1 sample (about 2 frames at 24 fps).
Not covered: audio was not analysed (no waveform listening; metrics audio_err). BPM and cuts-on-beat come from metrics_all.json only.

## RUNESPIRE_ref (client quality bar; 4K, 48.7 s, 16 cuts, median shot 1.65 s, 152 BPM, 75% of cuts on the beat)
- **Hook (0-3 s):** opens on black. A slow push-in down a dark stone corridor toward a lit throne room. God-rays bloom out from the vanishing point. No text before about 2 s.
- **Logo (about 2.5-4 s):** "RUNESPIRE" over a smaller "MC", centred, placed upper-middle over the throne. Font is a chunky pixel / Minecraft-style display face (Minecraft Ten / "Minecrafter" category), all caps.
  - Colour: vertical gradient, light cyan on top to deep blue below. "MC" uses a purple-to-violet gradient. Thin dark outline plus a 1-2 px dark drop shadow.
  - Size: grows from about 5% to 8% H over about 1.5 s (a slow scale-up of roughly 60%, matched to the camera push), with a subtle brightness shimmer. It fades in from the dark over about 6 frames. No per-letter animation.
  - Exit: a hard cut to the spawn exterior at 3.9 s, on the beat. The logo also appears in-world as a sign in the next shot.
- **Structure:**
  - 0-4 s: intro and logo
  - 4-8 s: world establishing shots (spawn, sunset forest, a kaleidoscope/mirror transition)
  - 8-20 s: feature montage, roughly 1.6 s per shot on the beat. Covers a warden dungeon, boss fight, crate wall, fishing minigame with a "CAUGHT! LEGENDARY" UI pop, and crate items with name tags
  - 20-22 s: "OPEN ALPHA" title card on black
  - 22-41 s: builds, then PvP combat (one long fight about 32-41 s)
  - 41-45 s: a glowing rune-circle VFX shot that fades out
  - 45-48.7 s: end card
- **Transitions:** about 13 of 16 are hard cuts (about 80%). There is 1 kaleidoscope/mirror warp transition (about 7-8 s), a fade to black before the end card, and a cut to black for the title. No whips or flashes.
- **Camera:** smooth slow dollies and orbits. Low-angle hero shots of builds. Third-person tracking during PvP.
- **VFX:** in-engine particle and beam effects (crossbow laser lines, rune circles), shaders with bloom and volumetric light.
- **Game-UI graphics:** a recreated fishing bar (yellow/green meter, "98%"). "CAUGHT!" in a gold gradient pixel font with sparkle stars, about 9% H, popped in, with "LEGENDARY" under it. Coloured floating name tags ("Gilded Echo Set", "Warden Set", "The Echo Crate") in the Minecraft font.
- **"OPEN ALPHA" card (about 20-22 s):** pure black background. Same pixel display face, cyan-to-blue vertical gradient with a thin gold/orange outline. About 6% H (cap height), centred.
  - In: rises from 30% to 100% brightness over about 3 frames, then brightens slowly with a light sweep (a gradient shimmer travels across it) for about 1.5 s. Barely any scale change.
  - Out: hard cut. Holds about 1.7 s.
- **End card (45-48.7 s):** black. Two lines in a pale-cyan pixel mono font: "JOIN NOW & CLAIM YOUR ALPHA TESTER ROLE" (about 2% H) and "PLAY.RUNESPIREMC.COM" (bold, about 2% H).
  - Animation: a **per-letter random decode**. Each glyph appears at a random time with a blur-to-sharp settle, about 10-12 samples (about 0.9 s) until the line is fully legible.
  - Hold about 2.5 s, then the video ends. The IP is shown as plain text with no box.
- **Grade:** rich, saturated, warm highlights, deep blacks, heavy bloom. Night shots lean teal/blue, day shots warm.
- **Music sync:** cuts land on a 152 BPM grid, about every 4 beats (1.6 s). This is the tightest beat sync in the set.

## Kelvin house style (all 6 videos share one template)
**Typography (shared):**
- Font: geometric sans, bold, ALL CAPS. Century Gothic Bold / Futura Bold class; "Avant Garde"-like round O's.
- Main line is pure white with a soft dark drop shadow, no outline. A smaller subtitle line sits under it (about 50-60% of the main size, wider tracking).
- Feature captions: cap height about 2-3% H, centred in the frame (dead centre or on the vertical middle).
- Titles and IP: about 4-6% H.

**Text animation (seen at 12 fps in V0Yx):**
- In: blur + fade over about 4-6 samples (8-12 frames at 24 fps), with a slight drift/scale (about 3-5%) and the text slightly skewed/tilted in 3D early on.
- Hold: about 1.5-2.5 s.
- Out: reverse blur-fade over about 4 samples.
- The card often sits on a blurred or grey background, and captions sit on footage that is defocused while the text is up.

**End card (all 6):**
- A per-letter 3D "scatter-assemble". Letters start scattered at random positions, depths and rotations across the frame, then fly together into place over about 1.2-1.5 s (about 15-18 samples), with blur on the moving letters.
- Content: server name (about 4-5% H), then "SERVER IP / WEBSITE / DISCORD" lines (about 1.5-2% H), then "RELEASE DATE", plus a tiny "TRAILER BY KELVIN" bottom-left.
- Holds about 4-6 s, then fades to black over about 1 s.

**Other shared traits:**
- Logo reveal: a 2D server logo fades/scales in over a defocused or dark background in the first 2-8 s.
- Transitions: mostly hard cuts plus defocus or blur-dissolves into text cards, occasional motion-blur whips, and dip-to-black between sections.
- Camera: constant slow drone glides, with heavy rack-focus / DoF.
- Grade: soft, low-contrast, pastel/haze. Lifted blacks in some, BSL/SEUS shaders.

### Per video
- **V0YxndnF0hg** (VaroxCraft Skyblock; 60 s, 36 cuts, median 0.96 s):
  - Hook: black, then a grey cloudy plate, a tiny logo dot zooming toward camera, and the full colour logo by 4 s.
  - Structure: alternates grey cloud-plate text cards (German captions, e.g. "KOMPLETT NEUES INSEL SYSTEM") with 1-3 s island shots. A black gap around 35-37 s. A lens-flare whip around 41 s. Scatter end card 50-55 s, then fade.
  - The text card has a small red dot accent under the caption and gets its own shot (not overlaid).
- **jCKhhZTL5Ww** (CityBuild Phoenix; 60 s, 13 cuts):
  - Hook: dark night village drift, then the gradient 3D "VAROX CRAFT" logo flies in at 7-8 s.
  - Flash to white at 9-11 s, black, then "CITY" with a white wipe.
  - Features are captions overlaid on shots (main word plus a subtitle, e.g. "NEUE PLOT / WELT").
  - Inventory-GUI screenshots are composited onto footage with a lower-left label ("NEUE EINSTELLUNGEN /settings").
  - Motion-blur whips around 40-43 s.
  - Big logo, then a huge "PHOENIX" (about 15% H) slides/scales down into "CITYBUILD PHOENIX / RELEASE 20.11.2020 17 UHR", which holds about 5 s.
- **eTp4PDZIgwo** (VaroxCraft general; 45 s, 9 cuts, median 4.4 s):
  - Hook: a 3 s black fade, then a dolly into golden doors, with the logo forming on the building at 6-7 s.
  - Captions overlaid at about 2% H ("SEIT 7 JAHREN ONLINE", "EINZIGARTIGE MINI-SPIELE").
  - Kaleidoscope/rotational warp transitions around 19 s.
  - End: "PLAY.VAROXCRAFT.DE" (about 4% H) with links, sun flare, fade out.
- **a_LowJGJZnY** (ZombieV; 60 s, 25 cuts):
  - Hook: a starfield black plate; a horizontal line expands into "PLAY.ZOMBIEV.NET" (scale-up) by 3-4 s.
  - Alternates black starfield caption cards (English, bold caps) with gameplay and GUIs.
  - Captions blur-out on exit (visible motion-blurred text at 13, 31, 37 s).
  - Scatter end card with a long social-links block.
- **mvh817RZXN4** (AimBlock HCF; 50 s, 11 cuts):
  - Hook: 6 s of near-black reddish haze, then the mascot logo zooms in from a point at about 7 s.
  - Captions are lighter weight with wider tracking ("KOTH & IMPROVISED EVENTS") at about 1.5% H.
  - Black gaps between sections.
  - End: logo left with "AIMBLOCK.EU / JOIN NOW" right, cherry tree, holds 6 s.
- **YSIg0fS_4i0** (VersusMC; 30 s, 6 cuts):
  - Hook: 2 s black, then a foggy blue reveal of a neon logo.
  - Captions are 2 lines ("EXPERIENCED / STAFF"), with some letters entering per-letter, falling from below ("GREAT" at 9 s).
  - Teal/foggy monochrome grade.
  - End: "VERSUSMC.CC / DISCORD / SOTW DATE", holds 3 s.

## Cross-video patterns (what the best share)
1. **Beat-locked hard cuts win.** RUNESPIRE is the best piece and has 75% of cuts on the beat, about 80% hard cuts, and shots about 1.6 s (4 beats at 152 BPM). Kelvin videos score 0-36% on the beat and feel floatier.
2. **Hook:** every video opens from black with a light-led push or reveal. The logo lands at 2.5-4 s in the best one; the weaker ones wait 6-8 s. Aim for the logo legible by 3 s.
3. **Typography that matches the IP beats generic sans.** RUNESPIRE uses a pixel display face with a vertical cool gradient, thin contrasting outline and drop shadow. It reads as "Minecraft" and premium. Kelvin's Century-Gothic white caps are clean but generic.
4. **Sizes:**
   - Logo 7-9% H (cap)
   - Section title on black 6-10% H
   - Game-UI pop ("CAUGHT!") about 9% H
   - Feature captions 2-3% H (main) and 1.2-1.5% H (subtitle)
   - End-card IP 2-5% H
5. **Timing:**
   - Text in: 6-12 frames (fade/blur), or a 3-frame brightness pop plus shimmer.
   - Holds: caption 1.5-2.5 s, title card 1.7 s, end card 2.5-6 s.
   - Out: hard cut (best) or a 4-8 frame blur-fade.
   - Per-letter end-card build: 0.9 s (decode) to 1.5 s (scatter).
6. **Diegetic game-UI graphics** (fishing meter, coloured item name tags, "CAUGHT! LEGENDARY") make the features feel real, not just captioned. This is the best device in the set.
7. **Transitions are rare.** Use hard cuts, plus one signature warp (kaleidoscope) and a dip to black for section breaks. Use at most 1-2 whips or flashes.
8. **Grade:** shaders with bloom and volumetric light, saturated warm/teal contrast (RUNESPIRE), rather than Kelvin's hazy pastel.
9. **End card:** black or defocused plate, centred, CTA line above the IP, letter-level animation, hold at least 2.5 s. To beat the references, put the logo on the end card and hold 3-4 s.
