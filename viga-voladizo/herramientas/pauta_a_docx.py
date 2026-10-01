#!/usr/bin/env python3
"""Regenera pauta/Pauta_Taller3_Viga_Voladiza.docx desde pauta/pauta_taller3.md (usa comun/md_a_docx.py)."""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(RAIZ, "..", "comun"))
import md_a_docx  # noqa: E402

if __name__ == "__main__":
    md_a_docx.main([os.path.join(RAIZ, "pauta", "pauta_taller3.md"),
                    os.path.join(RAIZ, "pauta", "Pauta_Taller3_Viga_Voladiza.docx")])
