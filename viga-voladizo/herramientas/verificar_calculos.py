#!/usr/bin/env python3
"""Recalcula los resultados del Taller 3 (viga en voladizo) a partir de los datos
de un grupo, para comparar contra lo que el grupo informó.

Sin dependencias externas (solo biblioteca estándar).

Uso típico (datos en SI):
    python3 verificar_calculos.py --b 0.0250 --h 0.00080 --L 0.300 \
        --masas 0.010 0.020 0.030 --flechas 0.0040 0.0085 0.0125

Opciones útiles:
    --masas-en-g        las masas vienen en gramos
    --flechas-en-mm     las flechas vienen en milímetros
    --dimensiones-en-mm b, h y L vienen en milímetros
    --g 9.80            aceleración de gravedad (por defecto 9,80 m/s², la del taller)
    --material acero    valor teórico de referencia (ver TABLA_Y)
    --Y-teorico 2.0e11  valor teórico explícito en Pa (anula --material)
    --informado-I, --informado-pendiente, --informado-Y, --informado-error
                        valores que reporta el grupo; el script los compara
    --json              salida en JSON
"""
import argparse
import json
import math
import sys

# Módulos de Young de referencia (Pa). Rango típico de tablas de física/ingeniería.
TABLA_Y = {
    "acero": (2.0e11, (1.9e11, 2.1e11)),
    "acero_inoxidable": (1.93e11, (1.90e11, 2.00e11)),
    "aluminio": (7.0e10, (6.9e10, 7.2e10)),
    "laton": (1.0e11, (9.0e10, 1.1e11)),
    "cobre": (1.1e11, (1.1e11, 1.3e11)),
}

# Tolerancia relativa para considerar "coincidente" un valor informado con el recalculado.
# Cubre redondeos razonables y el uso de g = 9,8 o 9,81.
TOL_COINCIDE = 0.03


def regresion_lineal(x, y):
    """Mínimos cuadrados y = m x + n. Devuelve m, n, R², sigma_m, sigma_n."""
    k = len(x)
    if k < 2:
        raise ValueError("Se necesitan al menos 2 puntos para la regresión")
    sx, sy = sum(x), sum(y)
    sxx = sum(v * v for v in x)
    sxy = sum(a * b for a, b in zip(x, y))
    den = k * sxx - sx * sx
    if den == 0:
        raise ValueError("Todas las fuerzas son iguales; no hay regresión posible")
    m = (k * sxy - sx * sy) / den
    n = (sy - m * sx) / k
    ym = sy / k
    ss_tot = sum((v - ym) ** 2 for v in y)
    ss_res = sum((yi - (m * xi + n)) ** 2 for xi, yi in zip(x, y))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
    if k > 2:
        s2 = ss_res / (k - 2)
        sigma_m = math.sqrt(k * s2 / den)
        sigma_n = math.sqrt(s2 * sxx / den)
    else:
        sigma_m = sigma_n = float("nan")
    return m, n, r2, sigma_m, sigma_n


def regresion_por_origen(x, y):
    """Ajuste y = m x (intercepto forzado a cero)."""
    return sum(a * b for a, b in zip(x, y)) / sum(a * a for a in x)


def comparar(informado, calculado):
    if informado is None:
        return None
    if calculado == 0:
        return {"informado": informado, "calculado": calculado, "coincide": informado == 0}
    rel = abs(informado - calculado) / abs(calculado)
    out = {"informado": informado, "calculado": calculado,
           "diferencia_relativa": rel, "coincide": rel <= TOL_COINCIDE}
    # Detecta errores típicos de potencia de 10 (unidades mm/m, g/kg, cm/m)
    if not out["coincide"] and informado != 0:
        ratio = abs(informado / calculado)
        exp = round(math.log10(ratio))
        if exp != 0 and abs(ratio / 10 ** exp - 1) <= TOL_COINCIDE:
            out["posible_error_de_unidades"] = f"factor 10^{exp}"
    return out


