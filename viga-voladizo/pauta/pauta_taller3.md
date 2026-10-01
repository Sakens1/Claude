# Pauta de corrección: Taller 3 IN1090C, Flexión de una viga en voladizo (Módulo de Young)

Pauta para evaluar talleres resueltos por los grupos. Cada grupo tiene **sus propios datos experimentales**, por lo que no se corrige comparando contra los números de la solución modelo, sino verificando **método, coherencia interna, unidades y orden de magnitud**. La solución modelo (`../solucion/Taller3_Viga_Voladiza_RESUELTO.docx`) sirve como referencia de lo que se espera en cada ítem.

## Resumen de puntajes

| Ítem | Contenido | Puntaje |
|---|---|---|
| 1.1 | Hipótesis | 10 |
| 1.2 | Tabla 1: dimensiones b, h, L | 6 |
| 1.3 | Tabla 2: masas, fuerzas y flechas | 15 |
| 1.4 | Momento de inercia I | 8 |
| 1.5 | Gráfico y_F vs F, tendencia y ecuación | 10 |
| 1.5.1 | Interpretación de pendiente e intercepto | 8 |
| 1.5.2 | Módulo de Young experimental | 10 |
| 1.6 | Comparación con valor teórico (error %) | 8 |
| 1.7.1 | Tipos de deformación en vigas | 5 |
| 1.7.2 | Ventaja de vigas horizontales | 5 |
| 1.8 | Conclusión | 15 |
| **Total** | | **100** |

**Conversión a nota (escala chilena, exigencia 60 %)**, opcional:
- Si P ≥ 60: nota = 4,0 + 3,0·(P − 60)/40
- Si P < 60: nota = 1,0 + 3,0·P/60

## Fórmulas y valores de control

| Magnitud | Expresión | Unidad SI | Orden esperado (regla de acero escolar) |
|---|---|---|---|
| Fuerza | F_i = M_i · g, con g = 9,80 m/s² | N | 0,05 a 2 N |
| Momento de inercia | I = b·h³/12 (h = espesor, en dirección de la carga) | m⁴ | 10⁻¹³ a 10⁻¹¹ |
| Modelo | y_F = c_f · F, c_f = L³/(3·Y·I) | m/N | pendiente 10⁻³ a 10⁻¹ |
| Módulo de Young | Y = L³/(3·m·I), m = pendiente | Pa = N/m² | 10¹¹ (acero ≈ 2,0×10¹¹) |
| Error porcentual | E% = abs(Y_exp − Y_teo)/Y_teo · 100 | % | aceptable < 10 %; bueno < 5 % |

Valores teóricos aceptados: acero 190 a 210 GPa (200 GPa típico), acero inoxidable ≈ 193 GPa, aluminio ≈ 70 GPa, latón ≈ 100 GPa. Se acepta cualquier valor de tabla con fuente citada.

Herramienta de verificación: `python3 ../herramientas/verificar_calculos.py` recalcula I, pendiente, Y y E% con los datos del grupo y detecta errores de unidades (factores de 10ⁿ).

---

## Criterios por ítem

### 1.1 Hipótesis (10 pts)

Debe ser una afirmación verificable, previa al experimento, que relacione variables.

| Puntaje | Criterio |
|---|---|
| 10 | Establece que la flecha y_F es **directamente proporcional** a F (relación lineal, y_F = c_f·F) en régimen elástico/pequeñas deformaciones **y** que de la pendiente se obtendrá Y, con un valor esperado cercano al tabulado del material (p. ej. ≈ 200 GPa para acero). |
| 7 | Plantea la proporcionalidad y_F ∝ F pero no la vincula con la obtención de Y, o no menciona valor esperado. |
| 4 | Hipótesis vaga ("la regla se doblará más con más peso") sin indicar el tipo de relación. |
| 0 a 2 | No es hipótesis (es un objetivo, una descripción del procedimiento, o una pregunta), o no responde. |

Errores típicos: redactarla como objetivo ("determinar el módulo de Young…"); escribir una conclusión en vez de una hipótesis.

### 1.2 Tabla 1: dimensiones (6 pts)

