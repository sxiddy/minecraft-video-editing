"""Tides SMP V2 edit decision list (EDIT_V2.md). Shared by render_v2.py, audio_v2.py and build_v2.py.

Every cut sits on the music's beat grid: Chill Wave from 115.25 s, beats measured with librosa
(99.4 BPM) and fitted to B(n) = 0.5795 + 0.60365 n. Swells: B15 (9.57) breakdown phrase 2,
B31 (19.29) the lift, B63 (38.61) the full groove.

python timeline_v2.py  -> prints the cut list and writes timeline_v2.json
"""
import json, os, pathlib

FPS = 60
TRACK = os.environ.get("TRACK", "chill-wave")  # music candidate; grids from tracks_v2.py
_T = json.loads((pathlib.Path(__file__).parent / "tracks_v2.json").read_text())[TRACK]
BEAT0, BEAT = _T["beat0"], _T["beat"]
MUSIC_FILE, MUSIC_IN = _T["file"], _T["t_in"]

_AN = _T.get("anchors")  # piecewise map from the edit's beat numbers to this track's beats (phrase-aligned)

def B(n):
    if _AN:
        for (o0, n0), (o1, n1) in zip(_AN, _AN[1:]):
            if n <= o1 or (o1, n1) == tuple(_AN[-1]):
                n = round(n0 + (n - o0) * (n1 - n0) / (o1 - o0))
                break
    return round(BEAT0 + BEAT * n, 4)

def NB(n):  # a time in this track's own beats (bypasses the anchor map)
    return round(BEAT0 + BEAT * n, 4)

INTRO = 8 if TRACK == "neon-laser-horizon" else 0   # kinetic-type cold open (beats) before the edit's beat 0
_B0 = B
def B(n):
    return round(_B0(n) + BEAT * INTRO, 4)

# Transition half-lengths in frames (out side, in side) around the cut.
TRANS = {"none": (0, 0), "cut": (0, 0), "fade": (12, 12), "zoom": (8, 8), "whip": (8, 8),
         "flash": (6, 22), "dip": (4, 8), "ripple": (15, 15), "leak": (15, 15)}

# start, clip, source in (s), speed ramp, transition IN, overlays, shake on entry
# ramps: fs fast->slow, sf slow->fast (accelerating into the next cut), slow 0.55x, n 1x, half 0.5x
SHOTS = [
    # V5 (client notes after v4): open with a BANG, smooth flowing transitions, calmer pacing, ~87 s.
    # Neon Laser Horizon from 39.1 s (its loud A section) so frame 0 already hits. B(n) = this track's beats.
    # bang montage: 4 hero shots, 2 beats each, whip/zoom-blur between them
    # cold open on black: kinetic words on the beat over the track's quiet tail (overlay_v2.kinetic)
    (0.0,   1, 8.0, "n",    "none",   "black", 0),
    (B(0),  1, 8.0, "n",    "dip",    "flare", 1),
    (B(2),  28, 2.6, "n",   "whip",   "flare z1.3", 0),
    (B(4),  13, 2.0, "n",   "zoom",   "rays bubbles", 0),
    (B(6),  3, 1.3, "n",    "whip",   "rain bolt", 0),
    # white flash -> TIDES SMP logo over the golden island, held
    (B(8),  1, 9.0, "slow", "ripple", "flare leak", 1),
    # sailing: 8-beat (3 s) shots joined by dissolves
    (B(24), 28, 1.2, "n",   "fade",   "flare", 0),
    (B(32), 31, 1.2, "n",   "leak",   "flare", 0),
    (B(40), 5, 1.5, "n",    "fade",   "flare", 0),
    (B(48), 5, 4.5, "n",    "fade",   "leak z1.2", 0),
    # the dive (ripple) into the quiet reef: muffled, 8-beat holds, dissolves
    (B(56), 8, 8.4, "slow", "ripple", "rays bubbles", 0),
    (B(64), 10, 1.3, "n",   "fade",   "rays bubbles", 0),
    (B(72), 27, 1.3, "n",   "fade",   "rays bubbles z1.2", 0),
    (B(80), 13, 2.0, "slow", "fade",  "rays bubbles", 0),
    (B(88), 25, 1.5, "sf",  "fade",   "rays bubbles", 0),
    # DROP: surface into the storm (flash + boom), 4-beat shots, zoom/whip blur transitions
    (B(96), 3, 1.3, "fs",   "ripple", "rain bolt", 1),
    (B(100), 8, 2.8, "n",   "zoom",   "rain z1.25", 0),
    (B(104), 14, 2.0, "n",  "whip",   "rain z1.3", 0),
    (B(108), 11, 1.0, "n",  "zoom",   "rain bolt", 1),
    (B(112), 3, 5.5, "slow", "whip",  "rain", 0),
    (B(116), 8, 5.5, "n",   "zoom",   "rain bolt z1.25", 1),
    (B(120), 14, 6.5, "n",  "whip",   "rain", 0),
    (B(124), 4, 4.0, "n",  "zoom",   "rain z1.3", 1),
    (B(128), 4, 1.5, "slow", "ripple", "rain z1.2", 0),
    # calm after the storm: island discovered, build on the waves
    (B(136), 28, 1.2, "fs", "leak",   "flare", 1),
    (B(144), 5, 3.0, "n",   "fade",   "flare", 0),
    (B(152), 26, 2.5, "slow", "fade", "leak flare", 0),
    (B(160), 29, 1.0, "n",  "fade",   "flare z1.2", 0),
    (B(168), 31, 5.5, "n",  "leak",   "flare", 0),
    # climax flash + montage, 2 beats each with whips
    (B(176), 1, 11.0, "n",  "ripple", "flare", 1),
    (B(178), 3, 6.5, "n",   "whip",   "rain bolt", 0),
    (B(180), 10, 4.0, "n",  "zoom",   "rays z1.3", 0),
    (B(182), 28, 5.0, "n",  "whip",   "flare", 0),
    (B(184), 13, 3.0, "n",  "zoom",   "rays bubbles", 0),
    (B(186), 5, 4.5, "n",   "whip",   "flare z1.3", 0),
    (B(188), 8, 3.0, "n",   "zoom",   "rain", 0),
    (B(190), 27, 2.0, "n",  "whip",   "rays bubbles", 0),
    # who you bring matters -> multiplayer screen -> end card
    (B(192), 31, 7.0, "slow", "fade", "flare", 0),
    (B(204), 29, 4.5, "half", "fade", "blur", 0),
]

