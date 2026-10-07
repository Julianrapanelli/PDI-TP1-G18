import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv
from pathlib import Path

RAIZ = Path(__file__).parent
DATA = RAIZ / 'data'
SALIDA = RAIZ / 'resultados' / 'problema2'

CAMPOS = ['Legajo', 'Nombre y Apellido', 'Parcial 1', 'Parcial 2', 'Parcial 3', 'Condición Final']


def agrupar_consecutivos(indices):
    """Convierte [10,11,12, 50,51] en [(10,12), (50,51)]: inicio y fin de cada línea."""
    grupos = []
    if len(indices) == 0:
        return grupos
    inicio = indices[0]
    previo = indices[0]
    for idx in indices[1:]:
        if idx != previo + 1:
            grupos.append((inicio, previo))
            inicio = idx
        previo = idx
    grupos.append((inicio, previo))
    return grupos


def detectar_lineas(img, th=100, frac_h=0.6, frac_v=0.6):
    # Binarizar: 1 donde hay píxel oscuro (línea o texto)
    img_th = (img < th).astype(np.uint8)

    # Suma por filas y por columnas
    suma_filas = np.sum(img_th, axis=1)
    suma_cols = np.sum(img_th, axis=0)

    # Umbral relativo al máximo
    filas_linea = np.where(suma_filas > frac_h * suma_filas.max())[0]
    cols_linea = np.where(suma_cols > frac_v * suma_cols.max())[0]

    return agrupar_consecutivos(filas_linea), agrupar_consecutivos(cols_linea), img_th

def extraer_celdas(img, lineas_h, lineas_v, margen=3):
    """Devuelve una lista de 20 registros; cada uno es un dict con el recorte de cada campo."""
    nombres_campos = ['Legajo', 'Nombre y Apellido', 'Parcial 1', 'Parcial 2', 'Parcial 3', 'Condición Final']
    registros = []

    # lineas_h[0] es el borde superior; lineas_h[1] cierra el encabezado.
    # Las filas de datos van de lineas_h[1] a lineas_h[-1].
    for r in range(1, len(lineas_h) - 1):
        y0 = lineas_h[r][1] + margen         # justo debajo de la línea
        y1 = lineas_h[r + 1][0] - margen     # justo encima de la siguiente

        registro = {}
        # Columna 0 es Nro; los campos empiezan en la columna 1
        for c, nombre in enumerate(nombres_campos, start=1):
            x0 = lineas_v[c][1] + margen
            x1 = lineas_v[c + 1][0] - margen
            registro[nombre] = img[y0:y1, x0:x1]
        registros.append(registro)

    return registros

def analizar_celda(celda, th=160, th_area=2, frac_palabra=0.6, ratio_ancho=0.8):
    """Devuelve (cantidad de caracteres, cantidad de palabras, huecos)."""
    celda_th = (celda < th).astype(np.uint8)

    n, labels, stats, _ = cv2.connectedComponentsWithStats(celda_th, connectivity=8)

    stats = stats[1:]
    stats = stats[stats[:, cv2.CC_STAT_AREA] > th_area]

    if len(stats) == 0:
        return 0, 0, []

    stats = stats[np.argsort(stats[:, cv2.CC_STAT_LEFT])]

    alto_ref = np.max(stats[:, cv2.CC_STAT_HEIGHT])
    umbral_hueco = frac_palabra * alto_ref
    ancho_char = ratio_ancho * alto_ref   # ancho esperado de un carácter

    # Caracteres: un bloque muy ancho cuenta como varios caracteres pegados.
    # Sólo se aplica a bloques altos (letras/números), no al guion ni al punto.
    caracteres = 0
    for s in stats:
        if s[cv2.CC_STAT_HEIGHT] >= 0.5 * alto_ref:
            caracteres += max(1, int(round(s[cv2.CC_STAT_WIDTH] / ancho_char)))
        else:
            caracteres += 1

    huecos = []
    palabras = 1
    for k in range(len(stats) - 1):
        fin = stats[k, cv2.CC_STAT_LEFT] + stats[k, cv2.CC_STAT_WIDTH]
        hueco = stats[k + 1, cv2.CC_STAT_LEFT] - fin
        huecos.append(int(hueco))
        if hueco > umbral_hueco:
            palabras += 1

    return caracteres, palabras, huecos

