# Pauta de corrección: Taller 2 IN1090C/IN1111C, Conservación de la energía en movimiento de rototraslación

Pauta para evaluar talleres resueltos por los grupos. Cada grupo tiene **sus propios datos** (obtenidos en un simulador web), por lo que no se corrige comparando contra los números de la solución modelo, sino verificando **método, coherencia interna, unidades y análisis**. La solución modelo (`../solucion/Taller2_Rototraslacion_RESUELTO.docx`) muestra el nivel esperado en cada ítem.

**Criterio del docente sobre los datos:** la exigencia en la toma de datos es baja. Se considera el error humano: no se descuenta por dispersión de los datos, por una energía mecánica que no sea perfectamente constante ni por la cantidad de puntos (salvo que sean tan pocos que impidan el análisis, menos de 5). Se evalúa el método, los cálculos y que el análisis sea coherente con los propios datos.

## Resumen de puntajes

| Id (para el JSON) | Ítem del taller | Puntaje |
|---|---|---|
| d(t) | Gráfico posición-tiempo y ecuación d(t) | 10 |
| Tabla 3 | Tabla 3 de energías (hoja de cálculo) | 10 |
| Hipótesis | Hipótesis | 5 |
| KRot y KTras | Gráfico K_Rot y K_Tras vs d, e inferencia | 20 |
| KTot, Ug y Emec | Gráfico K_Tot, U_g y E_mec vs d, ajustes y preguntas | 25 |
| Promedio Emec | Promedio de E_mec con su error | 10 |
| Conclusión | Conclusión | 20 |
| **Total** | | **100** |

Las Tablas 1 y 2 no tienen puntaje propio: sus errores (por ejemplo, el momento de inercia o el ángulo) se descuentan donde afectan, en la Tabla 3, y luego se aplica arrastre.

**Conversión a nota (escala chilena, exigencia 60 %)**:
- Si P ≥ 60: nota = 4,0 + 3,0·(P − 60)/40
- Si P < 60: nota = 1,0 + 3,0·P/60

## Fórmulas de control

| Magnitud | Expresión |
|---|---|
| Momento de inercia del anillo | I = ½·M·(R_int² + R_ext²) |
| Ángulo del plano | con función trigonométrica, p. ej. sen θ = h₀/L |
| Posición | d(t) = A·t² + B·t + C (polinomio de grado 2) |
| Rapidez | v(t) = 2A·t + B (derivada de d(t)) |
| Altura | h_i = (D − d_i)·sen θ (D: posición donde h = 0, cualquier referencia consistente) |
| Energías | K_Rot = ½·I·(v/R)², K_Tras = ½·M·v², K_Tot = K_Rot + K_Tras, U_g = M·g·h, E_mec = K_Tot + U_g |
| Promedio y error | ⟨E⟩ = ΣE_i/N, σ = √(Σ(E_i − ⟨E⟩)²/N) (se acepta N − 1) |

Herramienta: `python3 ../herramientas/verificar_energia.py` recalcula todo con los datos del grupo (tolerancia ±5 %).

---

## Criterios por ítem

### d(t): gráfico posición-tiempo (10 pts)

| Puntaje | Criterio |
|---|---|
| 3 | Gráfico de dispersión con t en el eje X y d en el eje Y, ejes rotulados con magnitud y unidad. |
| 4 | Línea de tendencia **polinómica de grado 2**. Un ajuste lineal u otro tipo: 0 en este criterio (y se aplica arrastre en la Tabla 3: el método posterior se corrige con su ajuste). |
| 3 | Ecuación d(t) escrita con sus coeficientes y coherente con los datos de la Tabla 2 (±5 % en el coeficiente de t²). 2 pts si falta escribirla fuera del gráfico o sin unidades, pero es visible en el gráfico. |

### Tabla 3 (10 pts)

Se revisan dos o tres filas con el verificador.

| Puntaje | Criterio |
|---|---|
| 2 | Alturas h_i calculadas con el ángulo (seno) y con una referencia consistente. |
| 2 | Rapidez v_i calculada con la derivada v(t) = 2A·t + B (no con d/t). |
| 2 | K_Rot con el momento de inercia del anillo y ω = v/R (I de la Tabla 1 correcto; si I está mal, −1 aquí y arrastre). |
| 2 | K_Tras y K_Tot correctos. |
| 2 | U_g y E_mec correctos, con unidades (J). |

Tolerancia ±5 %. Un mismo error (p. ej. radio en cm) se descuenta una vez.

### Hipótesis (5 pts)

| Puntaje | Criterio |
|---|---|
| 3 | Predice el comportamiento de las energías al descender: U_g disminuye, K_Rot y K_Tras aumentan y la energía mecánica se mantiene constante. |
| 2 | Fundamentación científica: rueda sin deslizar, el roce estático no realiza trabajo / solo trabaja el peso (fuerza conservativa). |

Si solo dice "la energía mecánica se conserva" sin describir las energías ni fundamentar: 2/5. Si es un objetivo o un procedimiento: 0 a 1.

### KRot y KTras: gráfico e inferencia (20 pts)

| Puntaje | Criterio |
|---|---|
| 6 | Ambas series en **un mismo gráfico** vs d (no vs t), ejes rotulados con unidades y leyenda que distinga las curvas. 3 pts si están en gráficos separados o falta leyenda/unidades. |
| 4 | Valores coherentes con la Tabla 3. |
| 10 | **Inferencia**: ambas aumentan al descender (aprox. linealmente con d) (3); la de traslación es mayor que la de rotación (2); la razón entre ellas es constante e igual a I/(M·R²), o se reconoce que una parte fija de la energía cinética es de rotación (3); relación con el modelo de cuerpo rígido: con momento de inercia no despreciable, la rotación no se puede ignorar (2). |

