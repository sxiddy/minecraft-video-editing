"""V4 audio: the music alone (no synthetic SFX), Neon Laser Horizon from song beat 96, -14 LUFS.
TRACK=neon-laser-horizon python audio_v4.py -> WORK/<track>/sound.wav"""
import subprocess, pathlib
from timeline_v2 import TOTAL, MUSIC_FILE, MUSIC_IN
WORK = pathlib.Path("C:/Users/Siddharth D/tides-work/v2/neon-laser-horizon")
out = WORK / "sound.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{MUSIC_IN:.4f}", "-t", f"{TOTAL:.3f}", "-i", MUSIC_FILE,
                "-af", f"afade=t=in:d=0.4,afade=t=out:st={TOTAL - 1.6:.3f}:d=1.6,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000",
                "-ac", "2", str(out)], check=True)
print("WROTE", out)