def analizar(a):
    fd = 1e-3 if a.dimensiones_en_mm else 1.0
    b, h, L = a.b * fd, a.h * fd, a.L * fd
    masas = [m * (1e-3 if a.masas_en_g else 1.0) for m in a.masas]
    flechas = [y * (1e-3 if a.flechas_en_mm else 1.0) for y in a.flechas]
    if len(masas) != len(flechas):
        raise ValueError("Debe haber igual cantidad de masas y de flechas")

    fuerzas = [m * a.g for m in masas]
    I = b * h ** 3 / 12.0
    m, n, r2, sm, sn = regresion_lineal(fuerzas, flechas)
    m0 = regresion_por_origen(fuerzas, flechas)
    Y = L ** 3 / (3.0 * m * I)
    Y0 = L ** 3 / (3.0 * m0 * I)

    if a.Y_teorico is not None:
        Yt, rango = a.Y_teorico, None
    else:
        Yt, rango = TABLA_Y[a.material]
    err = abs(Y - Yt) / Yt * 100.0

    avisos = []
    if h > b:
        avisos.append("h > b: probablemente se intercambiaron ancho y espesor. "
                      "Con h y b intercambiados I cambia en un factor (b/h)^2.")
    if not (1e-4 <= h <= 5e-3):
        avisos.append(f"Espesor h = {h:g} m fuera del rango típico de una regla metálica "
                      "(0,1 mm a 5 mm): revisar unidades.")
    if not (0.05 <= L <= 1.5):
        avisos.append(f"Longitud L = {L:g} m poco plausible: revisar unidades.")
    if max(flechas) / L > 0.15:
        avisos.append("Flecha máxima > 15 % de L: se sale de la hipótesis de pendientes "
                      "pequeñas; los últimos puntos pueden curvar la tendencia.")
    if m <= 0:
        avisos.append("Pendiente no positiva: los datos no muestran y_F creciente con F.")
    if r2 < 0.98:
        avisos.append(f"R² = {r2:.4f} bajo para esta experiencia (esperable > 0,99).")
    if abs(n) > 0.1 * max(flechas):
        avisos.append("Intercepto mayor al 10 % de la flecha máxima: posible error de "
                      "cero (referencia mal tomada) o tendencia no lineal.")
    if not (1e10 <= Y <= 5e11):
        avisos.append(f"Y = {Y:.3e} Pa fuera del orden de magnitud de un metal "
                      "(10^10 a 10^11 Pa): casi seguro hay un error de unidades.")

    # Incertidumbre relativa del Y (propagación lineal), con resoluciones por defecto
    du = {
        "L": a.res_L / L,
        "h": a.res_h / h,
        "b": a.res_b / b,
        "pendiente": (sm / m) if (m and not math.isnan(sm)) else 0.0,
    }
    dY_rel = 3 * du["L"] + 3 * du["h"] + du["b"] + du["pendiente"]

    res = {
        "entradas_SI": {"b_m": b, "h_m": h, "L_m": L, "g": a.g,
                        "masas_kg": masas, "fuerzas_N": fuerzas, "flechas_m": flechas},
        "I_m4": I,
        "ajuste": {"pendiente_m_por_N": m, "intercepto_m": n, "R2": r2,
                   "sigma_pendiente": sm, "sigma_intercepto": sn},
        "ajuste_por_origen": {"pendiente_m_por_N": m0, "Y_Pa": Y0},
        "c_f_teorico_m_por_N": L ** 3 / (3 * Yt * I),
        "Y_experimental_Pa": Y,
        "Y_teorico_Pa": Yt,
        "rango_tabla_Pa": rango,
        "error_porcentual": err,
        "incertidumbre_relativa_Y": dY_rel,
        "contribuciones_incertidumbre": {"3·ΔL/L": 3 * du["L"], "3·Δh/h": 3 * du["h"],
                                         "Δb/b": du["b"], "Δm/m": du["pendiente"]},
        "avisos": avisos,
        "comparaciones": {
            "I": comparar(a.informado_I, I),
            "pendiente": comparar(a.informado_pendiente, m),
            "Y": comparar(a.informado_Y, Y),
            "error_porcentual": comparar(a.informado_error, err),
        },
    }
    return res


def fmt(v):
    return f"{v:.4e}".replace(".", ",")


