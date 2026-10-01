#!/usr/bin/env python3
"""Recalcula los resultados del Taller 2 (energía en movimiento de rototraslación) a partir de los
datos de un grupo, para compararlos con lo que el grupo informó.

Sin dependencias externas (solo biblioteca estándar).

Modelo (anillo o cilindro hueco que rueda sin deslizar sobre un plano inclinado):
    I = (1/2)·M·(Rint² + Rext²)            ω = v / R   (R = radio de rodadura, por defecto Rext)
    d(t) = A·t² + B·t + C  (ajuste cuadrático)  ⟹  v(t) = 2A·t + B,  a = 2A
    h_i = (D − d_i)·sen θ                   (D: posición sobre el plano donde h = 0)
    K_rot = ½·I·ω²   K_tras = ½·M·v²   K_tot = K_rot + K_tras   U_g = M·g·h   E_mec = K_tot + U_g
    <E> ± σ, con σ = sqrt( Σ (E_i − <E>)² / N )   (fórmula del taller)
    a_teórica = g·sen θ / (1 + I/(M·R²))

Uso típico (SI):
    python3 verificar_energia.py --M 0.450 --Rint 0.025 --Rext 0.035 --theta 2.87 \
        --d 0 0.01 0.035 ... --t 0 0.25 0.5 ... --D 1.20

Opciones útiles:
    --masa-en-g, --radios-en-mm, --radios-en-cm, --d-en-cm
    --theta GRADOS  o  --h0 ALTURA --largo LARGO (sen θ = h0/largo)
    --D POSICION     posición (en el eje d) donde la altura es cero; por defecto la última posición medida
    --h h1 h2 ...    usar directamente las alturas que informó el grupo (anula --D)
    --R-rodadura R   radio con el que rueda (por defecto Rext)
    --g 9.8
    --informado-I, --informado-A, --informado-B, --informado-Emec, --informado-sigma
    --json
"""
import argparse
import json
import math
import sys

TOL_COINCIDE = 0.05  # 5 %: el docente pidió no exigir mucho en la toma de datos (simulador, error humano)


# ---------------------------------------------------------------- ajustes
def resolver3(m, v):
    """Resuelve un sistema 3x3 por Cramer."""
    def det(a):
        return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
                - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
                + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))
    D = det(m)
    if abs(D) < 1e-300:
        raise ValueError("Sistema singular: revise que los tiempos sean distintos")
    res = []
    for c in range(3):
        mc = [row[:] for row in m]
        for r in range(3):
            mc[r][c] = v[r]
        res.append(det(mc) / D)
    return res


def ajuste_cuadratico(t, d):
    """d = A t² + B t + C por mínimos cuadrados. Devuelve A, B, C, R²."""
    if len(t) < 3:
        raise ValueError("Se necesitan al menos 3 puntos para el ajuste cuadrático")
    s = [sum(x ** k for x in t) for k in range(5)]
    sy = [sum(y * x ** k for x, y in zip(t, d)) for k in range(3)]
    C, B, A = resolver3([[s[0], s[1], s[2]], [s[1], s[2], s[3]], [s[2], s[3], s[4]]], sy)
    ym = sum(d) / len(d)
    ss_tot = sum((y - ym) ** 2 for y in d)
    ss_res = sum((y - (A * x * x + B * x + C)) ** 2 for x, y in zip(t, d))
    return A, B, C, (1 - ss_res / ss_tot if ss_tot > 0 else 1.0)


def ajuste_lineal(x, y):
    n = len(x)
    sx, sy = sum(x), sum(y)
    sxx = sum(v * v for v in x)
    sxy = sum(a * b for a, b in zip(x, y))
    den = n * sxx - sx * sx
    m = (n * sxy - sx * sy) / den if den else 0.0
    b = (sy - m * sx) / n
    ym = sy / n
    ss_tot = sum((v - ym) ** 2 for v in y)
    ss_res = sum((yi - (m * xi + b)) ** 2 for xi, yi in zip(x, y))
    return m, b, (1 - ss_res / ss_tot if ss_tot > 0 else 1.0)


def comparar(informado, calculado):
    if informado is None:
        return None
    if calculado == 0:
        return {"informado": informado, "calculado": calculado, "coincide": informado == 0}
    rel = abs(informado - calculado) / abs(calculado)
    out = {"informado": informado, "calculado": calculado, "diferencia_relativa": rel,
           "coincide": rel <= TOL_COINCIDE}
    if not out["coincide"] and informado != 0:
        ratio = abs(informado / calculado)
        exp = round(math.log10(ratio))
        if exp != 0 and abs(ratio / 10 ** exp - 1) <= TOL_COINCIDE:
            out["posible_error_de_unidades"] = f"factor 10^{exp}"
    return out


