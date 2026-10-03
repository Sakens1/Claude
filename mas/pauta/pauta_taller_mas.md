# Pauta de corrección: Taller de Movimiento Armónico Simple (IN1090C/IN1111C)

Pauta para evaluar talleres resueltos por los grupos. Cada grupo tiene **sus propios datos** (resortes reales, regla y cronómetro), por lo que no se corrige comparando contra los números de la solución modelo (`../solucion/Taller_MAS_RESUELTO.docx`), sino verificando **método, coherencia interna, unidades y análisis**.

**Criterio del docente (actualizado tras el primer lote): pauta estricta en método, gráficos y análisis.** Se tolera el error humano propio de las mediciones (tiempo de reacción, lectura de la regla), pero **se descuenta**:
- inventar o agregar puntos que no son mediciones (por ejemplo una fila o un punto (0,0));
- un ajuste o gráfico que no representa los datos (puntos que no siguen la recta por un error de método, escalas o ejes mal leídos);
- un análisis que no reconoce o contradice lo que muestran sus propios datos (llamar "clara tendencia recta" a un ajuste con R² = 0,87, no comentar un intercepto grande, decir "cercanas" a constantes que difieren más de 10 %).

**Cada punto otorgado debe estar respaldado por algo escrito o visible en el taller.** Ante la duda no se completa lo que el grupo no escribió.

## Resumen de puntajes

| Id (para el JSON) | Ítem del taller | Pts |
|---|---|---|
| Hipótesis P1 | Parte I, A: hipótesis | 6 |
| Tabla 1 | Parte I, B: tabla de datos | 6 |
| Gráfico 1 | Parte I, B: gráfico deformación vs fuerza | 10 |
| k parte 1 | Parte I, C: constante elástica | 6 |
| Análisis P1 | Parte I, C: ¿datos acordes a lo esperado? | 6 |
| Hipótesis P2 | Parte II, A: hipótesis | 10 |
| Tabla 2 | Parte II, B: tabla de datos | 8 |
| Gráfico 2 | Parte II, B: gráfico T² vs m | 10 |
| k parte 2 | Parte II, C: constante elástica | 10 |
| Complete la frase | Parte II, C: complete la frase | 8 |
| Conclusión P2 | Conclusión parte 2 | 20 |
| **Total** | | **100** |

**Conversión a nota (escala chilena, exigencia 60 %):** P ≥ 60: nota = 4,0 + 3,0·(P − 60)/40; P < 60: nota = 1,0 + 3,0·P/60. Se redondea a un decimal (0,05 hacia arriba).

## Fórmulas de control

| Magnitud | Expresión |
|---|---|
| Fuerza | F = m·g (g = 9,8 m/s²; se acepta 9,81) |
| Deformación | x = L − L₀ |
| Parte I | x = F/k ⟹ pendiente de x vs F = 1/k ⟹ **k₁ = 1/pendiente** |
| Periodo | T = t₁₀/10 |
| Parte II | T² = (4π²/k)·m ⟹ pendiente de T² vs m = 4π²/k ⟹ **k₂ = 4π²/pendiente** |
| Masa del resorte | intercepto de T² vs m = 4π²·m_ef/k, con m_ef ≈ m_resorte/3 |
| Comparación | diferencia % = abs(k₁ − k₂)/k_ref·100 (razonable hasta ~10 %) |

Herramienta: `python3 ../herramientas/verificar_mas.py` recalcula todo con los datos del grupo (tolerancia ±5 %).

---

## Criterios por ítem

### Hipótesis P1 (6 pts)

| Pts | Criterio |
|---|---|
| 3 | La deformación **aumenta** al aumentar el peso, con un **porqué** (el resorte ejerce una fuerza igual al peso; ley de Hooke). 1 si solo dice que aumenta sin justificar. |
| 3 | La relación es **lineal / directamente proporcional**, justificada con la ley de Hooke (x = F/k, k constante en el rango elástico). 1 si dice "lineal" sin justificar. 0 si dice otra forma. |

### Tabla 1 (6 pts)

| Pts | Criterio |
|---|---|
| 2 | Al menos 5 **mediciones reales** con masas distintas (la plantilla tiene 6). Una fila (0, 0, 0) agregada no es una medición: no cuenta y descuenta 1. 1 si quedan 3 o 4 mediciones. |
| 2 | F = m·g correcto en todas las filas (masa en kg). −1 por fila mal (mínimo 0). |
| 2 | Deformación x (no la longitud total) en metros, coherente con la regla. 1 si está en cm/mm con la unidad indicada; 0 si usa la longitud total sin restar L₀. |

### Gráfico 1 (10 pts)

El enunciado exige: gráfico de dispersión, título, títulos de ejes con unidades, línea de tendencia, ecuación y R².

