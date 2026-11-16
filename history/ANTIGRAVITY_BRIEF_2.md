CONTEXT BRIEF — Tides SMP Minecraft server trailer (deadline today 8:30 PM)

WHAT THIS IS
A ~50 s trailer for "Tides SMP", a water-world Minecraft survival server (Java + Bedrock). I'm the editor
(Discord name "Bio"); Leon and notkvd are the client. Built so far by Claude Code with a Python pipeline
(numpy/OpenCV compositor + ffmpeg), NOT an NLE. I want your critique and a concrete edit plan, not tool lists.

THE FOOTAGE (all the source I have — please don't suggest shots that aren't here)
31 raw shader clips, ~10 s each, 1080p60, NO audio tracks. Water-world only: no redstone, pets, interiors,
elytra or campfires. The good ones:
- c31 sun glare on water   - c1 golden island, slow camera move (13 s)   - c28 raft, the most motion
- c5 sailing under clouds  - c8 player swims then DIVES under (client favourite, dive at ~7.5 s)
- c13 underwater shader light   - c10 coral reef   - c29 raft at open sea   - c26 sunset   - c14 bright sea
- c25/c27/c30 more sea/islands; c6, c9, c12, c15-24 are dark night clips (mostly unusable)
Footage already has shaders. Client wants it untouched (no grade, no overlays on it).

MUSIC: "Neon Laser Horizon" by Kevin MacLeod, 160 BPM (CC BY 4.0, credit line required on the end card).
Song has a breakdown at 65-75 s and a drop at 75.06 s.

SERVER FACTS (must appear on the end card)
Java: pm-twirl.gl.joinmc.link | Bedrock: listed-completing.gl.at.ply.gg port 35634 | Bedrock names start with "." (.Steve)

THE CLIENT'S ACTUAL WORDS (Discord, today)
- "make it look less like a condom ad", "no cartoonish shit", "no repetitive clips", "don't reuse the same clips"
- "last part is awesome / dont [remove it] / keep end part" -> the ending = a recreated Minecraft multiplayer
  screen where the server gets added/joined, then an end card with the IPs. This MUST stay.
- "I'm gonna beat your ass up if I see claude make you a video again" -> it reads as AI-made
- "holy advertisement", "1 should be enough", "there's a thumbnail in our watermark" -> about the THUMBNAIL
  watermark (it was tiled all over). Thumbnail gets ONE centred mark. The VIDEO preview must stay
  full-frame watermarked (light tiling) so it can't be reuploaded before payment.
- "the sky feels fake" -> about the thumbnail, handled separately.
Earlier client notes: length ~50 s; fonts are judged first (they rejected Montserrat, Lilita, cartoon/glossy
logos, pixel fonts over footage); keep it calm.

VERSION HISTORY — what was wrong
- V1: slow crossfades + text -> "no edit, AI slop".
- V2: 89 s, the same raft/sunset clips repeated 3+ times, ~4 s of black at the end, garbled text line.
- V3: 90 s, 74 fast cuts recycling the same clips, bubble/god-ray/lens-flare/light-leak overlays on the shader
  footage, whip/zoom/ripple template transitions, bouncy scale-pop captions -> "AI slop", "condom ad".
- V4: 50 s, 12 long clips, no overlays, BUT: glowing Cinzel serif title with a light sweep, a dark scrim behind
  every caption, generic captions ("A WORLD OF WATER / every island is earned"), a fake "Advancement Made!"
  toast on a calm shot, flat music loudness with no real ending, cuts on a fixed 1.5 s bar grid. It also
  dropped the multiplayer ending. User: still looks AI-generated.

V5 (just rendered, 54.75 s, not yet reviewed)
0-4.5 c31 sun glare (quiet open) | 4.5-9 c1 golden island + plain "TIDES" title, no glow/sweep/scrim
9-13.5 c28 raft | 13.5-17.25 c5 sailing | 17.25-25.5 c8 swim -> dive, the dive lands exactly on the song's
drop at 22.5 s | 25.5-30 c13 underwater light | 30-34.5 c10 reef | 34.5-39 c29 raft at sea | 39-43.5 c26 sunset
| 43.5-54.75 c14 (blurred) behind the multiplayer server-join screen, then the end card + music credit.
Straight cuts, one slow dissolve into the ending. Each clip once, real speed. No captions, no toast.
Music: quiet open, swells through the breakdown into the dive, one-beat breath, then a hit on the end card.
-14 LUFS, LRA 7.4.

