"""Section 8: fetch a player's real Minecraft skin by username (Java edition). Never repaint a skin.

    python pipeline/mc_skin.py <username> [--out <folder>]

Asks Mojang's API for the account, downloads the skin PNG and writes <username>.png plus
<username>.json (uuid, model "slim" or "classic", source URL). Falls back to minotar.net if Mojang
does not answer. Default folder: media-library/skins. Bedrock-only players have no Java skin: ask
the client for the PNG instead.
"""
import argparse
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from config import SKINS

UA = {"User-Agent": "video-pipeline/1.0"}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return r.read()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("username")
    ap.add_argument("--out", default=str(SKINS))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"username": a.username}
    try:
        prof = json.loads(get(f"https://api.mojang.com/users/profiles/minecraft/{a.username}"))
        meta.update(username=prof["name"], uuid=prof["id"])
        sess = json.loads(get(f"https://sessionserver.mojang.com/session/minecraft/profile/{prof['id']}"))
        tex = json.loads(base64.b64decode(next(p["value"] for p in sess["properties"] if p["name"] == "textures")))
        skin = tex["textures"].get("SKIN")
        if not skin:
            sys.exit(f"STOP: {prof['name']} has no custom skin (default Steve/Alex). Ask the client.")
        meta.update(model=skin.get("metadata", {}).get("model", "classic"), source=skin["url"])
        png = get(skin["url"])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            sys.exit(f"STOP: no Java account named '{a.username}'. Check the spelling or ask for the PNG.")
        raise
    except (urllib.error.URLError, TimeoutError) as e:
        print("Mojang did not answer (", e, "); trying minotar.net")
        meta.update(model="unknown: check the arm width (3 px = slim, 4 px = classic)",
                    source=f"https://minotar.net/skin/{a.username}")
        png = get(meta["source"])
    if png[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit("STOP: the download is not a PNG")
    w, h = int.from_bytes(png[16:20], "big"), int.from_bytes(png[20:24], "big")
    meta["size"] = f"{w}x{h}"
    if (w, h) != (64, 64):
        print(f"WARN: skin is {w}x{h}, not 64x64 (old 64x32 skins have no outer layer on the body)")
    name = meta["username"]
    (out / f"{name}.png").write_bytes(png)
    (out / f"{name}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"{name}: {meta['size']}, model {meta['model']} -> {out / (name + '.png')}")
    print("In Blender (MCprep): pick the rig matching the model, then swap the skin texture to this file.")

if __name__ == "__main__":
    main()
