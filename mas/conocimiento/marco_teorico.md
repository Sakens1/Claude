# Marco teórico: Movimiento Armónico Simple con resorte (resumen del taller y la presentación)

Fuentes: `../fuentes/Taller_MAS_IN1090C-IN1111C_enunciado.docx` (guía y taller) y `../fuentes/Presentacion_apoyo_MAS.pptx` (presentación de apoyo, 25 diapositivas). Los datos se toman en el **laboratorio, con resortes reales**, regla y cronómetro.

## Objetivos del taller

1. Analizar el comportamiento de las variables cinemáticas (posición, velocidad y aceleración) de una partícula en MAS.
2. Determinar experimentalmente los parámetros característicos de la función de posición de una partícula en MAS y relacionarlos con las características del sistema oscilatorio.

## Parte I: ley de Hooke (estática)

- Dentro del rango elástico, la deformación es proporcional a la fuerza: **x = ΔL = L − L₀ = F/k**. El resorte ejerce F = −k·x (fuerza restauradora).
- Cuerpo en reposo colgado: k·x = m·g, con **F = m·g** (g = 9,8 m/s²).
- Gráfico pedido: **deformación (eje Y) versus fuerza (eje X)**. Es una recta por el origen con **pendiente 1/k** ⟹ **k = 1/pendiente** [N/m].
  - Si el grupo grafica F vs x, la pendiente es k directamente (el docente descuenta −2 en el gráfico por no seguir lo pedido, pero acepta el cálculo de k).
- Intercepto: idealmente ≈ 0. En resortes de estiramiento de espiras apretadas puede aparecer un intercepto negativo en x (o positivo en F) por la **tensión inicial**: el resorte no se estira hasta superar cierta fuerza. Es un comentario válido, no un error.
- Hipótesis esperada: la deformación aumenta con el peso porque el resorte debe ejercer una fuerza igual al peso; la relación es **lineal** (directamente proporcional, ley de Hooke).

## Parte II: oscilaciones (MAS)

- Ecuación del movimiento: d²y/dt² + ω²·y = 0, con solución **y(t) = A·cos(ωt + φ)**.
  - El marco teórico de la plantilla tiene dos erratas: escribe "d²y/dt² + ω² = 0" (falta la y) y la última igualdad aparece como "T² = 2π²·m/k" (debe ser **T² = (2π)²·m/k = 4π²·m/k**). No se penaliza a los grupos que las copien; sí si calculan k con un 2π² en vez de 4π².
- **ω = √(k/m)**, **f = ω/2π = (1/2π)·√(k/m)**, **T = 1/f = 2π·√(m/k)**.
- A y φ dependen de las condiciones iniciales: A = √(x₀² + v₀²/ω²), φ = arctan(−v₀/(ω·x₀)). El periodo **no depende de la amplitud** (para un resorte ideal).
- Velocidad y aceleración: v(t) = −A·ω·sen(ωt + φ), a(t) = −A·ω²·cos(ωt + φ) = −ω²·x.
- Procedimiento: tiempo de **10 oscilaciones** y T = t/10 (reduce el efecto del tiempo de reacción del cronómetro). Amplitud ≤ 5 cm.
- Gráfico pedido: **T² (eje Y) versus m (eje X)**. Recta de **pendiente 4π²/k** ⟹ **k = 4π²/pendiente** [kg/s² = N/m].
- Hipótesis esperada: al aumentar la masa el periodo aumenta (más inercia con la misma fuerza restauradora), T ∝ √m, por lo que **T² es lineal (proporcional) con m**. T vs m no es lineal (es una función potencia de exponente ½).
- Complete la frase (respuestas correctas):
  - Mismo resorte, más masa ⟹ la **frecuencia disminuye** y el **periodo aumenta**.
  - Misma masa, resorte más rígido (mayor k) ⟹ la **frecuencia aumenta** y el **periodo disminuye**.

## Masa del resorte (verificado en fuentes externas)

