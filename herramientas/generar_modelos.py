"""Genera los modelos low-poly del juego (abeja secreta, gallo guardian, oso guardian).

Uso:  pip install bpy==4.2.0  &&  python3 herramientas/generar_modelos.py
Salida: modelos/<nombre>/<nombre>.fbx, paleta.png y vista previa .png
Escala: 1 unidad de Blender = 1 stud de Roblox.
"""
import math
import os

import bpy

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "modelos")

# Paleta compartida: cada color es un cuadro de 16x16 px en una textura de 128x128.
COLORES = {
    "negro": (0.05, 0.04, 0.06), "morado_osc": (0.16, 0.05, 0.28), "morado": (0.42, 0.16, 0.70),
    "oro": (1.00, 0.76, 0.12), "cian": (0.20, 0.95, 1.00), "magenta": (1.00, 0.20, 0.75),
    "ala": (0.75, 0.95, 1.00), "blanco": (0.95, 0.95, 0.92), "rojo": (0.85, 0.08, 0.08),
    "rojo_brillo": (1.00, 0.15, 0.05), "naranja": (0.95, 0.45, 0.10), "cafe_rojo": (0.55, 0.18, 0.08),
    "cafe_osc": (0.25, 0.12, 0.05), "amarillo": (1.00, 0.82, 0.20), "verde_osc": (0.03, 0.25, 0.15),
    "acero": (0.55, 0.58, 0.62), "acero_osc": (0.30, 0.32, 0.36), "cafe": (0.42, 0.24, 0.10),
    "beige": (0.80, 0.62, 0.40), "miel": (1.00, 0.60, 0.05), "naranja_brillo": (1.00, 0.55, 0.00),
    "madera": (0.45, 0.28, 0.12),
}
NOMBRES = list(COLORES)
CELDA, TAM = 16, 128


