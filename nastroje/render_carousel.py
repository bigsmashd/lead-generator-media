"""Layout A (Brand Kit, 16. 11. 2026): plná červená #B71C1C, horní proužek #7F0000,
štítek tématu nahoře, text svisle na střed, dole monogram DD + jméno a „Přejeďte →“ / číslo slidu.
Použití: python3 render_carousel.py slides.json out_dir
slides.json: {"tema": "...", "slidy": [{"nadpis": "...", "text": "..."}, ...], "poznamka": "..."}
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
RED, DARK = "#B71C1C", "#7F0000"
WHITE = "#FFFFFF"
F = "/usr/share/fonts/opentype/inter/"
XB = F + "Inter-ExtraBold.otf"
BD = F + "Inter-Bold.otf"
MD = F + "Inter-Medium.otf"
SB = F + "Inter-SemiBold.otf"
M = 96  # okraj


def font(path, size):
    return ImageFont.truetype(path, size)


def nbsp(text):
    """Česká typografie: jednopísmenné předložky a spojky a číslo + slovo nezůstanou na konci řádku."""
    import re
    text = re.sub(r"(?<![\w])([aikosuvzAIKOSUVZ]) ", "\\1\u00a0", text)
    return re.sub(r"(\d) ", "\\1\u00a0", text)


def wrap(draw, text, fnt, width):
    lines = []
    for para in nbsp(text).split("\n"):
        words, cur = [w for w in para.split(" ") if w], ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=fnt) <= width:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def fit(draw, text, path, start, minsize, width, maxh, spacing=1.22):
    size = start
    while size >= minsize:
        fnt = font(path, size)
        lines = wrap(draw, text, fnt, width)
        h = len(lines) * size * spacing
        if h <= maxh:
            return fnt, lines, size * spacing
        size -= 2
    fnt = font(path, minsize)
    return fnt, wrap(draw, text, fnt, width), minsize * spacing


def render(spec, out):
    out.mkdir(parents=True, exist_ok=True)
    n = len(spec["slidy"])
    paths = []
    for i, s in enumerate(spec["slidy"], 1):
        im = Image.new("RGB", (W, H), RED)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, W, 18], fill=DARK)

        # štítek tématu
        tf = font(SB, 30)
        label = spec["tema"].upper()
        tw = d.textlength(label, font=tf)
        d.rounded_rectangle([M, 80, M + tw + 44, 80 + 58], radius=29, outline=WHITE, width=3)
        d.text((M + 22, 80 + 29), label, font=tf, fill=WHITE, anchor="lm")

        # obsah svisle na střed
        top, bottom = 200, H - 230
        area = bottom - top
        blocks = []
        if s.get("nadpis"):
            start = 84 if i == 1 else 66
            hf, hl, hlh = fit(d, s["nadpis"], XB, start, 44, W - 2 * M, area * (0.9 if not s.get("text") else 0.5))
            blocks.append((hf, hl, hlh))
        if s.get("text"):
            used = sum(len(b[1]) * b[2] for b in blocks)
            bf, bl, blh = fit(d, s["text"], MD, 46, 32, W - 2 * M, area - used - 40)
            blocks.append((bf, bl, blh))
        gap = 40
        total = sum(len(b[1]) * b[2] for b in blocks) + gap * (len(blocks) - 1)
        y = top + (area - total) / 2
        for bi, (f_, lines, lh) in enumerate(blocks):
            for ln in lines:
                d.text((M, y), ln, font=f_, fill=WHITE)
                y += lh
            if bi == 0 and len(blocks) > 1:
                # poloprůhledné bílé podtržení pod nadpisem
                ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(ov).rectangle([M, y + 8, M + 160, y + 16], fill=(255, 255, 255, 120))
                im.paste(Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB"))
                d = ImageDraw.Draw(im)
            y += gap

        # patička
        if spec.get("poznamka") and i == n:
            pf = font(MD, 26)
            d.text((M, H - 200), spec["poznamka"], font=pf, fill=(255, 220, 220))
        cy, r = H - 110, 38
        d.ellipse([M, cy - r, M + 2 * r, cy + r], outline=WHITE, width=3)
        d.text((M + r, cy), "DD", font=font(BD, 30), fill=WHITE, anchor="mm")
        d.text((M + 2 * r + 22, cy), "Dominik Dyntar", font=font(SB, 32), fill=WHITE, anchor="lm")
        right = "Přejeďte →" if i < n else f"{i}/{n}"
        if i < n:
            right = f"{i}/{n}  ·  Přejeďte →"
        d.text((W - M, cy), right, font=font(MD, 28), fill=WHITE, anchor="rm")

        p = out / f"{i:02d}.png"
        im.save(p, optimize=True)
        paths.append(p)
    return paths


if __name__ == "__main__":
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for p in render(spec, Path(sys.argv[2])):
        print(p)
