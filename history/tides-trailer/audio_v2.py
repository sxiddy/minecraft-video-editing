"""Soundtrack for the V2 edit: music on the beat grid + transition SFX + ambience, mastered to -14 LUFS / -1 dBTP.

TRACK=newer-wave python audio_v2.py [DURATION]  -> WORK/<track>/sound.wav (48 kHz stereo)
SFX are synthesised from timeline_v2: whip = whoosh, zoom = short riser + thump, flash = long riser + boom,
ripple = bubbly swell + splash, leak = shimmer, hard cut with shake = impact. Ambience follows the overlays
(rain shots get rain, underwater shots get the muffled bed and the music low-passed).
"""
import json, pathlib, subprocess, sys
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt
from timeline_v2 import TOTAL, TRACK, MUSIC_FILE, MUSIC_IN, TRANS, FPS, shots

WORK = pathlib.Path("C:/Users/Siddharth D/tides-work/v2") / TRACK
WORK.mkdir(parents=True, exist_ok=True)
SR = 48000
D = float(sys.argv[1]) if len(sys.argv) > 1 else TOTAL
N = int(D * SR)
rng = np.random.default_rng(7)
S = [s for s in shots() if s["a"] < D]

def ff(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)

def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "bandpass", fs=SR, output="sos"), x)

def lp(x, f, order=2):
    return sosfilt(butter(order, f, "lowpass", fs=SR, output="sos"), x)

def place(buf, sig, t, gain=1.0):
    i = int(t * SR)
    if i < 0:
        sig, i = sig[-i:], 0
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += sig[:j - i] * gain

def env(n, a, r):
    e = np.ones(n)
    ka, kr = int(a * SR), int(r * SR)
    e[:ka] = np.linspace(0, 1, ka) ** 2
    e[n - kr:] *= np.linspace(1, 0, kr) ** 1.5
    return e

def noise(sec):
    return rng.standard_normal(int(sec * SR))

def sweep_noise(sec, f0, f1, q=0.6):
    """Band of noise whose centre glides f0 -> f1 (block-wise bandpass)."""
    x, out, blk = noise(sec), np.zeros(int(sec * SR)), 1024
    for k in range(0, len(x), blk):
        f = f0 * (f1 / f0) ** (k / len(x))
        out[k:k + blk] = bp(x[max(0, k - 4096):k + blk], f * (1 - q / 2), f * (1 + q / 2))[-len(x[k:k + blk]):]
    return out

def whoosh():
    s = sweep_noise(0.42, 300, 2600) * np.sin(np.linspace(0, np.pi, int(0.42 * SR))) ** 1.5
    return s / np.abs(s).max()

def riser(sec, f0=200, f1=4000):
    s = sweep_noise(sec, f0, f1, 0.8) * np.linspace(0, 1, int(sec * SR)) ** 2.5
    return s / np.abs(s).max()

def boom(sec=1.4, f0=70):
    t = np.arange(int(sec * SR)) / SR
    s = np.sin(2 * np.pi * (f0 * t - 18 * t ** 2)) * np.exp(-t * 3.2)
    s += lp(noise(sec), 300) * 0.25 * np.exp(-t * 9)
    return s / np.abs(s).max()

def thump():
    t = np.arange(int(0.35 * SR)) / SR
    return np.sin(2 * np.pi * (110 * t - 90 * t ** 2)) * np.exp(-t * 14)

def shimmer(sec=1.2):
    t = np.arange(int(sec * SR)) / SR
    s = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate([1760, 2217, 2637, 3520])) * 0.25
    s *= (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t)) * np.sin(np.pi * t / sec) ** 2
    return s

def splash():
    t = np.arange(int(0.7 * SR)) / SR
    s = bp(noise(0.7), 500, 5000) * np.exp(-t * 7)
    for k in range(14):  # bubbles: short rising chirps
        tt = rng.uniform(0.05, 0.6); f = rng.uniform(500, 1400)
        n = int(0.04 * SR); u = np.arange(n) / SR
        place(s, np.sin(2 * np.pi * (f * u + 6000 * u ** 2)) * np.exp(-u * 70) * 0.5, tt)
    return s / np.abs(s).max()

