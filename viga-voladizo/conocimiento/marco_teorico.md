# Marco teórico: viga en voladizo (resumen de la guía de estudio)

Fuente: `../fuentes/Guia_de_estudio_Viga_en_Voladizo.pdf` (A. Inostroza S.), complementada con notas para la corrección.

## Conceptos

- **Viga**: elemento estructural alargado, de sección recta constante, que soporta cargas en distintos puntos de su longitud. Con cargas perpendiculares al eje se producen esfuerzo cortante y momento flector; con cargas no perpendiculares aparecen además esfuerzos axiales. La principal deformación es la **flexión**.
- **Tipos de carga**: concentradas (F), distribuidas (P, carga por unidad de longitud) y pares o momentos concentrados (M).
- **Clasificación por vínculos**: apoyada (doblemente apoyada), apoyada y empotrada, **en voladizo**, empotrada (doblemente empotrada), con múltiples apoyos. La distancia entre soportes es la **luz** de la viga.
- **Viga en voladizo**: apoyada rígidamente (empotrada) en un extremo, donde aparecen reacciones en x, y y un momento de empotramiento; el otro extremo está libre. Ejemplos: estanterías cantilever, balcones/edificios en voladizo, puentes construidos por avance en voladizo.
- **Elástica**: curva que describe la deformación del eje neutro de la viga.

## Condiciones (supuestos) del modelo

1. La viga es recta.
2. La sección transversal es uniforme.
3. Las cargas actúan perpendiculares al eje.
4. La viga casi no se tuerce.
5. Material homogéneo, con igual módulo de elasticidad en tracción y compresión.
6. Longitud mucho mayor que las dimensiones de la sección.
7. Deformación por peso propio despreciable.
8. Solo para vigas linealmente elásticas con pendientes pequeñas.

El taller agrega: la sección no cambia al doblarse (espesor pequeño frente al radio de curvatura).

## Método área-momento

- Ángulo entre tangentes: θ_B/A = θ_B − θ_A.
- dθ = ds/ρ; con pendientes pequeñas ds ≈ dx; y 1/ρ = M/(YI), luego dθ = M dx/(YI).
- Para voladizo con carga P en el extremo libre, el diagrama M/(YI) es un triángulo de altura −PL/(YI):
  - Rotación en el extremo: θ_B = A = −PL²/(2YI) (θ_A = 0 por el empotramiento).
  - Flecha: t_B/A = x̄·A = (−PL²/(2YI))·(2L/3) = −PL³/(3YI).

## Resultado que usa el taller

- Flecha del extremo libre: **y_F = c_f·F**, proporcional a F para pequeñas deformaciones.
- Constante de flexibilidad: **c_f = L³/(3·Y·I)** [m/N].
- Momento de inercia (área) de sección rectangular respecto al eje neutro que pasa por el centro de gravedad: **I = b·h³/12**, b = ancho, h = espesor (dimensión en la dirección de la carga).
- Por lo tanto, la pendiente m del gráfico y_F vs F permite obtener **Y = L³/(3·m·I)**.

Notación: la guía usa **Y** para el módulo de Young (en la imagen de área-momento aparece como E). Ambas se aceptan.

## Notas para el revisor

- **Sensibilidad**: ΔY/Y = 3ΔL/L + 3Δh/h + Δb/b + Δm/m. El espesor h es la medición crítica: 1 % de error en h produce 3 % en Y.
- **Empotramiento real**: si la mordaza permite girar, la flecha medida aumenta y Y se subestima.
- **Grandes deflexiones**: si y_F supera ~10 a 15 % de L, la relación deja de ser lineal (la curva se "aplana" en los últimos puntos).
- La guía titula "flexión pura" a esta sección; estrictamente, con carga puntual en el extremo hay también cortante (flexión no uniforme). No se penaliza a estudiantes que usen el término de la guía.
- Valores de referencia de Y: acero 190 a 210 GPa; acero inoxidable ≈ 193 GPa; aluminio ≈ 69 a 70 GPa; latón ≈ 100 GPa; cobre ≈ 110 a 130 GPa.
- Deformaciones en vigas: flexión (la más común), corte, axial (tracción/compresión, pandeo) y torsión.
