# lead-generator-media

Veřejné obrázky postů pro Metricool (stahuje je přes raw URL). Jen hotové vizuály schválených postů, žádná osobní data.

- `posty/<ID>/NN.png` – slidy 1080 × 1350, layout A (Brand Kit)
- `posty/<ID>/slidy.json` – zdrojový text slidů
- `nastroje/render_reel.py` – Reel 1080 × 1920 z `posty/<ID>/reel.json` (snímky s délkou v s, prolínání, bez hudby): `python3 nastroje/render_reel.py posty/<ID>/reel.json posty/<ID>` → `reel.mp4`
- `nastroje/render_carousel.py` – renderer layoutu A: `python3 nastroje/render_carousel.py posty/<ID>/slidy.json posty/<ID>`

Zápis rovnou do `main` (rozhodnutí obchodníka 23. 11. 2026).