### KTot, Ug y Emec: gráfico, ajustes y preguntas (25 pts)

| Puntaje | Criterio |
|---|---|
| 6 | Las tres series en un gráfico común vs d, con ejes rotulados, unidades y leyenda. |
| 4 | Ajustes pertinentes (lineales) con sus ecuaciones. 2 pts si los ajustes no son lineales o faltan ecuaciones. |
| 5 | Responde el valor de la **energía mecánica total** (con unidad), coherente con sus datos (promedio, valor inicial o intercepto del ajuste de E_mec). |
| 5 | Responde **K_Tot y U_g a la mitad del recorrido** (con unidad), coherentes con sus datos o ajustes. 3 pts si solo da uno de los dos. |
| 5 | Análisis: K_Tot aumenta y U_g disminuye en la misma medida, por lo que E_mec queda casi constante; comenta la variación de E_mec (sin exigir que sea cero). |

### Promedio Emec (10 pts)

| Puntaje | Criterio |
|---|---|
| 4 | Promedio ⟨E⟩ correcto con sus datos (±5 %). |
| 4 | Error σ con la fórmula del taller (desviación estándar; se acepta N − 1). Si usa otra medida (p. ej. diferencia máx − mín) bien calculada: 2. |
| 2 | Resultado expresado como E = (⟨E⟩ ± σ) con unidad (J) y cifras coherentes entre valor y error. |

### Conclusión (20 pts)

| Puntaje | Criterio |
|---|---|
| 8 | Se refiere a los **resultados de aprendizaje**: cómo cambian las energías (análisis gráfico) (4) y si se comprobó la conservación de la energía mecánica, usando el momento de inercia / modelo de cuerpo rígido (4). |
| 6 | **Hipótesis**: dice explícitamente si se confirma o no y con qué criterio (p. ej. σ pequeño frente al promedio, pendiente casi nula de E_mec). |
| 6 | **Análisis de datos**: cuantifica la variación de E_mec (σ o %), menciona posibles causas (lectura de posiciones y tiempos, roce de rodadura, deslizamiento) y es coherente con sus resultados. |

Una conclusión que solo resume el procedimiento obtiene como máximo 6 pts.

---

## Reglas generales

1. **Arrastre de errores**: un error que se propaga (ajuste lineal, I o radio mal calculado, ángulo mal calculado) se descuenta donde se origina. Los ítems siguientes se corrigen con los valores del grupo; si el método posterior es correcto, se otorga su puntaje.
2. **Unidades**: un resultado sin unidad pierde el punto de unidad del ítem. Una conversión errada (cm, mm, g) se descuenta una vez.
3. **Tolerancia** ±5 % frente al recálculo.
4. **Referencia de altura**: cualquiera, si se indica y se usa igual en todas las filas.
5. **Datos**: no se descuenta por dispersión ni por que E_mec no sea exactamente constante (simulador, error humano). Sí se descuenta si el análisis contradice los propios datos.
6. **Coherencia interna**: los valores de las tablas, los gráficos y las respuestas deben coincidir entre sí.
7. **Datos sospechosos** o copiados: no se descuenta automáticamente; se informa al docente.

## Criterios homologados (decididos al corregir el primer lote)

| Situación | Criterio |
|---|---|
| Rapidez calculada como v = 2·d/t (o d/t) en vez de derivar d(t) | 0/2 en el criterio de rapidez de la Tabla 3 (confirmado por el docente: el taller pide derivar). Los ítems siguientes se corrigen con sus valores. |
| d(t): datos bien ubicados pero rótulos de los ejes intercambiados | 2/3 en el criterio del gráfico. |
| d(t): ejes invertidos (t en el eje Y) | 1/3 en el criterio del gráfico; si la ecuación es t(d) y no d(t), 0/3 en la ecuación. |
| Ecuación escrita sin unidades o con "x" en vez de t | 2/3 en el criterio de la ecuación (un solo descuento aunque falten ambas cosas). |
| Gráfico sin leyenda y/o sin unidades en los ejes | Mitad del criterio del gráfico (3/6). |
| Eje X del gráfico de energías con el número de medición en vez de d | 4/6 en el criterio del gráfico. |
| Gráfico de K_Tot, U_g y E_mec sin ninguna línea de tendencia | 0/4 en ajustes (el parcial de 2 es para ajustes no lineales o sin ecuación). |
| Promedio y error con distinto número de decimales | 1/2 en el criterio de expresión del resultado. |
| Altura medida hacia abajo desde el inicio (U_g crece al bajar) | 1/2 en el criterio de alturas; el análisis que no lo detecta se descuenta en el ítem de energías. |
| Nota | Se redondea a un decimal hacia arriba desde 0,05 (5,35 → 5,4). |

## Formato del informe de revisión

1. Identificación del grupo y archivo.
2. Tabla de puntajes por ítem con justificación.
3. Recálculo: informado vs recalculado (I, coeficientes de d(t), ⟨E⟩, σ y algunas filas de la Tabla 3).
4. Retroalimentación para el grupo.
5. Puntaje total y nota.
6. Observaciones para el docente.
