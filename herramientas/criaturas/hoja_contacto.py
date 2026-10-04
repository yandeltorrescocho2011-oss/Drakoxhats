"""Hace una hoja con cuadros del GIF de una criatura para revisar la animacion de un vistazo.

Uso: python3 herramientas/criaturas/hoja_contacto.py GalloSamurai [salida.png]
"""
import os
import sys

from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
nombre = sys.argv[1]
gif = Image.open(os.path.join(AQUI, "..", "..", "modelos", "criaturas", nombre, "animacion.gif"))
n = gif.n_frames
COLUMNAS, FILAS = 6, 4
indices = [round(i * (n - 1) / (COLUMNAS * FILAS - 1)) for i in range(COLUMNAS * FILAS)]
lado = gif.size[0]
hoja = Image.new("RGB", (COLUMNAS * lado, FILAS * lado))
dibujo = ImageDraw.Draw(hoja)
for k, i in enumerate(indices):
    gif.seek(i)
    x, y = (k % COLUMNAS) * lado, (k // COLUMNAS) * lado
    hoja.paste(gif.convert("RGB"), (x, y))
    dibujo.text((x + 6, y + 6), f"cuadro {i}", fill=(255, 255, 255))
salida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(AQUI, "..", "..", "modelos", "criaturas", nombre,
                                                              "_hoja_contacto.png")
hoja.save(salida)
print(salida)
