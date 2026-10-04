"""Genera los modelos low-poly del juego y los exporta en FBX para Roblox Studio.

Uso:  pip install bpy==4.2.0  &&  python3 herramientas/generar_modelos.py [NombreModelo ...]
Salida: modelos/<Nombre>/<Nombre>.fbx, paleta.png, vista_previa.png y modelos/poster_epico.png
Escala: 1 unidad de Blender = 1 stud de Roblox. El frente de cada modelo mira hacia -Y.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

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
    "madera": (0.45, 0.28, 0.12), "carbon": (0.05, 0.045, 0.05), "gris_osc": (0.18, 0.17, 0.19),
    "oro_osc": (0.70, 0.45, 0.05), "fuego_rojo": (1.00, 0.15, 0.02), "fuego_naranja": (1.00, 0.45, 0.02),
    "fuego_amarillo": (1.00, 0.85, 0.25), "plata": (0.80, 0.82, 0.88), "crema": (0.98, 0.90, 0.75),
    "amarillo_brillo": (1.00, 0.90, 0.10), "rojo_osc": (0.40, 0.03, 0.03), "hueso": (0.92, 0.88, 0.75),
    "paja": (0.80, 0.65, 0.30), "azul_profundo": (0.05, 0.10, 0.35), "blanco_cian": (0.80, 1.00, 1.00),
    "oro_brillo": (1.00, 0.80, 0.20), "cafe_claro": (0.60, 0.38, 0.18),
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


def material(nombre, img, alfa=1.0, emision=0.0):
    mat = bpy.data.materials.new(nombre)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.6
    if emision:
        mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = emision
    if alfa < 1.0:
        bsdf.inputs["Alpha"].default_value = alfa
        mat.blend_method = "BLEND"
    return mat


class Modelo:
    def __init__(self, nombre, desplazar=(0, 0, 0)):
        self.nombre = nombre
        self.desplazar = Vector(desplazar)
        self.piezas = {}  # grupo -> lista de objetos

    def _crear(self, tipo, kw):
        if tipo == "esfera":
            bpy.ops.mesh.primitive_uv_sphere_add(segments=kw.get("seg", 12), ring_count=kw.get("anillos", 8))
        elif tipo == "ico":
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=kw.get("subdiv", 1))
        elif tipo == "cubo":
            bpy.ops.mesh.primitive_cube_add(size=1)
        elif tipo == "cilindro":
            bpy.ops.mesh.primitive_cylinder_add(vertices=kw.get("lados", 8), radius=1, depth=1)
        elif tipo == "cono":
            bpy.ops.mesh.primitive_cone_add(vertices=kw.get("lados", 8), radius1=1, radius2=kw.get("punta", 0), depth=1)
        elif tipo == "toro":
            bpy.ops.mesh.primitive_torus_add(major_segments=kw.get("seg", 16), minor_segments=6,
                                             major_radius=kw["radio"], minor_radius=kw["grosor"])
        return bpy.context.active_object

    def _terminar(self, obj, color, grupo):
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
        # Las piezas que brillan se separan por color para poder ponerles Material Neon en Roblox.
        if grupo == "Brillo":
            grupo = "Brillo_" + color.title().replace("_", "")
        self.piezas.setdefault(grupo, []).append(obj)
        return obj

    def pieza(self, tipo, pos, esc=(1, 1, 1), color="negro", grupo="Cuerpo", rot=(0, 0, 0), espejo=False, **kw):
        if espejo:
            self.pieza(tipo, pos, esc, color, grupo, rot, **kw)
            pos = (-pos[0], pos[1], pos[2])
            rot = (rot[0], -rot[1], -rot[2])
        if isinstance(esc, (int, float)):
            esc = (esc, esc, esc)
        obj = self._crear(tipo, kw)
        obj.location = Vector(pos) + self.desplazar
        obj.scale = esc
        obj.rotation_euler = tuple(math.radians(a) for a in rot)
        return self._terminar(obj, color, grupo)

    def entre(self, a, b, radio, color="negro", grupo="Cuerpo", tipo="cono", aplanar=1.0, espejo=False, **kw):
        """Pieza que va del punto a al punto b (cuernos, plumas, garras, picos, palos...)."""
        if espejo:
            self.entre(a, b, radio, color, grupo, tipo, aplanar, **kw)
            a, b = (-a[0], a[1], a[2]), (-b[0], b[1], b[2])
        a, b = Vector(a), Vector(b)
        d = b - a
        obj = self._crear(tipo, kw)
        obj.location = (a + b) / 2 + self.desplazar
        largo = d.length / 2 if tipo == "esfera" else d.length
        obj.scale = (radio, radio * aplanar, largo)
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = d.to_track_quat("Z", "Y")
        return self._terminar(obj, color, grupo)

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


def lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def alargar(a, b, extra):
    """Punto que sigue la direccion a->b una distancia extra mas alla de b."""
    d = (Vector(b) - Vector(a)).normalized()
    return tuple(Vector(b) + d * extra)


def sobre_elipsoide(centro, radios, x, z, dentro=0.05):
    """Coordenada Y del frente (-Y) de un elipsoide para pegar piezas en su superficie."""
    cx, cy, cz = centro
    rx, ry, rz = radios
    k = 1 - ((x - cx) / rx) ** 2 - ((z - cz) / rz) ** 2
    return cy - ry * math.sqrt(max(k, 0)) + dentro


# ================================================================ modelos v1

def abeja_secreta(m):
    """Abeja Eclipse: reina secreta con corona, 4 alas, ojos y franjas que brillan."""
    m.pieza("esfera", (0, 0, 2), (0.9, 0.9, 0.85), "morado_osc")
    m.pieza("esfera", (0, 1.4, 1.85), (1.0, 1.4, 1.0), "negro", rot=(-12, 0, 0))
    for dy, r in ((-0.55, 0.97), (0.05, 1.04), (0.65, 0.88)):
        m.pieza("toro", (0, 1.4 + dy, 1.85 - dy * 0.21), 1, "oro", "Brillo", rot=(90 - 12, 0, 0), radio=r, grosor=0.11)
    m.pieza("esfera", (0, 0.4, 2.65), (0.7, 0.55, 0.3), "morado", rot=(-20, 0, 0))
    m.pieza("esfera", (0, -1.0, 2.3), 0.75, "morado_osc")
    m.pieza("esfera", (0.4, -1.52, 2.45), (0.3, 0.22, 0.38), "cian", "Brillo", espejo=True)
    m.pieza("cilindro", (0.25, -1.25, 3.1), (0.04, 0.04, 0.8), "negro", rot=(-25, 20, 0), espejo=True)
    m.pieza("ico", (0.4, -1.45, 3.5), 0.16, "cian", "Brillo", espejo=True)
    m.pieza("cilindro", (0, -0.95, 2.95), (0.42, 0.42, 0.22), "oro", lados=10)
    for k in range(5):
        a = math.radians(k * 72 + 90)
        m.pieza("cono", (0.38 * math.cos(a), -0.95 + 0.38 * math.sin(a), 3.22), (0.11, 0.11, 0.35), "oro", lados=4)
    m.pieza("ico", (0, -1.36, 3.05), 0.11, "magenta", "Brillo")
    m.pieza("cono", (0, 3.0, 1.55), (0.22, 0.6, 0.22), "magenta", "Brillo", rot=(-90 + 12, 0, 0))
    m.pieza("esfera", (1.25, 0.3, 3.05), (1.3, 0.6, 0.05), "ala", "Alas", rot=(0, -20, -25), espejo=True)
    m.pieza("esfera", (1.0, 0.85, 2.7), (0.9, 0.42, 0.05), "ala", "Alas", rot=(0, -10, -45), espejo=True)
    for y in (-0.35, 0.0, 0.35):
        m.pieza("cilindro", (0.55, y, 1.2), (0.06, 0.06, 0.8), "negro", rot=(0, -25, 0), espejo=True)


def gallo_guardian(m):
    """Gallo Guardian: gallo de pelea con casco y pechera de acero, espolones y ojos rojos."""
    m.pieza("esfera", (0, 0.1, 3), (1.3, 1.7, 1.4), "cafe_rojo")
    m.pieza("esfera", (0, -0.8, 3.1), (1.05, 0.85, 1.15), "naranja")
    m.pieza("esfera", (0, -1.4, 3.15), (0.9, 0.3, 0.95), "acero", rot=(10, 0, 0))
    m.pieza("cilindro", (0, -1.68, 3.3), (0.12, 0.12, 0.04), "acero_osc", rot=(90, 0, 0))
    m.pieza("esfera", (0, -1.1, 4.3), (0.65, 0.65, 0.95), "naranja")
    m.pieza("esfera", (0, -1.3, 5.1), 0.62, "cafe_rojo")
    m.pieza("cilindro", (0, -1.3, 5.38), (0.66, 0.66, 0.3), "acero", lados=10)
    m.pieza("cono", (0, -1.3, 5.68), (0.66, 0.66, 0.3), "acero_osc", lados=10, punta=0.3)
    for k, y in enumerate((-1.65, -1.3, -0.95)):
        m.pieza("esfera", (0, y, 5.9 + (0.15 if k == 1 else 0)), (0.14, 0.24, 0.32), "rojo")
    m.pieza("cono", (0, -2.0, 5.0), (0.2, 0.45, 0.16), "amarillo", rot=(90, 0, 0), lados=6)
    m.pieza("esfera", (0, -1.8, 4.55), (0.14, 0.14, 0.3), "rojo")
    m.pieza("esfera", (0.32, -1.78, 5.2), 0.13, "rojo_brillo", "Brillo", espejo=True)
    m.pieza("cubo", (0.3, -1.85, 5.38), (0.32, 0.06, 0.07), "negro", rot=(0, -25, 0), espejo=True)
    m.pieza("esfera", (1.25, 0.2, 3.1), (0.35, 1.25, 0.85), "cafe_osc", rot=(-15, 0, 0), espejo=True)
    m.pieza("esfera", (1.35, -0.25, 3.5), (0.38, 0.5, 0.4), "acero", espejo=True)
    for k, (inc, x) in enumerate(((25, 0), (45, 0.3), (5, -0.3), (65, 0.1), (-10, 0.15))):
        m.pieza("esfera", (x, 1.9 + k * 0.05, 3.9), (0.22, 0.45, 1.5), "verde_osc" if k % 2 == 0 else "negro",
                rot=(inc, 0, x * 30))
    m.pieza("cilindro", (0.5, 0, 1.0), (0.14, 0.14, 1.6), "amarillo", espejo=True)
    for ang in (-30, 0, 30):
        a = math.radians(ang - 90)
        m.pieza("cubo", (0.5 + 0.3 * math.cos(a), 0.3 * math.sin(a), 0.1), (0.12, 0.6, 0.12), "amarillo",
                rot=(0, 0, ang), espejo=True)
    m.pieza("cono", (0.5, 0.3, 0.7), (0.09, 0.09, 0.45), "acero", rot=(90, 0, 0), espejo=True)


def oso_guardian(m):
    """Oso Guardian del Panal: oso con bandana, hombrera de panal, garrote con miel y ojos naranja."""
    m.pieza("esfera", (0, 0, 3.3), (1.9, 1.6, 2.2), "cafe")
    m.pieza("esfera", (0, -0.95, 3.0), (1.35, 0.75, 1.6), "beige")
    m.pieza("esfera", (0, -0.2, 6.1), (1.35, 1.25, 1.2), "cafe")
    m.pieza("esfera", (0, -1.3, 5.8), (0.65, 0.5, 0.45), "beige")
    m.pieza("esfera", (0, -1.75, 6.0), (0.25, 0.15, 0.16), "negro")
    m.pieza("esfera", (0.95, -0.1, 7.1), 0.42, "cafe", espejo=True)
    m.pieza("esfera", (0.95, -0.38, 7.1), (0.25, 0.12, 0.25), "beige", espejo=True)
    m.pieza("esfera", (0.5, -1.25, 6.45), 0.14, "naranja_brillo", "Brillo", espejo=True)
    m.pieza("cubo", (0.5, -1.33, 6.68), (0.42, 0.08, 0.1), "cafe_osc", rot=(0, -22, 0), espejo=True)
    m.pieza("cilindro", (0.3, -1.6, 5.5), (0.08, 0.05, 0.25), "blanco", espejo=True)
    m.pieza("cilindro", (0, -0.1, 5.0), (1.3, 1.15, 0.35), "rojo", lados=12)
    m.pieza("cono", (0, 1.05, 4.6), (0.45, 0.2, 0.7), "rojo", rot=(180, 0, 0), lados=3)
    m.pieza("esfera", (2.0, -0.3, 3.7), (0.62, 0.68, 1.45), "cafe", rot=(0, 15, 0), espejo=True)
    m.pieza("esfera", (2.25, -0.4, 2.3), (0.55, 0.6, 0.45), "beige", espejo=True)
    for k in range(3):
        m.pieza("cono", (2.0 + k * 0.22, -0.85, 2.15), (0.07, 0.07, 0.3), "blanco", rot=(-120, 0, 0), espejo=True)
    m.pieza("esfera", (-1.85, -0.1, 4.75), (0.75, 0.85, 0.45), "acero_osc")
    for dx, dy in ((0, 0), (0.32, 0.18), (-0.32, 0.18), (0, 0.37), (0.32, -0.18), (-0.32, -0.18), (0, -0.37)):
        m.pieza("cilindro", (-1.85 + dx * 0.9, -0.1 + dy * 1.1, 5.15), (0.17, 0.17, 0.14), "miel", lados=6)
    m.pieza("cilindro", (2.3, -1.0, 3.3), (0.17, 0.17, 3.2), "madera", rot=(35, 0, 0))
    m.pieza("esfera", (2.3, -1.9, 4.6), (0.5, 0.5, 0.6), "madera", rot=(35, 0, 0))
    m.pieza("esfera", (2.3, -2.0, 4.85), (0.42, 0.42, 0.3), "miel", rot=(35, 0, 0))
    for dx in (-0.3, 0.3):
        m.pieza("cono", (2.3 + dx * 1.6, -1.85, 4.6), (0.1, 0.1, 0.35), "acero", rot=(0, 90 if dx > 0 else -90, 0))
    m.pieza("cilindro", (0, 0, 2.15), (1.8, 1.55, 0.3), "cafe_osc", lados=14)
    m.pieza("cilindro", (-1.2, -1.1, 1.95), (0.35, 0.35, 0.55), "miel", lados=8)
    m.pieza("cilindro", (-1.2, -1.1, 2.28), (0.3, 0.3, 0.12), "madera", lados=8)
    m.pieza("esfera", (0.9, -0.1, 0.95), (0.8, 0.9, 1.0), "cafe", espejo=True)
    m.pieza("esfera", (0.9, -0.55, 0.25), (0.65, 0.75, 0.3), "beige", espejo=True)


# ================================================================ modelos epicos (v2)

def patas_de_gallo(m, x, y, z_pie, largo=0.6, radio=0.1, color="amarillo", garra="negro", navaja=None):
    """Tres dedos al frente, uno atras, garras y (opcional) navaja de pelea en el espolon."""
    for ang in (-35, 0, 35):
        a = math.radians(ang)
        punta = (x + largo * math.sin(a), y - largo * math.cos(a), z_pie)
        m.entre((x, y, z_pie + 0.05), punta, radio, color, tipo="cilindro", espejo=True)
        m.entre(punta, alargar((x, y, z_pie), punta, largo * 0.4), radio * 1.1, garra, espejo=True)
    m.entre((x, y, z_pie + 0.05), (x, y + largo * 0.6, z_pie), radio, color, tipo="cilindro", espejo=True)
    if navaja:
        m.entre((x, y + 0.2, z_pie + 0.6), (x + 0.05, y + 1.2, z_pie + 0.35), radio * 0.8, navaja, espejo=True)


def cola_de_gallo(m, base, escala=1.0, colores=("verde_osc", "carbon"), fuego=False):
    """Plumas en forma de hoz: suben hacia atras y caen, como la cola de un gallo de pelea."""
    bx, by, bz = base
    for k in range(7):
        x = (k - 3) * 0.2 * escala
        alto = (1.5 + (k % 3) * 0.45) * escala
        medio = (x, by + 1.1 * escala, bz + alto)
        punta = (x * 1.4, by + (2.1 + (k % 2) * 0.35) * escala, bz + alto * 0.3)
        color = colores[k % 2]
        m.entre((x * 0.4, by, bz), medio, 0.3 * escala, color, tipo="esfera", aplanar=0.3, seg=8, anillos=6)
        m.entre(medio, punta, 0.24 * escala, color, tipo="esfera", aplanar=0.3, seg=8, anillos=6)
        if fuego:
            m.entre(lerp(medio, punta, 0.75), alargar(medio, punta, 0.75 * escala), 0.17 * escala,
                    ("fuego_amarillo", "fuego_naranja", "fuego_rojo")[k % 3], "Brillo", lados=6)


def gallo_infernal(m):
    """Gallo Infernal: gallo negro de palenque con cresta y cola de fuego, cuernos y armadura de oro."""
    cuerpo = ((0, 0.2, 3.3), (1.35, 1.8, 1.5))
    m.pieza("esfera", *cuerpo, "carbon", seg=16, anillos=10)
    m.pieza("esfera", (0, -0.8, 3.4), (1.1, 0.95, 1.3), "gris_osc", seg=16, anillos=10)
    # pechera de oro con rubi
    m.pieza("esfera", (0, -1.38, 3.4), (0.95, 0.35, 1.05), "oro", rot=(8, 0, 0), seg=16, anillos=10)
    m.pieza("toro", (0, -1.66, 3.45), (1, 1, 1), "oro_osc", rot=(90, 0, 0), radio=0.3, grosor=0.07)
    m.pieza("ico", (0, -1.72, 3.45), 0.24, "rojo_brillo", "Brillo")
    # hombreras con picos
    m.pieza("esfera", (1.3, -0.3, 4.0), (0.55, 0.65, 0.45), "oro", espejo=True)
    for dy, dz in ((-0.35, 0.0), (0.0, 0.25), (0.35, 0.0)):
        m.entre((1.45, -0.3 + dy, 4.2), (2.0, -0.3 + dy * 1.4, 4.8 + dz), 0.13, "oro_osc", espejo=True)
    # plumas de fuego del cuello
    for k, ang in enumerate((300, 330, 0, 30, 60, 90, 120, 150, 180, 210, 240)):
        a = math.radians(ang)
        base = (0.55 * math.cos(a), -1.0 + 0.55 * math.sin(a), 4.95)
        punta = (1.05 * math.cos(a), -1.0 + 1.05 * math.sin(a), 3.85)
        m.entre(base, punta, 0.24, "rojo" if k % 2 else "naranja")
    # cuello y cabeza
    m.pieza("esfera", (0, -1.1, 4.6), (0.7, 0.7, 1.0), "carbon")
    m.pieza("esfera", (0, -1.35, 5.4), 0.66, "carbon", seg=14, anillos=9)
    # cresta de fuego (llamas hacia atras)
    for k, (y, alto) in enumerate(((-1.8, 0.55), (-1.5, 0.95), (-1.2, 1.15), (-0.9, 0.95), (-0.6, 0.7))):
        color = ("fuego_amarillo", "fuego_naranja", "fuego_rojo")[k % 3]
        m.entre((0, y, 5.85), (0, y + 0.35 + k * 0.1, 5.9 + alto), 0.2, color, "Brillo", lados=6)
    # pico de oro y barbillas
    m.entre((0, -1.85, 5.42), (0, -2.5, 5.25), 0.2, "oro", lados=6)
    m.entre((0, -1.85, 5.22), (0, -2.25, 5.15), 0.12, "oro_osc", lados=6)
    m.pieza("esfera", (0.1, -1.92, 4.95), (0.12, 0.12, 0.28), "rojo", espejo=True)
    # ojos de fuego y cejas de oro
    m.pieza("esfera", (0.33, -1.87, 5.55), (0.14, 0.1, 0.11), "rojo_brillo", "Brillo", espejo=True)
    m.pieza("cubo", (0.3, -1.93, 5.72), (0.42, 0.1, 0.1), "oro", rot=(0, -28, 0), espejo=True)
    # cuernos de oro curvos
    m.entre((0.4, -1.3, 5.85), (0.75, -0.9, 6.35), 0.15, "oro", punta=0.55, espejo=True)
    m.entre((0.75, -0.9, 6.35), (0.95, -0.2, 6.6), 0.083, "oro", espejo=True)
    # alas: abanico de plumas con puntas de fuego
    for k in range(5):
        base = (1.25, 0.0 + k * 0.12, 3.75)
        punta = (1.9 + k * 0.12, 0.3 + k * 0.45, 4.9 - k * 0.38)
        m.entre(base, punta, 0.3, "carbon", tipo="esfera", aplanar=0.35, espejo=True)
        m.entre(lerp(base, punta, 0.8), alargar(base, punta, 0.55), 0.13,
                ("fuego_naranja", "fuego_rojo")[k % 2], "Brillo", lados=6, espejo=True)
    # cola de fuego
    cola_de_gallo(m, (0, 1.5, 3.9), 1.15, fuego=True)
    # piernas con grebas de oro y navajas de palenque
    m.pieza("cilindro", (0.55, 0.1, 1.15), (0.16, 0.16, 2.0), "gris_osc", espejo=True)
    m.pieza("cono", (0.55, 0.1, 1.5), (0.26, 0.26, 0.8), "oro", lados=8, punta=0.7, espejo=True)
    patas_de_gallo(m, 0.55, 0.1, 0.12, navaja="plata")


def oso_gallo(m):
    """OsoGallo: bestia mitad oso mitad gallo. Cuerpo y garras de oso, cabeza, cresta, alas y cola de gallo."""
    cuerpo = ((0, 0, 3.5), (2.0, 1.7, 2.3))
    m.pieza("esfera", *cuerpo, "cafe", seg=16, anillos=10)
    # pecho cubierto de plumas
    for fila, (z, n) in enumerate(((4.7, 3), (3.95, 4), (3.2, 4), (2.45, 3))):
        for i in range(n):
            x = (i - (n - 1) / 2) * 0.62
            y = sobre_elipsoide(*cuerpo, x, z, dentro=0.12)
            m.pieza("esfera", (x, y, z), (0.4, 0.2, 0.55), "blanco" if (fila + i) % 2 else "crema", rot=(18, 0, 0),
                    seg=8, anillos=6)
    # melena de plumas en el cuello
    for k, ang in enumerate(range(0, 360, 30)):
        a = math.radians(ang)
        m.entre((0.7 * math.cos(a), -0.4 + 0.65 * math.sin(a), 5.9), (1.35 * math.cos(a), -0.4 + 1.2 * math.sin(a), 4.9),
                0.3, ("naranja", "rojo", "amarillo")[k % 3])
    # cabeza de gallo con orejas de oso
    m.pieza("esfera", (0, -0.6, 6.4), (0.95, 0.95, 0.9), "blanco", seg=16, anillos=10)
    m.pieza("esfera", (0.82, -0.25, 7.05), 0.33, "cafe", espejo=True)
    m.pieza("esfera", (0.82, -0.5, 7.05), (0.2, 0.1, 0.2), "beige", espejo=True)
    for k, (y, alto) in enumerate(((-1.25, 0.32), (-0.9, 0.45), (-0.5, 0.52), (-0.1, 0.42), (0.25, 0.3))):
        m.pieza("esfera", (0, y, 7.2 + alto * 0.5), (0.2, 0.26, alto), "rojo")
    m.entre((0, -1.38, 6.5), (0, -2.3, 6.25), 0.3, "amarillo", lados=6)
    m.entre((0, -1.38, 6.18), (0, -2.0, 6.05), 0.18, "oro_osc", lados=6)
    m.pieza("esfera", (0.16, -1.5, 5.7), (0.17, 0.15, 0.42), "rojo", espejo=True)
    m.pieza("esfera", (0.45, -1.38, 6.65), (0.16, 0.1, 0.15), "amarillo_brillo", "Brillo", espejo=True)
    m.pieza("cubo", (0.42, -1.46, 6.88), (0.48, 0.1, 0.12), "negro", rot=(0, -25, 0), espejo=True)
    m.pieza("cubo", (-0.45, -1.47, 6.62), (0.07, 0.05, 0.7), "rojo_osc", rot=(0, 30, 0))  # cicatriz
    # brazos de oso con brazaletes y garras
    m.pieza("esfera", (2.1, -0.3, 4.0), (0.72, 0.78, 1.5), "cafe", rot=(0, 15, 0), espejo=True)
    m.pieza("cilindro", (2.3, -0.35, 3.15), (0.66, 0.7, 0.42), "acero", lados=10, rot=(0, 15, 0), espejo=True)
    m.pieza("esfera", (2.45, -0.45, 2.45), (0.62, 0.68, 0.52), "cafe_osc", espejo=True)
    for k in range(3):
        x = 2.2 + k * 0.25
        m.entre((x, -0.95, 2.45), (x + 0.05, -1.5, 2.1), 0.09, "blanco", espejo=True)
    # alas de gallo en la espalda
    for k in range(4):
        base = (0.9, 1.25, 5.0)
        m.entre(base, (1.9 + k * 0.25, 2.3 + k * 0.2, 6.4 - k * 0.5), 0.32, "cafe_rojo", tipo="esfera",
                aplanar=0.35, espejo=True)
    # cola de gallo
    cola_de_gallo(m, (0, 1.3, 3.8), 1.4, ("verde_osc", "negro"))
    # cinturon de pelea
    m.pieza("cilindro", (0, 0, 2.35), (1.82, 1.55, 0.35), "cafe_osc", lados=16)
    m.pieza("cubo", (0, -1.6, 2.35), (0.65, 0.15, 0.48), "oro")
    # piernas de oso con patas de gallo
    m.pieza("esfera", (0.95, -0.1, 1.35), (0.85, 0.95, 1.1), "cafe", espejo=True)
    m.pieza("cilindro", (0.95, -0.1, 0.4), (0.24, 0.24, 0.6), "amarillo", espejo=True)
    patas_de_gallo(m, 0.95, -0.1, 0.12, largo=0.85, radio=0.14)


def oso_titan(m):
    """Oso Titan: oso de guerra que cuida el nido. Yelmo con cuernos, armadura, martillo de panal y ojos de miel."""
    m.pieza("esfera", (0, 0, 3.8), (2.3, 1.9, 2.6), "cafe_osc", seg=16, anillos=10)
    m.pieza("esfera", (0, -1.1, 3.4), (1.6, 0.85, 1.8), "cafe_claro")
    # coraza con emblema de panal
    m.pieza("esfera", (0, -1.45, 4.4), (1.65, 0.5, 1.25), "acero", seg=16, anillos=10)
    m.pieza("cilindro", (0, -1.95, 4.45), (0.5, 0.5, 0.12), "acero_osc", rot=(90, 0, 0), lados=6)
    m.pieza("cilindro", (0, -2.0, 4.45), (0.36, 0.36, 0.12), "miel", "Brillo", rot=(90, 0, 0), lados=6)
    # cabeza
    m.pieza("esfera", (0, -0.3, 7.1), (1.5, 1.4, 1.3), "cafe_osc", seg=14, anillos=9)
    m.pieza("esfera", (0, -1.5, 6.75), (0.78, 0.58, 0.52), "cafe_claro")
    m.pieza("esfera", (0, -2.02, 6.98), (0.3, 0.17, 0.2), "negro")
    for x in (0.38, -0.38):  # colmillos
        m.entre((x, -1.9, 6.55), (x * 0.9, -2.05, 6.05), 0.1, "hueso")
    # yelmo de guerra con cuernos
    m.pieza("esfera", (0, -0.3, 7.95), (1.55, 1.45, 0.95), "acero", seg=16, anillos=10)
    m.pieza("toro", (0, -0.3, 7.6), (1.55, 1.45, 1), "acero_osc", radio=1, grosor=0.12)
    m.pieza("cubo", (0, -1.72, 7.65), (0.22, 0.14, 0.6), "acero_osc")
    m.entre((1.25, -0.35, 8.2), (2.0, -0.5, 8.9), 0.28, "hueso", punta=0.5, espejo=True)
    m.entre((2.0, -0.5, 8.9), (2.15, -1.1, 9.7), 0.14, "hueso", espejo=True)
    # ojos de miel, cicatriz y pintura de guerra
    m.pieza("esfera", (0.55, -1.52, 7.25), (0.17, 0.1, 0.13), "naranja_brillo", "Brillo", espejo=True)
    m.pieza("cubo", (-0.55, -1.6, 7.2), (0.08, 0.05, 0.8), "rojo_osc", rot=(0, 25, 0))
    for dz in (0, -0.2):
        m.pieza("cubo", (1.0, -1.22, 6.85 + dz), (0.55, 0.08, 0.09), "rojo", rot=(0, -15, -20), espejo=True)
    # collar de picos
    m.pieza("toro", (0, -0.2, 6.05), (1.0, 0.9, 1.0), "cafe_osc", radio=1.55, grosor=0.2)
    for ang in range(0, 360, 36):
        a = math.radians(ang)
        b = (1.6 * math.cos(a), -0.2 + 1.42 * math.sin(a), 6.05)
        m.entre(b, (2.15 * math.cos(a), -0.2 + 1.9 * math.sin(a), 6.1), 0.13, "acero")
    # hombreras con picos
    m.pieza("esfera", (2.2, -0.2, 5.35), (0.95, 1.05, 0.65), "acero", espejo=True)
    m.pieza("toro", (2.2, -0.2, 5.15), (0.95, 1.05, 1), "acero_osc", radio=1, grosor=0.1, espejo=True)
    for dy in (-0.45, 0.0, 0.45):
        m.entre((2.45, -0.2 + dy, 5.8), (2.75, -0.2 + dy * 1.3, 6.6), 0.15, "hueso", espejo=True)
    # brazos, brazaletes, puños y garras
    m.pieza("esfera", (2.55, -0.3, 3.9), (0.82, 0.88, 1.7), "cafe_osc", rot=(0, 12, 0), espejo=True)
    m.pieza("cilindro", (2.75, -0.4, 3.0), (0.78, 0.82, 0.55), "acero_osc", lados=10, rot=(0, 12, 0), espejo=True)
    m.pieza("esfera", (2.85, -0.55, 2.2), (0.68, 0.72, 0.58), "cafe_claro", espejo=True)
    for k in range(3):
        x = 2.6 + k * 0.25
        m.entre((x, -1.1, 2.15), (x + 0.05, -1.65, 1.8), 0.1, "hueso", espejo=True)
    # martillo de guerra con cabeza de panal (mano derecha)
    m.entre((2.85, -0.7, 0.5), (2.85, -0.7, 5.9), 0.17, "madera", tipo="cilindro")
    m.pieza("cilindro", (2.85, -0.7, 6.1), (0.8, 0.8, 1.7), "acero_osc", rot=(0, 90, 0), lados=6)
    for lado in (-1, 1):
        m.pieza("cilindro", (2.85 + lado * 0.87, -0.7, 6.1), (0.6, 0.6, 0.08), "miel", "Brillo", rot=(0, 90, 0), lados=6)
    m.entre((2.85, -0.7, 6.9), (2.85, -0.7, 7.6), 0.18, "acero")
    # cinturon con botes de miel
    m.pieza("cilindro", (0, 0, 2.15), (2.08, 1.72, 0.4), "cafe", lados=16)
    m.pieza("cubo", (0, -1.75, 2.15), (0.7, 0.15, 0.55), "oro")
    for x in (-1.3, 1.3):
        m.pieza("cilindro", (x, -1.25, 1.85), (0.35, 0.35, 0.55), "miel", lados=8)
        m.pieza("cilindro", (x, -1.25, 2.18), (0.3, 0.3, 0.12), "madera", lados=8)
    # piernas y pies
    m.pieza("esfera", (1.05, -0.1, 1.15), (0.95, 1.0, 1.15), "cafe_osc", espejo=True)
    m.pieza("esfera", (1.05, -0.6, 0.28), (0.75, 0.85, 0.32), "cafe_claro", espejo=True)
    for k in range(3):
        m.entre((0.8 + k * 0.25, -1.35, 0.25), (0.8 + k * 0.27, -1.7, 0.1), 0.09, "hueso", espejo=True)


def nido_dorado(m):
    """Nido con huevos normales, uno manchado y un huevo de oro brillante."""
    rnd = random.Random(7)
    m.pieza("toro", (0, 0, 0.4), (1, 1, 0.75), "madera", radio=1.6, grosor=0.5, seg=20)
    m.pieza("esfera", (0, 0, 0.25), (1.6, 1.6, 0.3), "paja", seg=16)
    for k in range(18):  # ramitas
        a = math.radians(k * 20 + rnd.uniform(-8, 8))
        c = (1.65 * math.cos(a), 1.65 * math.sin(a), 0.4 + rnd.uniform(-0.2, 0.3))
        t = (-math.sin(a), math.cos(a), rnd.uniform(-0.4, 0.4))
        largo = rnd.uniform(0.7, 1.1)
        m.entre(tuple(c[i] - t[i] * largo for i in range(3)), tuple(c[i] + t[i] * largo for i in range(3)),
                0.06, ("madera", "cafe_osc", "paja")[k % 3], tipo="cilindro", lados=5)
    huevos = ((0.65, 0.3, "blanco"), (-0.55, 0.45, "crema"), (0.05, -0.65, "blanco"), (-0.6, -0.35, "crema"))
    for x, y, color in huevos:
        m.pieza("esfera", (x, y, 0.75), (0.3, 0.3, 0.4), color, rot=(rnd.uniform(-15, 15), rnd.uniform(-15, 15), 0))
    for k in range(6):  # manchas del huevo crema
        a = math.radians(k * 60)
        m.pieza("esfera", (-0.55 + 0.28 * math.cos(a), 0.45 + 0.28 * math.sin(a), 0.7 + (k % 3) * 0.12), 0.06, "cafe")
    m.pieza("esfera", (0, 0.15, 0.85), (0.38, 0.38, 0.5), "oro_brillo", "Brillo", seg=14, anillos=9)


def abeja_cristal(m):
    """Abeja Reina de Cristal (secreta): cristales en la espalda, 6 alas, corona de cristal y cetro."""
    m.pieza("esfera", (0, 0, 3.0), (0.95, 0.95, 0.9), "plata", seg=14, anillos=9)
    for ang in range(0, 360, 40):  # cuello de pelusa
        a = math.radians(ang)
        m.pieza("esfera", (0.75 * math.cos(a), -0.55, 3.0 + 0.7 * math.sin(a)), 0.3, "blanco")
    m.pieza("esfera", (0, 1.6, 2.75), (1.1, 1.6, 1.1), "azul_profundo", rot=(-15, 0, 0), seg=16, anillos=10)
    for dy, r in ((-0.6, 1.05), (0.05, 1.13), (0.7, 0.95)):
        m.pieza("toro", (0, 1.6 + dy, 2.75 - dy * 0.27), 1, "cian", "Brillo", rot=(75, 0, 0), radio=r, grosor=0.1)
    # cristales en la espalda
    cristales = ((0, 1.0, 3.7, 0, 0.6, 4.9), (0.45, 1.5, 3.6, 0.9, 1.9, 4.6), (-0.45, 1.5, 3.6, -0.9, 1.9, 4.6),
                 (0, 2.0, 3.55, 0, 2.6, 4.7), (0.4, 2.4, 3.25, 0.8, 3.2, 4.0), (-0.4, 2.4, 3.25, -0.8, 3.2, 4.0))
    for k, c in enumerate(cristales):
        m.entre(c[:3], c[3:], 0.24 if k == 0 else 0.18, "blanco_cian" if k % 2 else "cian", "Brillo", lados=5)
    m.pieza("esfera", (0, -1.05, 3.3), 0.8, "azul_profundo", seg=14, anillos=9)
    m.pieza("esfera", (0.42, -1.6, 3.45), (0.32, 0.24, 0.4), "blanco_cian", "Brillo", espejo=True)
    # antenas curvas con orbes
    m.entre((0.25, -1.4, 3.95), (0.45, -1.8, 4.6), 0.05, "plata", tipo="cilindro", espejo=True)
    m.entre((0.45, -1.8, 4.6), (0.7, -1.7, 5.0), 0.05, "plata", tipo="cilindro", espejo=True)
    m.pieza("ico", (0.7, -1.7, 5.05), 0.17, "magenta", "Brillo", espejo=True)
    # corona de cristal
    m.pieza("cilindro", (0, -0.95, 4.0), (0.48, 0.48, 0.22), "plata", lados=10)
    for k in range(5):
        a = math.radians(k * 72 + 90)
        x, y = 0.42 * math.cos(a), -0.95 + 0.42 * math.sin(a)
        m.entre((x, y, 4.05), (x * 1.3, y + 0.42 * math.sin(a) * 0.3, 4.75 if k == 0 else 4.5), 0.12,
                "cian", "Brillo", lados=4)
    m.pieza("ico", (0, -1.4, 4.0), 0.14, "magenta", "Brillo")
    # aguijon de cristal
    m.entre((0, 3.05, 2.4), (0, 4.1, 1.95), 0.25, "blanco_cian", "Brillo", lados=5)
    # 6 alas
    m.pieza("esfera", (1.55, 0.2, 4.1), (1.65, 0.7, 0.05), "ala", "Alas", rot=(0, -25, -20), espejo=True)
    m.pieza("esfera", (1.35, 0.75, 3.75), (1.25, 0.5, 0.05), "ala", "Alas", rot=(0, -15, -40), espejo=True)
    m.pieza("esfera", (1.05, 1.15, 3.3), (0.85, 0.35, 0.05), "ala", "Alas", rot=(0, -5, -60), espejo=True)
    # patas y cetro
    for y in (-0.35, 0.0, 0.35):
        m.entre((0.5, y, 2.4), (0.85, y - 0.1, 1.5), 0.06, "plata", tipo="cilindro", espejo=True)
    m.entre((0.55, -0.6, 2.4), (0.35, -1.55, 2.2), 0.06, "plata", tipo="cilindro")
    m.entre((0.4, -1.6, 2.0), (0.25, -1.55, 3.4), 0.06, "plata", tipo="cilindro")
    m.pieza("ico", (0.25, -1.55, 3.55), 0.22, "cian", "Brillo")


def abeja_guerrera(m):
    """Abeja Guerrera: armadura espartana, casco con penacho, lanza y escudo de panal."""
    m.pieza("esfera", (0, 0, 3.0), (0.95, 0.95, 0.9), "negro", seg=14, anillos=9)
    m.pieza("esfera", (0, -0.45, 3.0), (0.85, 0.6, 0.82), "oro", seg=14, anillos=9)
    m.pieza("esfera", (0, 1.5, 2.7), (1.0, 1.5, 1.0), "amarillo", rot=(-15, 0, 0), seg=16, anillos=10)
    for dy, r in ((-0.55, 0.96), (0.05, 1.03), (0.65, 0.86)):
        m.pieza("toro", (0, 1.5 + dy, 2.7 - dy * 0.27), 1, "negro", rot=(75, 0, 0), radio=r, grosor=0.14)
    m.entre((0, 2.9, 2.32), (0, 3.4, 2.15), 0.2, "negro", lados=6)
    m.entre((0, 3.4, 2.15), (0, 3.85, 2.0), 0.1, "acero", lados=6)
    # cabeza y casco con penacho
    m.pieza("esfera", (0, -1.05, 3.3), 0.78, "amarillo", seg=14, anillos=9)
    m.pieza("esfera", (0, -1.0, 3.5), (0.86, 0.86, 0.72), "oro_osc", seg=14, anillos=9)
    m.pieza("cubo", (0, -1.83, 3.25), (0.16, 0.1, 0.55), "oro_osc")
    for k in range(7):
        y = -1.6 + k * 0.32
        m.pieza("esfera", (0, y, 4.3 - (0.0 if k < 5 else (k - 4) * 0.25)), (0.13, 0.22, 0.42), "rojo")
    m.pieza("esfera", (0.38, -1.68, 3.2), (0.22, 0.14, 0.2), "rojo_brillo", "Brillo", espejo=True)
    m.entre((0.25, -1.65, 2.85), (0.05, -2.0, 2.7), 0.08, "negro", espejo=True)  # mandibulas
    m.entre((0.3, -1.1, 4.1), (0.55, -1.6, 4.6), 0.04, "negro", tipo="cilindro", espejo=True)
    # alas
    m.pieza("esfera", (1.3, 0.3, 3.9), (1.4, 0.6, 0.05), "ala", "Alas", rot=(0, -20, -25), espejo=True)
    m.pieza("esfera", (1.05, 0.9, 3.5), (0.95, 0.42, 0.05), "ala", "Alas", rot=(0, -10, -45), espejo=True)
    # patas
    for y in (-0.3, 0.05, 0.4):
        m.entre((0.5, y, 2.4), (0.9, y - 0.1, 1.4), 0.07, "negro", tipo="cilindro", espejo=True)
    # lanza (derecha)
    m.entre((0.6, -0.5, 2.6), (1.05, -1.0, 2.6), 0.07, "negro", tipo="cilindro")
    m.entre((1.1, 0.3, 0.9), (1.1, -2.1, 5.3), 0.07, "madera", tipo="cilindro")
    m.entre((1.1, -2.1, 5.3), (1.1, -2.45, 6.15), 0.18, "acero", lados=4)
    m.pieza("esfera", (1.1, -2.02, 5.1), (0.12, 0.12, 0.2), "rojo")
    # escudo de panal (izquierda)
    m.entre((-0.6, -0.5, 2.6), (-1.1, -0.7, 2.7), 0.07, "negro", tipo="cilindro")
    m.pieza("cilindro", (-1.2, -0.7, 2.8), (1.0, 1.0, 0.14), "oro", rot=(0, 90, 0), lados=6)
    m.pieza("cilindro", (-1.26, -0.7, 2.8), (0.82, 0.82, 0.12), "oro_osc", rot=(0, 90, 0), lados=6)
    for dy, dz in ((0, 0), (0.3, 0.17), (-0.3, 0.17), (0.3, -0.17), (-0.3, -0.17), (0, 0.35), (0, -0.35)):
        m.pieza("cilindro", (-1.32, -0.7 + dy, 2.8 + dz), (0.13, 0.13, 0.1), "miel", "Brillo", rot=(0, 90, 0), lados=6)


MODELOS = {
    "AbejaEclipse": abeja_secreta, "GalloGuardian": gallo_guardian, "OsoGuardian": oso_guardian,
    "GalloInfernal": gallo_infernal, "OsoGallo": oso_gallo, "OsoTitan": oso_titan, "NidoDorado": nido_dorado,
    "AbejaCristal": abeja_cristal, "AbejaGuerrera": abeja_guerrera,
}
# Orden y posicion en el poster: (modelo, x, y)
POSTER = (("AbejaGuerrera", -12.5, 0.5), ("GalloInfernal", -7.0, 0), ("OsoTitan", 0, 1.0), ("NidoDorado", 0, -2.6),
          ("OsoGallo", 7.0, 0), ("AbejaCristal", 12.5, 0.5))


# ================================================================ render y exportacion

def limpiar():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def materiales_vista_previa(objs, img):
    """Solo para la imagen: lo que brilla emite luz y las alas son transparentes."""
    brillo = material("brillo_preview", img, emision=2.5)
    for o in objs:
        if o.name.startswith("Brillo"):
            o.data.materials[0] = brillo


def preparar_render(objs, ruta, ancho=900, alto=900, poster=False):
    esc = bpy.context.scene
    esc.render.engine = "CYCLES"
    esc.cycles.device = "CPU"
    esc.cycles.samples = 64
    esc.render.resolution_x, esc.render.resolution_y = ancho, alto
    esc.render.filepath = ruta
    esc.view_settings.view_transform = "Standard"
    mundo = bpy.data.worlds.new("cielo")
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs["Color"].default_value = (0.09, 0.06, 0.14, 1)
    mundo.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    esc.world = mundo
    puntos = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    minimo = Vector([min(p[i] for p in puntos) for i in range(3)])
    maximo = Vector([max(p[i] for p in puntos) for i in range(3)])
    centro = (minimo + maximo) / 2
    tam = max(maximo - minimo)
    # piso
    bpy.ops.mesh.primitive_plane_add(size=tam * 8, location=(centro.x, centro.y, minimo.z))
    piso = bpy.context.active_object
    mat = bpy.data.materials.new("piso")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.13, 0.1, 0.09, 1)
    piso.data.materials.append(mat)
    # camara
    if poster:
        dist = (maximo.x - minimo.x) * 1.25
        pos = centro + Vector((dist * 0.08, -dist, dist * 0.2))
    else:
        dist = tam * 1.9
        pos = centro + Vector((dist * 0.55, -dist * 0.95, dist * 0.3))
    bpy.ops.object.camera_add(location=pos)
    cam = bpy.context.active_object
    cam.data.lens = 45
    rastreo = cam.constraints.new("TRACK_TO")
    bpy.ops.object.empty_add(location=centro)
    rastreo.target = bpy.context.active_object
    esc.camera = cam
    # luces: principal, contraluz calido y relleno frio
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(45), math.radians(10), math.radians(25)))
    bpy.context.active_object.data.energy = 3.0
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(-60), 0, math.radians(200)))
    bpy.context.active_object.data.energy = 4.0
    bpy.context.active_object.data.color = (1.0, 0.55, 0.25)
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(60), 0, math.radians(-70)))
    bpy.context.active_object.data.energy = 1.2
    bpy.context.active_object.data.color = (0.5, 0.6, 1.0)
    # resplandor alrededor de lo que brilla
    esc.use_nodes = True
    arbol = esc.node_tree
    capas = arbol.nodes.get("Render Layers") or arbol.nodes.new("CompositorNodeRLayers")
    salida = arbol.nodes.get("Composite") or arbol.nodes.new("CompositorNodeComposite")
    glare = arbol.nodes.new("CompositorNodeGlare")
    glare.glare_type = "FOG_GLOW"
    glare.quality = "HIGH"
    glare.threshold = 1.0
    glare.size = 8
    arbol.links.new(capas.outputs["Image"], glare.inputs["Image"])
    arbol.links.new(glare.outputs["Image"], salida.inputs["Image"])
    bpy.ops.render.render(write_still=True)


def construir(nombre, img, desplazar=(0, 0, 0)):
    modelo = Modelo(nombre, desplazar)
    MODELOS[nombre](modelo)
    return modelo, modelo.unir(img)


def exportar(nombre):
    limpiar()
    carpeta = os.path.join(RAIZ, nombre)
    os.makedirs(carpeta, exist_ok=True)
    img = crear_paleta(os.path.join(carpeta, "paleta.png"))
    _, objs = construir(nombre, img)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=os.path.join(carpeta, f"{nombre}.fbx"), use_selection=True,
                             path_mode="COPY", embed_textures=True, apply_unit_scale=True,
                             global_scale=1.0, mesh_smooth_type="FACE")
    tris = sum(len(p.vertices) - 2 for o in objs for p in o.data.polygons)
    print(f"{nombre}: {len(objs)} piezas ({', '.join(o.name for o in objs)}), ~{tris} triangulos")
    materiales_vista_previa(objs, img)
    preparar_render(objs, os.path.join(carpeta, "vista_previa.png"))


def poster():
    limpiar()
    img = crear_paleta(os.path.join(RAIZ, "paleta.png"))
    objs = []
    for nombre, x, y in POSTER:
        objs += construir(nombre, img, (x, y, 0))[1]
    materiales_vista_previa(objs, img)
    preparar_render(objs, os.path.join(RAIZ, "poster_epico.png"), ancho=1920, alto=820, poster=True)
    os.remove(os.path.join(RAIZ, "paleta.png"))


if __name__ == "__main__":
    pedidos = [a for a in sys.argv[1:] if a in MODELOS or a == "poster"] or [*MODELOS, "poster"]
    for nombre in pedidos:
        poster() if nombre == "poster" else exportar(nombre)