Un resorte real también oscila y aporta una **masa efectiva ≈ un tercio de su masa**: T = 2π·√((m + m_ef)/k), m_ef ≈ m_resorte/3. Por eso el gráfico T² vs m es una recta con la misma pendiente 4π²/k pero con **intercepto positivo** 4π²·m_ef/k, y m_ef = intercepto/pendiente.

- Fuentes: [Wikipedia, "Effective mass (spring–mass system)"](https://en.wikipedia.org/wiki/Effective_mass_(spring%E2%80%93mass_system)); [College of San Mateo, Physics 250, Lab 13 "Linear Simple Harmonic Motion"](https://collegeofsanmateo.edu/physics/docs/physics250/lab13.pdf); [Texas A&M, Simple Harmonic Motion lab manual](https://www.webassign.net/question_assets/tamucolphysmechl1/lab_6/manual.pdf).
- Consecuencias para corregir:
  - Calcular k **con la pendiente** del ajuste (con intercepto) es el método correcto y elimina el efecto de la masa del resorte.
  - Calcular k **punto a punto** con k = 4π²·m/T², o forzar el ajuste por el origen, da un k algo menor (sobre todo con masas pequeñas). No es el método pedido.
  - Atribuir el intercepto (o la diferencia entre k₁ y k₂) a la masa del resorte es un análisis correcto y valioso.

## Comparación de las dos constantes

- Diferencia porcentual: |k₁ − k₂| / k_ref · 100 (k_ref puede ser k₁, k₂ o el promedio; se acepta cualquiera si se indica).
- Criterio del docente: **hasta ~10 %** es razonable. Sobre 10 %, el grupo debe explicar causas concretas: masa del resorte, tiempo de reacción, número de oscilaciones contadas, lectura de la regla, amplitud grande u oscilaciones no verticales (péndulo), deformación permanente del resorte por sobrecarga, uso de un resorte distinto en las dos partes.
- Valores típicos de k para resortes de laboratorio: de unos pocos N/m a unos cientos de N/m.

## Errores típicos de los estudiantes

- Usar la longitud total L en vez de la deformación x = L − L₀.
- Masas en gramos o deformaciones en cm sin convertir (k sale ×10 o ×1000).
- F = m (olvidar g) o F = m·g con m en gramos.
- Tomar la pendiente de x vs F como k (en vez de 1/k).
- Informar como periodo el tiempo de 10 oscilaciones, o dividir por un número distinto.
- Graficar T vs m (curva) en vez de T² vs m, o forzar el intercepto a cero sin decirlo.
- k = pendiente/4π² o 4π²·pendiente (despeje incorrecto); usar 2π² (errata de la plantilla).
- Unidades de k mal escritas (N·m, kg/s, N/kg…).
- Gráficos sin título, sin unidades, sin ecuación o sin R², que el enunciado exige explícitamente.
- Confundir frecuencia y frecuencia angular, o decir que la frecuencia aumenta con la masa.
- Conclusión que no compara numéricamente k₁ y k₂, o que no incluye la relación algebraica del gráfico 2.

## Contenido de la presentación de apoyo

Oscilaciones y vibraciones; punto de equilibrio, elongación, amplitud, ciclo, periodo, frecuencia (Hz); MAS como movimiento periódico sin fricción con fuerza restauradora proporcional y opuesta al desplazamiento (F = −k·x); ω = 2π·f; ω = √(k/m), f = (1/2π)·√(k/m), T = 2π·√(m/k); x(t) = A·cos(ωt + φ) (o con seno), v(t) = −ω·A·sen(ωt + φ), a(t) = −ω²·A·cos(ωt + φ); relación con el movimiento circular uniforme; efecto de A, m y k sobre las curvas x(t) (al aumentar m el periodo crece; al aumentar k el periodo disminuye; A no cambia el periodo); amplitud y ángulo de fase a partir de las condiciones iniciales.