def crear_paleta(ruta):
    img = bpy.data.images.new("paleta", TAM, TAM, alpha=False)
    px = [0.0] * (TAM * TAM * 4)
    for i, nombre in enumerate(NOMBRES):
        cx, cy = (i % 8) * CELDA, (i // 8) * CELDA
        r, g, b = COLORES[nombre]
        for y in range(cy, cy + CELDA):
            for x in range(cx, cx + CELDA):
                j = (y * TAM + x) * 4
                px[j:j + 4] = [r, g, b, 1.0]
    img.pixels = px
    img.filepath_raw = ruta
    img.file_format = "PNG"
    img.save()
    return img


def material(nombre, img, alfa=1.0):
    mat = bpy.data.materials.new(nombre)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.7
    if alfa < 1.0:
        bsdf.inputs["Alpha"].default_value = alfa
        mat.blend_method = "BLEND"
    return mat


class Modelo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.piezas = {}  # grupo -> lista de objetos

    def pieza(self, tipo, pos, esc=(1, 1, 1), color="negro", grupo="Cuerpo", rot=(0, 0, 0), espejo=False, **kw):
        if espejo:
            self.pieza(tipo, pos, esc, color, grupo, rot, **kw)
            pos = (-pos[0], pos[1], pos[2])
            rot = (rot[0], -rot[1], -rot[2])
        if isinstance(esc, (int, float)):
            esc = (esc, esc, esc)
        rot = tuple(math.radians(a) for a in rot)
        if tipo == "esfera":
            bpy.ops.mesh.primitive_uv_sphere_add(segments=kw.get("seg", 12), ring_count=kw.get("anillos", 8))
        elif tipo == "ico":
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1)
        elif tipo == "cubo":
            bpy.ops.mesh.primitive_cube_add(size=1)
        elif tipo == "cilindro":
            bpy.ops.mesh.primitive_cylinder_add(vertices=kw.get("lados", 8), radius=1, depth=1)
        elif tipo == "cono":
            bpy.ops.mesh.primitive_cone_add(vertices=kw.get("lados", 8), radius1=1, radius2=kw.get("punta", 0), depth=1)
        elif tipo == "toro":
            bpy.ops.mesh.primitive_torus_add(major_segments=14, minor_segments=6,
                                             major_radius=kw["radio"], minor_radius=kw["grosor"])
        obj = bpy.context.active_object
        obj.location, obj.scale, obj.rotation_euler = pos, esc, rot
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        # Todas las caras apuntan al cuadro de su color en la paleta.
        i = NOMBRES.index(color)
        u = ((i % 8) * CELDA + CELDA / 2) / TAM
        v = ((i // 8) * CELDA + CELDA / 2) / TAM
        uv = obj.data.uv_layers.active or obj.data.uv_layers.new()
        for loop in uv.data:
            loop.uv = (u, v)
        for p in obj.data.polygons:
            p.use_smooth = False
        self.piezas.setdefault(grupo, []).append(obj)
        return obj

    def unir(self, img):
        """Une las piezas de cada grupo en un solo objeto (una MeshPart en Roblox)."""
        mat_solido = material(f"{self.nombre}_mat", img)
        mat_ala = material(f"{self.nombre}_ala", img, alfa=0.45)
        objetos = []
        for grupo, objs in self.piezas.items():
            bpy.ops.object.select_all(action="DESELECT")
            for o in objs:
                o.select_set(True)
            bpy.context.view_layer.objects.active = objs[0]
            if len(objs) > 1:
                bpy.ops.object.join()
            obj = bpy.context.active_object
            obj.name = obj.data.name = grupo
            obj.data.materials.clear()
            obj.data.materials.append(mat_ala if grupo == "Alas" else mat_solido)
            bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
            objetos.append(obj)
        return objetos


# ---------------------------------------------------------------- modelos

def abeja_secreta():
    """Abeja Eclipse: reina secreta con corona, 4 alas, ojos y franjas que brillan."""
    m = Modelo("AbejaEclipse")
    m.pieza("esfera", (0, 0, 2), (0.9, 0.9, 0.85), "morado_osc")                      # torax
    m.pieza("esfera", (0, 1.4, 1.85), (1.0, 1.4, 1.0), "negro", rot=(-12, 0, 0))     # abdomen
    for dy, r in ((-0.55, 0.97), (0.05, 1.04), (0.65, 0.88)):                         # franjas brillantes
        m.pieza("toro", (0, 1.4 + dy, 1.85 - dy * 0.21), 1, "oro", "Brillo_Oro", rot=(90 - 12, 0, 0),
                radio=r, grosor=0.11)
    m.pieza("esfera", (0, 0.4, 2.65), (0.7, 0.55, 0.3), "morado", rot=(-20, 0, 0))    # pelusa
    m.pieza("esfera", (0, -1.0, 2.3), 0.75, "morado_osc")                             # cabeza
    m.pieza("esfera", (0.4, -1.52, 2.45), (0.3, 0.22, 0.38), "cian", "Brillo_Cian", espejo=True)  # ojos
    m.pieza("cilindro", (0.25, -1.25, 3.1), (0.04, 0.04, 0.8), "negro", rot=(-25, 20, 0), espejo=True)
    m.pieza("ico", (0.4, -1.45, 3.5), 0.16, "cian", "Brillo_Cian", espejo=True)       # puntas antenas
    # corona
    m.pieza("cilindro", (0, -0.95, 2.95), (0.42, 0.42, 0.22), "oro", lados=10)
    for k in range(5):
        a = math.radians(k * 72 + 90)
        m.pieza("cono", (0.38 * math.cos(a), -0.95 + 0.38 * math.sin(a), 3.22), (0.11, 0.11, 0.35), "oro", lados=4)
    m.pieza("ico", (0, -1.36, 3.05), 0.11, "magenta", "Brillo_Magenta")               # joya
    m.pieza("cono", (0, 3.0, 1.55), (0.22, 0.6, 0.22), "magenta", "Brillo_Magenta", rot=(-90 + 12, 0, 0))  # aguijon
    # alas (2 pares)
    m.pieza("esfera", (1.25, 0.3, 3.05), (1.3, 0.6, 0.05), "ala", "Alas", rot=(0, -20, -25), espejo=True)
    m.pieza("esfera", (1.0, 0.85, 2.7), (0.9, 0.42, 0.05), "ala", "Alas", rot=(0, -10, -45), espejo=True)
    # patas
    for y in (-0.35, 0.0, 0.35):
        m.pieza("cilindro", (0.55, y, 1.2), (0.06, 0.06, 0.8), "negro", rot=(0, -25, 0), espejo=True)
    return m


def gallo_guardian():
    """Gallo Guardian: gallo de pelea con casco y pechera de acero, espolones y ojos rojos."""
    m = Modelo("GalloGuardian")
    m.pieza("esfera", (0, 0.1, 3), (1.3, 1.7, 1.4), "cafe_rojo")                       # cuerpo
    m.pieza("esfera", (0, -0.8, 3.1), (1.05, 0.85, 1.15), "naranja")                   # pecho
    m.pieza("esfera", (0, -1.4, 3.15), (0.9, 0.3, 0.95), "acero", rot=(10, 0, 0))      # pechera
    m.pieza("cilindro", (0, -1.68, 3.3), (0.12, 0.12, 0.04), "acero_osc", rot=(90, 0, 0), espejo=False)
    m.pieza("esfera", (0, -1.1, 4.3), (0.65, 0.65, 0.95), "naranja")                   # cuello
    m.pieza("esfera", (0, -1.3, 5.1), 0.62, "cafe_rojo")                               # cabeza
    m.pieza("cilindro", (0, -1.3, 5.38), (0.66, 0.66, 0.3), "acero", lados=10)         # casco
    m.pieza("cono", (0, -1.3, 5.68), (0.66, 0.66, 0.3), "acero_osc", lados=10, punta=0.3)
    for k, y in enumerate((-1.65, -1.3, -0.95)):                                       # cresta
        m.pieza("esfera", (0, y, 5.9 + (0.15 if k == 1 else 0)), (0.14, 0.24, 0.32), "rojo")
    m.pieza("cono", (0, -2.0, 5.0), (0.2, 0.45, 0.16), "amarillo", rot=(90, 0, 0), lados=6)  # pico
    m.pieza("esfera", (0, -1.8, 4.55), (0.14, 0.14, 0.3), "rojo")                      # barbilla
    m.pieza("esfera", (0.32, -1.78, 5.2), 0.13, "rojo_brillo", "Brillo_Rojo", espejo=True)  # ojos
    m.pieza("cubo", (0.3, -1.85, 5.38), (0.32, 0.06, 0.07), "negro", rot=(0, -25, 0), espejo=True)  # cejas
    m.pieza("esfera", (1.25, 0.2, 3.1), (0.35, 1.25, 0.85), "cafe_osc", rot=(-15, 0, 0), espejo=True)  # alas
    m.pieza("esfera", (1.35, -0.25, 3.5), (0.38, 0.5, 0.4), "acero", espejo=True)       # hombreras
    for k, (inc, x) in enumerate(((25, 0), (45, 0.3), (5, -0.3), (65, 0.1), (-10, 0.15))):  # cola
        m.pieza("esfera", (x, 1.9 + k * 0.05, 3.9), (0.22, 0.45, 1.5), "verde_osc" if k % 2 == 0 else "negro",
                rot=(inc, 0, x * 30))
    m.pieza("cilindro", (0.5, 0, 1.0), (0.14, 0.14, 1.6), "amarillo", espejo=True)       # patas
    for ang in (-30, 0, 30):                                                           # dedos
        a = math.radians(ang - 90)
        m.pieza("cubo", (0.5 + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.1), (0.12, 0.6, 0.12), "amarillo",
                rot=(0, 0, ang), espejo=True)
    m.pieza("cono", (0.5, 0.3, 0.7), (0.09, 0.09, 0.45), "acero", rot=(-90 + 180, 0, 0), espejo=True)  # espolones
    return m


def oso_guardian():
    """Oso Guardian del Panal: oso enorme con bandana, hombrera de panal, garrote con miel y ojos naranja."""
    m = Modelo("OsoGuardian")
    m.pieza("esfera", (0, 0, 3.3), (1.9, 1.6, 2.2), "cafe")                            # cuerpo
    m.pieza("esfera", (0, -0.95, 3.0), (1.35, 0.75, 1.6), "beige")                     # panza
    m.pieza("esfera", (0, -0.2, 6.1), (1.35, 1.25, 1.2), "cafe")                       # cabeza
    m.pieza("esfera", (0, -1.3, 5.8), (0.65, 0.5, 0.45), "beige")                      # hocico
    m.pieza("esfera", (0, -1.75, 6.0), (0.25, 0.15, 0.16), "negro")                    # nariz
    m.pieza("esfera", (0.95, -0.1, 7.1), 0.42, "cafe", espejo=True)                    # orejas
    m.pieza("esfera", (0.95, -0.38, 7.1), (0.25, 0.12, 0.25), "beige", espejo=True)
    m.pieza("esfera", (0.5, -1.25, 6.45), 0.14, "naranja_brillo", "Brillo_Naranja", espejo=True)  # ojos
    m.pieza("cubo", (0.5, -1.33, 6.68), (0.42, 0.08, 0.1), "cafe_osc", rot=(0, -22, 0), espejo=True)  # cejas
    m.pieza("cilindro", (0.3, -1.6, 5.5), (0.08, 0.05, 0.25), "blanco", espejo=True)   # colmillos
    m.pieza("cilindro", (0, -0.1, 5.0), (1.3, 1.15, 0.35), "rojo", lados=12)          # bandana
    m.pieza("cono", (0, 1.05, 4.6), (0.45, 0.2, 0.7), "rojo", rot=(180, 0, 0), lados=3)
    m.pieza("esfera", (2.0, -0.3, 3.7), (0.62, 0.68, 1.45), "cafe", rot=(0, 15, 0), espejo=True)  # brazos
    m.pieza("esfera", (2.25, -0.4, 2.3), (0.55, 0.6, 0.45), "beige", espejo=True)      # patas delanteras
    for k in range(3):                                                                 # garras
        m.pieza("cono", (2.0 + k * 0.22, -0.85, 2.15), (0.07, 0.07, 0.3), "blanco", rot=(-120, 0, 0), espejo=True)
    # hombrera de panal (izquierda)
    m.pieza("esfera", (-1.85, -0.1, 4.75), (0.75, 0.85, 0.45), "acero_osc")
    for dx, dy in ((0, 0), (0.32, 0.18), (-0.32, 0.18), (0, 0.37), (0.32, -0.18), (-0.32, -0.18), (0, -0.37)):
        m.pieza("cilindro", (-1.85 + dx * 0.9, -0.1 + dy * 1.1, 5.15), (0.17, 0.17, 0.14), "miel", lados=6)
    # garrote con miel (mano derecha)
    m.pieza("cilindro", (2.3, -1.0, 3.3), (0.17, 0.17, 3.2), "madera", rot=(35, 0, 0))
    m.pieza("esfera", (2.3, -1.9, 4.6), (0.5, 0.5, 0.6), "madera", rot=(35, 0, 0))
    m.pieza("esfera", (2.3, -2.0, 4.85), (0.42, 0.42, 0.3), "miel", rot=(35, 0, 0))
    for dx in (-0.3, 0.3):
        m.pieza("cono", (2.3 + dx * 1.6, -1.85, 4.6), (0.1, 0.1, 0.35), "acero", rot=(0, 90 if dx > 0 else -90, 0))
    # cinturon con bote de miel
    m.pieza("cilindro", (0, 0, 2.15), (1.8, 1.55, 0.3), "cafe_osc", lados=14)
    m.pieza("cilindro", (-1.2, -1.1, 1.95), (0.35, 0.35, 0.55), "miel", lados=8)
    m.pieza("cilindro", (-1.2, -1.1, 2.28), (0.3, 0.3, 0.12), "madera", lados=8)
    m.pieza("esfera", (0.9, -0.1, 0.95), (0.8, 0.9, 1.0), "cafe", espejo=True)          # piernas
    m.pieza("esfera", (0.9, -0.55, 0.25), (0.65, 0.75, 0.3), "beige", espejo=True)      # pies
    return m


# ---------------------------------------------------------------- render y exportacion

def limpiar():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def preparar_render(objs, ruta, ancho=720):
    esc = bpy.context.scene
    esc.render.engine = "CYCLES"
    esc.cycles.device = "CPU"
    esc.cycles.samples = 48
    esc.render.resolution_x = esc.render.resolution_y = ancho
    esc.render.filepath = ruta
    mundo = bpy.data.worlds.new("cielo")
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.7, 0.9, 1)
    mundo.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    esc.world = mundo
    # Encuadre: limites de todos los objetos.
    puntos = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    minimo = [min(p[i] for p in puntos) for i in range(3)]
    maximo = [max(p[i] for p in puntos) for i in range(3)]
    centro = [(a + b) / 2 for a, b in zip(minimo, maximo)]
    tam = max(b - a for a, b in zip(minimo, maximo))
    bpy.ops.mesh.primitive_plane_add(size=tam * 6, location=(centro[0], centro[1], minimo[2]))
    piso = bpy.context.active_object
    mat = bpy.data.materials.new("piso")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.35, 0.55, 0.25, 1)
    piso.data.materials.append(mat)
    dist = tam * 2.0
    bpy.ops.object.camera_add(location=(centro[0] + dist * 0.75, centro[1] - dist * 1.0, centro[2] + dist * 0.45))
    cam = bpy.context.active_object
    cam.data.lens = 45
    rastreo = cam.constraints.new("TRACK_TO")
    bpy.ops.object.empty_add(location=centro)
    rastreo.target = bpy.context.active_object
    esc.camera = cam
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(40), math.radians(15), math.radians(30)))
    bpy.context.active_object.data.energy = 3.5
    bpy.ops.render.render(write_still=True)


def exportar(fabrica):
    limpiar()
    modelo = fabrica()
    carpeta = os.path.join(RAIZ, modelo.nombre)
    os.makedirs(carpeta, exist_ok=True)
    img = crear_paleta(os.path.join(carpeta, "paleta.png"))
    objs = modelo.unir(img)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=os.path.join(carpeta, f"{modelo.nombre}.fbx"), use_selection=True,
                             path_mode="COPY", embed_textures=True, apply_unit_scale=True,
                             global_scale=1.0, mesh_smooth_type="FACE")
    tris = sum(len(p.vertices) - 2 for o in objs for p in o.data.polygons)
    print(f"{modelo.nombre}: {len(objs)} piezas, ~{tris} triangulos -> {carpeta}")
    preparar_render(objs, os.path.join(carpeta, "vista_previa.png"))


if __name__ == "__main__":
    for f in (abeja_secreta, gallo_guardian, oso_guardian):
        exportar(f)
