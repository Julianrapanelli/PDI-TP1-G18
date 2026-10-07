import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

RAIZ = Path(__file__).parent
DATA = RAIZ / 'data'
SALIDA = RAIZ / 'resultados' / 'problema1'


def ecualizacion_local(img, M, N):
    pad_v = M // 2
    pad_h = N // 2
    img_pad = cv2.copyMakeBorder(img, pad_v, pad_v, pad_h, pad_h, cv2.BORDER_REPLICATE)
    salida = np.zeros_like(img)

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            ventana = img_pad[i:i + M, j:j + N]
            ventana_eq = cv2.equalizeHist(ventana)
            salida[i, j] = ventana_eq[M // 2, N // 2]

    return salida


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    img = cv2.imread(str(DATA / 'Imagen_con_detalles_escondidos.tif'), cv2.IMREAD_GRAYSCALE)

    # Figura 1: ecualización global vs. local
    img_global = cv2.equalizeHist(img)
    img_local = ecualizacion_local(img, 31, 31)  

    plt.figure(figsize=(15, 8))
    imagenes = [(img, 'Original'),
                (img_global, 'Ecualización global'),
                (img_local, 'Ecualización local 31x31')]
    for k, (im, titulo) in enumerate(imagenes):
        plt.subplot(2, 3, k + 1)
        plt.imshow(im, cmap='gray', vmin=0, vmax=255)
        plt.title(titulo)
        plt.subplot(2, 3, k + 4)
        plt.hist(im.flatten(), 256, range=[0, 256])
        plt.title('Histograma')
        plt.xlabel('Intensidad')
        plt.ylabel('Cantidad de píxeles')
    plt.tight_layout()
    plt.savefig(SALIDA / 'p1_global_vs_local.png', dpi=150)

    # Figura 2: distintos tamaños de ventana
    tamanos = [(3, 3), (7, 7), (15, 15), (31, 31), (71, 71), (5, 31)]

    plt.figure(figsize=(15, 10))
    plt.subplot(2, 4, 1)
    plt.imshow(img, cmap='gray', vmin=0, vmax=255)
    plt.title('Original')

    for k, (M, N) in enumerate(tamanos):
        res = ecualizacion_local(img, M, N)
        plt.subplot(2, 4, k + 2)
        plt.imshow(res, cmap='gray', vmin=0, vmax=255)
        plt.title(f'{M}x{N}')

    plt.tight_layout()
    plt.savefig(SALIDA / 'p1_ventanas.png', dpi=150)
    plt.show()


if __name__ == "__main__":
    main()