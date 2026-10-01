# Revisores de talleres de laboratorio de Física (IN1090C / IN1111C)

Agentes de Claude Code que corrigen talleres de laboratorio resueltos por los estudiantes: aplican la pauta del docente, recalculan los resultados con los datos de cada grupo y entregan el taller corregido (copia exacta del PDF del grupo con puntaje y comentarios por ítem) más un informe para el docente.

| Taller | Agente | Carpeta |
|---|---|---|
| Taller 3: Flexión de una viga en voladizo (módulo de Young) | `revisor-viga-voladizo` | [`viga-voladizo/`](viga-voladizo/README.md) |
| Taller 2: Energía en movimiento de rototraslación | `revisor-rototraslacion` | [`rototraslacion/`](rototraslacion/README.md) |

Herramientas compartidas en `comun/`:

- `anotar_pdf.py`: escribe puntajes y comentarios sobre una copia exacta del PDF entregado, en los espacios en blanco de cada ítem, sin cruzar texto, imágenes, gráficos ni bordes de recuadros (los ítems se definen en el `items.json` de cada taller).
- `extraer_taller.py`: extrae a texto un taller .docx o .pdf, con sus tablas e imágenes.
- `verificar_superposicion.py`: compara el PDF corregido con el original y avisa si alguna marca tapa contenido.
- `md_a_docx.py`: convierte una pauta en Markdown a Word.
- `docx_util.py`: funciones para escribir respuestas dentro de las plantillas .docx.

Uso, en Claude Code dentro de este repositorio: `Usa el agente revisor-rototraslacion para corregir <archivo.pdf>`.

Las carpetas `*/revisiones/` están excluidas de git porque contienen nombres y notas de estudiantes.
