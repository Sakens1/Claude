#!/usr/bin/env python3
"""Extrae el contenido de un taller resuelto (.docx o .pdf) a texto plano para revisarlo.

- .docx: recorre el cuerpo en orden, incluye tablas (también las que están dentro de
  cuadros de texto, como la Tabla 2 del taller), ecuaciones (OMML) y marca las imágenes.
  Las imágenes se guardan en --imagenes DIR para poder mirarlas (p. ej. el gráfico 1.5).
- .pdf: usa `pdftotext -layout` (poppler).

Uso:
    python3 extraer_taller.py taller_grupo3.docx [--imagenes /tmp/grupo3_img]
"""
import argparse
import os
import subprocess
import sys
import zipfile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"


def texto(el):
    partes = []
    for n in el.iter():
        if n.tag in (W + "t", M + "t") and n.text:
            partes.append(n.text)
        elif n.tag == W + "tab":
            partes.append("\t")
    return "".join(partes)


def sin_fallback(el):
    """Elimina las copias mc:Fallback (Word duplica el contenido de los cuadros de texto)."""
    for fb in list(el.iter(MC + "Fallback")):
        fb.getparent().remove(fb)
    return el


def volcar_tabla(tbl, sangria=""):
    out = []
    for tr in tbl.findall(W + "tr"):
        celdas = []
        for tc in tr.findall(W + "tc"):
            ps = [texto(p).strip() for p in tc.findall(W + "p")]
            celdas.append(" / ".join(x for x in ps if x))
        out.append(sangria + "| " + " | ".join(celdas) + " |")
    return out


def docx_a_texto(ruta, dir_img=None):
    from lxml import etree
    with zipfile.ZipFile(ruta) as z:
        raiz = etree.fromstring(z.read("word/document.xml"))
        if dir_img:
            os.makedirs(dir_img, exist_ok=True)
            for n in z.namelist():
                if n.startswith("word/media/"):
                    with open(os.path.join(dir_img, os.path.basename(n)), "wb") as f:
                        f.write(z.read(n))
    sin_fallback(raiz)
    cuerpo = raiz.find(W + "body")
    lineas = []
    for el in cuerpo:
        if el.tag == W + "p":
            # tablas dentro de cuadros de texto
            for tx in el.iter(W + "txbxContent"):
                for hijo in tx:
                    if hijo.tag == W + "tbl":
                        lineas.append("[TABLA EN CUADRO DE TEXTO]")
                        lineas += volcar_tabla(hijo, "  ")
                    elif hijo.tag == W + "p" and texto(hijo).strip():
                        lineas.append("[cuadro] " + texto(hijo).strip())
                for tx in list(el.iter(W + "txbxContent")):
                    tx.getparent().remove(tx)
            t = texto(el).strip()
            img = any(True for _ in el.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"))
            if t:
                lineas.append(t)
            if img:
                lineas.append("[IMAGEN]")
        elif el.tag == W + "tbl":
            filas = el.findall(W + "tr")
            if len(filas) == 1 and len(filas[0].findall(W + "tc")) == 1:
                # cuadro de respuesta
                lineas.append("[RESPUESTA]")
                for p in filas[0].iter(W + "p"):
                    t = texto(p).strip()
                    if t:
                        lineas.append("  " + t)
                    if any(True for _ in p.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip")):
                        lineas.append("  [IMAGEN]")
                lineas.append("[FIN RESPUESTA]")
            else:
                lineas.append("[TABLA]")
                lineas += volcar_tabla(el, "  ")
    return "\n".join(lineas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archivo")
    ap.add_argument("--imagenes", help="directorio donde guardar las imágenes del .docx")
    a = ap.parse_args()
    ext = os.path.splitext(a.archivo)[1].lower()
    if ext == ".docx":
        print(docx_a_texto(a.archivo, a.imagenes))
    elif ext == ".pdf":
        print(subprocess.run(["pdftotext", "-layout", a.archivo, "-"],
                             capture_output=True, text=True, check=True).stdout)
    else:
        print("Formato no soportado (use .docx o .pdf)", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
