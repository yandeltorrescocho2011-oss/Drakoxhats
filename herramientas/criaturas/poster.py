"""Poster de las criaturas nuevas dentro de la Arena del Palenque, cada una en plena accion.

Uso: python3 herramientas/criaturas/poster.py
Salida: modelos/criaturas/poster.png
"""
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import generar  # noqa: E402
import motor  # noqa: E402

# (criatura, x, y, giro en grados, clip de accion o None, momento del clip 0-1)
ESCENA = [
    ("GalloQuetzal", 0.0, 4.0, 0, "Viento Divino", 0.55),
    ("GalloSamurai", -8.5, -1.0, -20, "Corte Veloz", 0.5),
    ("GalloRelampago", 8.5, -1.0, 20, "Rayo Encadenado", 0.5),
    ("GalloCatrin", -15.0, 2.5, -30, "Grito del Más Allá", 0.55),
    ("HuevoMimico", 14.5, 2.5, 30, "Mordisco", 0.45),
    ("PollitoBomba", 4.5, -6.5, 15, None, 0),
    ("PollitoBomba", -4.0, -7.0, -10, "¡Kabum!", 0.75),
]


def clip_de_habilidad(mod, nombre_habilidad):
    for h in mod.CONFIG.get("habilidades", []):
        if h["nombre"] == nombre_habilidad:
            return h.get("anim")
    return None


def colocar(nombre, x, y, giro, habilidad, momento, indice):
    mod = generar.cargar(nombre)
    paleta = motor.Paleta(getattr(mod, "COLORES_EXTRA", {}))
    paleta.crear_imagen(os.path.join("/tmp", f"paleta_poster_{indice}.png"))
    c = motor.Criatura(mod.NOMBRE, paleta)
    mod.construir(c)
    objetos = c.unir()
    for n in [n for n in objetos if n.startswith("_")]:
        bpy.data.objects.remove(objetos.pop(n))
    c.objetos = objetos
    anims = motor.normalizar_animaciones(mod.ANIMACIONES)
    pose = motor.evaluar_ciclo(anims.get("Idle", {}), 0.4 + indice * 0.3)
    clip = clip_de_habilidad(mod, habilidad) if habilidad else None
    if clip and clip in anims.get("clips", {}):
        datos = anims["clips"][clip]
        pose = motor.sumar_poses((pose, 1.0), (motor.evaluar_clip(datos, datos["duracion"] * momento), 1.0))
    reposo = {n: o.matrix_world.copy() for n, o in objetos.items()}
    motor.aplicar_pose(c, pose, reposo)
    # Gira alrededor del centro del cuerpo y mueve a su lugar.
    giro_m = motor.Matrix.Translation(Vector((x, y, 0))) @ motor.Matrix.Rotation(math.radians(giro), 4, "Z") \
        @ motor.Matrix.Translation(Vector((-c.centro.x, -c.centro.y, 0)))
    for o in objetos.values():
        o.matrix_world = giro_m @ o.matrix_world
    return list(objetos.values())


def principal():
    motor.limpiar()
    todos = []
    arena = generar.cargar("ArenaPalenque")
    paleta = motor.Paleta(getattr(arena, "COLORES_EXTRA", {}))
    paleta.crear_imagen("/tmp/paleta_poster_arena.png")
    c = motor.Criatura(arena.NOMBRE, paleta)
    arena.construir(c)
    objetos = c.unir()
    for n in [n for n in objetos if n.startswith("_")]:
        bpy.data.objects.remove(objetos.pop(n))
    criaturas = []
    for i, (nombre, x, y, giro, hab, momento) in enumerate(ESCENA):
        criaturas += colocar(nombre, x, y, giro, hab, momento, i)
    todos = list(objetos.values()) + criaturas
    esc = motor.escena_render(criaturas, 1920, 1000, muestras=64, poster=True, extra_piso=True)
    # Camara: de frente, un poco elevada, encuadrando a las criaturas con la arena de fondo.
    puntos = [o.matrix_world @ v.co for o in criaturas for v in o.data.vertices]
    minimo = Vector([min(p[i] for p in puntos) for i in range(3)])
    maximo = Vector([max(p[i] for p in puntos) for i in range(3)])
    centro = (minimo + maximo) / 2
    cam = esc.camera
    cam.location = Vector((centro.x, minimo.y - 30, centro.z + 9))
    cam.data.lens = 40
    for o in bpy.data.objects:
        if o.type == "EMPTY":
            o.location = centro + Vector((0, 0, -1.5))
    esc.render.filepath = os.path.join(generar.SALIDA_MODELOS, "poster.png")
    bpy.ops.render.render(write_still=True)
    print("poster listo", len(todos), "objetos")


if __name__ == "__main__":
    principal()