| Pts | Criterio |
|---|---|
| 2 | Dispersión con **x en el eje Y y F en el eje X** (lo pedido). Si está invertido (F vs x): 0 en este criterio (−2, criterio del docente) y no se descuenta en k si lo calcula bien con su gráfico. |
| 1 | Título del gráfico. |
| 2 | Títulos de ejes con unidades (1 si faltan las unidades). |
| 2 | Línea de tendencia lineal con su ecuación y R² visibles (1 si falta uno de los dos). |
| 3 | **El ajuste representa los datos medidos**: solo puntos medidos (sin puntos inventados como (0,0)), los puntos siguen la recta y la ecuación corresponde a esos datos. 0 si se agregó un punto que no es medición y altera la recta, o si la recta no representa los datos por un error de método. 1–2 si hay un problema menor (un punto mal graficado, escala que dificulta la lectura). |

### k parte 1 (6 pts)

| Pts | Criterio |
|---|---|
| 2 | Relaciona la pendiente con k: pendiente = 1/k (o = k si graficó F vs x). |
| 3 | Valor de k₁ correcto con **su** pendiente (±5 %). 1 si el procedimiento es correcto pero hay error de cálculo o de unidades. 0 si usa la pendiente de x vs F como k. |
| 1 | Unidad correcta (N/m). |

### Análisis P1 (6 pts)

| Pts | Criterio |
|---|---|
| 3 | Juzga si los datos son acordes a lo esperado con un criterio **coherente con sus datos**: linealidad (R²) y relación con la ley de Hooke o la hipótesis. Si el intercepto o un punto se apartan claramente (por ejemplo intercepto mayor al 10 % de la deformación máxima, R² < 0,98), debe reconocerlo y explicarlo (p. ej. tensión inicial del resorte): 1 si no lo comenta. 0 si el juicio contradice los datos ("clara tendencia recta" con R² = 0,87). |
| 3 | Incluye la **relación algebraica** obtenida del gráfico 1 (p. ej. x = 0,0397·F + 0,0004, o F = k·x con su valor). 1 si la menciona sin números. |

### Hipótesis P2 (10 pts)

| Pts | Criterio |
|---|---|
| 5 | El periodo **aumenta** al aumentar la masa, con un porqué (más inercia, misma fuerza restauradora; o T = 2π·√(m/k)). 2 si solo dice que aumenta. |
| 5 | **T² depende linealmente** (directamente proporcional) de m, justificado con T² = 4π²·m/k. 2 si dice lineal sin justificar. 0 si dice que T es lineal con m o propone otra forma para T². |

### Tabla 2 (8 pts)

| Pts | Criterio |
|---|---|
| 2 | Al menos 6 **mediciones reales** con masas distintas (la plantilla tiene 8). Una fila (0, 0, 0) agregada no es una medición (con masa cero el resorte también oscila): no cuenta y descuenta 1. 1 si quedan 4 o 5 mediciones. |
| 2 | Tiempo de 10 oscilaciones registrado. |
| 2 | T = t/10 correcto en todas las filas. |
| 2 | T² correcto en todas las filas, con unidades (s²). |

### Gráfico 2 (10 pts)

| Pts | Criterio |
|---|---|
| 2 | Dispersión de **T² (eje Y) vs m (eje X)**. Si grafica T vs m: 0 aquí y se aplica arrastre en k. Si los ejes están invertidos (m vs T²): 0 aquí, sin descuento en k si lo calcula bien. |
| 1 | Título. |
| 2 | Títulos de ejes con unidades (1 si faltan unidades). |
| 2 | Línea de tendencia lineal con ecuación y R² visibles (1 si falta uno de los dos). |
| 3 | **El ajuste representa los datos medidos**: sin puntos inventados (como (0,0)), los puntos siguen la recta y la ecuación corresponde a esos datos. 0 si se agregó un punto que no es medición y altera la recta o el intercepto, o si la recta no representa los datos por un error de método. 1–2 si hay un problema menor. |

### k parte 2 (10 pts)

| Pts | Criterio |
|---|---|
| 3 | Relaciona la pendiente con k: pendiente = 4π²/k (o la equivalente si invirtió ejes). |
| 5 | Valor de k₂ correcto con **su** pendiente (±5 %). 2 si el procedimiento es correcto con error de cálculo. 0 si usa 2π² en vez de 4π², o un despeje incorrecto. Calcular k punto a punto (4π²·m/T²) y promediar en vez de usar la pendiente: 2. |
| 2 | Unidad correcta (N/m o kg/s²). |

### Complete la frase (8 pts)

2 pts por cada respuesta correcta: más masa ⟹ frecuencia **disminuye**, periodo **aumenta**; mayor rigidez ⟹ frecuencia **aumenta**, periodo **disminuye**.

### Conclusión P2 (20 pts)