| Puntaje | Criterio |
|---|---|
| 2 | b, h y L registrados con valor numérico **y unidad en metros** (la tabla pide m). |
| 2 | Valores físicamente plausibles: h ≈ 0,3 a 1,5 mm (= 0,0003 a 0,0015 m), b ≈ 10 a 35 mm, L ≈ 0,15 a 0,60 m; h < b. |
| 2 | Cifras significativas acordes al instrumento (h con micrómetro o pie de metro, al menos 2 cifras significativas; L medido desde el empotramiento al punto de carga). |

Descuentos: intercambiar b y h (−2, y se arrastra a 1.4; ver "arrastre de errores"); unidades faltantes o incorrectas (−1 a −2).

Nota: el texto del enunciado dice "ancho a, altura o espesor b", pero la Tabla 1 y la Figura 2 usan **b = ancho, h = espesor**. No se descuenta si el grupo usa cualquiera de las dos nomenclaturas de forma consistente.

### 1.3 Tabla 2: datos masa y desplazamiento (15 pts)

| Puntaje | Criterio |
|---|---|
| 4 | Al menos 8 mediciones (ideal 10) con masas distintas y crecientes. 2 pts si tiene entre 5 y 7; 0 si menos de 5. |
| 4 | Masas en **kg** y flechas en **m**, como pide el encabezado de la tabla. 2 pts si las unidades están mal declaradas pero los números son consistentes. |
| 4 | F_i = M_i·g calculado correctamente para **todas** las filas (tolerancia por usar g = 9,8 o 9,81). −1 por cada fila mal calculada (mínimo 0). |
| 3 | Flechas plausibles: crecientes con F, referencia cero en la posición sin carga, flecha máxima menor que ~15 % de L. |

### 1.4 Momento de inercia (8 pts)

| Puntaje | Criterio |
|---|---|
| 2 | Escribe la fórmula I = (1/12)·b·h³. |
| 2 | Reemplaza correctamente los datos de **su** Tabla 1 (h es el espesor, elevado al cubo). |
| 3 | Resultado numérico correcto (tolerancia ±3 %) con su cálculo verificable. |
| 1 | Unidad correcta (m⁴) y notación científica adecuada. |

Errores típicos: elevar al cubo el ancho (I sale ~10³ veces mayor); usar mm sin convertir (I en mm⁴ presentado como m⁴, factor 10¹²); confundir con el momento de inercia de masa.

### 1.5 Gráfico y_F vs F (10 pts)

| Puntaje | Criterio |
|---|---|
| 2 | Gráfico de dispersión con F en el eje X y y_F en el eje Y (no al revés). |
| 2 | Ejes rotulados con magnitud y unidad; título o leyenda. |
| 3 | Línea de tendencia lineal trazada con su ecuación visible. |
| 2 | Ecuación coherente con los datos de la Tabla 2 (la pendiente recalculada coincide ±3 %). |
| 1 | Informa R² o comenta la calidad del ajuste. |

Si el grupo grafica F vs y_F (ejes invertidos), la pendiente obtenida es 1/c_f (rigidez k). Descontar 2 pts aquí; si luego en 1.5.2 usa correctamente Y = k·L³/(3I), no descontar de nuevo.

### 1.5.1 Significado de los parámetros (8 pts)

| Puntaje | Criterio |
|---|---|
| 4 | Identifica la **pendiente** como la constante de flexibilidad c_f = L³/(3YI), con unidad m/N. |
| 2 | La asocia a las variables L, I (b, h) e Y (geometría y material). |
| 2 | Interpreta el **intercepto** como la flecha con F = 0, que idealmente es cero (error de cero o de lectura si no lo es). |

Respuesta a "¿la podemos asociar a alguna variable?": sí, a L, I y especialmente a Y, que es la incógnita.

### 1.5.2 Módulo de Young experimental (10 pts)

| Puntaje | Criterio |
|---|---|
| 3 | Despeja correctamente Y = L³/(3·m·I) a partir de m = c_f. |
| 2 | Reemplaza con **su** pendiente, **su** L y **su** I. |
| 4 | Resultado numérico correcto (±3 % del recálculo). |
| 1 | Unidad correcta (Pa o N/m², o GPa con conversión correcta). |

Si el resultado está fuera de 10¹⁰ a 5×10¹¹ Pa, revisar unidades: casi siempre hay mm sin convertir. Aplicar arrastre de errores (ver abajo).

### 1.6 Comparación con valor teórico (8 pts)