# ---------------------------------------------------------------- cálculo
def analizar(a):
    M = a.M * (1e-3 if a.masa_en_g else 1.0)
    fr = 1e-3 if a.radios_en_mm else (1e-2 if a.radios_en_cm else 1.0)
    Rint, Rext = a.Rint * fr, a.Rext * fr
    R = a.R_rodadura * fr if a.R_rodadura is not None else Rext
    d = [x * (1e-2 if a.d_en_cm else 1.0) for x in a.d]
    t = list(a.t)
    if len(d) != len(t):
        raise ValueError("Debe haber igual cantidad de posiciones y de tiempos")
    if a.theta is not None:
        sen = math.sin(math.radians(a.theta))
        theta = a.theta
    elif a.h0 is not None and a.largo is not None:
        sen = a.h0 / a.largo
        theta = math.degrees(math.asin(sen))
    else:
        raise ValueError("Indique --theta o bien --h0 y --largo")

    I = 0.5 * M * (Rint ** 2 + Rext ** 2)
    beta = I / (M * R ** 2)
    A, B, C, r2 = ajuste_cuadratico(t, d)
    a_exp = 2 * A
    a_teo = a.g * sen / (1 + beta)

    if a.h is not None:
        h = list(a.h)
        if len(h) != len(d):
            raise ValueError("--h debe tener tantos valores como posiciones")
        ref = "alturas informadas por el grupo"
    else:
        D = a.D if a.D is not None else max(d)
        D *= (1e-2 if (a.d_en_cm and a.D is not None) else 1.0)
        h = [(D - x) * sen for x in d]
        ref = f"h = 0 en d = {D:g} m"

    filas = []
    for di, ti, hi in zip(d, t, h):
        v = 2 * A * ti + B
        w = v / R
        krot = 0.5 * I * w * w
        ktras = 0.5 * M * v * v
        ug = M * a.g * hi
        filas.append({"d": di, "t": ti, "h": hi, "v": v, "Krot": krot, "Ktras": ktras,
                      "Ktot": krot + ktras, "Ug": ug, "Emec": krot + ktras + ug})
    E = [f["Emec"] for f in filas]
    Em = sum(E) / len(E)
    sigma = math.sqrt(sum((e - Em) ** 2 for e in E) / len(E))
    sigma_n1 = math.sqrt(sum((e - Em) ** 2 for e in E) / (len(E) - 1)) if len(E) > 1 else 0.0

    mK = ajuste_lineal(d, [f["Ktot"] for f in filas])
    mU = ajuste_lineal(d, [f["Ug"] for f in filas])
    mE = ajuste_lineal(d, E)
    d_mitad = (min(d) + max(d)) / 2
    variacion = (max(E) - min(E)) / Em * 100 if Em else float("nan")

    avisos = []
    if Rint >= Rext:
        avisos.append("Rint ≥ Rext: radios intercambiados o mal medidos.")
    if not (0.003 <= Rext <= 0.3):
        avisos.append(f"Rext = {Rext:g} m poco plausible para el anillo: revisar unidades.")
    if not (0.01 <= M <= 20):
        avisos.append(f"M = {M:g} kg poco plausible: revisar unidades (¿gramos?).")
    if theta > 20:
        avisos.append(f"θ = {theta:.1f}° alto para un plano 'levemente inclinado': revisar el cálculo del ángulo.")
    if A <= 0:
        avisos.append("Coeficiente de t² no positivo: los datos no muestran movimiento acelerado.")
    if r2 < 0.98:
        avisos.append(f"R² del ajuste cuadrático = {r2:.4f}: datos con bastante dispersión (no se penaliza la toma de datos).")
    if a_teo > 0 and abs(a_exp - a_teo) / a_teo > 0.25:
        avisos.append(f"Aceleración experimental ({a_exp:.4f} m/s²) difiere más de 25 % de la teórica "
                      f"({a_teo:.4f} m/s²): posible deslizamiento, ángulo o datos mal medidos.")
    if any(x < 0 for x in h):
        avisos.append("Hay alturas negativas: la referencia de altura no está en el punto más bajo usado.")
    if abs(variacion) > 10:
        avisos.append(f"La energía mecánica varía {variacion:.1f} % a lo largo del recorrido "
                      "(se evalúa el análisis del grupo, no el valor).")

    return {
        "entradas_SI": {"M": M, "Rint": Rint, "Rext": Rext, "R_rodadura": R, "theta_grados": theta,
                        "sen_theta": sen, "g": a.g, "referencia_altura": ref},
        "I": I, "I_sobre_MR2": beta,
        "ajuste_d_t": {"A": A, "B": B, "C": C, "R2": r2},
        "aceleracion_experimental": a_exp, "aceleracion_teorica": a_teo,
        "tabla3": filas,
        "Emec_promedio": Em, "sigma": sigma, "sigma_N_menos_1": sigma_n1,
        "variacion_Emec_pct": variacion,
        "ajustes_lineales": {"Ktot": mK, "Ug": mU, "Emec": mE},
        "mitad_recorrido": {"d": d_mitad, "Ktot": mK[0] * d_mitad + mK[1], "Ug": mU[0] * d_mitad + mU[1]},
        "avisos": avisos,
        "comparaciones": {
            "I": comparar(a.informado_I, I),
            "A": comparar(a.informado_A, A),
            "B": comparar(a.informado_B, B),
            "Emec_promedio": comparar(a.informado_Emec, Em),
            "sigma": comparar(a.informado_sigma, sigma),
        },
    }


