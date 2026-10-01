#!/usr/bin/env python3
"""Genera el taller corregido: el mismo PDF entregado por el grupo, con el puntaje junto a cada
ítem y, si hubo descuento, un comentario insertado bajo el ítem (antes de que empiece el siguiente).

Agrega además un encabezado con el puntaje total y la nota en la primera página y una hoja
final de resumen.

Uso:
    python3 anotar_pdf.py taller_grupo.pdf correccion.json -o taller_grupo_CORREGIDO.pdf

Formato de correccion.json:
{
  "grupo": "Nombre Apellido, ...",
  "total": 85, "maximo": 100, "nota": "5,9",
  "comentario_general": "texto opcional",
  "items": {
    "1.1": {"puntaje": 7, "max": 10, "comentario": "texto (solo si hay descuento)"},
    ...
  }
}

Si el taller está en .docx, conviértalo primero a PDF (Word: Guardar como PDF).
Requiere PyMuPDF (pip install pymupdf).
"""
import argparse
import json
import os
import re
import sys

import pymupdf

# Orden de los encabezados del taller; "1.7" no tiene puntaje pero delimita el fin de 1.6.
ORDEN = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.5.1", "1.5.2", "1.6", "1.7", "1.7.1", "1.7.2", "1.8"]

ROJO = (0.75, 0.05, 0.05)
VERDE = (0.0, 0.45, 0.15)
FONDO_COMENTARIO = (1.0, 0.94, 0.94)
FONDO_ENCABEZADO = (0.93, 0.95, 1.0)
AZUL = (0.12, 0.30, 0.47)

FUENTES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]
FUENTES_NEGRITA = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def cargar_fuente(rutas, respaldo):
    for r in rutas:
        if os.path.exists(r):
            return r, pymupdf.Font(fontfile=r)
    return None, pymupdf.Font(respaldo)


RUTA_F, FUENTE = cargar_fuente(FUENTES, "helv")
RUTA_FB, FUENTE_B = cargar_fuente(FUENTES_NEGRITA, "hebo")

TAM = 9.5          # tamaño de letra de los comentarios
INTERLINEA = 1.3
PAD = 6            # relleno interno de los recuadros
MARGEN_X = 51      # margen izquierdo del texto en la plantilla
MARGEN_DERECHO = 46  # el texto de la plantilla llega hasta x ≈ 564 en carta (612)
ZONA_PIE = 70      # alto del pie de página que se excluye al buscar el fin del contenido


# ---------------------------------------------------------------- utilidades de texto
def envolver(texto, ancho, fuente=FUENTE, tam=TAM):
    lineas = []
    for parrafo in texto.split("\n"):
        actual = ""
        for palabra in parrafo.split():
            prueba = (actual + " " + palabra).strip()
            if fuente.text_length(prueba, fontsize=tam) <= ancho:
                actual = prueba
            else:
                if actual:
                    lineas.append(actual)
                actual = palabra
        lineas.append(actual)
    return lineas


def escribir(page, x, y, texto, tam=TAM, color=(0, 0, 0), negrita=False):
    """Escribe una línea con la línea base en y."""
    nombre = "fb" if negrita else "fr"
    ruta = RUTA_FB if negrita else RUTA_F
    if ruta:
        page.insert_font(fontname=nombre, fontfile=ruta)
    else:
        nombre = "hebo" if negrita else "helv"
    page.insert_text((x, y), texto, fontname=nombre, fontsize=tam, color=color)


# ---------------------------------------------------------------- bloques insertados
class Bloque:
    """Recuadro de texto insertado entre porciones del PDF original."""

    def __init__(self, titulo, texto, ancho, fondo, color, borde):
        self.titulo, self.texto = titulo, texto
        self.ancho, self.fondo, self.color, self.borde = ancho, fondo, color, borde
        interior = ancho - 2 * PAD
        self.lineas_titulo = envolver(titulo, interior, FUENTE_B, TAM + 0.5) if titulo else []
        self.lineas = envolver(texto, interior) if texto else []
        n = len(self.lineas_titulo) + len(self.lineas)
        self.alto = 2 * PAD + n * TAM * INTERLINEA + 8  # +8: separación con el contenido

    def dibujar(self, page, x, y, s):
        """Dibuja en la página destino; (x, y) esquina sup. izq. ya transformada; s = escala."""
        alto = (self.alto - 8) * s
        r = pymupdf.Rect(x, y + 4 * s, x + self.ancho * s, y + 4 * s + alto)
        page.draw_rect(r, color=self.borde, fill=self.fondo, width=0.8)
        ty = r.y0 + PAD * s + TAM * s
        for ln in self.lineas_titulo:
            escribir(page, r.x0 + PAD * s, ty, ln, TAM * s + 0.5 * s, self.color, negrita=True)
            ty += TAM * INTERLINEA * s
        for ln in self.lineas:
            escribir(page, r.x0 + PAD * s, ty, ln, TAM * s, self.color)
            ty += TAM * INTERLINEA * s


