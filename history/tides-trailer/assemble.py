"""Footage track for the Tides SMP trailer (FINAL_PLAN.md section 3), built in ffmpeg.

python assemble.py   -> WORK/footage.mp4 (1920x1080 60 fps, 79.0 s, no audio)
Each shot gets its push-in/drift (zoompan on a 4K upscale, so the slow zoom stays smooth),
then the shots are chained with xfade at the plan's exact overlap windows.
"""
import pathlib, subprocess
from build import SHOTS, TOTAL

ROOT = pathlib.Path(__file__).parent
WORK = pathlib.Path("C:/Users/Siddharth D/tides-work")
WORK.mkdir(exist_ok=True)
FPS = 60

def ff(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)

def planes(c, xs, ys):
    return f"if(eq(PLANE,0),{c}0({xs},{ys}),if(eq(PLANE,1),{c}1({xs},{ys}),{c}2({xs},{ys})))"

def warp_expr(xs, ys, extra=""):
    return f"({planes('a', xs, ys)}*P+{planes('b', xs, ys)}*(1-P)){extra}"

D = "hypot(X-W/2,Y-H*0.45)"
RIP = f"(0.018*W*sin(PI*P)*sin({D}/W*55-(1-P)*12))"
# gbrp planes: 0 = G, 1 = B, 2 = R
GLOW = "255*0.55*sin(PI*P)*exp(-(pow((X-W*0.35)/(W*0.45),2)+pow((Y-H*0.35)/(H*0.6),2)))"
EXPR = {
    "ripple-waves": warp_expr(f"clip(X+{RIP}*(X-W/2)/({D}+1),0,W-1)", f"clip(Y+{RIP}*(Y-H*0.45)/({D}+1),0,H-1)"),
    "light-leak": f"min(255,A*P+B*(1-P)+{GLOW}*if(eq(PLANE,2),1,if(eq(PLANE,0),0.65,0.3)))",
    "cross-warp-morph": warp_expr("clip(X+0.02*W*sin(PI*P)*sin(Y/H*9+(1-P)*6),0,W-1)",
                                  "clip(Y+0.02*H*sin(PI*P)*cos(X/W*7+(1-P)*5),0,H-1)"),
    "domain-warp": warp_expr("clip(X+0.012*W*sin(PI*P)*sin(Y/H*14+X/W*5+(1-P)*8),0,W-1)",
                             "clip(Y+0.012*H*sin(PI*P)*sin(X/W*11-(1-P)*6),0,H-1)",
                             "+18*sin(PI*P)"),
}

def push(sid, a, b, sc, dx, dy):
    out = WORK / f"p_{sid}.mp4"
    if out.exists():
        return out
    n = round((b - a) * FPS)
    z = f"1+({sc}-1)*on/{max(n - 1, 1)}"
    x = f"(iw-iw/zoom)/2+{2 * dx}*on/{max(n - 1, 1)}"
    y = f"(ih-ih/zoom)/2+{2 * dy}*on/{max(n - 1, 1)}"
    vf = (f"tpad=stop_mode=clone:stop_duration=1,trim=end_frame={n},setpts=N/{FPS}/TB,"
          f"scale=3840:2160:flags=lanczos,zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS},"
          "format=yuv420p")
    ff("-i", str(ROOT / "assets" / f"{sid}.mp4"), "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "12", str(out))
    return out

def main():
    clips = [push(sid, a, b, sc, dx, dy) for sid, a, b, sc, dx, dy, _, _ in SHOTS]
    inputs = sum([["-i", str(c)] for c in clips], [])
    fc, prev = [], "[0:v]format=gbrp[v0]"
    fc.append(prev)
    for i in range(1, len(clips)):
        fc.append(f"[{i}:v]format=gbrp[c{i}]")
    last = "v0"
    chain_end = SHOTS[0][2] - SHOTS[0][1]
    for i, (sid, a, b, sc, dx, dy, tr, td) in enumerate(SHOTS[:-1]):
        # Overlap the next shot by the transition length, measured from where the chain really ends
        # (a hard cut is a 1-frame fade, so each one pulls the rest of the edit 1 frame earlier).
        dur = 2 / FPS if tr == "cut" else td  # xfade stops the chain on a 1-frame fade
        kind = "transition=fade" if tr in ("cut", "css") else f"transition=custom:expr='{EXPR[tr]}'"
        off = chain_end - dur
        nxt = SHOTS[i + 1]
        chain_end = off + (nxt[2] - nxt[1])
        fc.append(f"[{last}][c{i + 1}]xfade={kind}:duration={dur:.4f}:offset={off:.4f}[x{i + 1}]")
        last = f"x{i + 1}"
    end = chain_end
    fc.append(f"[{last}]format=yuv420p,tpad=stop_mode=add:stop_duration={TOTAL - end + 0.1:.3f}:color=black,"
              f"trim=duration={TOTAL}[out]")
    ff(*inputs, "-filter_complex", ";".join(fc), "-map", "[out]", "-r", str(FPS),
       "-c:v", "libx264", "-preset", "medium", "-crf", "12", str(WORK / "footage.mp4"))

if __name__ == "__main__":
    main()
