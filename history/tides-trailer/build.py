"""Generate index.html for the Tides SMP trailer, following ../FINAL_PLAN.md (locked).

Run: python build.py   then  npx hyperframes lint / check / snapshot
Scenes run back to back; each cut sits at the middle of the plan's overlap, and the
shader (or CSS fade) transition spans the plan's overlap window.
"""
import json, pathlib

ROOT = pathlib.Path(__file__).parent
TOTAL = 79.0

# id, plan in, plan out, end scale, drift x, drift y, transition OUT (shader | "css" | "cut"), its duration
SHOTS = [
    ("s01", 0.00, 4.50, 1.06, 0, 0, "ripple-waves", 1.0),
    ("s02", 3.50, 8.00, 1.04, -20, 0, "light-leak", 1.2),
    ("s03", 6.80, 16.80, 1.10, 0, 0, "css", 0.8),
    ("s04", 16.00, 19.00, 1.05, 0, 0, "cut", 0),
    ("s05", 19.00, 22.00, 1.04, 0, 12, "cut", 0),
    ("s17", 22.00, 25.00, 1.05, 0, 0, "css", 0.6),
    ("s06", 24.40, 28.15, 1.05, 0, 0, "css", 0.6),
    ("s07", 27.55, 33.80, 1.07, 30, 0, "css", 0.5),
    ("s08", 33.30, 38.25, 1.04, 0, 0, "ripple-waves", 1.0),
    ("s09", 37.25, 40.25, 1.08, 0, 0, "css", 0.8),
    ("s10", 39.45, 43.95, 1.04, 0, -25, "cross-warp-morph", 1.0),
    ("s11", 42.95, 46.95, 1.06, 0, 0, "ripple-waves", 1.0),
    ("s12", 45.95, 50.95, 1.00, 0, 0, "light-leak", 0.8),
    ("s13", 50.15, 53.15, 1.05, 0, 0, "css", 1.0),
    ("s14", 52.15, 57.15, 1.06, 0, 0, "domain-warp", 1.0),
    ("s15", 56.15, 61.15, 1.05, -30, 0, "css", 1.5),
    ("s16", 59.65, 78.65, 1.03, 0, 0, None, 0),
]

CUT_DUR = 0.04  # a "hard cut" is a near-instant CSS swap
scenes, transitions, tweens = [], [], []
prev_b = 0.0
for i, (sid, a, b, sc, dx, dy, tr, td) in enumerate(SHOTS):
    if tr is None:
        end = b
    else:
        nxt_in = SHOTS[i + 1][1]
        end = round((nxt_in + b) / 2, 3) if tr != "cut" else b
        t = {"time": round(nxt_in if tr != "cut" else b - CUT_DUR / 2, 3),
             "duration": td if tr != "cut" else CUT_DUR}
        if tr not in ("css", "cut"):
            t["shader"] = tr
        transitions.append(t)
    d = round(end - prev_b, 3)
    scenes.append(f'''      <div class="scene" id="{sid}" style="opacity:0;">
        <video id="{sid}-v" class="clip footage" src="assets/{sid}.mp4" data-start="{prev_b:.3f}" data-duration="{d:.3f}" data-track-index="0" muted playsinline></video>
      </div>''')
    tweens.append(f'tl.fromTo("#{sid}-v", {{scale: 1, x: 0, y: 0}}, {{scale: {sc}, x: {dx}, y: {dy}, duration: {d}, ease: "none"}}, {prev_b});')
    prev_b = end

def letters(text, cls):
    return "".join(f'<span class="{cls}">{"&nbsp;" if ch == " " else ch}</span>' for ch in text)

def words(text, cls):
    return " ".join(f'<span class="{cls}">{w}</span>' for w in text.split(" "))

def caption(n, start, end, main, sub):
    return f'''      <div id="o-c{n}" class="ov clip" data-start="{start - 0.9:.2f}" data-duration="{end - start + 0.9:.2f}" data-track-index="2">
        <div id="c{n}" class="cap"><div id="c{n}-main" class="cap-main">{main}</div><div id="c{n}-line" class="cap-line"></div><div id="c{n}-sub" class="cap-sub">{sub}</div></div>
      </div>'''

CAPS = [(1, 27.76, 32.60, "Survive the open sea", "every island is earned"),
        (2, 47.00, 50.40, "Build on the waves", "a home the tide can't take"),
        (3, 53.00, 56.20, "Java + Bedrock", "one ocean, any device")]

