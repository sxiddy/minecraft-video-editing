"""Section 7: copy Minecraft's own sounds out of the installed game so edits use the real ones.

    python pipeline/mc_sounds.py --list [--match <regex>]         # show what exists
    python pipeline/mc_sounds.py --match "random/levelup|entity/player/hurt"
    python pipeline/mc_sounds.py --all

The game stores sounds under hashed names; assets/indexes/<n>.json maps real names to hashes.
Copies to media-library/mc_sounds/<same path>.ogg. Uses the newest index unless --index is given.
Use these only in videos about Minecraft (Mojang's usage guidelines); do not redistribute them.
"""
import argparse
import json
import re
import shutil
import sys

from config import MC, MC_SOUNDS

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--match", help="regex on the path after minecraft/sounds/, e.g. 'block/chest|ambient/cave'")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true", help="print matching names, copy nothing")
    ap.add_argument("--index", help="index name without .json (default: highest number)")
    ap.add_argument("--out", default=str(MC_SOUNDS))
    a = ap.parse_args()
    if not (a.match or a.all or a.list):
        ap.error("give --match <regex>, --all or --list")
    idx_dir = MC / "assets" / "indexes"
    if not idx_dir.is_dir():
        sys.exit(f"STOP: {idx_dir} not found. Launch Minecraft once so it downloads its assets.")
    indexes = sorted(idx_dir.glob("*.json"), key=lambda p: (not p.stem.isdigit(), int(p.stem) if p.stem.isdigit() else 0, p.stem))
    idx = idx_dir / f"{a.index}.json" if a.index else [p for p in indexes if p.stem.isdigit()][-1]
    objects = json.loads(idx.read_text(encoding="utf-8"))["objects"]
    pat = re.compile(a.match) if a.match else None
    prefix = "minecraft/sounds/"
    hits = sorted((k[len(prefix):], v["hash"]) for k, v in objects.items()
                  if k.startswith(prefix) and k.endswith(".ogg") and (pat is None or pat.search(k[len(prefix):])))
    print(f"index {idx.name}: {len(hits)} matching sounds")
    if a.list:
        for name, _ in hits:
            print(" ", name)
        return
    from pathlib import Path
    out, copied, missing = Path(a.out), 0, 0
    for name, h in hits:
        src = MC / "assets" / "objects" / h[:2] / h
        if not src.is_file():
            missing += 1
            continue
        dst = out / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        copied += 1
    print(f"copied {copied} to {out}" + (f", {missing} not downloaded yet (launch that game version once)" if missing else ""))

if __name__ == "__main__":
    main()
