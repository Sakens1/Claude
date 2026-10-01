#!/usr/bin/env python3
"""Genera la solución modelo del Taller 3 (viga en voladizo) sobre la plantilla original.

- Lee  ../fuentes/Taller3_Viga_Voladiza_IN1090C_enunciado.docx
- Crea ../solucion/grafico_yF_vs_F.png
- Crea ../solucion/Taller3_Viga_Voladiza_RESUELTO.docx

Los datos experimentales son ILUSTRATIVOS (representativos de una regla de acero),
pensados para que la pauta muestre el procedimiento completo con números concretos.

Requiere: python-docx, matplotlib.
"""
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, Cm
from docx.table import Table
from docx.text.paragraph import Paragraph

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import verificar_calculos as vc  # noqa: E402

RAIZ = os.path.dirname(AQUI)
ENUNCIADO = os.path.join(RAIZ, "fuentes", "Taller3_Viga_Voladiza_IN1090C_enunciado.docx")
SALIDA_DOCX = os.path.join(RAIZ, "solucion", "Taller3_Viga_Voladiza_RESUELTO.docx")
SALIDA_PNG = os.path.join(RAIZ, "solucion", "grafico_yF_vs_F.png")

# ---------------------------------------------------------------- datos ilustrativos
B_MM, H_MM, L_MM = 25.0, 0.80, 250.0          # ancho, espesor, longitud libre
MASAS_G = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
FLECHAS_MM = [2.5, 5.0, 7.5, 10.0, 12.0, 15.0, 17.5, 20.0, 22.5, 24.5]
G = 9.80


def coma(x, dec):
    return f"{x:.{dec}f}".replace(".", ",")


def cient(x, dec=2):
    """1.0667e-12 -> '1,07×10^{-12}' (con marcado para superíndice)."""
    m, e = f"{x:.{dec}e}".split("e")
    return f"{m.replace('.', ',')}×10^{{{int(e)}}}"


def calcular():
    args = vc.argparse.Namespace(
        b=B_MM, h=H_MM, L=L_MM, dimensiones_en_mm=True,
        masas=MASAS_G, masas_en_g=True, flechas=FLECHAS_MM, flechas_en_mm=True,
        g=G, material="acero", Y_teorico=None,
        res_L=1e-3, res_h=1e-5, res_b=2e-5,
        informado_I=None, informado_pendiente=None, informado_Y=None, informado_error=None)
    return vc.analizar(args)


# ---------------------------------------------------------------- gráfico
def graficar(r):
    F = r["entradas_SI"]["fuerzas_N"]
    y = r["entradas_SI"]["flechas_m"]
    m = r["ajuste"]["pendiente_m_por_N"]
    n = r["ajuste"]["intercepto_m"]
    r2 = r["ajuste"]["R2"]
    fig, ax = plt.subplots(figsize=(7.0, 4.4), dpi=200)
    ax.scatter(F, y, color="#1f4e79", zorder=3, label="Datos experimentales (Tabla 2)")
    xs = [0, max(F) * 1.05]
    ax.plot(xs, [m * v + n for v in xs], color="#c00000", lw=1.4,
            label="Línea de tendencia (mínimos cuadrados)")
    ax.set_xlabel("Fuerza aplicada  $F_i$  [N]")
    ax.set_ylabel("Flecha de flexión  $y_{iF}$  [m]")
    ax.set_title("Flecha de flexión vs fuerza aplicada (regla de acero, L = 0,250 m)")
    fmt = FuncFormatter(lambda v, _: f"{v:.3f}".rstrip("0").rstrip(".").replace(".", ",") if v else "0")
    ax.xaxis.set_major_formatter(fmt)
    ax.yaxis.set_major_formatter(fmt)
    ax.set_xlim(0, max(F) * 1.05)
    ax.set_ylim(0, max(y) * 1.12)
    ax.grid(True, ls=":", alpha=0.6)
    def mt(x, dec):  # coma decimal sin espacio extra en mathtext
        return coma(x, dec).replace(",", "{,}")
    eq = f"$y_F = {mt(m, 5)}\\;F + {mt(n, 5)}$\n$R^2 = {mt(r2, 4)}$"
    ax.text(0.04, 0.95, eq, transform=ax.transAxes, va="top", fontsize=11,
            bbox=dict(boxstyle="round", fc="white", ec="#888888"))
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    fig.savefig(SALIDA_PNG)
    plt.close(fig)


