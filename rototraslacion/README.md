# Revisor de talleres: Energía en movimiento de rototraslación (IN1090C/IN1111C, Taller 2)

Agente especializado en corregir el **Taller 2: Conservación de la energía en movimiento de rototraslación** (anillo que rueda sin deslizar por un plano inclinado), con su solución modelo, la pauta de corrección y herramientas de verificación.

## Contenido

| Ruta | Qué es |
|---|---|
| `../.claude/agents/revisor-rototraslacion.md` | Definición del subagente de Claude Code (el revisor). |
| `solucion/Taller2_Rototraslacion_RESUELTO.docx` | Taller desarrollado completo sobre la plantilla original (datos de ejemplo de un anillo de hierro). |
| `solucion/grafico_*.png` | Gráficos d vs t, K_Rot y K_Tras vs d, y K_Tot, U_g y E_mec vs d. |
| `pauta/pauta_taller2.md` | Pauta de corrección por ítem (100 pts), usada por el agente. |
| `pauta/Pauta_Taller2_Rototraslacion.docx` | La misma pauta en Word, para el docente. |
| `conocimiento/marco_teorico.md` | Resumen de la guía, comportamiento esperado y errores típicos. |
| `herramientas/verificar_energia.py` | Recalcula I, ajuste d(t), v(t), la Tabla 3 completa, ⟨E⟩, σ y los valores a mitad de recorrido. |
| `herramientas/anotar_pdf.py` | Genera el taller corregido (usa `comun/anotar_pdf.py` con `items.json`). |
| `herramientas/items.json` | Cómo se reconoce en el PDF el enunciado de cada ítem. |
| `herramientas/generar_solucion.py` | Genera el taller desarrollado con datos de ejemplo o de un laboratorio. |
| `fuentes/` | Enunciado original del taller y guía de estudio. |

## Puntajes

| Ítem | Pts |
|---|---|
| Gráfico posición-tiempo y ecuación d(t) | 10 |
| Tabla 3 de energías | 10 |
| Hipótesis | 5 |
| Gráfico K_Rot y K_Tras vs d e inferencia | 20 |
| Gráfico K_Tot, U_g y E_mec vs d, ajustes y preguntas | 25 |
| Promedio de E_mec con su error | 10 |
| Conclusión | 20 |

Criterio del docente: los datos vienen de un simulador web; la exigencia en la toma de datos es baja (se acepta error humano). Se evalúa método, cálculos, coherencia y análisis. La altura puede medirse desde cualquier referencia consistente. El ajuste de d(t) debe ser un polinomio de grado 2.

## Resultado de la solución modelo

Anillo de hierro M = 0,450 kg, R_int = 25 mm, R_ext = 35 mm, plano de 1,20 m elevado 6,0 cm (θ = 2,87°):

- I = ½·M·(R_int² + R_ext²) = 4,16×10⁻⁴ kg·m²; K_Rot/K_Tras = 0,76 (43 % de la energía cinética es de rotación).
- d(t) = 0,1350·t² + 0,0014·t − 0,0012 [m]; v(t) = 0,2700·t + 0,0014 [m/s].
- E_mec = (0,263 ± 0,002) J, variación de 0,8 %.

## Uso del agente

En Claude Code, dentro de este repositorio:

```
> Usa el agente revisor-rototraslacion para corregir entregas/taller2_grupo1.pdf
```

Entrega el **taller corregido** (`<taller>_CORREGIDO.pdf`: copia exacta del documento del grupo con el puntaje de cada ítem en el margen, un comentario en rojo dentro de cada ítem con descuento y el total y la nota en la primera página) y un **informe para el docente** (`.md`). Las revisiones se guardan en `rototraslacion/revisiones/`, excluida de git.

Verificación manual de un grupo:

```bash
python3 rototraslacion/herramientas/verificar_energia.py --M 450 --masa-en-g --Rint 25 --Rext 35 --radios-en-mm \
  --h0 0.06 --largo 1.20 --D 1.20 --d 0 0.01 0.03 0.075 0.13 --t 0 0.25 0.5 0.75 1
```

Solución desarrollada con los datos de un laboratorio (mismas opciones más `--etiqueta` y `--salida`):

```bash
python3 rototraslacion/herramientas/generar_solucion.py --M 0.45 --Rint 0.025 --Rext 0.035 \
  --h0 0.06 --largo 1.2 --D 1.2 --d ... --t ... --etiqueta "Lab jueves" --salida rototraslacion/solucion/lab_jueves.docx
```

Requisitos: Python 3; `pymupdf` y `numpy` (anotar), `lxml` (extraer), `python-docx` y `matplotlib` (generar).
