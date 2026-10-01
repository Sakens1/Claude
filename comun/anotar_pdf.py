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
    python3 comun/anotar_pdf.py taller_grupo.pdf correccion.json --items <taller>/herramientas/items.json \
        -o taller_grupo_CORREGIDO.pdf

items.json define, en orden, cómo se reconoce el enunciado de cada ítem en el PDF:
[
  {"id": "1.1", "patron": "^1\\.1(?![\\d.]*\\d)"},
  {"id": "1.7", "patron": "^1\\.7 ", "puntua": false},   <- encabezado sin puntaje que cierra el ítem anterior
  ...
]
"patron" es una expresión regular que se busca en cada línea de texto del PDF. Cada ítem se busca
después del anterior, en orden de lectura. Los "id" deben coincidir con las claves de "items" del JSON
de corrección.

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
def localizar_items(doc, spec):
    """{id: (pagina, bbox de la línea del enunciado)}. Busca cada ítem de spec en orden de lectura,
    a partir de la posición del ítem anterior encontrado."""
    lineas = []
    for pno, page in enumerate(doc):
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                t = " ".join("".join(s["text"] for s in l["spans"]).split())
                if t:
                    r = pymupdf.Rect(l["bbox"])
                    lineas.append((pno, round(r.y0, 1), r.x0, t, r))
    lineas.sort(key=lambda z: (z[0], z[1], z[2]))
    pos, desde = {}, 0
    for item in spec:
        patron = re.compile(item["patron"], re.IGNORECASE)
        for i in range(desde, len(lineas)):
            if patron.search(lineas[i][3]):
                pos[item["id"]] = (lineas[i][0], lineas[i][4])
                desde = i + 1
                break
    return pos