font_faces = "\n".join(
    f'''      @font-face {{ font-family: "Cormorant Garamond"; font-style: {st}; font-weight: {w};
        src: url("assets/fonts/cormorant-{w}-{st}.woff2") format("woff2"); }}'''
    for w, st in [(400, "italic"), (500, "italic"), (500, "normal"), (600, "normal")])

html = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
{font_faces}
      :root {{
        --ink: #f4f1ea;
        --teal: #7fd6d2;
        --shadow: 0 2px 18px rgba(0, 20, 30, 0.45);
        --serif: "Cormorant Garamond", serif;
        --caps: "Montserrat", sans-serif;
        --ui: "Inter", sans-serif;
        --mono: "JetBrains Mono", monospace;
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: transparent; }}
      .scene {{ position: absolute; inset: 0; overflow: hidden; background: #000; }}
      .footage {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; }}
      .bar {{ position: absolute; left: 0; width: 1920px; height: 139px; background: #000; z-index: 40; }}
      #bar-top {{ top: 0; }}
      #bar-bot {{ bottom: 0; }}
      .ov {{ position: absolute; inset: 0; z-index: 50; pointer-events: none; color: var(--ink); text-shadow: var(--shadow); }}
      .center {{ position: absolute; left: 0; width: 1920px; text-align: center; }}
      .hair {{ position: absolute; height: 1px; background: rgba(244, 241, 234, 0.7); }}
      .ln {{ font-family: var(--serif); font-style: italic; font-weight: 400; font-size: 52px; letter-spacing: 0.02em; }}
      .ch {{ display: inline-block; }}
      /* TIDES title, rising out of the horizon line */
      #tt-mask {{ position: absolute; left: 0; top: 300px; width: 1920px; height: 240px; overflow: hidden; }}
      .tt {{ position: absolute; left: 0; width: 1920px; text-align: center; font-family: var(--serif); font-weight: 500;
            font-size: 190px; line-height: 240px; letter-spacing: 0.38em; padding-left: 0.38em; }}
      #tt-word {{ top: 0; }}
      #tt-refl {{ top: 540px; height: 240px; opacity: 0; filter: blur(2px); transform-origin: 50% 0;
                 -webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,0.9), transparent 70%); }}
      #ts {{ top: 580px; font-family: var(--ui); font-weight: 400; font-size: 22px; letter-spacing: 0.32em; padding-left: 0.32em;
            text-transform: uppercase; color: rgba(244, 241, 234, 0.78); }}
      /* captions */
      .cap {{ position: absolute; left: 0; top: 470px; width: 1920px; text-align: center; }}
      .cap-main {{ font-family: var(--caps); font-weight: 600; font-size: 36px; letter-spacing: 0.18em; padding-left: 0.18em; text-transform: uppercase; }}
      .cap-line {{ width: 160px; height: 1px; margin: 22px auto 18px; background: rgba(244, 241, 234, 0.75); }}
      .cap-sub {{ font-family: var(--serif); font-style: italic; font-weight: 500; font-size: 34px; letter-spacing: 0.02em; }}
      /* ending */
      #t1 {{ top: 470px; font-family: var(--serif); font-style: italic; font-weight: 500; font-size: 76px; letter-spacing: 0.01em; }}
      .w {{ display: inline-block; }}
      #t2 {{ top: 590px; font-family: var(--ui); font-size: 24px; letter-spacing: 0.30em; padding-left: 0.30em; text-transform: uppercase; color: rgba(244,241,234,0.8); }}
      #lk {{ position: absolute; left: 0; top: 400px; width: 1920px; height: 260px; }}
      #lk-word {{ top: 0; font-family: var(--serif); font-weight: 500; font-size: 118px; letter-spacing: 0.30em; padding-left: 0.30em; }}
      #lk-net {{ top: 160px; font-family: var(--ui); font-size: 20px; letter-spacing: 0.32em; padding-left: 0.32em; text-transform: uppercase; color: rgba(244,241,234,0.72); }}
      #shade {{ position: absolute; inset: 0; z-index: 45;
               background: radial-gradient(ellipse 60% 55% at 50% 48%, rgba(4,22,30,0.5), rgba(4,22,30,0.25) 70%, rgba(4,22,30,0.1)); opacity: 0; }}
      .lab {{ font-family: var(--ui); font-weight: 600; font-size: 18px; letter-spacing: 0.34em; padding-left: 0.34em; color: rgba(244,241,234,0.65); }}
      .addr {{ font-family: var(--mono); font-weight: 500; font-size: 46px; }}
      .port {{ font-family: var(--ui); font-size: 22px; color: rgba(244,241,234,0.6); margin: 0 10px 0 28px; }}
      #steve {{ top: 752px; font-family: var(--mono); font-size: 34px; }}
      #dot {{ display: inline-block; }}
      #note {{ top: 810px; font-family: var(--serif); font-style: italic; font-weight: 500; font-size: 34px; color: rgba(244,241,234,0.85); }}
      #drop {{ position: absolute; left: 0; top: 0; width: 14px; height: 19px; background: #fff;
              border-radius: 50% 50% 50% 50% / 62% 62% 38% 38%; box-shadow: 0 0 6px 2px rgba(127,214,210,0.8); opacity: 0; }}
      .ring {{ position: absolute; left: 0; top: 0; width: 120px; height: 120px; margin: -60px 0 0 -60px; border-radius: 50%;
              border: 1.5px solid rgba(127,214,210,0.9); opacity: 0; }}
      #credit {{ bottom: 22px; top: auto; font-family: var(--ui); font-size: 16px; color: rgba(255,255,255,0.5); text-shadow: none; }}
      #black {{ position: absolute; inset: 0; background: #000; z-index: 60; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">
      <div id="shade" class="clip" data-start="65.5" data-duration="13.5" data-track-index="1"></div>
      <div id="bar-top" class="bar"></div>
      <div id="bar-bot" class="bar"></div>

      <div id="o-open" class="ov clip" data-start="0.4" data-duration="15.4" data-track-index="2">
        <div id="l1" class="center ln" style="top:620px;">{letters("The world is shaped…", "ch l1c")}</div>
        <div id="l2" class="center ln" style="top:600px;">{letters("…by the players who sail into it.", "ch l2c")}</div>
        <div id="hz" class="hair" style="left:360px; top:540px; width:1200px;"></div>
        <div id="tt-mask"><div id="tt-word" class="tt">TIDES</div></div>
        <div id="tt-refl" class="tt">TIDES</div>
        <div id="ts" class="center">A water-world survival server</div>
      </div>
{chr(10).join(caption(*c) for c in CAPS)}
      <div id="o-end" class="ov clip" data-start="56.6" data-duration="22.0" data-track-index="2">
        <div id="t1" class="center">{words("Who you bring matters.", "w")}</div>
        <div id="t2" class="center">Invite friends · earn rewards</div>
        <div id="lk"><div id="lk-word" class="center">TIDES SMP</div><div id="lk-net" class="center">a NightClub Network server</div></div>
        <div id="ihair" class="hair" style="left:510px; top:418px; width:900px; background: rgba(244,241,234,0.6);"></div>
        <div id="jl" class="center lab" style="top:462px;">JAVA</div>
        <div id="ja" class="center addr" style="top:492px;">pm-twirl.gl.joinmc.link</div>
        <div id="bl" class="center lab" style="top:598px;">BEDROCK</div>
        <div id="ba" class="center addr" style="top:628px;">listed-completing.gl.at.ply.gg<span class="port">port</span>35634</div>
        <div id="steve" class="center"><span id="dot">.</span>Steve</div>
        <div id="note" class="center">Bedrock players: your name begins with a drop.</div>
        <div id="drop"></div>
        <div id="r1" class="ring"></div>
        <div id="r2" class="ring"></div>
        <div id="credit" class="center">Music: "Chill Wave" by Kevin MacLeod (incompetech.com) · Licensed under CC BY 4.0</div>
      </div>
      <div id="black" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="3"></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      var tl = gsap.timeline({{ paused: true }});

      // fade from black, dip to black
      tl.fromTo("#black", {{ opacity: 1 }}, {{ opacity: 0, duration: 1.2, ease: "sine.out" }}, 0);
      tl.to("#black", {{ opacity: 1, duration: 1.65, ease: "sine.in" }}, 77.0);
      // letterbox opens for the info
      tl.fromTo("#bar-top", {{ y: 0 }}, {{ y: -139, duration: 1.5, ease: "power2.inOut" }}, 63.6);
      tl.fromTo("#bar-bot", {{ y: 0 }}, {{ y: 139, duration: 1.5, ease: "power2.inOut" }}, 63.6);
      tl.fromTo("#shade", {{ opacity: 0 }}, {{ opacity: 1, duration: 1.5 }}, 65.5);

      var IN = {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.9, ease: "power2.out" }};
      function enter(sel, t, extra) {{ tl.fromTo(sel, Object.assign({{ opacity: 0, y: 14, filter: "blur(6px)" }}, extra || {{}}), IN, t); }}
      function leave(sel, t) {{ tl.to(sel, {{ opacity: 0, y: -8, duration: 0.7, ease: "power2.in" }}, t); }}

      // L1 / L2: letter by letter
      tl.fromTo(".l1c", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.6, stagger: 0.035, ease: "sine.out" }}, 0.6);
      leave("#l1", 3.1);
      tl.fromTo(".l2c", {{ opacity: 0, y: 6 }}, {{ opacity: 1, y: 0, duration: 0.6, stagger: 0.035, ease: "sine.out" }}, 3.9);
      leave("#l2", 7.1);
      // the horizon hairline, then TIDES rises out of it
      tl.fromTo("#hz", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 1.6, ease: "power3.inOut" }}, 4.6);
      tl.fromTo("#tt-word", {{ y: 250, filter: "blur(8px)" }}, {{ y: 0, filter: "blur(0px)", duration: 1.6, ease: "power3.out" }}, 9.5);
      tl.fromTo("#tt-refl", {{ opacity: 0, scaleY: 0 }}, {{ opacity: 0.14, scaleY: -1, duration: 1.6, ease: "power3.out" }}, 9.5);
      enter("#ts", 10.1);
      leave(["#tt-mask", "#tt-refl", "#ts", "#hz"], 15.0);

      // captions: hairline first, then the two lines
      {chr(10) + "      ".join(
          f'tl.fromTo("#c{n}-line", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.4, ease: "power2.out" }}, {s - 1.0:.2f}); '
          f'enter("#c{n}-main", {s - 0.9:.2f}); enter("#c{n}-sub", {s - 0.75:.2f}); leave("#c{n}", {e - 0.7:.2f});'
          for n, s, e, _, _ in CAPS)}

      // T1 word by word, T2, lockup
      tl.fromTo("#t1 .w", {{ opacity: 0, y: 12, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 1.2, stagger: 0.18, ease: "sine.out" }}, 56.9);
      leave("#t1", 60.9);
      enter("#t2", 61.0);
      leave("#t2", 63.7);
      enter("#lk", 63.5, {{ y: 40, filter: "blur(10px)" }});
      tl.to("#lk", {{ y: -185, scale: 0.62, duration: 0.8, ease: "power2.inOut" }}, 66.4);

      // info rows
      tl.fromTo("#ihair", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.8, ease: "power3.inOut" }}, 66.0);
      enter(["#jl", "#ja"], 66.3);
      enter(["#bl", "#ba"], 66.9);
      enter("#steve", 67.8);
      tl.set("#dot", {{ opacity: 0 }}, 0);
      // the droplet becomes the leading "."
      tl.fromTo("#drop", {{ x: 897, y: -20, opacity: 1 }}, {{ x: 897, y: 760, opacity: 1, duration: 0.7, ease: "power2.in" }}, 69.0);
      tl.to("#drop", {{ scale: 0.3, opacity: 0, duration: 0.12 }}, 69.7);
      tl.fromTo("#dot", {{ opacity: 0, scale: 1.8 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, 69.7);
      tl.fromTo("#r1", {{ x: 904, y: 786, scale: 0, opacity: 0.6 }}, {{ scale: 1, opacity: 0, duration: 0.9, ease: "sine.out" }}, 69.7);
      tl.fromTo("#r2", {{ x: 904, y: 786, scale: 0, opacity: 0.6 }}, {{ scale: 1, opacity: 0, duration: 0.9, ease: "sine.out" }}, 69.85);
      enter("#note", 69.1);
      tl.fromTo("#credit", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, 76.5);

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
if __name__ == "__main__":
  (ROOT / "index.html").write_text(html, encoding="utf-8")
  print("scenes", len(SHOTS), "transitions", len(transitions), "end", prev_b)
