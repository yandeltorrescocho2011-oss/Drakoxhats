"""Motor para crear criaturas animadas para Roblox con Blender (bpy).

Cada criatura se arma con PARTES que se mueven (Cuerpo, Cabeza, AlaIzq, AlaDer, Cola, PataIzq...).
Cada parte tiene un PADRE y un punto de UNION (la articulacion donde gira).

Convenciones (coordenadas de Blender, 1 unidad = 1 stud de Roblox):
  - El frente de la criatura mira hacia -Y, arriba es +Z, el piso esta en Z = 0.
  - El lado IZQUIERDO de la criatura es +X y el DERECHO es -X.
  - Las piezas con espejo=True se copian al otro lado; si la parte termina en "Izq",
    la copia va a la parte "Der" (y viceversa).

Ejes de animacion (marco de cada articulacion, igual que Motor6D.Transform en Roblox):
  X = derecha de la criatura, Y = arriba, Z = atras.
  rx > 0: la parte se inclina hacia ATRAS (la cabeza mira arriba);  rx < 0: hacia adelante/abajo.
  ry > 0: gira hacia la IZQUIERDA de la criatura.
  rz > 0: el lado derecho sube (rodar). Ala IZQUIERDA arriba = rz < 0; ala DERECHA arriba = rz > 0.
  px, py, pz: desplazamiento en studs (derecha, arriba, atras).
"""
import json
import math
import os
import random

import bpy
from mathutils import Matrix, Vector

# ------------------------------------------------------------------ paleta

COLORES_BASE = {
    "negro": (0.05, 0.04, 0.06), "blanco": (0.95, 0.95, 0.92), "crema": (0.98, 0.90, 0.75),
    "gris": (0.45, 0.45, 0.48), "gris_osc": (0.18, 0.17, 0.19), "carbon": (0.05, 0.045, 0.05),
    "rojo": (0.85, 0.08, 0.08), "rojo_osc": (0.40, 0.03, 0.03), "naranja": (0.95, 0.45, 0.10),
    "amarillo": (1.00, 0.82, 0.20), "oro": (1.00, 0.76, 0.12), "oro_osc": (0.70, 0.45, 0.05),
    "cafe": (0.42, 0.24, 0.10), "cafe_osc": (0.25, 0.12, 0.05), "cafe_claro": (0.60, 0.38, 0.18),
    "beige": (0.80, 0.62, 0.40), "madera": (0.45, 0.28, 0.12), "paja": (0.80, 0.65, 0.30),
    "verde": (0.10, 0.55, 0.20), "verde_osc": (0.03, 0.25, 0.15), "azul": (0.10, 0.30, 0.85),
    "azul_osc": (0.04, 0.08, 0.30), "morado": (0.42, 0.16, 0.70), "morado_osc": (0.16, 0.05, 0.28),
    "rosa": (1.00, 0.55, 0.70), "acero": (0.55, 0.58, 0.62), "acero_osc": (0.30, 0.32, 0.36),
    "plata": (0.80, 0.82, 0.88), "hueso": (0.92, 0.88, 0.75), "piel": (0.95, 0.70, 0.55),
    "ojo_blanco": (1.00, 1.00, 1.00),
}
CELDA, TAM = 16, 128  # paleta de 8x8 cuadros de 16 px = hasta 64 colores