| Puntaje | Criterio |
|---|---|
| 2 | Indica un valor teórico pertinente al material (acero ≈ 200 GPa) **con fuente** (libro, tabla o página web). 1 pt sin fuente. |
| 3 | Calcula correctamente el error porcentual con su Y experimental. |
| 3 | Analiza la discrepancia: identifica fuentes de error concretas (medición de h por su dependencia cúbica, definición de L, empotramiento no rígido, paralaje, grandes deflexiones) y/o juzga si el resultado es aceptable. |

No se penaliza un error porcentual alto si está bien calculado y analizado; se penaliza no analizarlo.

### 1.7.1 Tipos de deformación (5 pts)

| Puntaje | Criterio |
|---|---|
| 3 | Menciona al menos tres: flexión, corte/cizalle, axial (tracción/compresión), torsión (o pandeo). 1 pt por cada una, máximo 3. |
| 2 | Indica que la **flexión** es la más común (cargas perpendiculares al eje), acompañada del esfuerzo cortante. |

### 1.7.2 Ventaja de la disposición horizontal (5 pts)

| Puntaje | Criterio |
|---|---|
| 3 | Explica que, en horizontal, las cargas (peso) actúan perpendiculares al eje, la viga trabaja a flexión y transmite las cargas a apoyos/columnas, permitiendo cubrir luces y crear espacios libres (pisos, techos, puentes, balcones, voladizos). |
| 2 | Agrega una idea de eficiencia: orientar la mayor dimensión de la sección en la dirección de la carga maximiza I ∝ h³ y la rigidez; o da ejemplos de ingeniería/arquitectura pertinentes. |

### 1.8 Conclusión (15 pts)

La pauta del enunciado exige referirse a: resultado de aprendizaje, hipótesis y análisis de datos.

| Puntaje | Criterio |
|---|---|
| 4 | **Resultado de aprendizaje**: informa el valor de Y obtenido (con unidad) y si se logró determinarlo. |
| 4 | **Hipótesis**: dice explícitamente si se confirma o rechaza, apoyado en la linealidad del gráfico (R², intercepto ≈ 0). |
| 4 | **Análisis de datos**: comenta el error porcentual, sus causas principales y su efecto en el resultado. |
| 3 | Calidad: propone mejoras al procedimiento o menciona la validez/limitaciones del modelo; redacción clara, sin contradicciones con los resultados informados. |

Una conclusión que solo resume el procedimiento ("medimos la regla, colgamos masas…") obtiene como máximo 4 pts.

---

## Reglas generales

1. **Arrastre de errores (consecuencia de error previo)**: si un error en un ítem anterior (p. ej. I mal calculado) se propaga, los ítems posteriores se corrigen con el valor erróneo del grupo. Si el procedimiento posterior es correcto con ese valor, se otorga el puntaje del procedimiento y solo se descuenta el resultado numérico (máximo un descuento por el mismo error).
2. **Unidades**: un resultado sin unidad pierde el punto de unidad del ítem. Un error de conversión (mm a m, g a kg) se descuenta una vez donde se origina y luego se aplica arrastre.
3. **Tolerancias numéricas**: ±3 % frente al recálculo con los datos del grupo (cubre redondeos y g = 9,8/9,81).
4. **Coherencia interna**: los valores informados en distintos ítems deben coincidir entre sí (la pendiente de 1.5 es la que se usa en 1.5.2; el Y de 1.5.2 es el de 1.6 y 1.8).
5. **Datos sospechosos**: si los datos son "demasiado perfectos" (R² = 1,0000 con flechas que no respetan la resolución del instrumento) o copiados de otro grupo, no se descuenta automáticamente: se reporta al docente como observación.
6. **Respuestas parciales**: se otorga puntaje parcial proporcional según los criterios de cada tabla. No hay puntaje negativo.

## Formato del informe de revisión

Para cada taller el revisor entrega:

1. Identificación del grupo/integrantes y archivo revisado.
2. Tabla de puntajes por ítem (obtenido / máximo) con justificación breve por ítem.
3. Recálculo: tabla con los valores informados por el grupo vs recalculados (I, pendiente, Y, E%), indicando coincidencia.
4. Errores detectados (conceptuales, de cálculo, de unidades) y comentarios de retroalimentación para los estudiantes, en tono formativo.
5. Puntaje total y nota (si se pide).
6. Observaciones para el docente (casos dudosos, datos sospechosos, criterios que requieren su decisión).