# ---------------------------------------------------------------- utilidades docx
TOKEN = re.compile(r"(\*\*.+?\*\*|_\{.+?\}|\^\{.+?\})")


def agregar_texto(p, texto, tam=10, negrita=False, color=None):
    """Agrega runs a p. Marcado: **negrita**, _{subíndice}, ^{superíndice}."""
    for parte in TOKEN.split(texto):
        if not parte:
            continue
        run_neg, sub, sup = negrita, False, False
        if parte.startswith("**"):
            agregar_texto(p, parte[2:-2], tam=tam, negrita=True, color=color)
            continue
        if parte.startswith("_{"):
            parte, sub = parte[2:-1], True
        elif parte.startswith("^{"):
            parte, sup = parte[2:-1], True
        run = p.add_run(parte)
        run.font.name = "Arial"
        run._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
        run._element.rPr.rFonts.set(qn("w:cs"), "Arial")
        run.font.size = Pt(tam)
        run.bold = run_neg
        run.font.subscript = sub
        run.font.superscript = sup
        if color:
            run.font.color.rgb = docx.shared.RGBColor.from_string(color)


def vaciar_celda(celda):
    for p in list(celda.paragraphs)[1:]:
        p._element.getparent().remove(p._element)
    p = celda.paragraphs[0]
    for child in list(p._element):
        if child.tag != qn("w:pPr"):
            p._element.remove(child)
    return p


def llenar_cuadro(celda, bloques):
    """bloques: lista de (tipo, contenido). tipo in {'p','b','eq','img','lista'}."""
    p = vaciar_celda(celda)
    primero = True
    for tipo, cont in bloques:
        if not primero:
            p = celda.add_paragraph()
        primero = False
        p.paragraph_format.space_after = Pt(4)
        if tipo == "p":
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            agregar_texto(p, cont)
        elif tipo == "b":
            agregar_texto(p, cont, negrita=True)
        elif tipo == "eq":
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            agregar_texto(p, cont, tam=11)
        elif tipo == "lista":
            p.paragraph_format.left_indent = Cm(0.6)
            p.paragraph_format.first_line_indent = Cm(-0.4)
            agregar_texto(p, "• " + cont)
        elif tipo == "img":
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(cont, width=Cm(15))


def celda_simple(celda, texto, centrado=True):
    p = vaciar_celda(celda)
    if centrado:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    agregar_texto(p, texto)