class Paleta:
    def __init__(self, extra=None):
        self.colores = dict(COLORES_BASE)
        self.colores.update(extra or {})
        if len(self.colores) > 64:
            raise ValueError("Maximo 64 colores por criatura")
        self.nombres = list(self.colores)
        self.imagen = None

    def uv(self, color):
        if color not in self.colores:
            raise KeyError(f"Color desconocido: {color}. Agregalo en COLORES_EXTRA.")
        i = self.nombres.index(color)
        return (((i % 8) * CELDA + CELDA / 2) / TAM, ((i // 8) * CELDA + CELDA / 2) / TAM)

    def rgb255(self, color):
        return tuple(round(x * 255) for x in self.colores[color])

    def crear_imagen(self, ruta):
        img = bpy.data.images.new("paleta", TAM, TAM, alpha=False)
        img.colorspace_settings.name = "sRGB"
        px = [0.0] * (TAM * TAM * 4)
        for i, nombre in enumerate(self.nombres):
            cx, cy = (i % 8) * CELDA, (i // 8) * CELDA
            r, g, b = self.colores[nombre]
            for y in range(cy, cy + CELDA):
                for x in range(cx, cx + CELDA):
                    j = (y * TAM + x) * 4
                    px[j:j + 4] = [r, g, b, 1.0]
        img.pixels = px
        img.filepath_raw = ruta
        img.file_format = "PNG"
        img.save()
        self.imagen = img
        return img


# ------------------------------------------------------------------ utilidades geometricas

def lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def alargar(a, b, extra):
    """Punto que sigue la direccion a->b una distancia extra mas alla de b."""
    d = (Vector(b) - Vector(a)).normalized()
    return tuple(Vector(b) + d * extra)


def sobre_elipsoide(centro, radios, x, z, dentro=0.05):
    """Coordenada Y del frente (-Y) de un elipsoide, para pegar piezas en su superficie."""
    cx, cy, cz = centro
    rx, ry, rz = radios
    k = 1 - ((x - cx) / rx) ** 2 - ((z - cz) / rz) ** 2
    return cy - ry * math.sqrt(max(k, 0)) + dentro


def _lado_opuesto(parte):
    if parte.endswith("Izq"):
        return parte[:-3] + "Der"
    if parte.endswith("Der"):
        return parte[:-3] + "Izq"
    return parte


# ------------------------------------------------------------------ criatura

class Criatura:
    def __init__(self, nombre, paleta, desplazar=(0, 0, 0)):
        self.nombre = nombre
        self.paleta = paleta
        self.desplazar = Vector(desplazar)
        self.partes = {"Cuerpo": {"padre": None, "union": None}}
        self.actual = "Cuerpo"
        self.grupos = {}  # nombre del objeto final -> lista de objetos sueltos
        self.grupo_parte = {}  # nombre del objeto final -> parte a la que pertenece

    # ---- partes y articulaciones
    def parte(self, nombre, padre, union, espejo=False):
        """Declara una parte movible. union = punto (x,y,z) donde gira. Con espejo=True
        tambien declara la parte del otro lado (Izq <-> Der) con la union reflejada."""
        if padre not in self.partes:
            raise KeyError(f"La parte padre {padre} no existe todavia")
        self.partes[nombre] = {"padre": padre, "union": tuple(union)}
        if espejo:
            otro = _lado_opuesto(nombre)
            otro_padre = _lado_opuesto(padre)
            if otro == nombre:
                raise ValueError("espejo=True necesita una parte que termine en Izq o Der")
            self.partes[otro] = {"padre": otro_padre, "union": (-union[0], union[1], union[2])}
        return self

    def usar(self, parte):
        """Las siguientes piezas se agregan a esta parte."""
        if parte not in self.partes:
            raise KeyError(f"Parte desconocida: {parte}")
        self.actual = parte
        return self

    # ---- piezas
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
            bpy.ops.mesh.primitive_torus_add(major_segments=kw.get("seg", 16), minor_segments=kw.get("seg_menor", 6),
                                             major_radius=kw["radio"], minor_radius=kw["grosor"])
        else:
            raise ValueError(f"Tipo de pieza desconocido: {tipo}")
        return bpy.context.active_object

    def _terminar(self, obj, color, parte, brillo, vidrio):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        u, v = self.paleta.uv(color)
        uv = obj.data.uv_layers.active or obj.data.uv_layers.new()
        for loop in uv.data:
            loop.uv = (u, v)
        for p in obj.data.polygons:
            p.use_smooth = False
        if brillo:
            grupo = f"{parte}__Brillo_{color}"
        elif vidrio:
            grupo = f"{parte}__Vidrio"
        else:
            grupo = parte
        self.grupos.setdefault(grupo, []).append(obj)
        self.grupo_parte[grupo] = parte
        return obj

    def pieza(self, tipo, pos, esc=(1, 1, 1), color="negro", rot=(0, 0, 0), espejo=False, parte=None,
              brillo=False, vidrio=False, **kw):
        """Agrega una pieza. pos y rot (grados) en coordenadas del mundo. brillo=True la hace Neon en Roblox;
        vidrio=True la hace semitransparente (alas, cristales)."""
        parte = parte or self.actual
        if espejo:
            self.pieza(tipo, pos, esc, color, rot, False, parte, brillo, vidrio, **kw)
            pos = (-pos[0], pos[1], pos[2])
            rot = (rot[0], -rot[1], -rot[2])
            parte = _lado_opuesto(parte)
        if parte not in self.partes:
            raise KeyError(f"Parte desconocida: {parte}")
        if isinstance(esc, (int, float)):
            esc = (esc, esc, esc)
        obj = self._crear(tipo, kw)
        obj.location = Vector(pos) + self.desplazar
        obj.scale = esc
        obj.rotation_euler = tuple(math.radians(a) for a in rot)
        return self._terminar(obj, color, parte, brillo, vidrio)

    def entre(self, a, b, radio, color="negro", tipo="cono", aplanar=1.0, espejo=False, parte=None,
              brillo=False, vidrio=False, **kw):
        """Pieza que va del punto a al punto b (cuernos, plumas, garras, picos, palos...)."""
        parte = parte or self.actual
        if espejo:
            self.entre(a, b, radio, color, tipo, aplanar, False, parte, brillo, vidrio, **kw)
            a, b = (-a[0], a[1], a[2]), (-b[0], b[1], b[2])
            parte = _lado_opuesto(parte)
        if parte not in self.partes:
            raise KeyError(f"Parte desconocida: {parte}")
        a, b = Vector(a), Vector(b)
        d = b - a
        if d.length < 1e-6:
            raise ValueError("entre(): los puntos a y b son iguales")
        obj = self._crear(tipo, kw)
        obj.location = (a + b) / 2 + self.desplazar
        largo = d.length / 2 if tipo == "esfera" else d.length
        obj.scale = (radio, radio * aplanar, largo)
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = d.to_track_quat("Z", "Y")
        return self._terminar(obj, color, parte, brillo, vidrio)

    # ---- armado final
    def unir(self):
        """Une las piezas de cada grupo en un objeto (una MeshPart en Roblox).
        Devuelve {nombre_objeto: objeto} y agrega los marcadores _Frente y _Arriba."""
        img = self.paleta.imagen
        mat = _material(f"{self.nombre}_mat", img)
        mat_brillo = _material(f"{self.nombre}_brillo", img, emision=2.5)
        mat_vidrio = _material(f"{self.nombre}_vidrio", img, alfa=0.45)
        faltan = [p for p in self.partes if p not in self.grupo_parte.values()]
        if faltan:
            raise ValueError(f"Partes sin piezas: {faltan}")
        objetos = {}
        for grupo, objs in self.grupos.items():
            bpy.ops.object.select_all(action="DESELECT")
            for o in objs:
                o.select_set(True)
            bpy.context.view_layer.objects.active = objs[0]
            if len(objs) > 1:
                bpy.ops.object.join()
            obj = bpy.context.active_object
            obj.name = obj.data.name = grupo
            obj.data.materials.clear()
            obj.data.materials.append(mat_brillo if "__Brillo" in grupo else mat_vidrio if "__Vidrio" in grupo else mat)
            bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
            objetos[grupo] = obj
        self.objetos = objetos
        self.centro = _centro_limites(objetos["Cuerpo"])
        # Marcadores para que el script de Roblox sepa donde es el frente y arriba aunque
        # el importador gire o escale el modelo.
        for nombre, delta in (("_Frente", (0, -DIST_MARCADOR, 0)), ("_Arriba", (0, 0, DIST_MARCADOR))):
            bpy.ops.mesh.primitive_cube_add(size=0.2, location=self.centro + Vector(delta))
            m = bpy.context.active_object
            m.name = m.data.name = nombre
            m.data.materials.append(mat)
            objetos[nombre] = m
        return objetos

    def rig(self):
        """Datos de las articulaciones en el marco del cuerpo (f = adelante, r = derecha, u = arriba)
        relativos al centro del Cuerpo."""
        c = self.centro

        def marco(p):
            p = Vector(p) + self.desplazar
            return [round(-(p.y - c.y), 4), round(-(p.x - c.x), 4), round(p.z - c.z, 4)]

        minimo = min((o.matrix_world @ v.co).z for n, o in self.objetos.items() if not n.startswith("_")
                     for v in o.data.vertices)
        partes = {}
        for nombre, d in self.partes.items():
            if nombre == "Cuerpo":
                continue
            partes[nombre] = {"padre": d["padre"], "union": marco(d["union"])}
        adjuntos = {g: p for g, p in self.grupo_parte.items() if g != p}
        return {"marcador": DIST_MARCADOR, "suelo": round(minimo - c.z, 4), "partes": partes, "adjuntos": adjuntos}


DIST_MARCADOR = 2.0


def _centro_limites(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return Vector([(min(p[i] for p in pts) + max(p[i] for p in pts)) / 2 for i in range(3)])


def _material(nombre, img, alfa=1.0, emision=0.0):
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


# ------------------------------------------------------------------ animacion (misma matematica que Roblox)

CANALES = ("rx", "ry", "rz", "px", "py", "pz")


def espejar_animacion(anim):
    """Si hay animacion para 'XIzq' y no para 'XDer', crea la del otro lado (ry, rz y px cambian de signo)."""
    signo = {"ry": -1, "rz": -1, "px": -1}
    nuevo = dict(anim)
    for parte, oscs in anim.items():
        otro = _lado_opuesto(parte)
        if otro != parte and otro not in anim:
            nuevo[otro] = [(c, a * signo.get(c, 1), f, fase) for c, a, f, fase in oscs]
    return nuevo


def espejar_claves(claves):
    salida = []
    for t, pose in claves:
        p = dict(pose)
        for parte, canales in pose.items():
            otro = _lado_opuesto(parte)
            if otro != parte and otro not in pose:
                p[otro] = {c: v * (-1 if c in ("ry", "rz", "px") else 1) for c, v in canales.items()}
        salida.append((t, p))
    return salida


def normalizar_animaciones(anims):
    """Aplica el espejo automatico a todos los ciclos y clips."""
    salida = {}
    for nombre, datos in anims.items():
        if nombre == "clips":
            salida["clips"] = {n: {"duracion": c["duracion"], "claves": espejar_claves(c["claves"])}
                               for n, c in datos.items()}
        else:
            salida[nombre] = espejar_animacion(datos)
    return salida


def evaluar_ciclo(ciclo, t):
    """{parte: {canal: valor}} de un ciclo de osciladores (canal, amplitud, frecuencia Hz, fase 0-1)."""
    pose = {}
    for parte, oscs in ciclo.items():
        d = pose.setdefault(parte, {})
        for canal, amp, frec, fase in oscs:
            d[canal] = d.get(canal, 0.0) + amp * math.sin(2 * math.pi * (frec * t + fase))
    return pose


def _suave(x):
    return x * x * (3 - 2 * x)


def evaluar_clip(clip, t):
    claves = clip["claves"]
    if not claves:
        return {}
    if t <= claves[0][0]:
        return claves[0][1]
    for (t0, p0), (t1, p1) in zip(claves, claves[1:]):
        if t0 <= t <= t1:
            k = _suave((t - t0) / max(t1 - t0, 1e-6))
            pose = {}
            for parte in set(p0) | set(p1):
                a, b = p0.get(parte, {}), p1.get(parte, {})
                pose[parte] = {c: a.get(c, 0.0) + (b.get(c, 0.0) - a.get(c, 0.0)) * k for c in set(a) | set(b)}
            return pose
    return claves[-1][1]


def sumar_poses(*poses_y_pesos):
    total = {}
    for pose, peso in poses_y_pesos:
        for parte, canales in pose.items():
            d = total.setdefault(parte, {})
            for c, v in canales.items():
                d[c] = d.get(c, 0.0) + v * peso
    return total


def matriz_canales(canales):
    """Igual que CFrame.new(px,py,pz) * CFrame.Angles(rx,ry,rz) en Roblox (marco X=der, Y=arriba, Z=atras)."""
    rx, ry, rz = (math.radians(canales.get(c, 0.0)) for c in ("rx", "ry", "rz"))
    rot = Matrix.Rotation(rx, 4, "X") @ Matrix.Rotation(ry, 4, "Y") @ Matrix.Rotation(rz, 4, "Z")
    return Matrix.Translation((canales.get("px", 0.0), canales.get("py", 0.0), canales.get("pz", 0.0))) @ rot


# Base del marco de articulacion en coordenadas de Blender: columnas = derecha, arriba, atras.
_BASE = Matrix(((-1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def aplicar_pose(criatura, pose, reposo):
    """Mueve los objetos de Blender segun la pose (misma formula que los Motor6D de Roblox)."""
    deltas = {}

    def delta(parte):
        if parte in deltas:
            return deltas[parte]
        if parte == "Cuerpo":
            union = criatura.centro
            padre = Matrix.Identity(4)
            canales = pose.get("Raiz", {})
        else:
            datos = criatura.partes[parte]
            union = Vector(datos["union"]) + criatura.desplazar
            padre = delta(datos["padre"])
            canales = pose.get(parte, {})
        j = Matrix.Translation(union) @ _BASE
        deltas[parte] = padre @ j @ matriz_canales(canales) @ j.inverted()
        return deltas[parte]

    for grupo, obj in criatura.objetos.items():
        if grupo.startswith("_"):
            continue
        obj.matrix_world = delta(criatura.grupo_parte[grupo]) @ reposo[grupo]


# ------------------------------------------------------------------ exportar a Luau

def a_luau(valor, sangria=0):
    esp = "\t" * sangria
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, (int, float)):
        return repr(round(valor, 4)) if isinstance(valor, float) else str(valor)
    if isinstance(valor, str):
        return json.dumps(valor, ensure_ascii=False)
    if isinstance(valor, Color):
        return f"Color3.fromRGB({valor.r}, {valor.g}, {valor.b})"
    if isinstance(valor, (list, tuple)):
        if not valor:
            return "{}"
        if all(not isinstance(v, (dict, list, tuple)) for v in valor):
            return "{ " + ", ".join(a_luau(v) for v in valor) + " }"
        return "{\n" + "".join(f"{esp}\t{a_luau(v, sangria + 1)},\n" for v in valor) + esp + "}"
    if isinstance(valor, dict):
        if not valor:
            return "{}"
        lineas = []
        for k, v in valor.items():
            clave = k if (isinstance(k, str) and k.isidentifier()) else f"[{a_luau(k)}]"
            lineas.append(f"{esp}\t{clave} = {a_luau(v, sangria + 1)},\n")
        return "{\n" + "".join(lineas) + esp + "}"
    raise TypeError(f"No se puede convertir a Luau: {valor!r}")


class Color:
    """Color para Roblox (0-255)."""

    def __init__(self, r, g, b):
        self.r, self.g, self.b = int(r), int(g), int(b)


def config_luau(criatura, config, anims):
    """Arma el ModuleScript de configuracion de la criatura."""
    datos = {k: v for k, v in config.items() if k != "animaciones"}
    datos["tipo"] = criatura.nombre
    datos["rig"] = criatura.rig()
    # Colores de las piezas que brillan (se ponen en Neon con su color exacto).
    datos["coloresBrillo"] = {g: Color(*criatura.paleta.rgb255(g.split("__Brillo_")[1]))
                              for g in criatura.grupo_parte if "__Brillo_" in g}

    def oscs(ciclo):
        return {p: [list(o) for o in lista] for p, lista in ciclo.items()}

    datos["animaciones"] = {
        "ciclos": {n: oscs(c) for n, c in anims.items() if n != "clips"},
        "clips": {n: {"duracion": c["duracion"], "claves": [{"t": t, "pose": pose} for t, pose in c["claves"]]}
                  for n, c in anims.get("clips", {}).items()},
    }
    return ("-- Generado por herramientas/criaturas/generar.py. No lo edites a mano: cambia el archivo\n"
            f"-- herramientas/criaturas/{criatura.nombre.lower()}.py y vuelve a generar.\n"
            "return " + a_luau(datos) + "\n")


def convertir_colores(valor):
    """En CONFIG los colores se escriben como ("rgb", r, g, b); aqui se vuelven Color()."""
    if isinstance(valor, tuple) and len(valor) == 4 and valor[0] == "rgb":
        return Color(*valor[1:])
    if isinstance(valor, dict):
        return {k: convertir_colores(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [convertir_colores(v) for v in valor]
    return valor


# ------------------------------------------------------------------ escena y render

def limpiar():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def escena_render(objs, ancho, alto, muestras=48, poster=False, extra_piso=None):
    esc = bpy.context.scene
    esc.render.engine = "CYCLES"
    esc.cycles.device = "CPU"
    esc.cycles.samples = muestras
    esc.cycles.use_denoising = True
    esc.render.resolution_x, esc.render.resolution_y = ancho, alto
    esc.view_settings.view_transform = "Standard"
    mundo = bpy.data.worlds.new("cielo")
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs["Color"].default_value = (0.09, 0.06, 0.14, 1)
    esc.world = mundo
    puntos = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    minimo = Vector([min(p[i] for p in puntos) for i in range(3)])
    maximo = Vector([max(p[i] for p in puntos) for i in range(3)])
    centro = (minimo + maximo) / 2
    tam = max(maximo - minimo)
    if extra_piso is None:
        bpy.ops.mesh.primitive_plane_add(size=tam * 10, location=(centro.x, centro.y, minimo.z))
        piso = bpy.context.active_object
        mat = bpy.data.materials.new("piso")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.13, 0.1, 0.09, 1)
        piso.data.materials.append(mat)
    if poster:
        dist = (maximo.x - minimo.x) * 1.2
        pos = centro + Vector((dist * 0.06, -dist, dist * 0.25))
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
    for rot, energia, color in (((45, 10, 25), 3.0, (1, 1, 1)), ((-60, 0, 200), 4.0, (1.0, 0.55, 0.25)),
                                ((60, 0, -70), 1.2, (0.5, 0.6, 1.0))):
        bpy.ops.object.light_add(type="SUN", rotation=tuple(math.radians(a) for a in rot))
        luz = bpy.context.active_object.data
        luz.energy, luz.color = energia, color
    esc.use_nodes = True
    arbol = esc.node_tree
    capas = arbol.nodes.get("Render Layers") or arbol.nodes.new("CompositorNodeRLayers")
    salida = arbol.nodes.get("Composite") or arbol.nodes.new("CompositorNodeComposite")
    glare = arbol.nodes.new("CompositorNodeGlare")
    glare.glare_type, glare.quality, glare.threshold, glare.size = "FOG_GLOW", "HIGH", 1.0, 8
    arbol.links.new(capas.outputs["Image"], glare.inputs["Image"])
    arbol.links.new(glare.outputs["Image"], salida.inputs["Image"])
    return esc


def render(ruta):
    bpy.context.scene.render.filepath = ruta
    bpy.ops.render.render(write_still=True)
