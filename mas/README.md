# Revisor de talleres: Movimiento Armónico Simple (IN1090C/IN1111C)

Agente especializado en corregir el **Taller de Movimiento Armónico Simple** (ley de Hooke y oscilaciones de un cuerpo colgado de un resorte), con su solución modelo, la pauta de corrección y herramientas de verificación.

## Contenido

| Ruta | Qué es |
|---|---|
| `../.claude/agents/revisor-mas.md` | Definición del subagente de Claude Code (el revisor). Puede consultar la web para verificar conceptos. |
| `solucion/Taller_MAS_RESUELTO.docx` | Taller desarrollado completo sobre la plantilla original (datos de ejemplo). |
| `solucion/grafico_*.png` | Gráficos 1 (deformación vs fuerza) y 2 (periodo al cuadrado vs masa). |
| `pauta/pauta_taller_mas.md` | Pauta de corrección por ítem (100 pts), usada por el agente. |
| `pauta/Pauta_Taller_MAS.docx` | La misma pauta en Word, para el docente. |
| `conocimiento/marco_teorico.md` | Resumen del taller y la presentación, hechos verificados con fuentes, erratas de la plantilla y errores típicos. |
| `herramientas/verificar_mas.py` | Recalcula k por los dos métodos, la diferencia entre ellos y la masa efectiva del resorte. |
| `herramientas/anotar_pdf.py` | Genera el taller corregido (usa `comun/anotar_pdf.py` con `items.json`). |
| `herramientas/items.json` | Cómo se reconoce en el PDF el enunciado de cada ítem. |
| `herramientas/generar_solucion.py` | Genera el taller desarrollado con datos de ejemplo o de un laboratorio. |
| `fuentes/` | Enunciado original y presentación de apoyo. |

## Puntajes

| Ítem | Pts |
|---|---|
| Parte I: hipótesis | 6 |
| Parte I: Tabla 1 | 6 |
| Parte I: Gráfico 1 (deformación vs fuerza) | 10 |
| Parte I: constante elástica | 6 |
| Parte I: ¿datos acordes a lo esperado? | 6 |
| Parte II: hipótesis | 10 |
| Parte II: Tabla 2 | 8 |
| Parte II: Gráfico 2 (periodo² vs masa) | 10 |
| Parte II: constante elástica | 10 |
| Complete la frase | 8 |
| Conclusión parte 2 | 20 |

Criterios del docente: datos de laboratorio real con exigencia baja (se acepta error humano); gráfico 1 invertido −2 sin descontar k si está bien calculado; diferencia razonable entre las dos constantes hasta ~10 %.

## Resultado de la solución modelo

Resorte de estiramiento, masas de 50 a 400 g:

- Gráfico 1: x = 0,0397·F + 0,0004 (R² = 0,9999) ⟹ k₁ = 1/pendiente = 25,2 N/m.
- Gráfico 2: T² = 1,5701·m + 0,0184 (R² = 0,9976) ⟹ k₂ = 4π²/pendiente = 25,1 N/m.
- Diferencia entre ambos métodos: 0,2 %. Masa efectiva del resorte ≈ 12 g (intercepto/pendiente).

## Uso

```
> Usa el agente revisor-mas para corregir entregas/taller_mas_grupo1.pdf
```

Verificación manual de un grupo:

```bash
python3 mas/herramientas/verificar_mas.py --masas-en-g --x-en-mm \
  --m1 50 100 150 200 250 300 --x 20 39 59 78 98 117 \
  --m2 50 100 150 200 250 300 350 400 --t10 3.16 4.11 5.13 5.67 6.46 6.93 7.63 8.00
```

Solución desarrollada con los datos de un laboratorio: `python3 mas/herramientas/generar_solucion.py <mismas opciones> --etiqueta "Lab lunes" --salida mas/solucion/lab_lunes.docx`.

Las revisiones se guardan en `mas/revisiones/`, excluida de git.