def f(x, dec=4):
    return f"{x:.{dec}e}".replace(".", ",")


def c(x, dec=4):
    return f"{x:.{dec}f}".replace(".", ",")


def sg(x, dec=5):
    """Término con signo: ' + 0,0012' o ' − 0,0012'."""
    return (" + " if x >= 0 else " − ") + c(abs(x), dec)


def imprimir(r):
    e = r["entradas_SI"]
    print("=== Recálculo Taller 2: energía en rototraslación ===")
    print(f"M = {c(e['M'])} kg   Rint = {c(e['Rint'])} m   Rext = {c(e['Rext'])} m   "
          f"R rodadura = {c(e['R_rodadura'])} m   θ = {c(e['theta_grados'], 2)}°   g = {c(e['g'], 2)} m/s²")
    print(f"Referencia de altura: {e['referencia_altura']}")
    print(f"\nI = ½·M·(Rint² + Rext²) = {f(r['I'])} kg·m²     I/(M·R²) = {c(r['I_sobre_MR2'])}")
    aj = r["ajuste_d_t"]
    print(f"Ajuste d(t) = {c(aj['A'], 5)}·t²{sg(aj['B'])}·t{sg(aj['C'])}   R² = {c(aj['R2'], 5)}")
    print(f"v(t) = {c(2 * aj['A'], 5)}·t{sg(aj['B'])}")
    print(f"a experimental = {c(r['aceleracion_experimental'], 4)} m/s²   "
          f"a teórica (rodando sin deslizar) = {c(r['aceleracion_teorica'], 4)} m/s²")
    print("\n   d[m]     t[s]     h[m]     v[m/s]    Krot[J]    Ktras[J]   Ktot[J]    Ug[J]      Emec[J]")
    for x in r["tabla3"]:
        print(f"  {c(x['d'])}  {c(x['t'], 3)}  {c(x['h'])}  {c(x['v'])}  {c(x['Krot'], 5)}  "
              f"{c(x['Ktras'], 5)}  {c(x['Ktot'], 5)}  {c(x['Ug'], 5)}  {c(x['Emec'], 5)}")
    print(f"\n<Emec> = {c(r['Emec_promedio'], 5)} J   σ (÷N) = {c(r['sigma'], 5)} J   "
          f"σ (÷(N−1)) = {c(r['sigma_N_menos_1'], 5)} J   "
          f"σ/<E> = {c(100 * r['sigma'] / r['Emec_promedio'], 2)} %")
    print(f"Variación de Emec (máx − mín)/<E> = {c(r['variacion_Emec_pct'], 2)} %")
    for k, (m, b, rr) in r["ajustes_lineales"].items():
        print(f"Ajuste lineal {k}(d) = {c(m, 5)}·d{sg(b)}   R² = {c(rr, 4)}")
    mi = r["mitad_recorrido"]
    print(f"Mitad del recorrido (d = {c(mi['d'])} m): Ktot ≈ {c(mi['Ktot'], 5)} J   Ug ≈ {c(mi['Ug'], 5)} J")
    if r["avisos"]:
        print("\nAVISOS:")
        for av in r["avisos"]:
            print(" -", av)
    comps = {k: v for k, v in r["comparaciones"].items() if v}
    if comps:
        print(f"\nCOMPARACIÓN CON LO INFORMADO (tolerancia {int(TOL_COINCIDE * 100)} %):")
        for k, v in comps.items():
            estado = "OK" if v["coincide"] else "NO COINCIDE"
            extra = f" ({v['posible_error_de_unidades']})" if v.get("posible_error_de_unidades") else ""
            print(f" - {k}: informado {f(v['informado'])} vs calculado {f(v['calculado'])} -> {estado}{extra}")


def construir_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--M", type=float, required=True)
    p.add_argument("--Rint", type=float, required=True)
    p.add_argument("--Rext", type=float, required=True)
    p.add_argument("--R-rodadura", dest="R_rodadura", type=float)
    p.add_argument("--theta", type=float, help="ángulo en grados")
    p.add_argument("--h0", type=float, help="altura del plano (para sen θ = h0/largo)")
    p.add_argument("--largo", type=float, help="largo del plano (para sen θ = h0/largo)")
    p.add_argument("--d", type=float, nargs="+", required=True)
    p.add_argument("--t", type=float, nargs="+", required=True)
    p.add_argument("--D", type=float, help="posición sobre el plano donde la altura es cero")
    p.add_argument("--h", type=float, nargs="+", help="alturas informadas por el grupo")
    p.add_argument("--masa-en-g", action="store_true")
    p.add_argument("--radios-en-mm", action="store_true")
    p.add_argument("--radios-en-cm", action="store_true")
    p.add_argument("--d-en-cm", action="store_true")
    p.add_argument("--g", type=float, default=9.8)
    p.add_argument("--informado-I", type=float)
    p.add_argument("--informado-A", type=float)
    p.add_argument("--informado-B", type=float)
    p.add_argument("--informado-Emec", type=float)
    p.add_argument("--informado-sigma", type=float)
    p.add_argument("--json", action="store_true")
    return p


def main(argv=None):
    a = construir_parser().parse_args(argv)
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
