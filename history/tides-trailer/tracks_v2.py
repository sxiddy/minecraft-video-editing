"""Beat grids for the music candidates (librosa beat track from each in point, fitted to t = beat0 + n * beat).

python tracks_v2.py  -> tracks_v2.json, read by timeline_v2.py (pick with env TRACK=name)
"""
import json, pathlib
import librosa, numpy as np

LIB = "C:/Users/Siddharth D/Projects/drive-reel-mcp/music/library/"
HERE = pathlib.Path(__file__).parent
TRACKS = {  # name: (file, rough in point s)
    "chill-wave": (str(HERE.parent / "music-options" / "chill-wave.mp3"), 115.25),
    "newer-wave": (LIB + "newer-wave.mp3", 2.6),
    "voxel-revolution": (LIB + "voxel-revolution.mp3", 0.0),
    "ascending-the-vale": (str(HERE.parent / "music-options" / "ascending-the-vale.mp3"), 41.0),
}

out = {}
for name, (f, t_in) in TRACKS.items():
    y, sr = librosa.load(f, sr=22050, offset=t_in, duration=80)
    _, beats = librosa.beat.beat_track(y=y, sr=sr, tightness=400)
    bt = librosa.frames_to_time(beats, sr=sr)
    n = np.arange(len(bt))
    beat, b0 = np.polyfit(n, bt, 1)
    if name != "chill-wave":  # start the track exactly on a beat so the cut grid begins at video 0
        t_in += b0 % beat
        b0 = b0 - (b0 % beat)
        b0 = b0 % beat
    out[name] = dict(file=f, t_in=round(t_in, 4), beat0=round(float(b0), 4), beat=round(float(beat), 5),
                     bpm=round(60 / beat, 1))
    print(name, out[name])
(HERE / "tracks_v2.json").write_text(json.dumps(out, indent=1))
