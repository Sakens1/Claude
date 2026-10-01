#!/usr/bin/env python3
"""Genera el taller corregido: una copia EXACTA del PDF entregado por el grupo (mismas páginas,
mismo tamaño y misma posición de todo el contenido), sobre la que se escribe:

- el puntaje de cada ítem en el margen derecho, a la altura de su enunciado
  (verde si tiene puntaje completo, rojo si tiene descuento);
- si hubo descuento, un comentario en rojo dentro del mismo ítem, ubicado en un espacio en
  blanco entre su enunciado y el ítem siguiente (nunca sobre lo escrito por los estudiantes);
- el puntaje total y la nota en el margen superior de la primera página.

No se agregan ni se mueven páginas. Si un comentario no cabe en ningún espacio en blanco del ítem,
se agrega como nota emergente (ícono de comentario) junto al puntaje, y se avisa por consola.

Uso:
    python3 anotar_pdf.py taller_grupo.pdf correccion.json -o taller_grupo_CORREGIDO.pdf

Formato de correccion.json:
{
  "grupo": "Nombre Apellido, ...",
  "total": 85, "maximo": 100, "nota": "5,9",
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

import numpy as np
import pymupdf

# Orden de los encabezados del taller; "1.7" no tiene puntaje pero delimita el fin de 1.6.
ORDEN = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.5.1", "1.5.2", "1.6", "1.7", "1.7.1", "1.7.2", "1.8"]

ROJO = (0.80, 0.0, 0.0)
VERDE = (0.0, 0.50, 0.15)
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

TAMANOS = [9.0, 8.5, 8.0, 7.5, 7.0]  # se prueba del más grande al más chico
INTERLINEA = 1.25
ZONA_ENCABEZADO = 72   # alto del encabezado de página (logo) que no se usa
ZONA_PIE = 62          # alto del pie de página que no se usa
DPI_ANALISIS = 2.0     # zoom para detectar espacios en blanco


# ---------------------------------------------------------------- texto
def envolver(texto, ancho, fuente, tam):
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


def escribir(page, x, y, texto, tam, color, negrita=False):
    """Escribe una línea con la línea base en y."""
    ruta = RUTA_FB if negrita else RUTA_F
    nombre = ("fb" if negrita else "fr") if ruta else ("hebo" if negrita else "helv")
    if ruta:
        page.insert_font(fontname=nombre, fontfile=ruta)
    page.insert_text((x, y), texto, fontname=nombre, fontsize=tam, color=color)


def fmt(v):
    return f"{v:g}".replace(".", ",")


# ---------------------------------------------------------------- análisis de la página
def localizar_items(doc):
    """{item: (pagina, bbox de la línea del enunciado)}."""
    pos = {}
    for pno, page in enumerate(doc):
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                t = "".join(s["text"] for s in l["spans"]).strip()
                m = re.match(r"^(1\.\d(?:\.\d)?)(?![\d.]*\d)", t)
                if m and m.group(1) in ORDEN and m.group(1) not in pos:
                    pos[m.group(1)] = (pno, pymupdf.Rect(l["bbox"]))
    return pos


def zona_texto(doc):
    """Límites horizontales del texto (x0, x1) según los enunciados del documento."""
    x0s, x1s = [], []
    for page in doc:
        for b in page.get_text("blocks"):
            if b[2] - b[0] > page.rect.width * 0.5:
                x0s.append(b[0])
                x1s.append(b[2])
    if not x0s:
        return 50, doc[0].rect.width - 50
    x0s.sort()
    x1s.sort()
    return x0s[len(x0s) // 10], x1s[-max(1, len(x1s) // 10)]


class MapaBlancos:
    """Píxeles ocupados de una página, para buscar rectángulos en blanco donde escribir."""

    TOLERANCIA = 6  # píxeles oscuros admitidos por fila (bordes verticales de los recuadros)

    def __init__(self, page):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(DPI_ANALISIS, DPI_ANALISIS),
                              colorspace=pymupdf.csGRAY, alpha=False)
        self.z = DPI_ANALISIS
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        self.oscuro = img < 235
        # las imágenes (gráficos, fotos) cuentan como ocupadas aunque tengan zonas blancas
        for info in page.get_image_info():
            x0, y0, x1, y1 = info["bbox"]
            self.ocupar(x0 - 2, y0 - 2, x1 + 2, y1 + 2)

    def buscar(self, y0, y1, x0, x1, alto):
        """Primera y (en puntos) en [y0, y1 - alto] con el rectángulo x0..x1 × alto en blanco."""
        c0, c1 = int(x0 * self.z), int(x1 * self.z)
        f0, f1 = max(0, int(y0 * self.z)), min(self.oscuro.shape[0], int(y1 * self.z))
        necesita = int(np.ceil(alto * self.z))
        if f1 - f0 < necesita:
            return None
        blanca = self.oscuro[f0:f1, c0:c1].sum(axis=1) <= self.TOLERANCIA
        corrida = 0
        for i, v in enumerate(blanca):
            corrida = corrida + 1 if v else 0
            if corrida >= necesita:
                return (f0 + i - necesita + 1) / self.z
        return None

    def ocupar(self, x0, y0, x1, y1):
        self.oscuro[int(y0 * self.z):int(np.ceil(y1 * self.z)), int(x0 * self.z):int(np.ceil(x1 * self.z))] = True


ANCHOS = [1.0, 0.75, 0.6, 0.5, 0.42]  # fracciones del ancho de texto que se prueban


def buscar_lugar(texto, tramos, mapa, tx0, tx1, pendientes):
    """Ubica el comentario en el primer espacio en blanco del ítem (en orden de lectura).
    Prefiere letra más grande y luego mayor ancho; prueba rectángulos alineados a la izquierda,
    a la derecha y en posiciones intermedias (p. ej. al lado de una tabla o figura)."""
    ancho_total = (tx1 - 6) - (tx0 + 6)
    for f in ANCHOS:            # primero el ancho completo (bajo lo escrito), aunque con letra menor
        for tam in TAMANOS:
            w = ancho_total * f
            lineas = envolver(texto, w - 2, FUENTE, tam)
            alto = len(lineas) * tam * INTERLINEA + 3
            xs = sorted({tx0 + 6 + k * (ancho_total - w) / 6 for k in range(7)})
            for p, a, b in tramos:
                mejor = None
                for x in xs:
                    y = mapa(p).buscar(a, b, x - 2, x + w + 2, alto + 4)
                    if y is not None and (mejor is None or y < mejor[1] - 0.5):
                        mejor = (x, y)
                if mejor:
                    x, y = mejor
                    y += 2
                    pendientes.append((p, x, y, lineas, tam))
                    mapa(p).ocupar(x - 2, y - 2, x + w + 2, y + alto + 2)
                    return True
    return False


# ---------------------------------------------------------------- corrección
def anotar(origen, corr, salida):
    doc = pymupdf.open(origen)
    pos = localizar_items(doc)
    tx0, tx1 = zona_texto(doc)
    mapas = {}

    def mapa(p):
        if p not in mapas:
            mapas[p] = MapaBlancos(doc[p])
        return mapas[p]

    items = corr["items"]
    presentes = [k for k in ORDEN if k in pos]
    avisos = []

    # 1) comentarios (se calculan sobre la página original, antes de dibujar nada)
    pendientes = []
    for i, k in enumerate(presentes):
        it = items.get(k)
        if not it or it["puntaje"] >= it["max"] or not it.get("comentario"):
            continue
        p_ini, r_ini = pos[k]
        sig = presentes[i + 1] if i + 1 < len(presentes) else None
        if sig:
            p_fin, y_fin = pos[sig][0], pos[sig][1].y0 - 1
        else:
            p_fin, y_fin = len(doc) - 1, doc[-1].rect.height - ZONA_PIE
        # tramos del ítem: (pagina, y_desde, y_hasta)
        tramos = []
        for p in range(p_ini, p_fin + 1):
            H = doc[p].rect.height
            desde = r_ini.y1 + 1 if p == p_ini else ZONA_ENCABEZADO
            hasta = y_fin if p == p_fin else H - ZONA_PIE
            if hasta > desde:
                tramos.append((p, desde, hasta))
        titulo = f"({fmt(it['puntaje'])}/{fmt(it['max'])}) "
        texto = titulo + it["comentario"]
        colocado = buscar_lugar(texto, tramos, mapa, tx0, tx1, pendientes)
        if not colocado:
            avisos.append(k)
            p, r = pos[k]
            nota = doc[p].add_text_annot(pymupdf.Point(doc[p].rect.width - 18, r.y0), texto, icon="Comment")
            nota.set_colors(stroke=ROJO)
            nota.set_info(title="Corrección")
            nota.update()

    for p, x, y, lineas, tam in pendientes:
        page = doc[p]
        yy = y + tam
        for ln in lineas:
            escribir(page, x, yy, ln, tam, ROJO)
            yy += tam * INTERLINEA

    # 2) puntaje junto a cada enunciado, en el margen derecho
    for k in presentes:
        if k not in items:
            continue
        it = items[k]
        p, r = pos[k]
        page = doc[p]
        W = page.rect.width
        etiqueta = f"{fmt(it['puntaje'])}/{fmt(it['max'])}"
        tam = 9
        ancho = FUENTE_B.text_length(etiqueta, fontsize=tam) + 8
        x = min(tx1 + 4, W - ancho - 3)
        caja = pymupdf.Rect(x, r.y0 - 2, x + ancho, r.y0 + tam + 4)
        color = VERDE if it["puntaje"] >= it["max"] else ROJO
        page.draw_rect(caja, color=color, fill=(1, 1, 1), width=1.0)
        escribir(page, caja.x0 + 4, caja.y1 - 4, etiqueta, tam, color, negrita=True)

    # 3) total y nota en el margen superior de la primera página
    page = doc[0]
    txt = (f"Puntaje total: {fmt(corr['total'])}/{fmt(corr.get('maximo', 100))}"
           f"     Nota: {corr['nota']}")
    escribir(page, tx0, 24, txt, 11, ROJO, negrita=True)

    doc.save(salida, garbage=3, deflate=True)
    return avisos


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
    avisos = anotar(a.pdf, corr, salida)
    print("Generado:", salida)
    if avisos:
        print("Sin espacio en blanco suficiente; comentario agregado como nota emergente en:", ", ".join(avisos))


if __name__ == "__main__":
    main()
