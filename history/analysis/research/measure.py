"""Measure every downloaded reference trailer: cuts, shot lengths, BPM, cut-on-beat share; make frame sheets."""
import json, pathlib, subprocess, re, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np

REFS = pathlib.Path("C:/Users/Siddharth D/tides-work/refs")
OUT = pathlib.Path(__file__).parent

def one(f):
    vid = f.stem
    d = OUT / vid; d.mkdir(exist_ok=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                               capture_output=True, text=True).stdout)
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-an", "-vf",
                          "scale=320:-2,select='gt(scene,0.27)',showinfo", "-f", "null", "-"], capture_output=True, text=True).stderr
    cuts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", log)]
    sl = np.diff([0] + cuts + [dur])
    res = dict(id=vid, dur=round(dur, 1), cuts=len(cuts), cuts_first20=sum(c < 20 for c in cuts),
               median_shot=round(float(np.median(sl)), 2), mean_shot=round(float(np.mean(sl)), 2), cut_times=[round(c, 2) for c in cuts])
    try:
        import librosa
        y, sr = librosa.load(str(f), sr=22050)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        bt = librosa.frames_to_time(beats, sr=sr)
        on = [min(abs(bt - c)) < 0.07 for c in cuts] if len(bt) else []
        res.update(bpm=round(float(np.atleast_1d(tempo)[0]), 1), cuts_on_beat=round(float(np.mean(on)) if on else 0, 2))
    except Exception as e:
        res["audio_err"] = str(e)[:80]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-t", "20", "-i", str(f), "-vf", "fps=4,scale=320:-2,tile=8x10", "-frames:v", "1",
                    str(d / "first20_4fps.jpg")])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-vf", "fps=1,scale=320:-2,tile=8x12", "-frames:v", "1",
                    str(d / "full_1fps.jpg")])
    (d / "metrics.json").write_text(json.dumps(res, indent=1))
    return res

if __name__ == "__main__":
    files = sorted(REFS.glob("*.mp4"))
    with ProcessPoolExecutor(8) as ex:
        rs = list(ex.map(one, files))
    (OUT / "metrics_all.json").write_text(json.dumps(rs, indent=1))
    for r in rs:
        print(f"{r['id']:14s} dur {r['dur']:5.1f} cuts {r['cuts']:3d} first20 {r['cuts_first20']:2d} median {r['median_shot']:4.2f}s "
              f"bpm {r.get('bpm','?')} onbeat {r.get('cuts_on_beat','?')}")
