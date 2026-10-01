#!/usr/bin/env python3
"""Atajo a comun/extraer_taller.py (extrae a texto un taller .docx o .pdf y sus imágenes)."""
import os
import runpy
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.argv[0] = os.path.join(AQUI, "..", "..", "comun", "extraer_taller.py")
runpy.run_path(sys.argv[0], run_name="__main__")
