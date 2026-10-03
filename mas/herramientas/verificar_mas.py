#!/usr/bin/env python3
"""Recalcula los resultados del Taller de Movimiento Armónico Simple (resorte) con los datos de un grupo.

Sin dependencias externas (solo biblioteca estándar).

Parte I (estática, ley de Hooke):  x = F/k  ⟹  gráfico x vs F: pendiente = 1/k  ⟹  k₁ = 1/pendiente
    (si el grupo graficó F vs x, la pendiente es k directamente).
Parte II (oscilaciones):  T = 2π·√(m/k)  ⟹  T² = (4π²/k)·m  ⟹  gráfico T² vs m: pendiente = 4π²/k
    ⟹  k₂ = 4π²/pendiente. El intercepto (positivo) se explica por la masa efectiva del resorte:
    T² = (4π²/k)·(m + m_ef), con m_ef ≈ m_resorte/3  ⟹  m_ef = intercepto/pendiente.

Uso típico (SI):
    python3 verificar_mas.py --m1 0.05 0.10 0.15 0.20 0.25 0.30 --x 0.020 0.041 0.060 0.081 0.100 0.121 \
        --m2 0.05 0.10 ... --t10 3.62 4.70 ...

Opciones útiles:
    --masas-en-g           masas en gramos (ambas partes)
    --x-en-cm, --x-en-mm   deformaciones en cm o mm
    --L0 L0 --L L1 L2 ...  en vez de --x: longitudes (x = L − L0), en las mismas unidades que --x
    --T T1 T2 ...          en vez de --t10: periodos ya divididos
    --g 9.8
    --informado-k1, --informado-k2, --informado-pendiente1, --informado-pendiente2
    --json
"""
import argparse
import json
import math
import sys

TOL = 0.05   # tolerancia relativa para dar por coincidente un valor informado (datos reales, cronómetro)
DIF_RAZONABLE = 10.0  # % de diferencia entre k₁ y k₂ que se considera razonable (criterio del docente)


def ajuste_lineal(x, y):
    n = len(x)
    if n < 2:
        raise ValueError("Se necesitan al menos 2 puntos")
    sx, sy = sum(x), sum(y)
    sxx = sum(v * v for v in x)
    sxy = sum(a * b for a, b in zip(x, y))
    den = n * sxx - sx * sx
    if den == 0:
        raise ValueError("Todos los valores del eje x son iguales")
    m = (n * sxy - sx * sy) / den
    b = (sy - m * sx) / n
    ym = sy / n
    ss_tot = sum((v - ym) ** 2 for v in y)
    ss_res = sum((yi - (m * xi + b)) ** 2 for xi, yi in zip(x, y))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return m, b, r2


def comparar(informado, calculado):
    if informado is None:
        return None
    rel = abs(informado - calculado) / abs(calculado) if calculado else float("inf")
    out = {"informado": informado, "calculado": calculado, "diferencia_relativa": rel, "coincide": rel <= TOL}
    if not out["coincide"] and informado and calculado:
        ratio = abs(informado / calculado)
        e = round(math.log10(ratio))
        if e != 0 and abs(ratio / 10 ** e - 1) <= TOL:
            out["posible_error_de_unidades"] = f"factor 10^{e}"
    return out