def zona_texto(doc, pos=None):
    """Límites horizontales del texto (x0, x1). Usa el margen izquierdo de los enunciados de ítem
    (márgenes simétricos, como en Word); si no hay, los bloques anchos del documento."""
    W = doc[0].rect.width
    if pos:
        x0s = sorted(r.x0 for _, r in pos.values())
        x0 = x0s[len(x0s) // 2]
        if 25 <= x0 <= W * 0.3:
            return x0, W - x0
    x0s, x1s = [], []
    for page in doc:
        for b in page.get_text("blocks"):
            if b[2] - b[0] > page.rect.width * 0.5:
                x0s.append(b[0])
                x1s.append(b[2])
    if not x0s:
        return 50, W - 50
    x0s.sort()
    x1s.sort()
    return x0s[len(x0s) // 10], x1s[-max(1, len(x1s) // 10)]


class MapaBlancos:
    """Píxeles ocupados de una página, para buscar rectángulos en blanco donde escribir."""

    TOLERANCIA = 1  # píxeles oscuros admitidos por fila (ruido); los bordes de recuadros NO se cruzan

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
        # líneas verticales (bordes de recuadros, tablas y gráficos) y gráficos vectoriales
        self.verticales = []
        dibujos = page.get_drawings()
        rects = []
        for dib in dibujos:
            for it in dib["items"]:
                if it[0] == "l":
                    p1, p2 = it[1], it[2]
                    if abs(p1.x - p2.x) < 1.5 and abs(p1.y - p2.y) >= 12:
                        self.verticales.append(((p1.x + p2.x) / 2, min(p1.y, p2.y), max(p1.y, p2.y)))
                elif it[0] == "re":
                    r = it[1]
                    if 12 <= r.height < page.rect.height * 0.9:
                        if r.width <= 2.5:
                            self.verticales.append(((r.x0 + r.x1) / 2, r.y0, r.y1))
                        else:
                            self.verticales += [(r.x0, r.y0, r.y1), (r.x1, r.y0, r.y1)]
                    if r.width > 80 and r.height > 50 and r.width * r.height < 0.4 * page.rect.width * page.rect.height:
                        rects.append(r)  # (los rectángulos casi de página completa son fondos, no gráficos)
        # gráficos vectoriales (p. ej. de Excel): si un rectángulo contiene muchos trazos, se ocupa la
        # zona que abarcan esos trazos (no el recuadro completo, que puede tener espacio libre para escribir)
        for r in rects:
            dentro = [d["rect"] for d in dibujos
                      if r.contains(d["rect"]) and d["rect"].get_area() < 0.9 * r.get_area()]
            if len(dentro) >= 15:
                u = pymupdf.Rect(dentro[0])
                for q in dentro[1:]:
                    u |= q
                self.ocupar(u.x0 - 3, u.y0 - 3, u.x1 + 3, u.y1 + 3)

    def buscar(self, y0, y1, x0, x1, alto):
        """Primera y (en puntos) en [y0, y1 - alto] con el rectángulo x0..x1 × alto en blanco."""
        c0, c1 = max(0, int(x0 * self.z)), min(self.oscuro.shape[1], int(np.ceil(x1 * self.z)))
        f0, f1 = max(0, int(y0 * self.z)), min(self.oscuro.shape[0], int(y1 * self.z))
        necesita = int(np.ceil(alto * self.z))
        if f1 - f0 < necesita or c1 <= c0:
            return None
        blanca = self.oscuro[f0:f1, c0:c1].sum(axis=1) <= self.TOLERANCIA
        corrida = 0
        for i, v in enumerate(blanca):
            corrida = corrida + 1 if v else 0
            if corrida >= necesita:
                return (f0 + i - necesita + 1) / self.z
        return None

    def ocupar(self, x0, y0, x1, y1):
        self.oscuro[max(0, int(y0 * self.z)):int(np.ceil(y1 * self.z)),
                    max(0, int(x0 * self.z)):int(np.ceil(x1 * self.z))] = True

    def intervalos(self, a, b, tx0, tx1):
        """Franjas horizontales delimitadas por líneas verticales que cruzan [a, b] (p. ej. el interior
        de un recuadro), además de la zona de texto completa."""
        xs = sorted({tx0, tx1} | {x for x, v0, v1 in self.verticales
                                  if v1 > a and v0 < b and tx0 - 15 < x < tx1 + 15})
        res = [(tx0, tx1)]
        for L, R in zip(xs, xs[1:]):
            if R - L >= 110 and (L, R) != (tx0, tx1):
                res.append((L, R))
        return sorted(set(res), key=lambda iv: -(iv[1] - iv[0]))


ANCHOS = [1.0, 0.75, 0.6, 0.5, 0.46, 0.42, 0.38]  # fracciones del ancho disponible que se prueban
MARGEN_INTERNO = 5                    # separación con bordes de recuadros


def buscar_lugar(texto, tramos, mapa, tx0, tx1, pendientes):
    """Ubica el comentario en el primer espacio en blanco del ítem (en orden de lectura), sin cruzar
    texto, imágenes, gráficos ni bordes de recuadros. Prefiere el ancho completo de la franja disponible
    (aunque con letra menor) y prueba posiciones a la izquierda, a la derecha e intermedias."""
    for f in ANCHOS:
        for tam in TAMANOS:
            for p, a, b in tramos:
                mejor = None
                for L, R in mapa(p).intervalos(a, b, tx0, tx1):
                    disp = (R - MARGEN_INTERNO) - (L + MARGEN_INTERNO)
                    w = disp * f
                    if w < 80:
                        continue
                    lineas = envolver(texto, w - 2, FUENTE, tam)
                    alto = len(lineas) * tam * INTERLINEA + 1.5
                    for k in range(7):
                        x = L + MARGEN_INTERNO + k * (disp - w) / 6
                        y = mapa(p).buscar(a, b, x - 2, x + w + 2, alto + 3)
                        if y is not None and (mejor is None or y < mejor[1] - 0.5):
                            mejor = (x, y, w, lineas, alto)
                if mejor:
                    x, y, w, lineas, alto = mejor
                    y += 1.5
                    pendientes.append((p, x, y, lineas, tam))
                    mapa(p).ocupar(x - 2, y - 2, x + w + 2, y + alto + 2)
                    return True
    return False


def limites_pagina(page):
    """(y_superior, y_inferior) utilizables: bajo la línea horizontal del encabezado y sobre la del pie,
    si existen; si no, los márgenes por defecto."""
    H, W = page.rect.height, page.rect.width
    arriba, abajo = ZONA_ENCABEZADO, H - ZONA_PIE
    for dib in page.get_drawings():
        r = dib["rect"]
        if r.height <= 3 and r.width >= W * 0.5:
            # solo en las franjas de encabezado y pie; más adentro son bordes de recuadros
            if r.y1 < 115:
                arriba = max(arriba, r.y1 + 3)
            elif r.y0 > H - 85:
                abajo = min(abajo, r.y0 - 3)
    return arriba, abajo


# ---------------------------------------------------------------- corrección
def anotar(origen, corr, salida, spec):
    doc = pymupdf.open(origen)
    pos = localizar_items(doc, spec)
    tx0, tx1 = zona_texto(doc, pos)
    mapas = {}

    def mapa(p):
        if p not in mapas:
            mapas[p] = MapaBlancos(doc[p])
        return mapas[p]

    items = corr["items"]
    presentes = [it["id"] for it in spec if it["id"] in pos]
    avisos = []
    faltan = [k for k in items if k not in pos]

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
            arriba, abajo = limites_pagina(doc[p])
            desde = r_ini.y1 + 1 if p == p_ini else arriba
            hasta = min(y_fin, abajo) if p == p_fin else abajo
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
        alto_c = tam + 6
        m = mapa(p)
        x = y0c = None
        # 1) a la altura del enunciado; 2) justo encima; 3) justo debajo. Lo más a la derecha posible,
        #    sin tapar nada (bordes, gráficos, texto).
        for ya in (r.y0 - 2, r.y0 - alto_c - 1, r.y1 + 1):
            xx = W - ancho - 3
            limite = r.x1 + 2 if ya == r.y0 - 2 else tx0
            while xx >= limite:
                if m.buscar(ya - 1, ya + alto_c + 1, xx - 1, xx + ancho + 1, alto_c + 1) is not None:
                    x, y0c = xx, ya
                    break
                xx -= 2
            if x is not None:
                break
        if x is None:  # sin espacio libre cerca: margen derecho, a la altura del enunciado
            x, y0c = min(tx1 + 4, W - ancho - 3), r.y0 - 2
        y1c = y0c + alto_c
        m.ocupar(x - 1, y0c - 1, x + ancho + 1, y1c + 1)
        caja = pymupdf.Rect(x, y0c, x + ancho, y1c)
        color = VERDE if it["puntaje"] >= it["max"] else ROJO
        page.draw_rect(caja, color=color, fill=(1, 1, 1), width=1.0)
        escribir(page, caja.x0 + 4, caja.y1 - 4, etiqueta, tam, color, negrita=True)

    # 3) total y nota en el margen superior de la primera página
    page = doc[0]
    txt = (f"Puntaje total: {fmt(corr['total'])}/{fmt(corr.get('maximo', 100))}"
           f"     Nota: {corr['nota']}")
    escribir(page, tx0, 24, txt, 11, ROJO, negrita=True)

    doc.save(salida, garbage=3, deflate=True)
    return avisos, faltan


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("correccion", help="JSON con puntajes y comentarios")
    ap.add_argument("--items", required=True, help="JSON con el orden y patrón de los encabezados de ítem")
    ap.add_argument("-o", "--salida")
    a = ap.parse_args(argv)
    spec = json.load(open(a.items, encoding="utf-8"))
    corr = json.load(open(a.correccion, encoding="utf-8"))
    suma = sum(it["puntaje"] for it in corr["items"].values())
    if abs(suma - corr["total"]) > 1e-9:
        print(f"Aviso: la suma de los ítems ({suma}) no coincide con el total ({corr['total']})", file=sys.stderr)
    salida = a.salida or os.path.splitext(a.pdf)[0] + "_CORREGIDO.pdf"
    avisos, faltan = anotar(a.pdf, corr, salida, spec)
    print("Generado:", salida)
    if faltan:
        print("NO se encontró en el PDF el enunciado de:", ", ".join(faltan),
              "(su puntaje y comentario no se escribieron; revise los patrones de items.json)")
    if avisos:
        print("Sin espacio en blanco suficiente; comentario agregado como nota emergente en:", ", ".join(avisos))


if __name__ == "__main__":
    main()
