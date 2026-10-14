#!/usr/bin/env python3
"""Logo de SudokuSolver : UNE source SVG, tout le reste en est rendu.

    QT_QPA_PLATFORM=offscreen python make_logo.py      (Pillow requis)

Sorties : logo.svg (la source), logo_{16,32,64,128,256,512}.png, logo.png
(= 512, icône de fenêtre et entrée de menu Linux), logo.ico (installeur
Windows, multi-tailles) et logo.icns (macOS). Les chiffres sont rendus avec
la police embarquée (polices/), pas avec celles du système : le logo est le
même sur toutes les machines qui le régénèrent.
"""
import sys
from pathlib import Path

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QFontDatabase, QImage, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QApplication

ICI = Path(__file__).resolve().parent

FOND_1, FOND_2 = "#1c2a4e", "#101628"
OR, OR_CLAIR, CHIFFRE = "#f0dca0", "#fff5d2", "#fff0be"
ACCENT = "#ffc450"
GRILLE = [
    "5...3...7", "...6.....", ".98....6.", "....6...3", "4..8.3..1",
    "7...2....", ".6....28.", "...4.9..5", "3...8...9",
]


def construire_svg() -> str:
    n, pad = 256, 26
    cote = n - 2 * pad
    case = cote / 9
    traits = []
    for i in range(10):
        p = pad + i * case
        epais = 3.2 if i % 3 == 0 else 1.0
        couleur = OR if i % 3 == 0 else OR_CLAIR
        op = "1" if i % 3 == 0 else "0.75"
        traits.append(f'<line x1="{p:.2f}" y1="{pad}" x2="{p:.2f}" y2="{n - pad}" '
                      f'stroke="{couleur}" stroke-width="{epais}" opacity="{op}"/>')
        traits.append(f'<line x1="{pad}" y1="{p:.2f}" x2="{n - pad}" y2="{p:.2f}" '
                      f'stroke="{couleur}" stroke-width="{epais}" opacity="{op}"/>')
    chiffres = []
    for r, ligne in enumerate(GRILLE):
        for c, ch in enumerate(ligne):
            if ch == ".":
                continue
            cx, cy = pad + (c + 0.5) * case, pad + (r + 0.5) * case
            chiffres.append(f'<text x="{cx:.2f}" y="{cy + case * 0.26:.2f}" '
                            f'text-anchor="middle">{ch}</text>')
    hx, hy = pad + 8.5 * case, pad + 0.5 * case
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{n}" height="{n}" viewBox="0 0 {n} {n}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="fond" cx="50%" cy="45%" r="70%">
      <stop offset="0%" stop-color="{FOND_1}"/>
      <stop offset="100%" stop-color="{FOND_2}"/>
    </radialGradient>
    <radialGradient id="halo" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{ACCENT}" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="{ACCENT}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="4" y="4" width="{n - 8}" height="{n - 8}" rx="34" fill="url(#fond)"/>
  <rect x="{pad - 6}" y="{pad - 6}" width="{cote + 12}" height="{cote + 12}" rx="16"
        fill="none" stroke="{ACCENT}" stroke-width="3"/>
  <circle cx="{hx:.2f}" cy="{hy:.2f}" r="{case * 0.62:.2f}" fill="url(#halo)"/>
  {chr(10).join("  " + t for t in traits)}
  <g font-family="Source Sans 3, DejaVu Sans, sans-serif" font-size="{case * 0.74:.1f}"
     font-weight="600" fill="{CHIFFRE}">
  {chr(10).join("    " + t for t in chiffres)}
  </g>
</svg>
'''


def rendre(svg: Path, sortie: Path, taille: int) -> None:
    img = QImage(taille, taille, QImage.Format.Format_ARGB32)
    img.fill(0)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    QSvgRenderer(str(svg)).render(p, QRectF(0, 0, taille, taille))
    p.end()
    img.save(str(sortie), "PNG")


def main():
    app = QApplication(sys.argv)  # noqa: F841 — requis pour le rendu
    for f in sorted((ICI / "polices").glob("*.otf")):
        QFontDatabase.addApplicationFont(str(f))
    svg = ICI / "logo.svg"
    svg.write_text(construire_svg(), encoding="utf-8")
    for taille in (16, 32, 64, 128, 256, 512):
        rendre(svg, ICI / f"logo_{taille}.png", taille)
    (ICI / "logo.png").write_bytes((ICI / "logo_512.png").read_bytes())
    from PIL import Image
    grand = ICI / "_logo_1024.png"
    rendre(svg, grand, 1024)
    img = Image.open(grand).convert("RGBA")
    img.save(ICI / "logo.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48),
                                      (64, 64), (128, 128), (256, 256)])
    img.save(ICI / "logo.icns")
    grand.unlink()
    print("logo.svg -> logo_*.png, logo.png, logo.ico, logo.icns")


if __name__ == "__main__":
    main()