# ---------------------------------------------------------------- contenido
def respuestas(r):
    I = r["I_m4"]
    m = r["ajuste"]["pendiente_m_por_N"]
    n = r["ajuste"]["intercepto_m"]
    r2 = r["ajuste"]["R2"]
    Y = r["Y_experimental_Pa"]
    Yt = r["Y_teorico_Pa"]
    err = r["error_porcentual"]
    dY = r["incertidumbre_relativa_Y"]
    b, h, L = B_MM / 1000, H_MM / 1000, L_MM / 1000
    den = 3 * m * I
    razon_I = (b / h) ** 2

    R = {}
    R["1.1"] = [
        ("b", "Hipótesis"),
        ("p", "Si se aplica una fuerza vertical concentrada F en el extremo libre de la regla metálica "
              "empotrada, y se trabaja en el régimen elástico con pequeñas deformaciones (pendientes pequeñas), "
              "entonces la flecha de flexión y_{F} será directamente proporcional a la fuerza aplicada:"),
        ("eq", "y_{F} = c_{f}·F,   con   c_{f} = L^{3} / (3·Y·I)"),
        ("p", "Por lo tanto, el gráfico y_{F} vs F será una recta que pasa aproximadamente por el origen, "
              "cuya pendiente es la constante de flexibilidad c_{f}. Conocidos L e I = b·h^{3}/12, a partir de "
              "esa pendiente se podrá determinar el módulo de Young de la regla, que debería ser cercano al valor "
              "tabulado para el acero (Y ≈ 2,0×10^{11} Pa = 200 GPa)."),
    ]
    R["1.4"] = [
        ("p", "Datos de la Tabla 1: ancho b = 0,0250 m (pie de metro, ±0,02 mm), espesor h = 0,00080 m "
              "(micrómetro, ±0,01 mm) y longitud libre L = 0,250 m (huincha, ±1 mm, medida desde el borde del "
              "empotramiento hasta el punto donde cuelga la masa)."),
        ("p", "La carga actúa en la dirección del espesor h, por lo que la flexión ocurre en torno al eje neutro "
              "paralelo al ancho b. El momento de inercia de la sección rectangular respecto a ese eje es:"),
        ("eq", "I = (1/12)·b·h^{3}"),
        ("eq", f"I = (1/12)·(0,0250 m)·(0,00080 m)^{{3}} = (1/12)·(0,0250)·(5,12×10^{{-10}}) m^{{4}}"),
        ("eq", f"**I = {cient(I, 2)} m^{{4}}**"),
    ]
    R["1.5"] = [
        ("img", SALIDA_PNG),
        ("p", "Ecuación de la línea de tendencia (ajuste lineal por mínimos cuadrados, F en N e y_{F} en m):"),
        ("eq", f"**y_{{F}} = {coma(m, 5)}·F + {coma(n, 5)}      R^{{2}} = {coma(r2, 4)}**"),
    ]
    R["1.5.1"] = [
        ("p", "La línea de tendencia tiene la forma y_{F} = m·F + n, que se compara con el modelo teórico "
              "y_{F} = c_{f}·F:"),
        ("lista", f"**Pendiente m = {coma(m, 5)} m/N**: corresponde a la constante de flexibilidad "
                  "c_{f} = L^{3}/(3·Y·I). Indica cuántos metros desciende el extremo libre por cada newton aplicado. "
                  "Se asocia a la longitud L (geometría), al momento de inercia I (forma y tamaño de la sección: b y h) "
                  "y al módulo de Young Y (material). Su inverso, k = 3YI/L^{3} ≈ "
                  f"{coma(1/m, 1)} N/m, es la rigidez de la viga."),
        ("lista", f"**Intercepto n = {coma(n, 5)} m ≈ 0**: es la flecha cuando F = 0. Teóricamente es cero, "
                  "porque la referencia se tomó en el extremo libre sin carga. Su valor "
                  f"({coma(n*1000, 2)} mm) es menor que la resolución de la regla graduada (0,5 mm), por lo que se "
                  "atribuye a errores de lectura y no a un efecto físico."),
        ("lista", f"**R^{{2}} = {coma(r2, 4)}**: muy cercano a 1, confirma la relación lineal (comportamiento "
                  "elástico, ley de Hooke) entre la flecha y la fuerza."),
    ]
    R["1.5.2"] = [
        ("p", "Igualando la pendiente experimental con la constante de flexibilidad y despejando Y:"),
        ("eq", "m = c_{f} = L^{3}/(3·Y·I)   ⟹   Y = L^{3}/(3·m·I)"),
        ("eq", f"Y = (0,250 m)^{{3}} / (3 · {coma(m, 5)} m/N · {cient(I, 3)} m^{{4}})"),
        ("eq", f"Y = 1,5625×10^{{-2}} m^{{3}} / {cient(den, 3)} m^{{5}}/N"),
        ("eq", f"**Y_{{exp}} = {cient(Y, 2)} Pa ≈ {coma(Y/1e9, 0)} GPa**"),
        ("p", f"Estimación de incertidumbre (propagación): ΔY/Y = 3ΔL/L + 3Δh/h + Δb/b + Δm/m ≈ "
              f"{coma(100*dY, 1)} %, es decir Y_{{exp}} = ({coma(Y/1e9, 0)} ± {coma(Y*dY/1e9, 0)}) GPa. "
              "El término dominante es el del espesor (3Δh/h ≈ 3,8 %), porque h aparece al cubo."),
    ]
    R["1.6"] = [
        ("p", "Valor teórico: módulo de Young del acero Y_{teo} = 2,0×10^{11} Pa = 200 GPa (tablas de "
              "propiedades de materiales, p. ej. Serway & Jewett, Física para ciencias e ingeniería; "
              "rango típico 190 a 210 GPa)."),
        ("eq", "E% = |Y_{exp} − Y_{teo}| / Y_{teo} × 100"),
        ("eq", f"E% = |{coma(Y/1e9, 1)} − 200| / 200 × 100 = **{coma(err, 1)} %**"),
        ("p", "El valor experimental tiene el orden de magnitud correcto (10^{11} Pa), queda dentro del rango "
              "tabulado del acero y el valor teórico cae dentro del intervalo de incertidumbre experimental; "
              "se concluye que la regla es de acero y que el método es adecuado."),
        ("p", "Fuentes de error que explican la diferencia:"),
        ("lista", "Medición del espesor h: un error de 0,01 mm en h produce ≈ 3,8 % de error en Y (dependencia h^{3})."),
        ("lista", "Definición de L: debe medirse desde el borde de la mordaza hasta el punto de aplicación de la "
                  "carga; 1 mm de error produce 1,2 % en Y (dependencia L^{3})."),
        ("lista", "Empotramiento no perfectamente rígido: la mordaza permite un pequeño giro que aumenta la flecha "
                  "y hace subestimar Y, coherente con obtener un valor menor que el teórico."),
        ("lista", "Lectura de la flecha con error de paralaje y resolución de 0,5 mm; oscilación de la masa."),
        ("lista", "Masa del portapesas y la aproximación de pendientes pequeñas (flecha máxima ≈ 10 % de L)."),
    ]
    R["1.7.1"] = [
        ("p", "Las vigas pueden sufrir deformaciones por:"),
        ("lista", "**Flexión**: curvatura del eje de la viga por cargas perpendiculares a él (momento flector)."),
        ("lista", "**Corte o cizalle**: deslizamiento relativo entre secciones por el esfuerzo cortante."),
        ("lista", "**Axial (tracción o compresión)**: cuando las cargas tienen componente paralela al eje; en "
                  "compresión puede producirse pandeo."),
        ("lista", "**Torsión**: giro de las secciones cuando la carga no pasa por el eje de la viga."),
        ("p", "La más común es la **flexión** (acompañada de esfuerzo cortante), porque en la mayoría de los casos "
              "las cargas, como el peso, actúan perpendiculares al eje de la viga. Es la deformación estudiada en "
              "este taller."),
    ]
    R["1.7.2"] = [
        ("lista", "En posición horizontal las cargas gravitacionales actúan perpendiculares al eje, de modo que la "
                  "viga trabaja a flexión y transmite esas cargas a los apoyos o columnas."),
        ("lista", "Permiten salvar luces (distancia entre apoyos) y generar espacios libres: losas, techos, puentes, "
                  "y en voladizo, balcones, aleros, graderías, estanterías cantilever y puentes construidos por avance "
                  "en voladizo, sin apoyos intermedios."),
        ("lista", "Orientando la sección con su mayor dimensión en dirección vertical (en la dirección de la carga) "
                  "se maximiza I ∝ h^{3} y la rigidez sin agregar material. En la regla del taller, si se cargara "
                  f"de canto (b en dirección de la carga) I aumentaría en un factor (b/h)^{{2}} ≈ {coma(razon_I, 0)}: "
                  "por eso las vigas reales son altas y angostas (o con perfil I)."),
    ]
    R["1.8"] = [
        ("p", "Respecto al resultado de aprendizaje, se determinó experimentalmente el módulo de Young de una "
              f"regla metálica, obteniéndose Y_{{exp}} = {cient(Y, 2)} Pa ≈ {coma(Y/1e9, 0)} GPa, con un error "
              f"porcentual de {coma(err, 1)} % respecto al valor tabulado del acero (200 GPa). Esto permite "
              "identificar el material de la regla como acero."),
        ("p", "La hipótesis se confirma: la flecha de flexión aumenta linealmente con la fuerza aplicada "
              f"(R^{{2}} = {coma(r2, 4)}) y el intercepto es prácticamente nulo ({coma(n*1000, 2)} mm), tal "
              "como predice y_{F} = c_{f}·F. La pendiente de la recta corresponde a la constante de flexibilidad "
              f"c_{{f}} = L^{{3}}/(3YI) = {coma(m, 4)} m/N."),
        ("p", "Del análisis de datos se concluye que la medición más crítica es el espesor h, seguida de la "
              "longitud L, por su dependencia cúbica; la incertidumbre estimada (≈ 6 %) es mayor que el error "
              "obtenido, por lo que la diferencia es atribuible a errores experimentales (principalmente medición "
              "de h y el giro de la mordaza, que tiende a subestimar Y). Para mejorar el resultado se propone "
              "medir h con micrómetro en varios puntos y promediar, asegurar firmemente el empotramiento y medir "
              "la flecha con un comparador o evitando el paralaje."),
        ("p", "Finalmente, el modelo de viga en voladizo es válido dentro de sus supuestos (material homogéneo y "
              "elástico, sección uniforme, peso propio despreciable y pequeñas deformaciones), los cuales se "
              "cumplieron en el experimento al mantener la flecha máxima por debajo del 10 % de L."),
    ]
    return R


