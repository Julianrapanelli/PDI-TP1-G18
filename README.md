# TP1 · Procesamiento de Imágenes I

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)

Trabajo Práctico N° 1 de **Procesamiento de Imágenes I (IA 4.4)**, Tecnicatura Universitaria en Inteligencia Artificial, FCEIA – Universidad Nacional de Rosario. 2° semestre 2026.

| Problema | Qué resuelve |
|---|---|
| **1. Ecualización local de histograma** | Revela detalles ocultos en zonas de una imagen donde la ecualización global no alcanza. |
| **2. Validación de planillas de calificaciones** | Lee una planilla escaneada, valida cada campo de cada registro y genera un CSV y una imagen con los alumnos que no aprobaron. |

<p align="center">
  <img src="docs/img/p2_05_validaciones.png" width="85%" alt="Las cuatro planillas validadas: cada celda en verde si está bien cargada y en rojo si no">
  <br><em>Resultado del Problema 2 sobre las cuatro planillas: verde = OK, rojo = MAL.</em>
</p>

## Contenido

- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Problema 1 – Ecualización local de histograma](#problema-1--ecualización-local-de-histograma)
- [Problema 2 – Validación de planillas](#problema-2--validación-de-planillas)
- [Integrantes](#integrantes)

## Instalación

Requiere Python 3.10 o superior.

```bash
git clone <url-del-repo>
cd <carpeta-del-repo>
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

Cada problema se ejecuta con un solo comando desde la raíz del repositorio:

```bash
python problema1.py              # Problema 1
python problema2.py              # Problema 2: valida las 4 planillas
python figuras_problema2.py      # (opcional) regenera las figuras de este README
```

Los resultados se guardan en `resultados/`. Las imágenes de entrada están en `data/`.

## Estructura del repositorio

```
.
├── README.md
├── requirements.txt
├── problema1.py                 # Problema 1
├── problema2.py                 # Problema 2
├── figuras_problema2.py         # figuras del pipeline para este README
├── data/                        # imágenes del enunciado
│   ├── Imagen_con_detalles_escondidos.tif
│   ├── grade_sheet_1.png … grade_sheet_4.png
│   └── grade_sheet_empty.png
├── resultados/
│   ├── problema1/
│   └── problema2/               # CSV, imagen de salida y validación de cada planilla
└── docs/img/                    # figuras usadas en este README
```

### Cómo funciona

#### 1. Detección de la grilla por proyecciones

La imagen se binariza (tinta = 1) y se suman los píxeles de cada fila y de cada columna. Las líneas de la tabla atraviesan toda la planilla, así que generan picos mucho más altos que el texto. Todo lo que supera el 60 % del pico máximo se toma como línea.

<p align="center"><img src="docs/img/p2_01_proyecciones.png" width="95%" alt="Imagen binarizada y gráficos de suma por filas y por columnas con el umbral"></p>

El umbral es **relativo al máximo**, no un número fijo de píxeles. Por eso funciona igual en las cuatro planillas, aunque tengan distinto tamaño y proporciones. Las filas de datos se toman como las **20 de abajo de todo**, así no importa cómo esté armado el encabezado.

<p align="center"><img src="docs/img/p2_02_grilla.png" width="100%" alt="Las cuatro planillas con la grilla detectada"></p>

#### 2. Caracteres y palabras en cada celda

Cada celda se recorta 3 px hacia adentro, para no arrastrar restos de las líneas. Después se buscan las **componentes conectadas**: cada una es, en general, una letra. Tres detalles hacen que el conteo sea correcto:

- **Filtro de área mínimo (> 2 px).** El guion mide 4–5 px y el punto 3 px. Un filtro más agresivo los borra, y entonces todos los legajos válidos quedan con 7 caracteres.
- **Letras pegadas.** En esta fuente ninguna letra es más ancha que alta. Si una componente mide unas dos alturas de ancho, son dos letras que se tocan, como los ceros de `100`.
- **Espacios.** Un hueco entre componentes mayor a media altura de letra es un espacio. Medido sobre las cuatro planillas, los huecos dentro de una palabra van de 0 a 4 px y los espacios de 10 a 13 px. Se usa la altura y no el ancho de las letras porque el ancho varía mucho (`1` contra `M`).

<p align="center"><img src="docs/img/p2_03_celdas.png" width="95%" alt="Seis celdas de ejemplo con las cajas de cada componente y los espacios detectados"></p>

#### 3. ¿Recupera o libre? (punto b)

Para armar la imagen de salida hay que saber si la condición es `L` o `R`. Se resuelve con dos rasgos de forma, sin OCR:

| Letra | Agujeros | Trazo vertical a la izquierda |
|---|---|---|
| L | 0 | sí |
| R | 1 | sí (100 % de las filas) |
| A | 1 | no (≈ 33–42 % de las filas) |

<p align="center"><img src="docs/img/p2_04_condicion.png" width="65%" alt="Las letras L, R y A con sus agujeros y su trazo izquierdo marcados"></p>

### Resultados

| Planilla | Legajo | Nombre | Parcial 1 | Parcial 2 | Parcial 3 | Condición | **Registros 100 % OK** | Recuperan | Libres |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| grade_sheet_1 | 15/20 | 15/20 | 15/20 | 15/20 | 15/20 | 15/20 | **15/20** | 4 | 6 |
| grade_sheet_2 | 12/20 | 11/20 | 13/20 | 16/20 | 13/20 | 12/20 | **3/20** | 0 | 3 |
| grade_sheet_3 | 10/20 | 11/20 | 13/20 | 15/20 | 12/20 | 12/20 | **0/20** | 0 | 0 |
| grade_sheet_4 | 14/20 | 13/20 | 16/20 | 15/20 | 15/20 | 14/20 | **6/20** | 2 | 2 |

Los resultados se contrastaron con una validación hecha a mano de las 480 celdas de las cuatro planillas: **coinciden en todas**.

**Imagen de salida (punto b)**, una por planilla. Naranja = recupera, rojo = libre:

<table>
  <tr>
    <td align="center" valign="top"><img src="resultados/problema2/grade_sheet_1_salida.png" width="380"><br><code>grade_sheet_1</code></td>
    <td align="center" valign="top"><img src="resultados/problema2/grade_sheet_4_salida.png" width="380"><br><code>grade_sheet_4</code></td>
  </tr>
</table>

Las salidas de [`grade_sheet_2`](resultados/problema2/grade_sheet_2_salida.png) y [`grade_sheet_3`](resultados/problema2/grade_sheet_3_salida.png) están en `resultados/problema2/`. La planilla 3 no tiene ningún registro completamente correcto, así que su imagen lo indica.

**CSV (punto c).** Un archivo por planilla. El `ID` corresponde al número de fila:

```csv
ID,Legajo,Nombre y apellido,Parcial 1,Parcial 2,Parcial 3,Condición Final
1,OK,MAL,OK,OK,OK,OK
2,OK,OK,OK,OK,MAL,OK
3,MAL,MAL,OK,OK,OK,OK
```

**Terminal (punto a)**, con el formato del enunciado:

```
> Registro 1:
> Legajo: OK
> Nombre y apellido: MAL
> Parcial 1: OK
...
```

## Integrantes

| Nombre |
|---|
|María Florencia Gomez|
|Candela Stefano|
|Julián Rapanelli|

---
