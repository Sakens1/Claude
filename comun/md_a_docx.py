#!/usr/bin/env python3
"""Convierte una pauta en Markdown a .docx (versión para el docente).

Uso:
    python3 comun/md_a_docx.py pauta.md Pauta.docx

Soporta el subconjunto de Markdown usado en la pauta: títulos #/##/###, párrafos,
listas con '-' o '1.', tablas con '|', negrita **...**, código `...` y reglas '---'.
Requiere python-docx.
"""
import argparse
import re

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm

AZUL = RGBColor(0x1F, 0x4E, 0x79)


def runs(p, texto, negrita=False):
    for parte in re.split(r"(\*\*.+?\*\*|`.+?`)", texto):
        if not parte:
            continue
        if parte.startswith("**"):
            r = p.add_run(parte[2:-2])
            r.bold = True
        elif parte.startswith("`"):
            r = p.add_run(parte[1:-1])
            r.font.name = "Consolas"
        else:
            r = p.add_run(parte)
            r.bold = negrita


def sombrear(celda, color):
    tcPr = celda._element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def tabla(d, filas):
    filas = [f for f in filas if not re.fullmatch(r"\|[\s\-:|]+\|", f)]
    datos = [[c.strip() for c in f.strip().strip("|").split("|")] for f in filas]
    ncol = len(datos[0])
    t = d.add_table(rows=len(datos), cols=ncol)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    # columna de criterio más ancha
    anchos = [Cm(2.2)] + [Cm((16.0 - 2.2) / (ncol - 1))] * (ncol - 1) if ncol > 1 else [Cm(16)]
    if ncol == 4:
        anchos = [Cm(3.5), Cm(4.5), Cm(4.0), Cm(4.0)]
    if ncol == 3:
        anchos = [Cm(1.8), Cm(11.4), Cm(2.8)]
    for i, fila in enumerate(datos):
        for j, txt in enumerate(fila[:ncol]):
            c = t.cell(i, j)
            c.width = anchos[j]
            p = c.paragraphs[0]
            runs(p, txt, negrita=(i == 0))
            for r in p.runs:
                r.font.size = Pt(9.5)
            if i == 0:
                sombrear(c, "D9E2F3")
    d.add_paragraph()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("salida")
    a = ap.parse_args(argv)
    ENTRADA, SALIDA = a.entrada, a.salida
    d = docx.Document()
    sec = d.sections[0]
    sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)
    sec.left_margin = sec.right_margin = Cm(2.0)
    sec.top_margin = sec.bottom_margin = Cm(2.0)
    est = d.styles["Normal"]
    est.font.name = "Arial"
    est.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    est.font.size = Pt(10.5)
    for nivel, tam in ((1, 15), (2, 13), (3, 11.5)):
        h = d.styles[f"Heading {nivel}"]
        h.font.name = "Arial"
        h.font.size = Pt(tam)
        h.font.color.rgb = AZUL

    lineas = open(ENTRADA, encoding="utf-8").read().splitlines()
    i = 0
    while i < len(lineas):
        ln = lineas[i]
        if ln.startswith("|"):
            bloque = []
            while i < len(lineas) and lineas[i].startswith("|"):
                bloque.append(lineas[i])
                i += 1
            tabla(d, bloque)
            continue
        if ln.startswith("```"):
            i += 1
            while i < len(lineas) and not lineas[i].startswith("```"):
                p = d.add_paragraph()
                r = p.add_run(lineas[i])
                r.font.name = "Consolas"
                r.font.size = Pt(9)
                i += 1
        elif m := re.match(r"(#{1,3}) (.*)", ln):
            d.add_heading(m.group(2), level=len(m.group(1)))
        elif ln.strip() == "---":
            p = d.add_paragraph()
            pPr = p._element.get_or_add_pPr()
            bdr = OxmlElement("w:pBdr")
            b = OxmlElement("w:bottom")
            for k, v in (("val", "single"), ("sz", "6"), ("space", "1"), ("color", "999999")):
                b.set(qn(f"w:{k}"), v)
            bdr.append(b)
            pPr.append(bdr)
        elif m := re.match(r"\s*- (.*)", ln):
            runs(d.add_paragraph(style="List Bullet"), m.group(1))
        elif m := re.match(r"\s*\d+\. (.*)", ln):
            runs(d.add_paragraph(style="List Number"), m.group(1))
        elif ln.strip():
            p = d.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            runs(p, ln)
        i += 1
    zoom = d.settings.element.find(qn("w:zoom"))  # la plantilla de python-docx omite w:percent
    if zoom is not None and zoom.get(qn("w:percent")) is None:
        zoom.set(qn("w:percent"), "100")
    d.save(SALIDA)
    print("Generado:", SALIDA)


if __name__ == "__main__":
    main()