# ---------------------------------------------------------------- armado del documento
def main():
    r = calcular()
    graficar(r)
    d = docx.Document(ENUNCIADO)
    cuerpo = list(d.element.body.iterchildren())

    def tabla(i):
        el = cuerpo[i]
        assert el.tag == qn("w:tbl"), f"elemento {i} no es tabla"
        return Table(el, d)

    # Integrantes
    llenar_cuadro(tabla(3).cell(0, 0), [("b", "SOLUCIÓN MODELO / PAUTA DOCENTE")])
    llenar_cuadro(tabla(3).cell(0, 1), [("p", "Datos experimentales ilustrativos (regla de acero)")])

    # Tabla 1: dimensiones
    t1 = tabla(19)
    celda_simple(t1.cell(0, 1), "0,0250 m")
    celda_simple(t1.cell(1, 1), "0,00080 m")
    celda_simple(t1.cell(2, 1), "0,250 m")

    # Tabla 2 (dentro de un cuadro de texto: hay 2 copias, AlternateContent Choice y Fallback)
    F = r["entradas_SI"]["fuerzas_N"]
    for tel in cuerpo[32].iter(qn("w:tbl")):
        t2 = Table(tel, d)
        assert len(t2.rows) == 11
        for i in range(10):
            fila = t2.rows[i + 1]
            celda_simple(fila.cells[1], coma(MASAS_G[i] / 1000, 3))
            celda_simple(fila.cells[2], coma(F[i], 3))
            celda_simple(fila.cells[3], coma(FLECHAS_MM[i] / 1000, 4))

    # Cuadros de respuesta (tablas 1x1 bajo cada pregunta)
    R = respuestas(r)
    mapa = {15: ("1.1", "1.1"), 51: ("1.4", "1.4"), 54: ("1.5", "1.5 Construya"),
            57: ("1.5.1", "1.5.1"), 61: ("1.5.2", "1.5.2"), 64: ("1.6", "1.6"),
            68: ("1.7.1", "1.7.1"), 72: ("1.7.2", "1.7.2"), 76: ("1.8", "1.8")}
    for idx, (clave, texto) in mapa.items():
        cerca = "".join(t.text or "" for el in cuerpo[max(0, idx - 4):idx] for t in el.iter(qn("w:t")))
        assert texto in cerca, f"La tabla {idx} no sigue a la pregunta {clave}"
        llenar_cuadro(tabla(idx).cell(0, 0), R[clave])

    d.save(SALIDA_DOCX)
    print("Generado:", SALIDA_DOCX)
    print("Generado:", SALIDA_PNG)
    vc.imprimir(r)


if __name__ == "__main__":
    main()
