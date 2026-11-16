"""V5 audio: Neon Laser Horizon only. The song's breakdown sits under the swim and its drop lands on the dive
(edit 22.5 s = song 75.06 s); a gain curve opens quiet and swells into the dive; a one-beat breath, then the
drop downbeat is spliced onto the end card and rings out. Normalised to -14 LUFS, true peak <= -1 dBTP.
TRACK=neon-laser-horizon python audio_v5.py -> WORK/<track>/sound.wav"""
import subprocess, pathlib, json
import numpy as np
from timeline_v2 import TOTAL, MUSIC_FILE, B, TEXT
WORK = pathlib.Path("C:/Users/Siddharth D/tides-work/v2/neon-laser-horizon")
SR, DROP_SONG, DIVE = 48000, 75.0634, B(60)
T_IN = DROP_SONG - DIVE
END = TEXT["END"][0]

STEMS = pathlib.Path("C:/Users/Siddharth D/tides-work/stems/htdemucs/neon-laser-horizon")

def load(f, start, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.4f}", "-t", f"{dur:.4f}", "-i", str(f),
                          "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

def env(t, pts):
    return 10 ** (np.interp(t, [p[0] for p in pts], [p[1] for p in pts]) / 20)

# V5.1 stem mix (demucs htdemucs): drums held out on the quiet open, back in with the travel shots
stem = {k: load(STEMS / f"{k}.wav", T_IN, END + 0.05) for k in ("drums", "bass", "other", "vocals")}
n = min(len(v) for v in stem.values())
tb = np.arange(n) / SR
drums = env(tb, [(0, -30), (9.0, -30), (10.5, 0), (99, 0)])
body = stem["drums"][:n] * drums[:, None] + stem["bass"][:n] + stem["other"][:n] + stem["vocals"][:n]
pts = [(0, -6), (9.0, -4), (DIVE - 0.4, 0), (DIVE + 6, 0), (B(104), -2), (B(112), -4),
       (END - B(1) - 0.02, -5), (END - B(1) + 0.08, -14), (END, -14)]
body *= env(tb, pts)[:, None]
hit = load(MUSIC_FILE, DROP_SONG, TOTAL - END + 0.05)
th = np.arange(len(hit)) / SR
tail = TOTAL - END
hit *= env(th, [(0, 0), (1.2, -3), (tail, -40)])[:, None]
n_end = int(END * SR)
out = np.concatenate([body[:n_end], hit])[: int(TOTAL * SR)]
out[:int(0.15 * SR)] *= np.linspace(0, 1, int(0.15 * SR))[:, None]
pre = WORK / "sound_pre.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(pre)],
               input=out.astype(np.float32).tobytes(), check=True)
# static gain to -14 LUFS (loudnorm would compress the swell away), then a limiter for the true peak
def lufs(f):
    e = subprocess.run(["ffmpeg", "-nostats", "-i", str(f), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(e[e.rindex("I:"):].split()[1])
gain = -14.0 - lufs(pre)
for _ in range(3):  # the limiter shaves a little loudness: correct and re-run
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(pre), "-af",
                    f"lowpass=f=500:p=2:enable='between(t,{DIVE - B(1):.3f},{DIVE:.3f})',"
                    f"volume={gain:.2f}dB,aresample=192000,alimiter=limit=0.80:level=false:attack=1:release=60,aresample=48000",
                    "-ac", "2", str(WORK / "sound.wav")], check=True)
    err = -14.0 - lufs(WORK / "sound.wav")
    if abs(err) < 0.15:
        break
    gain += err
print("WROTE", WORK / "sound.wav", "t_in", round(T_IN, 4), "gain", round(gain, 2))