# ---------------------------------------------------------------- localizar ítems
def localizar_items(doc):
    """Devuelve {item: (pagina, bbox_linea)} buscando líneas que comienzan con el número del ítem."""
    pos = {}
    for pno, page in enumerate(doc):
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                t = "".join(s["text"] for s in l["spans"]).strip()
                m = re.match(r"^(1\.\d(?:\.\d)?)(?![\d.]*\d)", t)
                if m and m.group(1) in ORDEN and m.group(1) not in pos:
                    pos[m.group(1)] = (pno, pymupdf.Rect(l["bbox"]))
    return pos


def fondo_contenido(page):
    """Coordenada y del final del contenido de la página, sin contar el pie de página."""
    limite = page.rect.height - ZONA_PIE
    ys = [b[3] for b in page.get_text("blocks") if b[1] < limite]
    ys += [d["rect"].y1 for d in page.get_drawings()
           if d["rect"].y0 < limite and d["rect"].height < page.rect.height * 0.95]
    for img in page.get_image_info():
        if img["bbox"][1] < limite:
            ys.append(img["bbox"][3])
    ys = [min(y, limite) for y in ys]
    return max(ys) if ys else page.rect.height - 72


# ---------------------------------------------------------------- armado
def construir(origen, corr, salida):
    src = pymupdf.open(origen)
    W, H = src[0].rect.width, src[0].rect.height
    ancho_bloque = W - 2 * MARGEN_X
    pos = localizar_items(src)
    items = corr["items"]
    no_ubicados = [k for k in items if k not in pos]

    # cortes: (pagina, y) -> bloque a insertar en ese punto
    cortes = {}
    presentes = [k for k in ORDEN if k in pos]
    for i, k in enumerate(presentes):
        if k not in items:
            continue
        it = items[k]
        if it["puntaje"] >= it["max"] or not it.get("comentario"):
            continue
        siguiente = presentes[i + 1] if i + 1 < len(presentes) else None
        if siguiente:
            pno, r = pos[siguiente]
            y = r.y0 - 3
        else:
            pno = len(src) - 1
            y = fondo_contenido(src[pno]) + 4
        desc = it["max"] - it["puntaje"]
        b = Bloque(f"Ítem {k}: {fmt(it['puntaje'])}/{fmt(it['max'])} pts (−{fmt(desc)})",
                   it["comentario"], ancho_bloque, FONDO_COMENTARIO, ROJO, ROJO)
        cortes.setdefault(pno, []).append((y, b))

    encabezado = Bloque(
        f"CORRECCIÓN Taller 3: puntaje {fmt(corr['total'])}/{fmt(corr.get('maximo', 100))}"
        f"   ·   Nota {corr['nota']}",
        corr.get("grupo", ""), ancho_bloque, FONDO_ENCABEZADO, AZUL, AZUL)

    out = pymupdf.open()
    for pno in range(len(src)):
        # secuencia de elementos de la página: ("pdf", y0, y1) o ("bloque", Bloque)
        elems = []
        y_prev = 0
        if pno == 0:
            elems.append(("bloque", encabezado))
        for y, b in sorted(cortes.get(pno, []), key=lambda t: t[0]):
            elems.append(("pdf", y_prev, y))
            elems.append(("bloque", b))
            y_prev = y
        elems.append(("pdf", y_prev, H))
        for grupo in paginar(elems, H):
            dibujar_pagina(out, src, pno, grupo, W, H, items, pos)

    resumen(out, corr, W, H, no_ubicados)
    out.save(salida, garbage=3, deflate=True)
    return no_ubicados


def alto(e):
    return e[2] - e[1] if e[0] == "pdf" else e[1].alto


def paginar(elems, H, escala_min=0.82):
    """Agrupa elementos en páginas; acepta reducir hasta escala_min antes de pasar a otra página."""
    paginas, actual, total = [], [], 0
    for e in elems:
        h = alto(e)
        if actual and total + h > H / escala_min:
            paginas.append(actual)
            actual, total = [], 0
            if e[0] == "pdf":  # margen superior para la continuación
                actual.append(("espacio", 36))
                total += 36
        actual.append(e)
        total += h
    if actual:
        paginas.append(actual)
    return paginas