def analizar(a):
    fm = 1e-3 if a.masas_en_g else 1.0
    fx = 1e-2 if a.x_en_cm else (1e-3 if a.x_en_mm else 1.0)
    res = {"g": a.g, "avisos": []}
    av = res["avisos"]

    # ---------------- Parte I
    k1 = None
    if a.m1:
        m1 = [v * fm for v in a.m1]
        if a.x is not None:
            x = [v * fx for v in a.x]
        elif a.L is not None and a.L0 is not None:
            x = [(v - a.L0) * fx for v in a.L]
        else:
            raise ValueError("Parte I: indique --x, o bien --L0 y --L")
        if len(x) != len(m1):
            raise ValueError("Parte I: igual cantidad de masas y deformaciones")
        F = [m * a.g for m in m1]
        p, b, r2 = ajuste_lineal(F, x)          # x vs F (lo pedido)
        k1 = 1 / p if p else float("nan")
        pk, bk, _ = ajuste_lineal(x, F)          # F vs x (alternativa)
        res["parte1"] = {"masas_kg": m1, "F_N": F, "x_m": x,
                         "ajuste_x_vs_F": {"pendiente_m_por_N": p, "intercepto_m": b, "R2": r2},
                         "k1_N_por_m": k1,
                         "ajuste_F_vs_x": {"pendiente_N_por_m": pk, "intercepto_N": bk},
                         "k_punto_a_punto": [f / xi if xi else float("nan") for f, xi in zip(F, x)]}
        if r2 < 0.98:
            av.append(f"Parte I: R² = {r2:.4f} (no se penaliza la toma de datos, pero revisa el análisis).")
        if any(xi <= 0 for xi in x):
            av.append("Parte I: hay deformaciones ≤ 0: ¿se informó la longitud total en vez de la deformación?")
        if abs(b) > 0.1 * max(x):
            av.append("Parte I: el intercepto del ajuste x vs F es apreciable; en resortes de estiramiento puede "
                      "deberse a la tensión inicial (el resorte no se estira hasta superar cierta fuerza).")
        if not (1 <= k1 <= 2000):
            av.append(f"Parte I: k₁ = {k1:.3g} N/m poco plausible para un resorte de laboratorio: revisar unidades.")

    # ---------------- Parte II
    k2 = None
    if a.m2:
        m2 = [v * fm for v in a.m2]
        if a.T is not None:
            T = list(a.T)
            t10 = [v * a.n_osc for v in T]
        elif a.t10 is not None:
            t10 = list(a.t10)
            T = [v / a.n_osc for v in t10]
        else:
            raise ValueError("Parte II: indique --t10 o --T")
        if len(T) != len(m2):
            raise ValueError("Parte II: igual cantidad de masas y tiempos")
        T2 = [v * v for v in T]
        p2, b2, r22 = ajuste_lineal(m2, T2)
        k2 = 4 * math.pi ** 2 / p2 if p2 else float("nan")
        mef = b2 / p2 if p2 else float("nan")
        # ajuste por el origen (si el grupo forzó intercepto 0)
        p0 = sum(a_ * b_ for a_, b_ in zip(m2, T2)) / sum(v * v for v in m2)
        res["parte2"] = {"masas_kg": m2, "t10_s": t10, "T_s": T, "T2_s2": T2,
                         "ajuste_T2_vs_m": {"pendiente_s2_por_kg": p2, "intercepto_s2": b2, "R2": r22},
                         "k2_N_por_m": k2, "masa_efectiva_resorte_kg": mef,
                         "masa_resorte_estimada_kg": 3 * mef,
                         "ajuste_por_origen": {"pendiente": p0, "k2": 4 * math.pi ** 2 / p0},
                         "k_punto_a_punto": [4 * math.pi ** 2 * m / t2 for m, t2 in zip(m2, T2)]}
        if r22 < 0.98:
            av.append(f"Parte II: R² = {r22:.4f} (no se penaliza la toma de datos, pero revisa el análisis).")
        if b2 < 0:
            av.append("Parte II: intercepto negativo en T² vs m (se esperaría ≥ 0 por la masa del resorte); "
                      "suele deberse a errores de tiempo.")
        if any(v > 5 for v in T):
            av.append("Parte II: periodos > 5 s: ¿se informó el tiempo de 10 oscilaciones como periodo?")

    if k1 and k2:
        dif = abs(k1 - k2) / ((k1 + k2) / 2) * 100
        res["comparacion"] = {"k1": k1, "k2": k2,
                              "diferencia_pct_respecto_promedio": dif,
                              "diferencia_pct_respecto_k1": abs(k1 - k2) / k1 * 100,
                              "razonable": dif <= DIF_RAZONABLE}
        if dif > DIF_RAZONABLE:
            av.append(f"k₁ y k₂ difieren {dif:.1f} % (> {DIF_RAZONABLE:.0f} %): el grupo debe explicar causas "
                      "(masa del resorte, tiempo de reacción, rango no lineal, distinto resorte...).")

    res["comparaciones_informado"] = {
        "k1": comparar(a.informado_k1, k1) if k1 else None,
        "k2": comparar(a.informado_k2, k2) if k2 else None,
        "pendiente1": comparar(a.informado_pendiente1, res["parte1"]["ajuste_x_vs_F"]["pendiente_m_por_N"])
        if a.informado_pendiente1 is not None and "parte1" in res else None,
        "pendiente2": comparar(a.informado_pendiente2, res["parte2"]["ajuste_T2_vs_m"]["pendiente_s2_por_kg"])
        if a.informado_pendiente2 is not None and "parte2" in res else None,
    }
    return res


def c(x, d=4):
    return f"{x:.{d}f}".replace(".", ",")


def sg(x, d=5):
    return (" + " if x >= 0 else " − ") + c(abs(x), d)


