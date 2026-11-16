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
# V3 (client + Opus review: "reads as a slideshow"): fast beat cuts (2-3 beats = 0.75-1.1 s), every cut a new
# image, in-game hook under the cold-open words, the full c8 swim -> dive kept as the hero moment.
def _seq(start, beats, spec, tr="cut", ov="", hit_tr=None):
    out = []
    for k, (clip, src, *extra) in enumerate(spec):
        o = extra[0] if extra else ov
        out.append((B(start + k * beats), clip, src, "n", (hit_tr if (hit_tr and k == 0) else
                    (tr[k % len(tr)] if isinstance(tr, list) else tr)), o, 1 if k % 4 == 0 else 0))
    return out

SHOTS = [
    # cold open: kinetic words over dimmed in-game footage, a new shot on every word
    (NB(0) * 0, 28, 0.4, "n",  "none",  "dim", 0),
    (NB(2), 2, 2.0, "n",       "cut",   "dim", 0),
    (NB(4), 11, 2.5, "n",      "cut",   "dim rain", 0),
    (NB(6), 5, 6.0, "n",       "cut",   "dim flare", 0),
    # bang montage: 2 beats each
    *_seq(0, 2, [(1, 8.0, "flare"), (28, 2.6, "flare z1.3"), (13, 2.0, "rays bubbles"), (3, 1.3, "rain bolt")],
          tr=["whip", "zoom"], hit_tr="dip"),
    # TIDES title over the golden island (held - it is the logo moment)
    (B(8), 1, 9.0, "slow", "ripple", "flare leak", 1),
    (B(16), 1, 4.0, "n", "zoom", "flare", 0),
    # sailing: 3-beat cuts
    *_seq(24, 3, [(28, 0.4, "flare"), (31, 1.0, "flare"), (5, 1.5, "flare"), (7, 3.0, "flare"), (26, 0.5, "leak"),
                  (28, 4.2, "flare z1.2"), (31, 6.0, "flare"), (5, 6.5, "z1.25"), (29, 1.5, "flare"),
                  (7, 7.5, "flare z1.2"), (26, 4.0, "leak")], tr=["cut", "cut", "whip"], hit_tr="ripple"),
    # THE DIVE: the whole c8 swim -> dive under (the client's favourite moment), real time
    (B(57), 8, 3.4, "n", "zoom", "", 1),
    # reef: 3-beat cuts, muffled
    *_seq(72, 3, [(10, 1.3, "rays bubbles"), (27, 1.3, "rays bubbles z1.2"), (13, 4.0, "rays bubbles"),
                  (25, 1.5, "rays bubbles"), (30, 2.0, "rays bubbles"), (10, 5.5, "rays bubbles z1.2"),
                  (27, 6.5, "rays bubbles"), (25, 7.0, "rays bubbles z1.2")], tr="fade", hit_tr="ripple"),
    # DROP: storm, 2-beat cuts, zoom/whip/shake
    *_seq(96, 2, [(3, 1.3, "rain bolt"), (11, 1.0, "rain z1.25"), (14, 2.0, "rain"), (4, 1.0, "rain bolt z1.2"),
                  (8, 2.5, "rain"), (3, 4.5, "rain z1.3"), (11, 5.0, "rain bolt"), (14, 5.5, "rain z1.2"),
                  (4, 4.0, "rain"), (15, 2.5, "rain bolt"), (16, 3.0, "rain z1.2"), (3, 7.5, "rain"),
                  (11, 8.0, "rain bolt z1.2"), (14, 8.0, "rain"), (4, 7.5, "rain z1.3"), (15, 6.5, "rain bolt")],
          tr=["cut", "zoom", "cut", "whip"], hit_tr="ripple"),
    # after the storm: island, build - 3-beat cuts
    *_seq(128, 3, [(4, 5.5, "rain z1.2"), (28, 1.2, "flare"), (1, 1.0, "flare"), (5, 3.0, "flare"),
                   (26, 2.5, "leak flare"), (29, 4.0, "flare z1.2"), (28, 6.5, "flare"), (31, 3.5, "flare"),
                   (1, 4.0, "flare z1.2"), (7, 5.5, "flare"), (26, 6.0, "leak"), (29, 7.0, "flare"),
                   (31, 8.0, "flare z1.2"), (1, 11.5, "flare"), (28, 8.0, "flare"), (5, 8.5, "flare z1.2")],
           tr=["cut", "cut", "whip"], hit_tr="ripple"),
    # climax: 2-beat flurry
    *_seq(176, 2, [(1, 11.0, "flare"), (3, 6.5, "rain bolt"), (10, 4.0, "rays z1.3"), (28, 5.0, "flare"),
                   (13, 3.0, "rays bubbles"), (5, 4.5, "flare z1.3"), (8, 2.0, "rain"), (27, 2.0, "rays bubbles")],
          tr=["whip", "zoom"], hit_tr="ripple"),
    # who you bring matters -> multiplayer screen -> end card
    (B(192), 31, 7.0, "n", "zoom", "flare", 1),
    (B(196), 28, 9.0, "n", "cut", "flare", 0),
    (B(200), 26, 7.5, "n", "whip", "leak", 0),
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
# V3: a game-UI toast every ~8-10 s
TOASTS = [(B(40), B(47), "Advancement Made!", "Set Sail"),
          (B(60), B(68), "Advancement Made!", "Hold Your Breath"),
          (B(72) + 0.2, B(80), "Advancement Made!", "Into the Deep"),
          (B(112), B(120), "Challenge Complete!", "Weather the Storm"),
          (B(128) + 0.1, B(136) - 0.1, "Challenge Complete!", "Storm Survived"),
          (B(136) + 0.2, B(144) - 0.1, "Advancement Made!", "Island Discovered"),
          (B(160), B(167), "Advancement Made!", "Home on the Waves"),
          (B(184), B(191), "Goal Reached!", "One Ocean")]

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
