# Tides SMP: V2 rework (approved by the client)

The client rejected V1. The verdict was "no edit in it, looks like AI slop". Calm music does NOT mean zero editing.
V1 lives in deliver/TidesSMP_Trailer_MASTER_1080p60.mp4 (reference only, of what NOT to do).

## Fixed facts
- Server info, story beats and text copy: see FINAL_PLAN.md (section 4/5 copy and info stay; structure changes below).
- Java `pm-twirl.gl.joinmc.link`; Bedrock `listed-completing.gl.at.ply.gg` port `35634`; Bedrock names start with "." (`.Steve`).
- Music: Chill Wave, Kevin MacLeod, CC BY 4.0 (music-options/chill-wave.mp3, use 115.25 s onward, ~99 BPM, lift at +19.0 s, full groove at +38.25 s). Credit line required.
- Output: 1920x1080, 60 fps, 50–90 s. Everything must run locally, with no paid APIs.
- Footage: raw/clips/vid2 (31 clips, 1080p60). Index in analysis/index.txt, contact sheets in analysis/sheet1-7.jpg. The usable/rejected list is in FINAL_PLAN.md section 9.
- Client tone: very picky and impatient. Send progress screenshots often (SendUserFile).

## Video V2: what "edited" means here
1. Cut on the beat: shots of 1–2.5 s timed to the music's beat grid, with 2–3 shots pulled per source clip (~40 cuts, not 16).
2. Speed ramps on most shots (fast → slow-mo into the moment), with motion blur from frame blending on the 60 fps footage.
3. Real transitions, each with matching SFX (whoosh, riser or impact):
   - zoom-blur punch-ins
   - smooth directional-blur whip-pans
   - flash-to-white on the title drop
   - water ripple for dives and surfacing
4. Overlays:
   - underwater: god rays and floating bubbles
   - sunny shots: lens flares and light leaks
   - storm: rain streaks
   - hits: subtle camera shake
5. A 3D title "TIDES SMP" in Blender (match the thumbnail title style: Luckiest Guy, glossy aqua→white TIDES, gold SMP, thick navy outline; see thumb/title3d.py). Animate it in on the drop and render it as transparent video.
6. Kinetic captions: per-letter animation with glow, Kelvin-style (refs/sheet_kelvin_*.jpg).
7. The info section is a recreated Minecraft "Multiplayer" screen:
   - "Add Server" is clicked and the address types itself in.
   - The Tides SMP server row pops in with ping bars, for Java, then Bedrock.
   - Then the ".Steve" droplet note.
8. Keep the calm vibe (music and grade), but every second should show editing.

## Thumbnail V2: rebuilt fully in Blender
- Build a real 3D scene, not a screenshot:
  - a Minecraft-style character with a skin matching the footage (red and black outfit, dark hair; client said "use a character that would match")
  - ocean, raft (crafting table and furnace), sunset lighting
  - the 3D title
- YouTube-style: big chunky title, character large and expressive, saturated, high contrast, readable at 320x180.
- References: refs/thumbs2_sheet.jpg. Blender 5.2 is at C:/Program Files/Blender Foundation/Blender 5.2/blender.exe.
