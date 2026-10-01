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
| `herramientas/extraer_taller.py` | Extrae a texto un taller .docx/.pdf (incluida la Tabla 2 dentro del cuadro de texto) y sus imágenes. |
| `herramientas/generar_solucion.py` | Regenera la solución modelo y el gráfico. |
| `herramientas/pauta_a_docx.py` | Regenera la pauta .docx desde el .md. |
| `fuentes/` | Enunciado original del taller y guía de estudio. |

## Resultado de la solución modelo

Regla de acero, b = 25,0 mm, h = 0,80 mm, L = 250 mm, masas de 10 a 100 g:

- I = b·h³/12 = 1,07×10⁻¹² m⁴
- Ajuste: y_F = 0,02526·F + 0,00003 (R² = 0,9993)
- Y_exp = L³/(3·m·I) = 1,93×10¹¹ Pa ≈ 193 GPa, frente a 200 GPa del acero: E% = 3,4 %

Los datos son **ilustrativos**: muestran el procedimiento completo. Cada grupo se corrige con sus propios datos.

## Uso del agente

En Claude Code, dentro de este repositorio:

```
> Usa el agente revisor-viga-voladizo para corregir talleres/grupo1.docx
> Revisa con revisor-viga-voladizo todos los .docx de la carpeta entregas/ y dame una tabla resumen con notas
```

El agente extrae cada taller, recalcula con `verificar_calculos.py`, puntúa ítem por ítem con la pauta y entrega un informe con puntaje, recálculo, retroalimentación para el grupo y observaciones para el docente.

Verificación manual de un grupo:

```bash
python3 viga-voladizo/herramientas/verificar_calculos.py --b 25 --h 0.8 --L 250 --dimensiones-en-mm \
  --masas 10 20 30 40 50 --masas-en-g --flechas 2.5 5 7.5 10 12 --flechas-en-mm
```

Requisitos: Python 3. `verificar_calculos.py` no necesita librerías externas; `extraer_taller.py` usa `lxml` y los generadores usan `python-docx` y `matplotlib`.

## Ajustes

- Puntajes y criterios: editar `pauta/pauta_taller3.md` (y regenerar el .docx con `pauta_a_docx.py`).
- Datos de la solución modelo: constantes al inicio de `herramientas/generar_solucion.py`.