def imprimir(r):
    print("=== Recálculo Taller MAS (resorte) ===")
    print(f"g = {c(r['g'], 2)} m/s²")
    if "parte1" in r:
        p = r["parte1"]
        aj = p["ajuste_x_vs_F"]
        print("\nPARTE I (estática)\n  N   m [kg]    F [N]     x [m]     F/x [N/m]")
        for i, (m, F, x, k) in enumerate(zip(p["masas_kg"], p["F_N"], p["x_m"], p["k_punto_a_punto"]), 1):
            print(f"  {i}   {c(m)}   {c(F)}   {c(x)}   {c(k, 2)}")
        print(f"  Ajuste x vs F:  x = {c(aj['pendiente_m_por_N'], 5)}·F{sg(aj['intercepto_m'])}   R² = {c(aj['R2'], 4)}")
        print(f"  k₁ = 1/pendiente = {c(p['k1_N_por_m'], 2)} N/m")
        print(f"  (Si graficaron F vs x: F = {c(p['ajuste_F_vs_x']['pendiente_N_por_m'], 3)}·x"
              f"{sg(p['ajuste_F_vs_x']['intercepto_N'], 4)}; pendiente = k)")
    if "parte2" in r:
        p = r["parte2"]
        aj = p["ajuste_T2_vs_m"]
        print("\nPARTE II (oscilaciones)\n  N   m [kg]    t10 [s]   T [s]     T² [s²]   4π²m/T² [N/m]")
        for i, (m, t, T, T2, k) in enumerate(zip(p["masas_kg"], p["t10_s"], p["T_s"], p["T2_s2"], p["k_punto_a_punto"]), 1):
            print(f"  {i}   {c(m)}   {c(t, 2)}    {c(T)}   {c(T2)}   {c(k, 2)}")
        print(f"  Ajuste T² vs m:  T² = {c(aj['pendiente_s2_por_kg'], 4)}·m{sg(aj['intercepto_s2'], 4)}   R² = {c(aj['R2'], 4)}")
        print(f"  k₂ = 4π²/pendiente = {c(p['k2_N_por_m'], 2)} N/m")
        print(f"  Masa efectiva del resorte = intercepto/pendiente = {c(p['masa_efectiva_resorte_kg'] * 1000, 1)} g "
              f"(masa del resorte ≈ {c(p['masa_resorte_estimada_kg'] * 1000, 1)} g si m_ef = m_resorte/3)")
        print(f"  (Ajuste forzado por el origen: pendiente {c(p['ajuste_por_origen']['pendiente'], 4)} → "
              f"k₂ = {c(p['ajuste_por_origen']['k2'], 2)} N/m)")
    if "comparacion" in r:
        cp = r["comparacion"]
        print(f"\nCOMPARACIÓN: k₁ = {c(cp['k1'], 2)} N/m, k₂ = {c(cp['k2'], 2)} N/m → diferencia "
              f"{c(cp['diferencia_pct_respecto_promedio'], 1)} % (respecto del promedio), "
              f"{c(cp['diferencia_pct_respecto_k1'], 1)} % (respecto de k₁): "
              + ("razonable" if cp["razonable"] else "mayor que 10 %"))
    print("\nCOMPLETE LA FRASE (respuesta correcta): mismo resorte y más masa → frecuencia DISMINUYE, periodo AUMENTA;"
          " misma masa y resorte más rígido → frecuencia AUMENTA, periodo DISMINUYE.")
    if r["avisos"]:
        print("\nAVISOS:")
        for a in r["avisos"]:
            print(" -", a)
    comps = {k: v for k, v in r["comparaciones_informado"].items() if v}
    if comps:
        print(f"\nCOMPARACIÓN CON LO INFORMADO (tolerancia {int(TOL * 100)} %):")
        for k, v in comps.items():
            e = " (" + v["posible_error_de_unidades"] + ")" if v.get("posible_error_de_unidades") else ""
            print(f" - {k}: informado {v['informado']:.5g} vs calculado {v['calculado']:.5g} -> "
                  f"{'OK' if v['coincide'] else 'NO COINCIDE'}{e}")


def construir_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--m1", type=float, nargs="+", help="masas de la parte I")
    p.add_argument("--x", type=float, nargs="+", help="deformaciones de la parte I")
    p.add_argument("--L0", type=float)
    p.add_argument("--L", type=float, nargs="+")
    p.add_argument("--m2", type=float, nargs="+", help="masas de la parte II")
    p.add_argument("--t10", type=float, nargs="+", help="tiempo de N oscilaciones (por defecto 10)")
    p.add_argument("--T", type=float, nargs="+", help="periodos")
    p.add_argument("--n-osc", type=int, default=10)
    p.add_argument("--masas-en-g", action="store_true")
    p.add_argument("--x-en-cm", action="store_true")
    p.add_argument("--x-en-mm", action="store_true")
    p.add_argument("--g", type=float, default=9.8)
    p.add_argument("--informado-k1", type=float)
    p.add_argument("--informado-k2", type=float)
    p.add_argument("--informado-pendiente1", type=float)
    p.add_argument("--informado-pendiente2", type=float)
    p.add_argument("--json", action="store_true")
    return p


def main(argv=None):
    a = construir_parser().parse_args(argv)
    try:
        r = analizar(a)
    except ValueError as e:
        print("Error:", e, file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        imprimir(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
