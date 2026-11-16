"""Build the trailer soundtrack (FINAL_PLAN.md section 6) -> assets/soundtrack.wav (79 s, 48 kHz stereo).

Every layer is rendered as its own stem, measured (integrated LUFS, so silence is ignored),
set to its planned level relative to the music, then mixed and mastered to -14 LUFS / -1 dBTP.
"""
import json, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).parent
TMP = ROOT / "work_audio"
TMP.mkdir(exist_ok=True)
MUSIC = ROOT.parent / "music-options" / "chill-wave.mp3"
D = 79.0
SR = 48000

def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)

def lufs(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])

def gate(windows, fade=0.3):
    """volume expression: 1 inside any (start, end) window, with linear fades."""
    parts = [f"clip(min((t-({a}))/{fade},({b}-t)/{fade}),0,1)" for a, b in windows]
    expr = parts[0]
    for p in parts[1:]:  # ffmpeg's max() takes exactly two arguments
        expr = f"max({expr},{p})"
    return expr

def noise(name, color, chain, windows, fade=0.3):
    out = TMP / f"{name}.wav"
    ff("-f", "lavfi", "-i", f"anoisesrc=d={D}:c={color}:r={SR}:a=0.5:s=7",
       "-af", f"{chain},volume='{gate(windows, fade)}':eval=frame,aformat=channel_layouts=stereo", str(out))
    return out

stems = {}

# Music: 115.25 -> 194.25, fade in 1.0-2.5 (waves solo first), low-pass under water until the surface break
# at 3.5-4.5, duck -3 dB under the info card, equal-power fade out 74-79.
m = TMP / "music.wav"
duck = "1-0.292*clip(min((t-66.5)/0.5,(77.5-t)/0.5),0,1)"
ff("-ss", "115.25", "-t", str(D), "-i", str(MUSIC), "-filter_complex",
   f"[0:a]aresample={SR},asplit[a][b];"
   "[a]lowpass=f=900,volume='clip((4.5-t),0,1)':eval=frame[lp];"
   "[b]volume='clip((t-3.5),0,1)':eval=frame[hp];"
   f"[lp][hp]amix=inputs=2:normalize=0,volume='{duck}':eval=frame,"
   "afade=t=in:st=1.0:d=1.5,afade=t=out:st=74:d=5:curve=qsin,aformat=channel_layouts=stereo", str(m))
stems["music"] = (m, 0)

stems["waves"] = (noise("waves", "pink", "lowpass=f=1200,volume='0.75+0.25*sin(2*PI*0.12*t)':eval=frame",
                        [(0.0, 79.0)]), -20)
# waves are muted under water: multiply by an inverse gate
w2 = TMP / "waves_g.wav"
ff("-i", str(stems["waves"][0]), "-af",
   "volume='1-max(clip(min((t+1)/0.4,(4.0-t)/0.4),0,1),clip(min((t-38.25)/0.4,(46.0-t)/0.4),0,1))':eval=frame", str(w2))
stems["waves"] = (w2, -20)
stems["under"] = (noise("under", "brown", "lowpass=f=350", [(-1, 4.2), (37.6, 46.6)], 0.4), -22)
stems["rain"] = (noise("rain", "white", "highpass=f=2000,lowpass=f=9000", [(18.9, 33.8)], 0.2), -21)

# campfire crackle: sparse random clicks, band-limited
cf = TMP / "fire.wav"
ff("-f", "lavfi", "-i", f"aevalsrc='if(gt(random(0),0.9988),(random(1)*2-1),0)':s={SR}:d={D}",
   "-af", f"bandpass=f=2200:width_type=h:w=2600,volume='{gate([(50.2, 53.4)])}':eval=frame,aformat=channel_layouts=stereo", str(cf))
stems["fire"] = (cf, -24)

# transition swells: rising filtered noise, 1 s, ending on each transition time
sw = TMP / "swell1.wav"
ff("-f", "lavfi", "-i", f"anoisesrc=d=1.0:c=pink:r={SR}:a=0.6:s=3", "-af",
   "lowpass=f=3000,volume='pow(t/1.0,2.2)':eval=frame,afade=t=out:st=0.92:d=0.08,aformat=channel_layouts=stereo", str(sw))
sw_times = [3.5, 6.8, 37.25, 45.95, 50.15]
swells = TMP / "swells.wav"
inputs = sum([["-i", str(sw)] for _ in sw_times], [])
delays = ";".join(f"[{i}:a]adelay={int(t * 1000)}|{int(t * 1000)}[d{i}]" for i, t in enumerate(sw_times))
ff(*inputs, "-filter_complex", delays + ";" + "".join(f"[d{i}]" for i in range(len(sw_times)))
   + f"amix=inputs={len(sw_times)}:normalize=0,apad=whole_dur={D}", "-t", str(D), str(swells))
stems["swells"] = (swells, -24)

# surface splash / bubble burst
sp = TMP / "splash1.wav"
ff("-f", "lavfi", "-i", f"anoisesrc=d=0.6:c=white:r={SR}:a=0.7:s=5", "-af",
   "bandpass=f=1400:width_type=h:w=2000,volume='exp(-t*9)':eval=frame,aformat=channel_layouts=stereo", str(sp))
splash = TMP / "splash.wav"
ff("-i", str(sp), "-i", str(sp), "-filter_complex",
   "[0:a]adelay=4450|4450[a];[1:a]adelay=38200|38200[b];[a][b]amix=inputs=2:normalize=0,apad=whole_dur=79",
   "-t", str(D), str(splash))
stems["splash"] = (splash, -22)

# droplet plip: sine 1.8k -> 900 Hz over 60 ms, short reverb tail, at 69.70
pl = TMP / "plip.wav"
ff("-f", "lavfi", "-i", f"aevalsrc='sin(2*PI*(1800*t-7500*t*t))*exp(-t*28)':s={SR}:d=0.4",
   "-af", "aecho=0.8:0.6:45|90|140:0.35|0.22|0.12,adelay=69700|69700,apad=whole_dur=79,aformat=channel_layouts=stereo",
   "-t", str(D), str(pl))
stems["plip"] = (pl, -14)

ref = lufs(m)
inputs, chains = [], []
for i, (name, (path, rel)) in enumerate(stems.items()):
    g = (ref + rel) - lufs(path) if name != "music" else 0.0
    inputs += ["-i", str(path)]
    chains.append(f"[{i}:a]volume={g:.2f}dB[s{i}]")
    print(f"{name:7s} gain {g:+.1f} dB (target {rel} dB vs music)")
mix = TMP / "mix.wav"
ff(*inputs, "-filter_complex", ";".join(chains) + ";" + "".join(f"[s{i}]" for i in range(len(stems)))
   + f"amix=inputs={len(stems)}:normalize=0,acompressor=ratio=2:threshold=-18dB:attack=20:release=250",
   "-t", str(D), str(mix))

# two-pass loudnorm to -14 LUFS / -1 dBTP
meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(mix), "-af",
                       "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
                      capture_output=True, text=True).stderr
j = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
ff("-i", str(mix), "-af",
   f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
   f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,"
   f"aresample={SR}", "-c:a", "pcm_s16le", str(ROOT / "assets" / "soundtrack.wav"))
print("final LUFS", lufs(ROOT / "assets" / "soundtrack.wav"))