def dibujar_pagina(out, src, pno, elems, W, H, items, pos):
    tot = sum(e[1] if e[0] == "espacio" else alto(e) for e in elems)
    s = min(1.0, H / tot)
    x0 = (W - W * s) / 2
    page = out.new_page(width=W, height=H)
    y = 0.0
    for e in elems:
        if e[0] == "espacio":
            y += e[1]
            continue
        if e[0] == "bloque":
            e[1].dibujar(page, x0 + MARGEN_X * s, y * s, s)
            y += e[1].alto
            continue
        _, y0, y1 = e
        if y1 - y0 < 1:
            continue
        clip = pymupdf.Rect(0, y0, W, y1)
        destino = pymupdf.Rect(x0, y * s, x0 + W * s, (y + y1 - y0) * s)
        page.show_pdf_page(destino, src, pno, clip=clip)
        # puntaje junto a los encabezados de ítem que caen en esta porción
        for k, (p, r) in pos.items():
            if p == pno and k in items and y0 <= r.y0 < y1:
                it = items[k]
                ok = it["puntaje"] >= it["max"]
                yy = (y + r.y0 - y0) * s
                etiqueta = f"{fmt(it['puntaje'])}/{fmt(it['max'])}"
                tam = 9
                ancho_et = FUENTE_B.text_length(etiqueta, fontsize=tam) + 8
                # siempre en el margen derecho, a la altura del encabezado del ítem
                # (la línea del encabezado puede continuar tras una ecuación, así que no se usa r.x1)
                xr = min(x0 + (W - MARGEN_DERECHO) * s, W - ancho_et - 3)
                caja = pymupdf.Rect(xr, yy - 2, xr + ancho_et, yy + tam + 4)
                color = VERDE if ok else ROJO
                page.draw_rect(caja, color=color, fill=(1, 1, 1), width=1.0)
                escribir(page, caja.x0 + 4, caja.y1 - 4, etiqueta, tam, color, negrita=True)
        y += y1 - y0


def resumen(out, corr, W, H, no_ubicados):
    page = out.new_page(width=W, height=H)
    x, y = 60, 70
    escribir(page, x, y, "Resumen de la corrección: Taller 3, viga en voladizo", 14, AZUL, negrita=True)
    y += 22
    for ln in envolver(corr.get("grupo", ""), W - 2 * x, FUENTE, 10):
        escribir(page, x, y, ln, 10)
        y += 14
    y += 10
    col = [x, x + 70, x + 150]
    for c, t in zip(col, ["Ítem", "Puntaje", "Máximo"]):
        escribir(page, c, y, t, 10, AZUL, negrita=True)
    y += 6
    page.draw_line((x, y), (x + 230, y), color=AZUL, width=0.8)
    y += 14
    for k in ORDEN:
        if k not in corr["items"]:
            continue
        it = corr["items"][k]
        color = VERDE if it["puntaje"] >= it["max"] else ROJO
        escribir(page, col[0], y, k, 10)
        escribir(page, col[1], y, fmt(it["puntaje"]), 10, color, negrita=True)
        escribir(page, col[2], y, fmt(it["max"]), 10)
        y += 15
    page.draw_line((x, y - 9), (x + 230, y - 9), color=AZUL, width=0.8)
    y += 4
    escribir(page, col[0], y, "Total", 11, negrita=True)
    escribir(page, col[1], y, fmt(corr["total"]), 11, AZUL, negrita=True)
    escribir(page, col[2], y, fmt(corr.get("maximo", 100)), 11, negrita=True)
    y += 20
    escribir(page, x, y, f"Nota: {corr['nota']}", 13, AZUL, negrita=True)
    y += 26
    if corr.get("comentario_general"):
        escribir(page, x, y, "Comentario general", 11, AZUL, negrita=True)
        y += 16
        for ln in envolver(corr["comentario_general"], W - 2 * x, FUENTE, 10):
            escribir(page, x, y, ln, 10)
            y += 13.5
    if no_ubicados:
        y += 10
        escribir(page, x, y, "Ítems no ubicados en el documento (comentario solo en este resumen):", 10, ROJO, True)
        y += 14
        for k in no_ubicados:
            it = corr["items"][k]
            for ln in envolver(f"{k} ({fmt(it['puntaje'])}/{fmt(it['max'])}): {it.get('comentario', '')}",
                               W - 2 * x, FUENTE, 10):
                escribir(page, x, y, ln, 10, ROJO)
                y += 13.5


def fmt(v):
    return (f"{v:g}").replace(".", ",")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("correccion", help="JSON con puntajes y comentarios")
    ap.add_argument("-o", "--salida")
    a = ap.parse_args()
    corr = json.load(open(a.correccion, encoding="utf-8"))
    suma = sum(it["puntaje"] for it in corr["items"].values())
    if abs(suma - corr["total"]) > 1e-9:
        print(f"Aviso: la suma de los ítems ({suma}) no coincide con el total ({corr['total']})", file=sys.stderr)
    salida = a.salida or os.path.splitext(a.pdf)[0] + "_CORREGIDO.pdf"
    no = construir(a.pdf, corr, salida)
    print("Generado:", salida)
    if no:
        print("Ítems no ubicados (van en el resumen):", ", ".join(no))


if __name__ == "__main__":
    main()