def validar_registro(reg, contar_espacio=False):
    """Devuelve un dict {campo: 'OK' / 'MAL'} aplicando las reglas del enunciado."""
    res = {}

    # Legajo: 8 caracteres, una sola palabra
    c, p, _ = analizar_celda(reg['Legajo'])
    res['Legajo'] = 'OK' if (c == 8 and p == 1) else 'MAL'

    #  Nombre y apellido: al menos 2 palabras y no más de 12 caracteres en total
    c, p, _ = analizar_celda(reg['Nombre y Apellido'])
    total = c + (p - 1 if contar_espacio and c > 0 else 0)
    res['Nombre y Apellido'] = 'OK' if (p >= 2 and total <= 12) else 'MAL'

    # Notas: 1 o 2 caracteres consecutivos (una sola palabra)
    for parcial in ['Parcial 1', 'Parcial 2', 'Parcial 3']:
        c, p, _ = analizar_celda(reg[parcial])
        res[parcial] = 'OK' if (c in (1, 2) and p == 1) else 'MAL'

    # Condición Final: un único carácter
    c, p, _ = analizar_celda(reg['Condición Final'])
    res['Condición Final'] = 'OK' if c == 1 else 'MAL'

    return res


def clasificar_condicion(celda, th=160, th_area=2):
    """Devuelve 'A', 'L' o 'R' para una celda con un único carácter."""
    celda_th = (celda < th).astype(np.uint8)
    _, _, stats, _ = cv2.connectedComponentsWithStats(celda_th, connectivity=8)
    stats = stats[1:]
    stats = stats[stats[:, cv2.CC_STAT_AREA] > th_area]
    x, y, w, h, area = stats[np.argmax(stats[:, cv2.CC_STAT_AREA])]

    relleno = area / (w * h)
    if relleno > 0.42:      # la R tiene mucha más tinta que A y L
        return 'R'
    if w / h > 0.8:         # entre las que quedan, la A es la más ancha
        return 'A'
    return 'L'


def guardar_csv(resultados, ruta):
    with open(ruta, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['ID'] + CAMPOS)
        for k, res in enumerate(resultados, start=1):
            w.writerow([k] + [res[c] for c in CAMPOS])


def armar_imagen_salida(items, ancho_crop=360, alto_crop=40, ancho_label=160):
    """items: lista de (crop, condicion). Devuelve una única imagen con todos."""
    filas = []
    for crop, cond in items:
        h, w = crop.shape
        escala = min(ancho_crop / w, alto_crop / h)
        crop = cv2.resize(crop, (int(w * escala), int(h * escala)), interpolation=cv2.INTER_CUBIC)

        # Panel con el crop centrado sobre fondo blanco
        panel = np.full((alto_crop + 10, ancho_crop + 10), 255, np.uint8)
        y0 = (panel.shape[0] - crop.shape[0]) // 2
        x0 = 5
        panel[y0:y0 + crop.shape[0], x0:x0 + crop.shape[1]] = crop
        panel = cv2.cvtColor(panel, cv2.COLOR_GRAY2BGR)

        # Indicador: R = naranja (recupera), L = rojo (libre)
        color = (0, 140, 255) if cond == 'R' else (0, 0, 220)
        texto = 'RECUPERA (R)' if cond == 'R' else 'LIBRE (L)'
        etiqueta = np.full((panel.shape[0], ancho_label, 3), 255, np.uint8)
        cv2.rectangle(etiqueta, (0, 0), (ancho_label - 1, panel.shape[0] - 1), color, -1)
        cv2.putText(etiqueta, texto, (8, panel.shape[0] // 2 + 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        fila = np.hstack([panel, etiqueta])
        cv2.rectangle(fila, (0, 0), (fila.shape[1] - 1, fila.shape[0] - 1), color, 2)
        filas.append(fila)

    return np.vstack(filas)

def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    no_aprobados = []   # (crop del nombre, 'L' o 'R') de todas las planillas

    for nombre in ['grade_sheet_1', 'grade_sheet_2', 'grade_sheet_3', 'grade_sheet_4']:
        img = cv2.imread(str(DATA / f'{nombre}.png'), cv2.IMREAD_GRAYSCALE)
        lineas_h, lineas_v, _ = detectar_lineas(img, th=160)
        registros = extraer_celdas(img, lineas_h, lineas_v)

        resultados = []
        print(f'\n##### {nombre}')
        for k, reg in enumerate(registros, start=1):
            res = validar_registro(reg)
            resultados.append(res)

            # salida por terminal
            print(f'> Registro {k}:')
            for campo, valor in res.items():
                print(f'> {campo}: {valor}')
            print('>')

            # solo registros totalmente correctos con condición L o R
            if all(v == 'OK' for v in res.values()):
                cond = clasificar_condicion(reg['Condición Final'])
                if cond in ('L', 'R'):
                    no_aprobados.append((reg['Nombre y Apellido'], cond))

        # un CSV por planilla
        guardar_csv(resultados, SALIDA / f'resultados_{nombre}.csv')

    # única imagen de salida
    salida = armar_imagen_salida(no_aprobados)
    cv2.imwrite(str(SALIDA / 'alumnos_no_aprobados.png'), salida)
    print(f'\nAlumnos no aprobados en la imagen: {len(no_aprobados)}')

    plt.figure(figsize=(8, 10))
    plt.imshow(cv2.cvtColor(salida, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()


if __name__ == "__main__":
    main()