| Pts | Criterio |
|---|---|
| 5 | ¿Gráfico 2 acorde a lo esperado? Lo juzga con criterio (linealidad de T² con m, R²) y lo relaciona con la hipótesis. |
| 4 | Incluye la **relación algebraica** del gráfico 2 (T² = a·m + b con sus valores). 1 si la menciona sin números. |
| 6 | **Compara k₁ y k₂ numéricamente**: diferencia porcentual (3) y juicio de si son consistentes (3). Si la diferencia supera ~10 %, el juicio exige explicar causas concretas. |
| 5 | Justifica con causas concretas y coherentes con sus datos: masa del resorte / intercepto, tiempo de reacción, lectura de la regla, amplitud, etc. (no solo "errores experimentales"). |

---

## Reglas generales

1. **Arrastre de errores**: un error se descuenta donde se origina; los ítems siguientes se corrigen con los valores del grupo (si el método posterior es correcto, se otorga su puntaje).
2. **Unidades**: un resultado sin unidad pierde el punto de unidad del ítem; una conversión errada (g, cm, mm) se descuenta una vez.
3. **Tolerancia** ±5 % frente al recálculo.
4. **Erratas de la plantilla** (d²y/dt² + ω² = 0; T² = 2π²·m/k): no se descuentan si solo se copian; sí si se usan para calcular mal k.
5. **Datos**: se tolera la dispersión propia de las mediciones, pero se descuentan los puntos inventados, los ajustes que no representan los datos y los análisis que no reconocen o contradicen lo que muestran sus propios datos.
8. **Sin crédito por suposición**: cada punto otorgado debe estar respaldado por lo escrito o graficado. No se completa lo que el grupo no escribió ni se da el beneficio de la duda en lo conceptual.
6. **Coherencia interna**: tablas, gráficos y respuestas deben coincidir entre sí.
7. **Datos sospechosos** o copiados: no se descuenta automáticamente; se informa al docente.

## Criterios homologados (decididos al corregir el primer lote)

| Situación | Criterio |
|---|---|
| Conclusión P2: compara k₁ y k₂ con sus valores numéricos pero sin calcular la diferencia porcentual | 1/3 en el criterio de diferencia porcentual. |
| Conclusión P2: juicio de consistencia | 3 = juicio explícito y correcto respecto del ~10 % (una diferencia de 10–11 % se considera dentro); 2 = juicio vago ("del mismo orden"); 0 = sin juicio o contradictorio con los datos (p. ej. "cercanas" con ~18 % de diferencia). |
| Conclusión P2: causas | 5 = dos o más causas concretas ligadas a sus datos (puntos que se alejan de la recta, intercepto, masa del resorte, tensión inicial); 4 = dos o más causas concretas de la lista, sin ligarlas a sus datos; 3 = una causa concreta ligada a sus datos, o una coherente y otra que contradice sus datos; 2 = una causa concreta sin ligar; 0 = solo "errores experimentales / de medición". |
| Relación algebraica pedida en un ítem pero escrita solo en otro (o solo en el gráfico) | 1 pt en ese criterio ("la menciona sin números"). |
| Análisis P1 sin comentar un intercepto grande del gráfico 1 | Reemplazado por el criterio estricto: 1/3 en el juicio si no lo comenta (el intercepto puede deberse a la tensión inicial del resorte, y eso es lo que debe explicar). |
| Un valor de F mal copiado en la Tabla 1 que no afecta al gráfico | −1 por fila, como dice la pauta. |
| Punto (0,0) agregado a las tablas o gráficos | Reemplazado por el criterio estricto: −1 en la tabla y 0/3 en "el ajuste representa los datos" del gráfico si altera la recta. k se corrige con su pendiente (arrastre). |
| k₂ correcto sin escribir la relación pendiente = 4π²/k | 1/3 en ese criterio. |
| Punto (0,0) agregado al gráfico 2 que casi no cambia la pendiente pero sí el intercepto o el R² | 0/3 en "el ajuste representa los datos", igual que en el gráfico 1 (lectura literal de la pauta). |
| Análisis P1: afirma proporcionalidad o "como dice la ley de Hooke" sin comentar un intercepto grande | 1/3 en el juicio (la omisión del intercepto ya es el descuento). 0/3 se reserva para un juicio de linealidad que contradice el R² ("clara tendencia recta" con R² = 0,87). |
| Conclusión P2: juicio del gráfico 2 que no reconoce lo que muestran sus datos | −2 por cada aspecto no reconocido: R² < 0,98; intercepto (positivo o negativo) mayor al 10 % del T² máximo. Bajo esos umbrales no se descuenta en el juicio. |

## Formato del informe de revisión

1. Identificación del grupo y archivo.
2. Tabla de puntajes por ítem con justificación.
3. Recálculo: informado vs recalculado (pendientes, k₁, k₂, diferencia %, masa efectiva del resorte).
4. Retroalimentación para el grupo.
5. Puntaje total y nota.
6. Observaciones para el docente (incluye fuentes web consultadas, si las hubo).
