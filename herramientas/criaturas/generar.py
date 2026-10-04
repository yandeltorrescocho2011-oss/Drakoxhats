"""Genera las criaturas animadas: FBX para Roblox, configuracion Luau, imagen y GIF de animacion.

Uso:
  pip install bpy==4.2.0 pillow
  python3 herramientas/criaturas/generar.py                      # todas
  python3 herramientas/criaturas/generar.py PollitoBomba         # solo una
  python3 herramientas/criaturas/generar.py PollitoBomba --rapido  # sin GIF (para probar formas)

Cada criatura vive en su propio archivo (por ejemplo pollitobomba.py) con:
  NOMBRE, COLORES_EXTRA, construir(c), CONFIG (vida, habilidades...) y ANIMACIONES.
Los escenarios sin animacion ponen ESTATICO = True y no necesitan CONFIG ni ANIMACIONES.
"""
import importlib
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import bpy  # noqa: E402
from PIL import Image  # noqa: E402

import motor  # noqa: E402

RAIZ = os.path.normpath(os.path.join(AQUI, "..", ".."))
SALIDA_MODELOS = os.path.join(RAIZ, "modelos", "criaturas")
SALIDA_CONFIGS = os.path.join(RAIZ, "roblox", "SistemaCriaturas", "Compartido", "Configs")

CRIATURAS = ["PollitoBomba", "GalloRelampago", "GalloSamurai", "GalloCatrin", "GalloQuetzal", "HuevoMimico",
             "ArenaPalenque"]
FPS = 12


def cargar(nombre):
    return importlib.import_module(nombre.lower())


def construir(mod, desplazar=(0, 0, 0)):
    paleta = motor.Paleta(getattr(mod, "COLORES_EXTRA", {}))
    return paleta, motor.Criatura(mod.NOMBRE, paleta, desplazar)


def secuencia_gif(anims, config):
    """Lista de (t, pose): reposo -> caminar -> cada clip de habilidad -> derrota."""
    frames = []
    ciclos = anims
    clips = anims.get("clips", {})

    def ciclo(nombre, segundos, base=0.0):
        for i in range(int(segundos * FPS)):
            t = base + i / FPS
            frames.append(motor.evaluar_ciclo(ciclos.get(nombre, {}), t))

    ciclo("Idle", 1.5)
    ciclo("Caminar", 1.5)
    usados = [h.get("anim") for h in config.get("habilidades", []) if h.get("anim") in clips]
    for extra in ("Despertar", "Derrota"):
        if extra in clips:
            usados.append(extra)
    for nombre in dict.fromkeys(usados):
        clip = clips[nombre]
        pasos = int((clip["duracion"] + 0.35) * FPS)
        for i in range(pasos):
            t = i / FPS
            base = motor.evaluar_ciclo(ciclos.get("Idle", {}), t)
            frames.append(motor.sumar_poses((base, 1.0), (motor.evaluar_clip(clip, min(t, clip["duracion"])), 1.0)))
    return frames


def generar(nombre, rapido=False):
    mod = cargar(nombre)
    motor.limpiar()
    carpeta = os.path.join(SALIDA_MODELOS, mod.NOMBRE)
    os.makedirs(carpeta, exist_ok=True)
    paleta, c = construir(mod)
    paleta.crear_imagen(os.path.join(carpeta, "paleta.png"))
    mod.construir(c)
    objetos = c.unir()
    estatico = getattr(mod, "ESTATICO", False)
    anims = {} if estatico else motor.normalizar_animaciones(mod.ANIMACIONES)
    if not estatico:
        _validar_animaciones(c, anims, mod.CONFIG)

    # FBX con una MeshPart por parte (y piezas de brillo/vidrio aparte) + marcadores.
    bpy.ops.object.select_all(action="DESELECT")
    for o in objetos.values():
        o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=os.path.join(carpeta, f"{mod.NOMBRE}.fbx"), use_selection=True,
                             path_mode="COPY", embed_textures=True, apply_unit_scale=True, global_scale=1.0,
                             mesh_smooth_type="FACE")
    # Configuracion Luau para el sistema de Roblox (los escenarios estaticos no la necesitan).
    if not estatico:
        os.makedirs(SALIDA_CONFIGS, exist_ok=True)
        config = motor.convertir_colores(mod.CONFIG)
        with open(os.path.join(SALIDA_CONFIGS, f"{mod.NOMBRE}.lua"), "w") as f:
            f.write(motor.config_luau(c, config, anims))

    tris = {n: sum(len(p.vertices) - 2 for p in o.data.polygons) for n, o in objetos.items()}
    print(f"{mod.NOMBRE}: {len(objetos)} objetos, {sum(tris.values())} triangulos, mayor {max(tris.values())}")
    for n in sorted(objetos):
        print(f"   {n}: {tris[n]}")

    visibles = [o for n, o in objetos.items() if not n.startswith("_")]
    for n, o in objetos.items():
        if n.startswith("_"):
            o.hide_render = True
    # En modo rapido (para probar formas) la imagen sale mas chica y con menos muestras.
    motor.escena_render(visibles, 600 if rapido else 900, 600 if rapido else 900, muestras=24 if rapido else 48)
    motor.render(os.path.join(carpeta, "vista_previa.png"))
    if rapido or estatico:
        return
    # GIF: misma matematica de animacion que usa Roblox.
    esc = bpy.context.scene
    esc.render.resolution_x = esc.render.resolution_y = 420
    esc.cycles.samples = 10
    reposo = {n: o.matrix_world.copy() for n, o in objetos.items()}
    tmp = os.path.join(carpeta, "_frames")
    os.makedirs(tmp, exist_ok=True)
    imagenes = []
    for i, pose in enumerate(secuencia_gif(anims, mod.CONFIG)):
        motor.aplicar_pose(c, pose, reposo)
        ruta = os.path.join(tmp, f"{i:04d}.png")
        motor.render(ruta)
        imagenes.append(Image.open(ruta).convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    imagenes[0].save(os.path.join(carpeta, "animacion.gif"), save_all=True, append_images=imagenes[1:],
                     duration=int(1000 / FPS), loop=0, optimize=True)
    for archivo in os.listdir(tmp):
        os.remove(os.path.join(tmp, archivo))
    os.rmdir(tmp)
    print(f"   animacion.gif: {len(imagenes)} cuadros")


def _validar_animaciones(c, anims, config):
    validas = set(c.partes) | {"Raiz"}
    for nombre, datos in anims.items():
        poses = []
        if nombre == "clips":
            for clip in datos.values():
                poses += [p for _, p in clip["claves"]]
        else:
            poses.append(datos)
        for pose in poses:
            for parte, canales in pose.items():
                if parte not in validas:
                    raise ValueError(f"Animacion {nombre}: parte desconocida {parte}")
                lista = canales if isinstance(canales, list) else [(k,) for k in canales]
                for canal in lista:
                    if canal[0] not in motor.CANALES:
                        raise ValueError(f"Animacion {nombre}/{parte}: canal desconocido {canal[0]}")
    clips = anims.get("clips", {})
    for h in config.get("habilidades", []):
        if h.get("anim") and h["anim"] not in clips:
            raise ValueError(f"Habilidad {h['nombre']}: no existe el clip {h['anim']}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rapido = "--rapido" in sys.argv
    for n in args or CRIATURAS:
        generar(n, rapido)
