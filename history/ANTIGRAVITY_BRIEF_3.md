V5.1 FEEDBACK -> PLAN V6 (Tides SMP trailer)

We built V5.1 exactly to your plan (3/6/3/3/7.5/4.5/4.5/4.5/6 s cuts, stems, muffle, end hit, plain title).
Result: it reads like a PowerPoint. It has LESS edit than earlier versions. An independent review found why:

WHY IT'S A SLIDESHOW
- Every cut falls on a 1.5 s bar line. No motion carries across any cut: no match direction, no cut-on-action.
  Each shot starts "at rest" like a new slide.
- In-points sit on dead frames. c28 (the only high-motion clip, peak at 7 s) gets 3 s and leaves before its peak.
- 15-22.5 s: c8 is a tiny swimmer on a grey sea for 7.5 s, the flattest stretch, right where the build should be.
  The cut lands on the frame the head goes under, so the dive payoff is lost across the cut.
- No build: shots get LONGER after the drop (flat 4.5 s). The edit has no energy where the song peaks.
- The title is placed, not designed: a small static serif on c1, like a slide heading.
- No sound design. The footage is silent, so the dive has no splash, there are no water beds, and the muffle
  barely reads. That makes it feel like music over stills.
- The ending (blurred c14 + join UI) is 12.75 s, 23% of the runtime, and feels slow.

V6 PLAN (160 BPM, beat 0.375 s, each clip once, real footage only, NO overlays, NO grade)
0-3.0      c31 6.0->9.0   glare with no swimmer; slow 108% punch-in; wind/water bed fades up
3.0-7.5    c1 7.0->11.5   "TIDES" behind the island horizon (sky luma key, so land occludes the letter bottoms),
                          one letter per beat, 3.0 to 4.5
7.5-10.5   c5 0.4->3.4    cut on c1's drift (matching L->R direction); drums enter
10.5-15.0  c28 3.5->8.0   ends ON its 7 s motion peak; one hard 115% crop punch-in at 12.75
15.0-18.0  c29 0.4->3.4   acceleration starts
18.0-19.5  c26 5.5->7.0
19.5-22.5  c8 4.5->8.2    the ONE speed ramp: 1.0x->1.5x, then 0.5x as the head goes under; splash SFX on 22.5;
                          J-cut the underwater muffle from 21.75
22.5-25.5  c13 0.5->3.5   the drop; muffled
25.5-27.0  c10 8.0->9.5   cut on the reef's 9.5 s motion spike (the biggest motion in the footage)
27.0-28.5  c30 (best 1.5 s)  resurface; the muffle opens, breath/splash SFX
28.5-33.0  c25 0.4->4.9   hold the reflection (optional: one line tracked behind the horizon, a word per bar.
                          Default: no text)
33.0-~48   multiplayer join screen over blurred c14, cut down to ~9 s -> end card (IPs, Bedrock "." note,
           Kevin MacLeod CC BY credit) -> music hit
Rhythm: 4.5/4.5/3/4.5/3/1.5/3(ramp) into the drop, then 3/1.5/1.5, then breathe into the ending.
Font: condensed grotesk (Inter Tight SemiBold or Neue Haas Grotesk Display), all caps, tracking +80,
flat white at about 90% opacity. No glow, no serif, no sweep.

WHY THIS WON'T READ AS AI/TEMPLATE
cut-on-motion and match cuts are invisible craft; there is exactly ONE motivated ramp; punch-ins are hard crops,
never animated zooms; the type is occluded by the actual terrain; the SFX are diegetic water sounds, not
riser packs.

MUST NOT COME BACK
bubbles/god-rays/flares/light leaks/rain overlays; whip/zoom/ripple transitions; scale-pop captions; repeated
clips; Montserrat/Lilita/Cinzel glow/glossy/pixel fonts; caption scrims; generic slogans; fake advancement
toasts; black tail; colour grade. Keep: the multiplayer join ending, the end card, the full-frame video
watermark, and the single centred thumbnail mark.

WHAT I NEED FROM YOU
1. Critique this V6 plan. Correct any in/out point that doesn't actually land on the motion I describe.
2. How do I do the horizon-occluded title robustly in a numpy/OpenCV + ffmpeg pipeline (luma key vs. a
   hand-drawn mask per frame)?
3. Where to get clean, free diegetic water SFX (splash, underwater, waves) that suit Minecraft.
4. Is ~48 s fine, or should the ending stay longer?
