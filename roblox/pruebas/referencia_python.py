"""Calcula poses de referencia con la matematica de Python (vista previa de Blender) para compararlas con Luau."""
import json
import math
import os
import random
import sys

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "herramientas", "criaturas"))
import motor  # noqa: E402

nombre = sys.argv[1]
mod = __import__(nombre.lower())
anims = motor.normalizar_animaciones(mod.ANIMACIONES)
salida = {"ciclos": [], "clips": [], "matrices": []}
for ciclo in [n for n in anims if n != "clips"]:
    for t in (0.0, 0.37, 1.25, 2.9):
        salida["ciclos"].append({"ciclo": ciclo, "t": t, "pose": motor.evaluar_ciclo(anims[ciclo], t)})
for clip, datos in anims.get("clips", {}).items():
    for k in range(7):
        t = datos["duracion"] * k / 6
        salida["clips"].append({"clip": clip, "t": t, "pose": motor.evaluar_clip(datos, t)})
rnd = random.Random(3)
for _ in range(6):
    canales = {c: rnd.uniform(-90, 90) if c[0] == "r" else rnd.uniform(-2, 2) for c in motor.CANALES}
    m = motor.matriz_canales(canales)
    salida["matrices"].append({"canales": canales, "m": [[m[i][j] for j in range(4)] for i in range(3)]})
print(json.dumps(salida))
