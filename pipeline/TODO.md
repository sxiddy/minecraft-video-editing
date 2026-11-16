# Pipeline toolkit: state on 2026-11-16

The toolkit is complete. Every script below was run on real media on 2026-11-16. The list of
scripts with their stage is in `MASTER_PLAN.md` section 1, "The toolkit".
`python setup/check_setup.py` passes every required item.

## Tested and working
`config.py`, `new_job.py` (+ `templates/`), `build_edit.py`, `palette.py`, `audit_footage.py`,
`record_screen.py`, `qc.py`, `analyze_music.py`, `slowmo.py`, `depth.py`, `matte.py`,
`mask_track.py`, `sfx_fetch.py`, `sfx_normalize.py`, `sfx_check.py`, `master_audio.py`,
`thumb_check.py`, `setup/check_setup.py`.
Minecraft only: `mc_skin.py`, `mc_sounds.py`, `blender_mc_rig.py`.

## Open items (none blocks starting a job)
- NVENC: ffmpeg 9.0.2 needs NVIDIA driver 610 or newer; the laptop had 581.86 on 2026-11-16 and
  the user was installing the update. `python setup/check_setup.py` shows which encoder is in use.
  Until NVENC works, previews encode with Intel Quick Sync through `config.fast_encoder()`.
- No full job has been run through the pipeline end to end yet (brief to delivery), on any
  model. `build_edit.py` was tested on a 9 s, 4-shot edit (cut, hblur, speed 1.5, fadeblack, one
  text, music, two SFX). Expect small fixes on the first real job; log them in `LESSONS.md`.
- `build_edit.py` does not do: speed ramps inside a shot, keyframed zoom/reframe, camera shake,
  animated or masked text, 9:16 reframing. Make those as separate clips (HyperFrames, ffmpeg,
  Blender) and place them in the edit file.
- SFX: the 115 sounds are normalised (`media-library/sfx_norm/`) and machine-screened with
  `sfx_check.py` (GPU env, CLAP): 87 match their category, 28 are flagged in
  `sfx_norm/check.json` (8 wrong_category, 5 weak_match, 15 late_start). Open
  `sfx_norm/listen.html` to hear the flagged ones; late_start ones need trimming before use.
- `record_screen.py` was tested on the desktop only (4 s, 1920x1080, 53 of 60 frames per second
  on a still screen). Check the frame rate on a real game take before a shoot.
- jmc2obj: the jar runs, but the only world on disk is a `26.3` save that it cannot read
  (exported 0 faces). Test it on a 1.21.x world when a client supplies one:
  `<java> -jar jMc2Obj-128.jar -o <out> -c=-2,-2,2,2 --offset=center <world>` with Minecraft's
  bundled Java at `%APPDATA%/.minecraft/runtime/java-runtime-delta/windows/java-runtime-delta/bin/java.exe`.
  Run it with the jar's own folder as the working directory: jmc2obj unpacks a `conf/` folder
  into whatever folder it is started from.
- Minecraft `Fabric 1.21.1` has never been launched with Iris + Sodium + Flashback. The user has
  to launch it once, confirm it starts, and pick a shader pack in Options > Video Settings.
- Tides V8.3 master and watermarked preview (in the original `Video Editing/deliver` folder): audio
  peak fixed on 2026-11-16 with the user's approval (-14.1 LUFS, true peak -1.5 dBTP, video stream
  byte-identical). The old files are kept beside them as `..._ORIGINAL_peak-0.1dBTP.mp4`. One
  `qc.py` check still fails: frame 0 luma 1.2 (the trailer opens on black). That needs a re-edit.

## Limits seen in testing (work around them, they are not bugs)
- `matte.py` picks the most salient thing, which includes HUD popups. Record with the HUD off, or
  use `mask_track.py` with a point on the subject.
- `mask_track.py` jumps to another object when the subject leaves the frame; end the range first.
- `analyze_music.py` found no drop of 4 dB or more in any of the ten songs tried so far. Those
  tracks score 0 to 3 out of 6; pick music with a real drop for trailers.
- `mc_skin.py` only finds Java accounts. Bedrock-only players: ask the client for the PNG.
