"""Tides SMP V7 (= V6_PLAN.md): render the edit with the V5 pipeline, then add light grain to the footage
(0-42 s only; the join screen and end card stay clean) and the full-frame preview watermark. No captions.
python make_v7.py  (run from tides-trailer/)"""
import os, subprocess
W = "C:/Users/Siddharth D/tides-work/v2/neon-laser-horizon"
OUT = "../deliver/TidesSMP_Trailer_V8.2_MASTER_1080p60.mp4"
PREVIEW = "../deliver/TidesSMP_Trailer_V8.2_PREVIEW_watermarked.mp4"
env = dict(os.environ, TRACK="neon-laser-horizon", JOBS="10")
for cmd in (["python", "timeline_v2.py"], ["python", "audio_v5.py"], ["python", "render_v2.py"]):
    subprocess.run(cmd, env=env, check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/footage.mp4", "-i", f"{W}/sound.wav",
                "-map", "0:v", "-map", "1:a", "-vf", "noise=c0s=7:c0f=t+u:enable='lt(t,41.6)'",
                "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "320k", "-shortest", "-movflags", "+faststart", OUT], check=True)
print("WROTE", OUT)
subprocess.run(["python", "watermark.py", OUT, PREVIEW], check=True)
