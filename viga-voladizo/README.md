# Revisor de talleres: Viga en voladizo (IN1090C, Taller 3)

Agente especializado en corregir el **Taller 3: Flexión de una viga en voladizo, Módulo de Young**, con su solución modelo, la pauta de corrección y herramientas de verificación.

## Contenido

| Ruta | Qué es |
|---|---|
| `../.claude/agents/revisor-viga-voladizo.md` | Definición del subagente de Claude Code (el revisor). |
| `solucion/Taller3_Viga_Voladiza_RESUELTO.docx` | Taller desarrollado completo sobre la plantilla original (datos ilustrativos de una regla de acero). |
| `solucion/grafico_yF_vs_F.png` | Gráfico y_F vs F con línea de tendencia (ítem 1.5). |
| `pauta/pauta_taller3.md` | Pauta de corrección por ítem (100 pts), usada por el agente. |
| `pauta/Pauta_Taller3_Viga_Voladiza.docx` | La misma pauta en Word, para el docente. |
| `conocimiento/marco_teorico.md` | Resumen de la guía de estudio y notas físicas para el revisor. |
| `herramientas/verificar_calculos.py` | Recalcula I, pendiente, Y, E% e incertidumbre con los datos de un grupo y detecta errores de unidades. |
| `herramientas/anotar_pdf.py` | Genera el taller corregido: el PDF del grupo con el puntaje junto a cada ítem y comentarios bajo los ítems con descuento, más una hoja resumen. |
| `herramientas/extraer_taller.py` | Extrae a texto un taller .docx/.pdf (incluida la Tabla 2 dentro del cuadro de texto) y sus imágenes. |
| `herramientas/generar_solucion.py` | Genera el taller desarrollado con los datos de cualquier laboratorio (o los de ejemplo). |
| `herramientas/pauta_a_docx.py` | Regenera la pauta .docx desde el .md. |
| `fuentes/` | Enunciado original del taller y guía de estudio. |

## Resultado de la solución modelo

Regla de acero, b = 25,0 mm, h = 0,80 mm, L = 250 mm, masas de 10 a 100 g:

- I = b·h³/12 = 1,07×10⁻¹² m⁴
- Ajuste: y_F = 0,02526·F + 0,00003 (R² = 0,9993)
- Y_exp = L³/(3·m·I) = 1,93×10¹¹ Pa ≈ 193 GPa, frente a 200 GPa del acero: E% = 3,4 %

Los datos son **de ejemplo**. Como cada laboratorio toma sus propios datos en el momento, la corrección nunca compara contra estos números: el agente recalcula todo con los datos de cada grupo.

### Solución desarrollada con los datos de un laboratorio

```bash
python3 viga-voladizo/herramientas/generar_solucion.py \
  --b 25.1 --h 0.79 --L 300 --dimensiones-en-mm \
  --masas 20 40 60 80 100 --masas-en-g --flechas 6 12.5 18 24.5 31 --flechas-en-mm \
  --etiqueta "Lab martes 10:00" --salida viga-voladizo/solucion/lab_martes.docx
```

Genera el taller completo (tablas, gráfico, cálculos, comparación y conclusión) y redacta los juicios según los resultados: si el error es alto, si la hipótesis se confirma, si se respetan las pequeñas deformaciones, etc. Opciones: `--material` (acero, acero_inoxidable, aluminio, laton, cobre) o `--Y-teorico` en Pa; máximo 10 mediciones (filas de la Tabla 2).

## Uso del agente

En Claude Code, dentro de este repositorio:

```
> Usa el agente revisor-viga-voladizo para corregir talleres/grupo1.docx
> Revisa con revisor-viga-voladizo todos los .docx de la carpeta entregas/ y dame una tabla resumen con notas
```

El agente extrae cada taller, recalcula con `verificar_calculos.py`, puntúa ítem por ítem con la pauta y entrega:

- **El taller corregido** (`<taller>_CORREGIDO.pdf`): el mismo documento del grupo, con el puntaje de cada ítem en el margen, un comentario bajo cada ítem con descuento, el puntaje total y la nota en la primera página y una hoja final de resumen.
- **Un informe para el docente** (`.md`): justificación por ítem, recálculo y observaciones.

Las revisiones se guardan en `viga-voladizo/revisiones/`, carpeta excluida de git porque contiene nombres y notas.

Verificación manual de un grupo:

```bash
python3 viga-voladizo/herramientas/verificar_calculos.py --b 25 --h 0.8 --L 250 --dimensiones-en-mm \
  --masas 10 20 30 40 50 --masas-en-g --flechas 2.5 5 7.5 10 12 --flechas-en-mm
```

Requisitos: Python 3. `anotar_pdf.py` usa `pymupdf`. `verificar_calculos.py` no necesita librerías externas; `extraer_taller.py` usa `lxml` y los generadores usan `python-docx` y `matplotlib`.

## Ajustes

- Puntajes y criterios: editar `pauta/pauta_taller3.md` (y regenerar el .docx con `pauta_a_docx.py`).
- Datos de ejemplo de la solución: constante `EJEMPLO` en `herramientas/generar_solucion.py`.