THE OPEN QUESTION
My own feeling: "there should be a lot of different kinds of text, like text behind a character, learn from
typography edits; the effects were done wrong; the clips aren't used to their full potential, they're great
clips but the edit made them sloppy." The client never asked for more text. V5 removed almost all of it.

TOOLBOX — every repo/tool available, and what it would do on THIS edit
Machine: Windows 11, CPU only (no CUDA GPU). Pipeline language: Python + ffmpeg. 5 hours left.

A. Installed and working now
- ffmpeg (xfade, scdet, ebur128, loudnorm, drawtext with fontfile) — cutting, encoding, loudness, cut checks.
- Custom Python compositor (numpy + OpenCV) — renders every frame, so any per-frame effect or mask is possible.
- librosa — beats, onsets, sections of the song: cut on real hits, not a fixed grid.
- rembg (U^2-Net / isnet) + mediapipe — per-frame subject masks: "text behind the player / behind the island".
- transformers + torch (CPU) — SAM/segmentation models for cleaner masks (slow on CPU: ~1-3 s/frame).
- scikit-image, Pillow — typography rendering, kerning, masks.
- moviepy — quick test assemblies.
- HyperFrames (HTML + GSAP -> MP4, installed in the project) — designed kinetic typography layers rendered to
  alpha and composited over footage (learned: its shader transitions render black on <video>, so footage
  transitions stay in ffmpeg/Python).
- Blender (via MCP, on the user's machine) — 3D title/logo, camera-projected text placed "in" a shot.

B. From your list — what each would do here (and whether it fits)
1. remotion — same role as HyperFrames (code typography). Redundant; HyperFrames is already set up.
2. FFmpeg — in use.
3. motion-canvas — code motion graphics; redundant with HyperFrames.
4. moviepy — installed.
5. mlt / 28. olive / 29. kdenlive / 22. shotcut — NLEs/engines. Could export an MLT XML timeline so a human
   can fine-tune cuts in Kdenlive/Shotcut. Not installed.
6. libopenshot — same niche, skip.
7. PySceneDetect — confirm no clip repeats + find exact in-clip moments. pip-installable in a minute.
8. lossless-cut — manual GUI scrubbing; the user could pick in/out points by hand.
9. auto-editor — trims dead/still parts by motion. Could rank which seconds of each clip move most.
10. LiveCV — not needed (OpenCV already).
11. librosa — in use. 12. aubio / 14. madmom — better onset/downbeat tracking; pip-installable.
13. demucs — split the song into drums/bass/other: cut on drum hits, drop drums under the dive for a real
    breakdown, bring them back on the hit. CPU ~2-4 min per song. High value.
15. rife-ncnn-vulkan / 18. vs-rife / 17. VapourSynth — frame interpolation for clean slow motion (e.g. the
    dive at 0.5x without stutter). Vulkan build may run on the integrated GPU; not installed.
16. Real-ESRGAN — upscaling; footage is already 1080p, so only useful for punch-in crops (zoom to 130%+).
19. gl-transitions / 20. ffmpeg-gl-transition — GLSL transitions. The client hates template transitions, so at
    most one subtle luma wipe; the ffmpeg build here has no gltransition filter (xfade has ~40 built in).
21. Natron — node compositor (tracking + roto). Planar tracking would let text stick to the island/raft.
    OpenCV feature tracking can do the same in-pipeline.
23. ReplayMod / 24. Iris / 25. DistantHorizons / 26. Chunky / 27. sodium-extra — need access to the server
    world to record NEW footage (smooth camera paths, LOD vistas, path-traced stills). We have no world access
    and 5 hours, so not usable unless the client re-records.
30. OBS — re-recording; same as above.

QUESTIONS FOR YOU
1. Is V5's direction (clean, almost no text) right for this client, or does it need designed typography?
   If typography, use the toolbox above: say exactly where each piece goes (timestamp + clip), what it says,
   font, size, how it moves, and whether it sits behind the subject (rembg/SAM mask) or is tracked to the
   scene (OpenCV/Natron tracking) — without it reading as "advertisement" or AI.
2. Shot by shot: how to use each clip to its full potential (in/out points, hold vs cut, match cuts, punch-in
   crops, slow motion via RIFE) using only the footage listed.
3. Music: how to use demucs stems + onset detection for the swell, the breakdown under the swim, the dive hit
   and the end-card hit.
4. What makes an edit read as AI-made versus human-made, and the exact rules to avoid it in a scripted pipeline.
5. Rank the toolbox items by value-per-hour for a 5-hour deadline on CPU; say which to skip.
Be specific to this footage, this client and this machine. Don't add repos that aren't listed here.
