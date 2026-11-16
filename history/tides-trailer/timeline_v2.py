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

INTRO = 0  # V4: no cold open; the music's quiet bars are the intro   # kinetic-type cold open (beats) before the edit's beat 0
_B0 = B
def B(n):
    return round(_B0(n) + BEAT * INTRO, 4)

# Transition half-lengths in frames (out side, in side) around the cut.
TRANS = {"none": (0, 0), "cut": (0, 0), "fade": (12, 12), "zoom": (16, 12), "whip": (8, 8),
         "flash": (6, 22), "dip": (4, 8), "ripple": (15, 15), "leak": (15, 15), "slow": (22, 22)}

# start, clip, source in (s), speed ramp, transition IN, overlays, shake on entry
# ramps: fs fast->slow, sf slow->fast (accelerating into the next cut), slow 0.55x, n 1x, half 0.5x
# V4 (client: "use less clips, use long clips, ~50 s, calm, no overlays on our shader footage, no AI-template
# transitions"). Each clip once, real speed, untouched look, hard cuts on bar lines (1 bar = 4 beats = 1.5 s).
# Music from song beat 96: quiet bars, the A-section hit at e8 (3.0 s), the drop at e104 (39.0 s).
SHOTS = [
    # V8 (Opus review vs RuneSpire + user notes): punchier cut (1.5-4.5 s, uneven), kinetic cold open, chunky logo,
    # advancement toasts + gold pops back, the whole swim -> slow dive under, crash-zoom into the drop.
    # Each clip once (c28 = one take split by an intentional punch-in). No overlays/grade on the footage.
    (B(0),   31, 1.5, "n",    "none", "z1.04", 0),  # cold open: kinetic words
    (B(8),   1,  3.5, "n",    "dip",  "", 0),       # golden island: logo on the hit
    (B(20),  5,  2.0, "n",    "cut",  "", 0),       # sailing (drums in): NO MAINLAND
    (B(28),  28, 1.0, "n",    "whip", "", 0),       # raft: Set Sail toast
    (B(32),  28, 3.0, "n",    "cut",  "z1.15", 0),  # same take, punch-in
    (B(40),  8,  0.24, "dive", "fade", "", 0),      # V8.1: ONE continuous take: swim, 0.6x as he goes under (drop at 22.5), stays underwater
    (B(66),  13, 0.5, "n",    "cut",  "", 0),       # underwater light (c8 has run out)
    (B(70),  30, 1.0, "n",    "cut",  "", 0),       # V8.2: bright kelp/coral under THE DEEP (c10 was near-black)
    #  # reef: THE DEEP
    (B(78),  25, 1.0, "n",    "cut",  "", 0),       # underwater build
    (B(82),  4,  1.3, "n",    "cut",  "", 0),       # storm on the island
    (B(86),  29, 1.5, "n",    "whip", "", 0),       # calm after it: STORM SURVIVED pop
    (B(94),  26, 2.0, "n",    "cut",  "", 0),       # sunset: ISLAND DISCOVERED pop
    (B(102), 7,  1.0, "n",    "cut",  "", 0),       # bright open ocean: JAVA + BEDROCK
    (B(111), 14, 2.0, "half", "slow", "blur", 0),   # 0.75 s dissolve 41.25-42.0 into the join screen + end card
]

TOTAL = round(B(146), 3)
DROP, CLIMAX = B(60), B(134)
BUILDS = []
TITLE_WINDOWS = []
INFO = (B(112) + 0.5, B(134) - 0.1)                 # multiplayer screen (client-approved)
BARS_OPEN = (B(111), B(113))
FADE_OUT = (TOTAL - 0.5, TOTAL)

KINETIC = [(NB(0), "ONE OCEAN."), (NB(2), "NO MAP."), (NB(4), "NO WAY BACK."), (NB(6), "JUST THE TIDE.")]
KINETIC_END = B(8)
_X = (999.0, 999.5, "", "")
TEXT = {
    "LOGO": (B(8) + 0.05, B(19)),
    "C0": (B(20) + 0.1, B(27), "No mainland", "every island is earned"),
    "C1": _X, "C2": _X,
    "C3": (B(102) + 0.1, B(110), "Java + Bedrock", "one ocean, any device"),
    "T1": _X,
    "TOAST": (999.0, 999.5, "", ""),
    "POP2": (B(86) + 0.1, B(93) - 0.1, "STORM SURVIVED!", "+ the sea gives back"),
    "POP": (B(94) + 0.1, B(101) - 0.1, "ISLAND DISCOVERED!", "+ claim it, build it, keep it"),
    "END": (B(134), TOTAL),
    "CREDIT": (B(135), TOTAL - 0.3),
}
TOASTS = [(B(28) + 0.1, B(39), "Advancement Made!", "Set Sail"),
          (B(42), B(52), "Advancement Made!", "Hold Your Breath"),
          (B(61), B(69), "Advancement Made!", "Into the Deep")]

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
