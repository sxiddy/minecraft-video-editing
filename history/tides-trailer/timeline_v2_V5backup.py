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
TRANS = {"none": (0, 0), "cut": (0, 0), "fade": (12, 12), "zoom": (8, 8), "whip": (8, 8),
         "flash": (6, 22), "dip": (4, 8), "ripple": (15, 15), "leak": (15, 15), "slow": (45, 45)}

# start, clip, source in (s), speed ramp, transition IN, overlays, shake on entry
# ramps: fs fast->slow, sf slow->fast (accelerating into the next cut), slow 0.55x, n 1x, half 0.5x
# V4 (client: "use less clips, use long clips, ~50 s, calm, no overlays on our shader footage, no AI-template
# transitions"). Each clip once, real speed, untouched look, hard cuts on bar lines (1 bar = 4 beats = 1.5 s).
# Music from song beat 96: quiet bars, the A-section hit at e8 (3.0 s), the drop at e104 (39.0 s).
SHOTS = [
    # V5.1: uneven shot lengths (3 / 6 / 3 / 3 / 7.5 / 4.5 / 4.5 / 4.5 / 6 s), each clip ONCE, real speed, untouched.
    (B(0),   31, 1.0, "n", "none", "", 0),   # quiet open: sun glare
    (B(8),   1,  4.0, "n", "cut",  "", 0),   # golden island, middle of its slow move; TIDES
    (B(24),  5,  1.6, "n", "cut",  "", 0),   # sailing under the clouds (drums come in)
    (B(32),  28, 5.5, "n", "cut",  "", 0),   # raft at its busiest (motion peak ~7 s)
    (B(40),  8,  0.05, "n", "cut", "", 0),   # swim -> dive: head goes under (src 7.5) exactly at B60 = 22.5 s
    (B(60),  13, 1.0, "n", "cut",  "", 0),   # the drop: underwater shader light
    (B(72),  10, 3.5, "n", "cut",  "", 0),   # reef
    (B(84),  29, 1.0, "n", "cut",  "", 0),   # resurface: raft at sea
    (B(96),  26, 1.0, "n", "cut",  "", 0),   # sunset, held
    (B(112), 14, 2.0, "half", "slow", "blur", 0),  # the one slow dissolve: under the server join + end card
]

TOTAL = round(B(146), 3)
DROP, CLIMAX = B(60), B(134)
BUILDS = []
TITLE_WINDOWS = []                                  # no scrim/backdrop behind any text
INFO = (B(112) + 0.5, B(134) - 0.1)                 # multiplayer screen (V2/V3 sequence)
BARS_OPEN = (B(111), B(113))
FADE_OUT = (TOTAL - 0.5, TOTAL)

KINETIC = []
_X = (999.0, 999.5, "", "")
TEXT = {
    "LOGO": (B(12), B(21)),
    "C0": _X, "C1": _X, "C2": _X, "C3": _X, "T1": _X,
    "TOAST": (999.0, 999.5, "", ""),
    "POP": (999.0, 999.5, "", ""), "POP2": (999.0, 999.5, "", ""),
    "END": (B(134), TOTAL),
    "CREDIT": (B(135), TOTAL - 0.3),
}
TOASTS = []

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
