"""Rasterise figures from the paper at 400 dpi and crop them into assets/raster.

Boxes are (left, top, right, bottom) in pixels of a 400-dpi page render.
Run with: .venv/bin/python -I tools/crop_figures.py
"""
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "paper" / "paper.pdf"
OUT = ROOT / "assets" / "raster"
DPI = 400

# output name -> (page number, (left, top, right, bottom) in pixels of a 400-dpi page render).
# Render a page with `pdftoppm -f N -l N -r 400 -png paper/paper.pdf /tmp/page`, measure the box,
# then show the crop with PaperFigure("name.png", "Figure N") and annotate via figure.point(px, py).
FIGURES = {
    # "fig2_results.png": (7, (600, 420, 1730, 1170)),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        pages = {}
        for name, (page, box) in FIGURES.items():
            if page not in pages:
                prefix = Path(tmp) / f"p{page}"
                subprocess.run(
                    ["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(DPI), "-png", str(PDF), str(prefix)],
                    check=True,
                )
                pages[page] = Image.open(next(Path(tmp).glob(f"p{page}-*.png")))
            pages[page].crop(box).save(OUT / name)
            print(name, box)


if __name__ == "__main__":
    main()
