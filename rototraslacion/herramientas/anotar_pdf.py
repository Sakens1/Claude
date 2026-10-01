#!/usr/bin/env python3
"""Atajo a comun/anotar_pdf.py con los encabezados de ítem del Taller 2 (items.json de esta carpeta).

Uso:
    python3 rototraslacion/herramientas/anotar_pdf.py taller.pdf correccion.json -o taller_CORREGIDO.pdf
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "comun"))
import anotar_pdf  # noqa: E402

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--items" not in args:
        args += ["--items", os.path.join(AQUI, "items.json")]
    anotar_pdf.main(args)