def imprimir(r):
    e = r["entradas_SI"]
    print("=== Recalculo Taller 3: viga en voladizo ===")
    print(f"b = {fmt(e['b_m'])} m   h = {fmt(e['h_m'])} m   L = {fmt(e['L_m'])} m   g = {e['g']}")
    print("\n N   M [kg]      F [N]       y_F [m]")
    for i, (mm, f, y) in enumerate(zip(e["masas_kg"], e["fuerzas_N"], e["flechas_m"]), 1):
        print(f"{i:2d}   {mm:.4f}    {f:.4f}     {y:.5f}")
    print(f"\nI = b·h³/12 = {fmt(r['I_m4'])} m⁴")
    aj = r["ajuste"]
    print(f"Ajuste lineal: y_F = {fmt(aj['pendiente_m_por_N'])}·F + {fmt(aj['intercepto_m'])}"
          f"   R² = {aj['R2']:.5f}".replace(".", ","))
    print(f"  σ(pendiente) = {fmt(aj['sigma_pendiente'])} m/N   σ(intercepto) = {fmt(aj['sigma_intercepto'])} m")
    print(f"Ajuste por el origen: pendiente = {fmt(r['ajuste_por_origen']['pendiente_m_por_N'])} m/N"
          f" -> Y = {fmt(r['ajuste_por_origen']['Y_Pa'])} Pa")
    print(f"\nY_exp = L³/(3·m·I) = {fmt(r['Y_experimental_Pa'])} Pa"
          f" = {r['Y_experimental_Pa']/1e9:.1f} GPa".replace(".", ","))
    print(f"Y_teo = {fmt(r['Y_teorico_Pa'])} Pa")
    print(f"Error porcentual = {r['error_porcentual']:.2f} %".replace(".", ","))
    print(f"Incertidumbre relativa estimada de Y ≈ {100*r['incertidumbre_relativa_Y']:.1f} %".replace(".", ","))
    for k, v in r["contribuciones_incertidumbre"].items():
        print(f"   {k}: {100*v:.2f} %".replace(".", ","))
    print(f"c_f teórico (con Y_teo) = {fmt(r['c_f_teorico_m_por_N'])} m/N")
    if r["avisos"]:
        print("\nAVISOS:")
        for av in r["avisos"]:
            print(" -", av)
    comps = {k: v for k, v in r["comparaciones"].items() if v}
    if comps:
        print("\nCOMPARACIÓN CON LO INFORMADO:")
        for k, v in comps.items():
            estado = "OK" if v["coincide"] else "NO COINCIDE"
            extra = f" ({v['posible_error_de_unidades']})" if v.get("posible_error_de_unidades") else ""
            print(f" - {k}: informado {fmt(v['informado'])} vs calculado {fmt(v['calculado'])} -> {estado}{extra}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--b", type=float, required=True, help="ancho de la regla")
    p.add_argument("--h", type=float, required=True, help="espesor de la regla")
    p.add_argument("--L", type=float, required=True, help="longitud libre (empotramiento a punto de carga)")
    p.add_argument("--masas", type=float, nargs="+", required=True)
    p.add_argument("--flechas", type=float, nargs="+", required=True)
    p.add_argument("--masas-en-g", action="store_true")
    p.add_argument("--flechas-en-mm", action="store_true")
    p.add_argument("--dimensiones-en-mm", action="store_true")
    p.add_argument("--g", type=float, default=9.80)
    p.add_argument("--material", default="acero", choices=sorted(TABLA_Y))
    p.add_argument("--Y-teorico", dest="Y_teorico", type=float)
    p.add_argument("--res-L", type=float, default=1e-3, help="incertidumbre de L en m (huincha: 1 mm)")
    p.add_argument("--res-h", type=float, default=1e-5, help="incertidumbre de h en m (micrómetro: 0,01 mm)")
    p.add_argument("--res-b", type=float, default=2e-5, help="incertidumbre de b en m (pie de metro: 0,02 mm)")
    p.add_argument("--informado-I", type=float)
    p.add_argument("--informado-pendiente", type=float)
    p.add_argument("--informado-Y", type=float)
    p.add_argument("--informado-error", type=float)
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        r = analizar(a)
    except ValueError as ex:
        print(f"Error: {ex}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        imprimir(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