# ---------------------------------------------------------------- music
mus = WORK / "music_raw.wav"
ff("-ss", str(MUSIC_IN), "-t", str(D), "-i", MUSIC_FILE, "-ar", str(SR), "-ac", "2", str(mus))
m, _ = sf.read(mus)
m = np.pad(m, ((0, max(0, N - len(m))), (0, 0)))[:N]
# bass treatment (client pick D): +6 dB low shelf, punchy kick on every beat and an 808 sub every bar from the drop
from timeline_v2 import B as _B, BEAT, TEXT as _TX, DROP, CLIMAX, BUILDS
m = np.stack([sosfilt(butter(2, 90, "lowpass", fs=SR, output="sos"), m[:, c]) * (10 ** (6 / 20) - 1) + m[:, c]
              for c in range(2)], 1)
def _kick(n=0.45):
    u = np.arange(int(n * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(45 + 120 * np.exp(-u * 30)) / SR) * np.exp(-u * 6)
def _808(n=0.9, f0=41):
    u = np.arange(int(n * SR)) / SR
    return np.tanh(2.2 * np.sin(2 * np.pi * f0 * u)) * np.exp(-u * 2.2) * 0.8
low = np.zeros(N)
k_on, k_off = _B(0), _TX["END"][0]
quiet = BUILDS + [(_B(56), DROP)]  # no kick in the builds or the underwater reef
for n in range(int(TOTAL / BEAT) + 1):
    tb = n * BEAT
    if k_on <= tb < k_off and not any(q0 <= tb < q1 for q0, q1 in quiet):
        place(low, _kick(), tb, 0.5 * 0.5)
        if round((tb - k_on) / BEAT) % 4 == 0:
            place(low, _808(), tb, 0.6 * 0.5)
m = m + low[:, None] * np.abs(m).max()
# underwater: low-pass the music while the shot carries "rays" (blend by a smoothed mask)
under = np.zeros(N)
for s in S:
    if "rays" in s["ov"] and _B(56) <= s["a"] < DROP:  # only the reef dive is muffled, not montage flashes
        under[int(s["a"] * SR):int(min(s["b"], D) * SR)] = 1
k = int(0.25 * SR)
under = np.convolve(under[::480], np.ones(k // 480) / (k // 480), "same").repeat(480)[:N]
m_lp = np.stack([lp(m[:, c], 700) for c in range(2)], 1)
m = m * (1 - under[:, None] * 0.7) + m_lp * (under[:, None] * 0.7)
from timeline_v2 import B
tt = np.arange(N) / SR
drop, gap = DROP, 0.5
def _hp_win(x, a0, a1, f=150):
    hp = np.stack([sosfilt(butter(2, f, "highpass", fs=SR, output="sos"), x[:, c]) for c in range(2)], 1)
    w = np.clip(np.minimum((tt - a0) / 0.8, (a1 - tt) / 0.02), 0, 1)[:, None]
    return x * (1 - w) + hp * w
for b0_, b1_ in BUILDS:
    m = _hp_win(m, b0_, b1_)
hole = 1 - 0.92 * ((tt > drop - gap) & (tt < drop)).astype(float)
m *= hole[:, None]
fade_in = np.clip(np.arange(N) / (0.05 * SR), 0, 1)[:, None]
m *= fade_in
if D >= TOTAL - 0.01:
    t = np.arange(N) / SR
    m *= np.clip((TOTAL - t) / 4.0, 0, 1)[:, None] ** 0.5

# ---------------------------------------------------------------- sfx
sfx = np.zeros(N)
W, R, Bm, Th, Sh, Sp = whoosh(), riser(0.45), boom(), thump(), shimmer(), splash()
long_riser = riser(1.6, 150, 6000)
for tb_, g_ in [(B(0), 1.0), (B(8), 0.9), (DROP, 1.0), (CLIMAX, 1.0), (_TX['END'][0], 0.8)]:
    place(sfx, Bm, tb_, g_); place(sfx, _808(1.4, 36), tb_, 0.9 * g_)
for s in S:
    if s["i"] == 0:
        continue
    c, tr = s["a"], s["tr"]
    if tr == "whip":
        place(sfx, W, c - 0.24, 0.55)
    elif tr == "zoom":
        place(sfx, R, c - 0.45, 0.35); place(sfx, Th, c, 0.6)
    elif tr == "flash":
        place(sfx, W, c - 0.24, 0.6)
        place(sfx, long_riser, c - 1.6, 0.45); place(sfx, Bm, c, 0.9); place(sfx, Sh, c, 0.25)
    elif tr == "ripple":
        place(sfx, riser(0.5, 200, 1200), c - 0.5, 0.3); place(sfx, Sp, c - 0.05, 0.55)
    elif tr == "leak":
        place(sfx, Sh, c - 0.6, 0.3)
    elif tr == "cut" and s["shake"]:
        place(sfx, Bm, c, 0.85)
    if "bolt" in s["ov"]:  # thunder crack + roll
        tt = np.arange(int(2.5 * SR)) / SR
        th = lp(noise(2.5), 900) * np.exp(-tt * 1.6) * (0.4 + 0.6 * np.exp(-tt * 12))
        place(sfx, th / np.abs(th).max(), c + 0.05, 0.9)
    if s["clip"] != S[s["i"] - 1]["clip"] and s["ov"] != S[s["i"] - 1]["ov"]:
        place(sfx, W, c - 0.24, 0.4)  # section change whoosh
    if s["shake"] and tr not in ("cut", "flash"):
        place(sfx, Th, c, 0.5)
# cold open: each kinetic word lands with a thump + a short reversed-air whoosh into it
from timeline_v2 import KINETIC
for tw_, _w in KINETIC:
    place(sfx, Th, tw_, 0.9); place(sfx, W[::-1][-int(0.2 * SR):], tw_ - 0.2, 0.35)
place(sfx, long_riser, B(0) - 1.6, 0.6)
# UI sounds for the multiplayer screen: button clicks, key ticks, row pops, the droplet plip
from overlay_v2 import events
def tone(f0, f1, sec, decay):
    t = np.arange(int(sec * SR)) / SR
    return np.sin(2 * np.pi * (f0 * t + (f1 - f0) / (2 * sec) * t ** 2)) * np.exp(-t * decay)
UI = {"click": (bp(noise(0.03), 1500, 6000) * np.exp(-np.arange(int(0.03 * SR)) / SR * 150), 0.5),
      "key": (bp(noise(0.02), 2500, 8000) * np.exp(-np.arange(int(0.02 * SR)) / SR * 250), 0.18),
      "pop": (tone(500, 1100, 0.12, 30), 0.35), "plip": (tone(1800, 900, 0.3, 28), 0.5),
      "ding": (tone(1320, 1320, 0.9, 5) * 0.6 + tone(1980, 1980, 0.9, 7) * 0.4, 0.6),
      "sparkle": (shimmer(1.4) * 1.5, 0.7)}
for t_ev, kind in events():
    if t_ev < D:
        place(sfx, UI[kind][0], t_ev, UI[kind][1])
sfx = np.stack([sfx, sfx], 1)

# ---------------------------------------------------------------- ambience
def bed(kind, sec):
    x = noise(sec)
    if kind == "rain":
        return bp(x, 2000, 9000) * 0.6 + bp(x, 400, 1200) * 0.2
    if kind == "under":
        return lp(x, 300) * 1.6
    t = np.arange(len(x)) / SR  # ocean
    return lp(x, 1100) * (0.65 + 0.35 * np.sin(2 * np.pi * 0.13 * t))

amb = np.zeros(N)
beds = {k: bed(k, D) for k in ("rain", "under", "ocean")}
for kind in beds:
    mask = np.zeros(N)
    for s in S:
        ov = s["ov"]
        on = (kind == "rain" and "rain" in ov) or (kind == "under" and "rays" in ov) or \
             (kind == "ocean" and not ("rain" in ov or "rays" in ov))
        if on:
            mask[int(s["a"] * SR):int(min(s["b"], D) * SR)] = 1
    mask = np.convolve(mask[::480], np.ones(k // 480) / (k // 480), "same").repeat(480)[:N]
    amb += beds[kind] * mask * {"rain": 0.5, "under": 0.6, "ocean": 0.35}[kind]
amb = np.stack([amb, amb * 0.97], 1)

# ---------------------------------------------------------------- mix + master
def smooth_mask(x, k):
    c = np.cumsum(np.concatenate([[0.0], x]))
    y = (c[k:] - c[:-k]) / k
    return np.pad(y, (k // 2, len(x) - len(y) - k // 2), mode="edge")

def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)

mref = rms_db(m)
mix = m + sfx * 10 ** ((mref - 4 - rms_db(sfx[np.abs(sfx).sum(1) > 1e-4] if np.any(sfx) else sfx)) / 20) * 0.35 \
        + amb * 10 ** ((mref - 21 - rms_db(amb)) / 20)
raw = WORK / "mix_raw.wav"
sf.write(raw, np.clip(mix / max(1.0, np.abs(mix).max()) * 0.9, -1, 1), SR, subtype="FLOAT")
meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                       "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
out = WORK / "sound.wav"
ff("-i", str(raw), "-af",
   f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:"
   f"measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:"
   f"offset={j['target_offset']}:linear=true,alimiter=limit=0.85:level=false,aresample={SR}", "-c:a", "pcm_s16le", str(out))
print("WROTE", out)
