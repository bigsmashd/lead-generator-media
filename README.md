# lead-generator-media

Veřejné obrázky postů pro Metricool (stahuje je přes raw URL). Jen hotové vizuály schválených postů, žádná osobní data.

- `posty/<ID>/NN.png` – slidy 1080 × 1350, layout A (Brand Kit)
- `posty/<ID>/slidy.json` – zdrojový text slidů
- `nastroje/render_carousel.py` – renderer layoutu A: `python3 nastroje/render_carousel.py posty/<ID>/slidy.json posty/<ID>`

Zápis rovnou do `main` (rozhodnutí obchodníka 23. 11. 2026).
