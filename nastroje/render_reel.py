"""Reel ve stylu layoutu A (Brand Kit): 1080 × 1920, plná červená #B71C1C, horní proužek #7F0000,
štítek tématu, text svisle na střed (v bezpečné zóně Instagramu), dole monogram DD + jméno.
Snímky se prolínají (ffmpeg xfade), bez zvuku – hudbu lze přidat ručně v Metricoolu / IG.

Použití: python3 render_reel.py reel.json out_dir
reel.json: {"tema": "...", "stitek": "Modelová situace" (volitelné),
            "snimky": [{"nadpis": "...", "text": "...", "sekundy": 3.5}, ...],
            "poznamka": "..." (na posledním snímku)}
Výstup: out_dir/reel.mp4 a out_dir/snimek_NN.png (první snímek = obálka).
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from render_carousel import BD, DARK, MD, RED, SB, WHITE, XB, fit, font  # noqa: E402

W, H = 1080, 1920
M = 96
SAFE_TOP, SAFE_BOTTOM = 300, 1920 - 480  # IG překrývá horní lištu a spodní popisek
FADE = 0.4


def frame(spec, s, i, n):
    im = Image.new("RGB", (W, H), RED)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 18], fill=DARK)

    # štítek(y) nahoře v bezpečné zóně
    x, y0 = M, 230
    for label in [spec["tema"].upper()] + ([spec["stitek"].upper()] if spec.get("stitek") else []):
        tf = font(SB, 32)
        tw = d.textlength(label, font=tf)
        d.rounded_rectangle([x, y0, x + tw + 48, y0 + 62], radius=31, outline=WHITE, width=3)
        d.text((x + 24, y0 + 31), label, font=tf, fill=WHITE, anchor="lm")
        x += tw + 48 + 18

    top, bottom = SAFE_TOP + 60, SAFE_BOTTOM
    area = bottom - top
    blocks = []
    if s.get("nadpis"):
        hf, hl, hlh = fit(d, s["nadpis"], XB, 92 if i == 1 else 76, 50, W - 2 * M,
                          area * (0.85 if not s.get("text") else 0.55))
        blocks.append((hf, hl, hlh))
    if s.get("text"):
        used = sum(len(b[1]) * b[2] for b in blocks)
        bf, bl, blh = fit(d, s["text"], MD, 54, 38, W - 2 * M, area - used - 50)
        blocks.append((bf, bl, blh))
    gap = 50
    total = sum(len(b[1]) * b[2] for b in blocks) + gap * (len(blocks) - 1)
    y = top + (area - total) / 2
    for bi, (f_, lines, lh) in enumerate(blocks):
        for ln in lines:
            d.text((M, y), ln, font=f_, fill=WHITE)
            y += lh
        if bi == 0 and len(blocks) > 1:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(ov).rectangle([M, y + 10, M + 180, y + 19], fill=(255, 255, 255, 120))
            im.paste(Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB"))
            d = ImageDraw.Draw(im)
        y += gap

    if spec.get("poznamka") and i == n:
        d.text((M, SAFE_BOTTOM + 10), spec["poznamka"], font=font(MD, 30), fill=(255, 220, 220))

    # monogram + jméno nad spodní zónou popisku
    cy, r = SAFE_BOTTOM + 110, 40
    d.ellipse([M, cy - r, M + 2 * r, cy + r], outline=WHITE, width=3)
    d.text((M + r, cy), "DD", font=font(BD, 32), fill=WHITE, anchor="mm")
    d.text((M + 2 * r + 24, cy), "Dominik Dyntar", font=font(SB, 36), fill=WHITE, anchor="lm")
    return im


def render(spec, out):
    out.mkdir(parents=True, exist_ok=True)
    sn = spec["snimky"]
    n = len(sn)
    pngs = []
    for i, s in enumerate(sn, 1):
        p = out / f"snimek_{i:02d}.png"
        frame(spec, s, i, n).save(p, optimize=True)
        pngs.append(p)

    durs = [float(s.get("sekundy", 3)) for s in sn]
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for p, dur in zip(pngs, durs):
        cmd += ["-loop", "1", "-t", str(dur + FADE), "-framerate", "30", "-i", str(p)]
    # tichá zvuková stopa (některé platformy video bez audia hůř zpracují)
    total = sum(durs) + FADE
    cmd += ["-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
    chains, last, offset = [], "[0:v]", 0.0
    for k in range(1, n):
        offset += durs[k - 1]
        lab = f"[v{k}]"
        chains.append(f"{last}[{k}:v]xfade=transition=fade:duration={FADE}:offset={offset:.2f}{lab}")
        last = lab
    chains.append(f"{last}format=yuv420p[vout]")
    cmd += ["-filter_complex", ";".join(chains), "-map", "[vout]", "-map", f"{n}:a",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", "30",
            "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
            str(out / "reel.mp4")]
    subprocess.run(cmd, check=True)
    return out / "reel.mp4", pngs


if __name__ == "__main__":
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    mp4, pngs = render(spec, Path(sys.argv[2]))
    print(mp4)
