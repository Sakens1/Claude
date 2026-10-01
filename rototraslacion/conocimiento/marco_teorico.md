# Marco teórico: energía en movimiento de rototraslación (resumen de la guía)

Fuente: `../fuentes/Guia_Energia_Rototraslacion.pdf` (R. Sandoval V., DMFA) y enunciado del Taller 2 (`../fuentes/Taller2_Rototraslacion_IN1090C-IN1111C_enunciado.docx`).

## Resultados de aprendizaje

De la guía:
1. Analiza la dinámica de un cuerpo como cuerpo rígido para catalogarlo como sistema conservativo o no conservativo respecto de su energía mecánica.
2. Utiliza el momento de inercia de un cuerpo para determinar su energía cinética de rotación.
3. Aplica la ley de conservación de la energía mecánica al movimiento rototraslatorio de un cuerpo rígido.
4. Aplica el modelo de cuerpo rígido cuando el cuerpo en movimiento tiene momento de inercia no despreciable.

Del taller (los que se citan en la conclusión):
- Analizar gráficamente cómo cambian las energías que contribuyen a la energía mecánica de un cuerpo rígido mientras rueda sin deslizar sobre un plano inclinado.
- Comprobar la conservación de la energía mecánica de un cuerpo rígido que rueda sin deslizar sobre un plano inclinado.

## Rodadura sin deslizamiento

- El movimiento es la suma de una traslación del centro de masa y una rotación pura en torno a él. El punto de contacto está instantáneamente en reposo: v_cm = ω·R.
- Energía cinética: K = K_rot + K_tras = ½·I_cm·ω² + ½·M·v_cm².
- Sobre el cuerpo actúan el peso, la normal y el roce **estático**. Si rueda sin deslizar, el roce estático no realiza trabajo (no hay desplazamiento en el punto de contacto), por lo que **la energía mecánica se conserva**.

## Anillo (cilindro hueco) del taller

- Momento de inercia respecto de su eje: **I = ½·M·(R_int² + R_ext²)**. Se acepta también el de aro delgado I = M·R² si el grupo justifica que el anillo es delgado, o I = ½·M·R² si se trata como cilindro macizo, pero esto último es incorrecto para un anillo.
- Rueda sobre su radio externo: ω = v/R_ext (se acepta otro radio de rodadura si el grupo lo justifica, p. ej. un riel que apoya en otro radio).
- Razón constante: **K_rot/K_tras = I/(M·R²) = (R_int² + R_ext²)/(2·R_ext²)**, entre 0,5 (cilindro macizo) y 1 (aro delgado). Fracción de la energía cinética que es rotación: β/(1 + β).
- Aceleración esperada al rodar sin deslizar: **a = g·sen θ / (1 + I/(M·R²))**, constante.

## Procedimiento del taller

1. Tabla 1: M, R_int, R_ext, I y ángulo θ del plano (con función trigonométrica, p. ej. sen θ = h₀/L o tan θ = altura/base).
2. Tabla 2: posiciones d_i y tiempos t_i (en el taller original, leídos de un video con VideoPad; en este curso los datos se obtienen de un simulador web, por lo que la exigencia en la toma de datos es baja y se acepta error humano).
3. Gráfico d vs t con **ajuste polinómico de grado 2**: d(t) = A·t² + B·t + C. Derivando: **v(t) = 2A·t + B**, a = 2A.
4. Tabla 3, para cada fila: h_i (con el ángulo; h_i = (D − d_i)·sen θ, donde D es la posición donde h = 0), v_i = v(t_i), K_rot, K_tras, K_tot, U_g = M·g·h_i, E_mec = K_tot + U_g.
5. Gráficos: K_rot y K_tras vs d (mismo gráfico); K_tot, U_g y E_mec vs d (mismo gráfico, con ajustes lineales).
6. Promedio de E_mec con su error: **σ = √(Σ (E_i − ⟨E⟩)²/N)** (desviación estándar, con N según la fórmula del taller; se acepta N − 1).
7. Conclusión: resultados de aprendizaje e hipótesis.

## Comportamiento esperado

- U_g disminuye **linealmente** con d (pendiente −M·g·sen θ).
- K_tot, K_rot y K_tras aumentan **linealmente** con d (con a constante, v² = 2·a·d si parte del reposo), con pendiente total ≈ +M·g·sen θ.
- E_mec ≈ constante (recta casi horizontal); su valor ≈ M·g·h₀ (energía potencial inicial si parte del reposo y h se mide desde abajo).
- K_rot < K_tras para un anillo (razón < 1), y ambas mantienen una razón constante.
- A la mitad del recorrido (d medio), K_tot ≈ U_g perdida hasta ese punto; si h = 0 está al final del recorrido medido, K_tot ≈ U_g ≈ E_mec/2.

## Notas para el revisor

- **Referencia de altura**: cualquier referencia es válida si el grupo la indica y la usa igual en todas las filas (desplaza U_g y E_mec en una constante). Lo importante es que E_mec sea casi constante, no su valor absoluto.
- **Datos de simulador**: no se penaliza la calidad de los datos ni la dispersión; sí el método (ajuste correcto, cálculos, unidades) y el análisis.
- **Errores típicos**:
  - Ajuste lineal de d vs t (da v constante y K constantes: incorrecto).
  - Usar t en vez de v, o v = d/t (rapidez media) en lugar de la derivada.
  - Momento de inercia con fórmula de cilindro macizo o de aro sin justificación; radios en cm o mm sin convertir.
  - ω calculado con el diámetro o con otro radio sin justificar.
  - Altura h sin usar el ángulo (h = d) o con coseno en lugar de seno.
  - Ángulo en radianes/grados mezclado en Excel (SENO de Excel usa radianes).
  - Graficar contra t en vez de contra d.
  - Desviación estándar mal calculada o sin unidades.
  - Conclusión que no menciona si E_mec se conservó ni cuantifica la variación.