TOTAL = round(B(232), 3)
DROP, CLIMAX = B(96), B(176)
BUILDS = [(B(88), B(96)), (B(172), B(176))]          # bass stripped (high-passed) here, slammed back on the hit
TITLE_WINDOWS = [(B(8), B(22)), (B(216), TOTAL)]    # logo backdrop: the bang reveal, then the end card
INFO = (B(204) + 0.3, B(216) - 0.1)                  # multiplayer screen
BARS_OPEN = (B(203), B(204) + 0.2)
FADE_OUT = (TOTAL - 0.25, TOTAL)

KINETIC = [(NB(0), "ONE OCEAN."), (NB(2), "NO MAP."), (NB(4), "NO WAY BACK."), (NB(6), "JUST THE TIDE.")]
TEXT = {
    "LOGO": (B(8), B(22)),
    "C0": (B(33), B(46), "A world of water", "every island is earned"),
    "TOAST": (B(72) + 0.2, B(80)),
    "C1": (B(100), B(112), "Survive the open sea", "storms don't wait"),
    "POP2": (B(128) + 0.1, B(136) - 0.1, "STORM SURVIVED!", "+ the sea gives back"),
    "POP": (B(136) + 0.2, B(144) - 0.1, "ISLAND DISCOVERED!", "+ claim it, build it, keep it"),
    "C2": (B(153), B(166), "Build on the waves", "a home the tide can't take"),
    "C3": (B(168), B(176), "Java + Bedrock", "one ocean, any device"),
    "T1": (B(193), B(204) - 0.1, "Who you bring matters.", "invite friends - earn rewards"),
    "END": (B(216), TOTAL),
    "CREDIT": (B(218), TOTAL - 0.3),
}
TEXT["TOAST"] = (*TEXT["TOAST"], "Advancement Made!", "Into the Deep")

def shots():
    """Shots with their cut window [a, b) and the extended render window including transition handles."""
    out = []
    for i, (a, clip, src, ramp, tr, ov, shake) in enumerate(SHOTS):
        b = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else TOTAL
        tr_out = SHOTS[i + 1][4] if i + 1 < len(SHOTS) else "none"
        h_in = TRANS[tr][1] / FPS
        h_out = TRANS[tr_out][0] / FPS
        out.append(dict(i=i, a=a, b=b, clip=clip, src=src, ramp=ramp, tr=tr, tr_out=tr_out,
                        ov=ov.split(), shake=shake, ra=max(0.0, a - h_in), rb=min(TOTAL, b + h_out)))
    return out

if __name__ == "__main__":
    S = shots()
    for s in S:
        print(f"{s['i']:2d} {s['a']:6.2f}-{s['b']:6.2f} ({s['b'] - s['a']:.2f}s) c{s['clip']:<2d} @{s['src']:4.1f} {s['ramp']:4s} in:{s['tr']:6s} {' '.join(s['ov'])}")
    print(len(S), "shots,", sum(1 for s in S if s["tr"] != "none"), "cuts")
    pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(
        dict(shots=S, title=TITLE_WINDOWS, info=INFO, bars_open=BARS_OPEN, text=TEXT, total=TOTAL,
             trans={k: [v[0] / FPS, v[1] / FPS] for k, v in TRANS.items()}), indent=1))
