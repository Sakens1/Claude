#!/usr/bin/env python3
"""Verifica que el taller corregido no tape nada del original: compara cada página del PDF corregido
con la del PDF entregado y cuenta los píxeles que ya tenían contenido y que cambiaron.

Uso:
    python3 comun/verificar_superposicion.py original.pdf corregido.pdf

Sale con código 0 si no hay superposiciones y 1 si las hay (indica página y zona en puntos).
Requiere PyMuPDF y numpy.
"""
import sys

import numpy as np
import pymupdf

UMBRAL_PIXELES = 40  # tolerancia por página (antialias en bordes)


def imagen(page, zoom=2.0):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), colorspace=pymupdf.csGRAY, alpha=False)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).astype(int)


def revisar(original, corregido, zoom=2.0):
    a, b = pymupdf.open(original), pymupdf.open(corregido)
    problemas = []
    if len(a) != len(b):
        problemas.append(f"distinta cantidad de páginas: original {len(a)}, corregido {len(b)}")
    for i, (pa, pb) in enumerate(zip(a, b)):
        A, B = imagen(pa, zoom), imagen(pb, zoom)
        sobre = (np.abs(A - B) > 60) & (A < 200)
        n = int(sobre.sum())
        if n > UMBRAL_PIXELES:
            ys, xs = np.where(sobre)
            problemas.append(f"página {i + 1}: {n} píxeles tapados en x {xs.min() / zoom:.0f}–{xs.max() / zoom:.0f}, "
                             f"y {ys.min() / zoom:.0f}–{ys.max() / zoom:.0f} (puntos)")
    return problemas


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    problemas = revisar(sys.argv[1], sys.argv[2])
    if problemas:
        print("SUPERPOSICIONES:")
        for p in problemas:
            print(" -", p)
        return 1
    print("OK: el corregido no tapa contenido del original.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
