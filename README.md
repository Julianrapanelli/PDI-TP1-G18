# TP1 · Procesamiento de Imágenes I

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)

Trabajo Práctico N° 1 de **Procesamiento de Imágenes I (IA 4.4)**, Tecnicatura Universitaria en Inteligencia Artificial, FCEIA – Universidad Nacional de Rosario. 2° semestre 2026.

| Problema | Qué resuelve |
|---|---|
| **1. Ecualización local de histograma** | Revela detalles ocultos en zonas de una imagen donde la ecualización global no alcanza. |
| **2. Validación de planillas de calificaciones** | Lee una planilla escaneada, valida cada campo de cada registro y genera un CSV y una imagen con los alumnos que no aprobaron. |

El análisis completo está en el [informe](docs/Informe%20TP-PDI-G18.pdf).

## Contenido

- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Problema 1](#problema-1)
- [Problema 2](#problema-2)
- [Integrantes](#integrantes)

## Instalación

Requiere Python 3.10 o superior.

```bash
git clone <url-del-repo>
cd PDI-TP1-G18
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
python problema1.py
python problema2.py
```

Cada script lee sus imágenes de `data/` y guarda los resultados en `resultados/problema1/` o `resultados/problema2/`. Al terminar abre una ventana con las figuras.

## Estructura del repositorio

```
.
├── README.md
├── requirements.txt
├── problema1.py
├── problema2.py
├── data/                  # imágenes del enunciado
├── docs/                  # enunciado e informe
└── resultados/
    ├── problema1/         # figuras de la ecualización
    └── problema2/         # CSV por planilla e imagen de alumnos no aprobados
```

## Problema 1

`ecualizacion_local(img, M, N)` recorre la imagen con una ventana de M×N. En cada posición ecualiza el histograma de la ventana y se queda solo con el valor del píxel central. Los bordes se completan replicando los píxeles del borde (`cv2.copyMakeBorder` con `BORDER_REPLICATE`).

**Ecualización global contra local (ventana 31×31):**

<p align="center"><img src="resultados/problema1/p1_global_vs_local.png" width="90%" alt="Imagen original, ecualización global y ecualización local con sus histogramas"></p>

**Efecto del tamaño de ventana** (3×3, 7×7, 15×15, 31×31, 71×71 y 5×31):

<p align="center"><img src="resultados/problema1/p1_ventanas.png" width="90%" alt="Ecualización local con distintos tamaños de ventana"></p>

## Problema 2

### Cómo funciona

**1. Detección de la grilla.** La imagen se binariza y se suman los píxeles oscuros de cada fila y de cada columna. Las líneas de la tabla generan picos mucho más altos que el texto: todo lo que supera el 60 % del pico máximo se toma como línea. Como el umbral es relativo, funciona igual en las cuatro planillas aunque tengan distinto tamaño. Las 20 filas de datos empiezan en la línea que cierra el encabezado.

**2. Caracteres y palabras.** Cada celda se recorta 3 px hacia adentro, para no arrastrar restos de las líneas, y se buscan sus componentes conectadas. Cada componente es, en general, un carácter. Tres ajustes hacen que el conteo sea correcto:

- Se descartan solo las componentes de 2 px o menos, para no perder el guion (4–5 px) ni el punto (3 px).
- Letras pegadas: cada componente cuenta `round(ancho / (0.8 × alto de letra))` caracteres. Una letra normal da 1 y dos letras que se tocan dan 2, como los ceros de `100`.
- Un hueco entre componentes mayor a 0.6 × alto de letra es un espacio, es decir, una palabra nueva.

**3. ¿L o R?** Para la imagen de salida hay que distinguir la letra de la condición final sin OCR. Se usan dos medidas de la letra: relleno (área de tinta / área de la caja) y proporción ancho / alto.

| Letra | Relleno | Ancho / alto | Regla |
|---|---|---|---|
| R | 0.47 – 0.49 | 0.67 – 0.90 | relleno > 0.42 |
| A | 0.36 – 0.37 | 0.92 – 1.00 | si no es R, ancho / alto > 0.8 |
| L | 0.23 – 0.36 | 0.58 – 0.70 | el resto |

### Resultados

| Planilla | Legajo | Nombre | Parcial 1 | Parcial 2 | Parcial 3 | Condición | Registros 100 % OK | Recuperan | Libres |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| grade_sheet_1 | 15/20 | 15/20 | 15/20 | 15/20 | 15/20 | 15/20 | **15/20** | 4 | 6 |
| grade_sheet_2 | 12/20 | 11/20 | 13/20 | 16/20 | 13/20 | 12/20 | **3/20** | 0 | 3 |
| grade_sheet_3 | 10/20 | 11/20 | 13/20 | 15/20 | 12/20 | 12/20 | **0/20** | 0 | 0 |
| grade_sheet_4 | 14/20 | 13/20 | 16/20 | 15/20 | 15/20 | 14/20 | **6/20** | 2 | 2 |

Los resultados coinciden con una validación hecha a mano de las 480 celdas de las cuatro planillas.

**Imagen de salida (punto b).** Una sola imagen con los alumnos no aprobados de las cuatro planillas. Naranja = recupera, rojo = libre.

<p align="center"><img src="resultados/problema2/alumnos_no_aprobados.png" width="420" alt="Nombres de los alumnos que recuperan o quedaron libres"></p>

**CSV (punto c).** Un archivo por planilla, `resultados_grade_sheet_<id>.csv`. El `ID` es el número de fila:

```csv
ID,Legajo,Nombre y Apellido,Parcial 1,Parcial 2,Parcial 3,Condición Final
1,OK,OK,OK,OK,OK,OK
2,OK,OK,OK,OK,OK,OK
3,MAL,MAL,MAL,MAL,MAL,MAL
```

**Terminal (punto a):**

```
##### grade_sheet_1
> Registro 1:
> Legajo: OK
> Nombre y Apellido: OK
> Parcial 1: OK
...
```

## Integrantes

| Nombre |
|---|
| María Florencia Gomez |
| Candela Stefano |
| Julián Rapanelli |
