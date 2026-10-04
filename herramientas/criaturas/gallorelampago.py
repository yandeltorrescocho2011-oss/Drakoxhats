"""Gallo Relampago (Gallo Tormenta): gallo de pelea alto y atletico cargado de electricidad.

Plumaje azul electrico, pecho plateado con un rayo amarillo que brilla, cresta de tres rayos dentados,
ojos cian, cola de hoces azul marino con puntas en zigzag cian y tobilleras de metal con bobinas
tipo Tesla. Pica con descargas, lanza un rayo que salta entre enemigos y se lanza como un relampago.
"""
import math

from mathutils import Matrix, Vector

import motor

NOMBRE = "GalloRelampago"
COLORES_EXTRA = {
    "azul_rayo": (0.05, 0.24, 0.86),    # plumaje principal
    "azul_ala": (0.03, 0.15, 0.62),     # alas un poco mas oscuras
    "azul_claro": (0.32, 0.64, 1.00),   # puntas de las plumas del cuello
    "marino": (0.05, 0.08, 0.30),       # cola y plumas largas
    "pecho": (0.84, 0.88, 0.96),        # pecho plateado
    "rayo": (1.00, 0.86, 0.15),         # marcas de rayo (brillan)
    "rayo_blanco": (1.00, 0.95, 0.52),  # rayo central de la cresta (brilla)
    "cian_brillo": (0.30, 0.95, 1.00),  # ojos, puntas de la cola, bobinas (brillan)
    "cobre": (0.85, 0.43, 0.17),        # bobinas Tesla
    "pata": (0.30, 0.33, 0.46),         # patas gris azulado
    "pico": (0.98, 0.80, 0.30),
}

# ------------------------------------------------------------------ utilidades propias


def orientada(c, tipo, centro, eje_z, eje_y, esc, color, **kw):
    """Pieza con su eje local Z a lo largo de eje_z y su eje local Y lo mas cerca posible de eje_y."""
    z = Vector(eje_z).normalized()
    y = Vector(eje_y)
    y = (y - z * y.dot(z)).normalized()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed()
    rot = tuple(math.degrees(a) for a in m.to_euler("XYZ"))
    return c.pieza(tipo, tuple(centro), esc, color, rot=rot, **kw)


def tramo(c, a, b, ancho_a, ancho_b, grosor, normal, color, extra=0.0, **kw):
    """Tramo plano y afilado de a hasta b (rayos, plumas). Su cara plana mira hacia 'normal'."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    a2, b2 = a - d * extra, b + d * extra
    orientada(c, "cono", (a2 + b2) / 2, d, normal, (ancho_a, grosor, (b2 - a2).length), color, lados=4,
              punta=max(ancho_b, 0.0) / ancho_a, **kw)


def linea(c, puntos, anchos, grosor, normal, color, extra=0.04, **kw):
    """Cadena de tramos (zigzag o curva). normal puede ser un vector o una funcion del indice."""
    for i in range(len(puntos) - 1):
        n = normal(i) if callable(normal) else normal
        tramo(c, puntos[i], puntos[i + 1], anchos[i], anchos[i + 1], grosor, n, color, extra=extra, **kw)


class Elipsoide:
    """Elipsoide girado en X para pegar marcas en su superficie."""

    def __init__(self, centro, radios, rot_x=0.0):
        self.c, self.r = Vector(centro), radios
        self.m = Matrix.Rotation(math.radians(rot_x), 3, "X")

    def lado(self, u, v, signo=1, dentro=0.0):
        """Punto y normal en la cara lateral (signo=1: +X). u = largo local (Y), v = alto local (Z)."""
        rx, ry, rz = self.r
        x = signo * rx * math.sqrt(max(1 - (u / ry) ** 2 - (v / rz) ** 2, 0.0))
        return self._mundo(Vector((x, u, v)), dentro)

    def frente(self, x, v, dentro=0.0):
        """Punto y normal en la cara del frente (-Y). x = lado, v = alto local (Z)."""
        rx, ry, rz = self.r
        y = -ry * math.sqrt(max(1 - (x / rx) ** 2 - (v / rz) ** 2, 0.0))
        return self._mundo(Vector((x, y, v)), dentro)

    def _mundo(self, p, dentro):
        rx, ry, rz = self.r
        n = Vector((p.x / rx ** 2, p.y / ry ** 2, p.z / rz ** 2)).normalized()
        p = p - n * dentro
        return self.c + self.m @ p, self.m @ n


def marca(c, sup, puntos2d, anchos, grosor, color, sub=3, **kw):
    """Marca de rayo pegada a una superficie: sup(a, b) -> (punto, normal). Subdivide para seguir la curva."""
    pts, ns, ws = [], [], []
    for i in range(len(puntos2d) - 1):
        for k in range(sub):
            t = k / sub
            p, n = sup(*motor.lerp(puntos2d[i], puntos2d[i + 1], t))
            pts.append(p)
            ns.append(n)
            ws.append(anchos[i] + (anchos[i + 1] - anchos[i]) * t)
    p, n = sup(*puntos2d[-1])
    pts.append(p)
    ns.append(n)
    ws.append(anchos[-1])
    for i in range(len(pts) - 1):
        ancho_b = ws[i + 1] if ws[i + 1] > 0 else 0.0
        extra = 0.0 if i == len(pts) - 2 else ws[i] * 0.6
        tramo(c, pts[i], pts[i + 1], ws[i], ancho_b, grosor, (ns[i] + ns[i + 1]) / 2, color, extra=extra, **kw)


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * cc + t ** 3 * d
                 for a, b, cc, d in zip(p0, p1, p2, p3))


def rayo_crestal(c, base, crece, cara, alto, ancho, color, grosor=0.09, espejo=False):
    """Rayo dentado que sale de 'base' hacia 'crece'; su cara plana mira mas o menos hacia 'cara'."""
    u = Vector(crece).normalized()
    s = Vector(cara).cross(u).normalized()  # direccion de los dientes del zigzag
    b = Vector(base)
    p1 = b + u * (0.42 * alto) - s * (0.22 * alto)
    p2 = p1 + u * (0.06 * alto) + s * (0.38 * alto)
    p3 = p2 + u * (0.52 * alto) - s * (0.22 * alto)
    linea(c, [b, p1, p2, p3], [ancho, ancho * 0.85, ancho * 0.8, 0.0], grosor, u.cross(s), color,
          extra=ancho * 0.5, brillo=True, espejo=espejo)


# ------------------------------------------------------------------ geometria

TORSO = Elipsoide((0, 0.3, 3.15), (0.74, 1.25, 0.88), -25)
PECHO = Elipsoide((0, -0.45, 3.4), (0.66, 0.62, 0.8))
CABEZA = Elipsoide((0, -1.08, 5.42), (0.42, 0.5, 0.44))
ALA = Elipsoide((0.74, 0.36, 3.34), (0.19, 1.1, 0.52), -18)


def construir(c):
    c.parte("Cabeza", "Cuerpo", (0, -0.55, 3.95))
    c.parte("Cresta", "Cabeza", (0, -1.08, 5.8))
    c.parte("AlaIzq", "Cuerpo", (0.62, -0.5, 3.85), espejo=True)
    c.parte("PataIzq", "Cuerpo", (0.42, 0.2, 2.65), espejo=True)
    c.parte("Cola1", "Cuerpo", (0, 1.35, 3.25))
    c.parte("Cola2", "Cola1", (0, 2.0, 4.58))

    # ---------------- cuerpo
    c.usar("Cuerpo")
    c.pieza("esfera", tuple(TORSO.c), TORSO.r, "azul_rayo", rot=(-25, 0, 0), seg=18, anillos=12)
    c.pieza("esfera", tuple(PECHO.c), PECHO.r, "pecho", seg=18, anillos=12)
    # emblema: rayo grande en el pecho (brilla)
    emblema = [(0.17, 3.92), (-0.12, 3.36), (0.13, 3.42), (-0.09, 2.78)]
    marca(c, lambda x, z: PECHO.frente(x, z - PECHO.c.z, dentro=0.035), emblema, [0.21, 0.18, 0.18, 0.05], 0.05,
          "marino")
    marca(c, lambda x, z: PECHO.frente(x, z - PECHO.c.z, dentro=0.0), emblema, [0.14, 0.11, 0.11, 0.0], 0.05,
          "rayo", brillo=True)
    # plumas de la silla (espalda baja) que caen sobre la cola
    for k, (x, col) in enumerate(((0.18, "azul_claro"), (0.38, "azul_rayo"), (0.0, "azul_rayo"))):
        a = (x, 0.75 + 0.05 * k, 3.95 - 0.05 * k)
        b = (x * 1.3 + 0.02, 1.6 + 0.05 * k, 3.25 - 0.08 * k)
        tramo(c, a, b, 0.2, 0.0, 0.06, (x, 0.3, 1), col, espejo=x > 0)

    # ---------------- cabeza y cuello
    c.usar("Cabeza")
    c.entre((0, -0.5, 3.9), (0, -1.0, 5.25), 0.36, "azul_rayo", tipo="esfera", seg=14, anillos=10)
    c.pieza("esfera", (0, -1.08, 5.42), (0.42, 0.5, 0.44), "azul_rayo", seg=16, anillos=10)
    # golilla: plumas del cuello que caen hacia atras y hacia los lados
    for i, fi in enumerate(range(62, 300, 26)):
        f = math.radians(fi)
        d = Vector((math.sin(f), -math.cos(f), 0))
        a = Vector((0, -0.89, 4.95)) + d * 0.3
        b = Vector((0, -0.6, 3.9)) + d * 0.72 + Vector((0, 0.2, 0))
        tramo(c, a, b, 0.21, 0.0, 0.06, d, "azul_claro" if i % 2 else "azul_rayo")
    for fi in range(75, 290, 26):
        f = math.radians(fi)
        d = Vector((math.sin(f), -math.cos(f), 0))
        a = Vector((0, -0.97, 5.2)) + d * 0.29
        b = Vector((0, -0.78, 4.42)) + d * 0.52 + Vector((0, 0.1, 0))
        tramo(c, a, b, 0.17, 0.0, 0.05, d, "azul_rayo")
    # pico
    c.entre((0, -1.42, 5.45), (0, -2.05, 5.3), 0.15, "pico", lados=6, aplanar=0.85)
    c.entre((0, -1.97, 5.35), (0, -2.08, 5.18), 0.055, "pico", lados=5)
    c.entre((0, -1.42, 5.3), (0, -1.84, 5.22), 0.095, "pico", lados=6)
    # barbillas pequenas
    c.pieza("esfera", (0.065, -1.52, 5.08), (0.075, 0.085, 0.15), "oro", espejo=True, seg=8, anillos=6)
    # ojos: cuenca oscura + ojo que brilla cian + ceja enojada
    c.pieza("esfera", (0.28, -1.36, 5.53), (0.13, 0.13, 0.12), "marino", espejo=True, seg=10, anillos=7)
    c.pieza("ico", (0.32, -1.39, 5.53), 0.095, "cian_brillo", espejo=True, brillo=True, subdiv=2)
    c.entre((0.26, -1.15, 5.76), (0.36, -1.55, 5.64), 0.05, "marino", tipo="cilindro", lados=6, espejo=True)
    # antifaz: raya oscura que sale del ojo hacia atras en zigzag
    marca(c, lambda u, v: CABEZA.lado(u, v, dentro=0.02), [(-0.3, 0.1), (0.02, 0.02), (0.14, 0.14), (0.44, -0.04)],
          [0.12, 0.09, 0.08, 0.0], 0.05, "marino", espejo=True)

    # ---------------- cresta: tres rayos dentados
    c.usar("Cresta")
    c.pieza("esfera", (0, -1.08, 5.82), (0.1, 0.36, 0.1), "oro", seg=8, anillos=6)
    # corona: rayo central (se ve de lado) y dos rayos abiertos hacia los lados (se ven de frente)
    rayo_crestal(c, (0, -1.02, 5.8), (0, 0.12, 1), (1, 0, 0), 1.2, 0.22, "rayo_blanco")
    rayo_crestal(c, (0.13, -1.22, 5.72), (0.55, -0.05, 0.85), (0.45, -0.9, 0), 0.9, 0.19, "rayo", espejo=True)

    # ---------------- ala izquierda (la derecha se crea en espejo)
    c.usar("AlaIzq")
    c.pieza("esfera", tuple(ALA.c), ALA.r, "azul_ala", rot=(-18, 0, 0), espejo=True, seg=16, anillos=10)
    c.pieza("esfera", (0.7, -0.38, 3.7), (0.19, 0.38, 0.3), "azul_rayo", rot=(-18, 0, 0), espejo=True,
            seg=12, anillos=8)
    # plumas secundarias: fila de puntas en el borde de abajo
    for k in range(6):
        u = -0.7 + 0.3 * k
        p, n = ALA.lado(u, -0.3, dentro=0.06)
        q, _ = ALA.lado(u + 0.22, -0.5, dentro=0.1)
        tramo(c, p, q + Vector((0, 0, -0.22)), 0.15, 0.02, 0.045, n, "azul_rayo" if k % 2 else "azul_ala",
              espejo=True)
    # plumas largas (primarias) que salen hacia atras
    for k in range(4):
        a = (0.78, 0.55 + 0.08 * k, 3.25 - 0.12 * k)
        b = (0.72 - 0.02 * k, 1.95 + 0.06 * k, 2.85 - 0.16 * k)
        tramo(c, a, b, 0.17, 0.03, 0.05, (1, 0, 0.15), "marino" if k % 2 else "azul_ala", espejo=True)
    # marca de rayo sobre el ala (brilla)
    marca(c, lambda u, v: ALA.lado(u, v, dentro=0.015),
          [(-0.85, 0.2), (-0.08, -0.13), (0.1, 0.15), (0.95, -0.2)],
          [0.11, 0.085, 0.085, 0.0], 0.04, "rayo", brillo=True, espejo=True)

    # ---------------- pata izquierda
    c.usar("PataIzq")
    c.entre((0.44, 0.1, 2.9), (0.5, 0.33, 1.72), 0.3, "azul_rayo", tipo="esfera", espejo=True, seg=12, anillos=8)
    for fi in range(0, 360, 60):  # flecos de plumas del muslo
        f = math.radians(fi)
        d = Vector((math.sin(f), -math.cos(f), 0))
        a = Vector((0.5, 0.3, 2.05)) + d * 0.2
        b = Vector((0.5, 0.34, 1.55)) + d * 0.25
        tramo(c, a, b, 0.13, 0.0, 0.05, d, "azul_ala", espejo=True)
    hock, tobillo = Vector((0.5, 0.33, 1.62)), Vector((0.5, 0.08, 0.2))

    def eje(z):  # punto del eje de la canilla a la altura z
        return tuple(motor.lerp(tuple(tobillo), tuple(hock), (z - tobillo.z) / (hock.z - tobillo.z)))

    c.pieza("esfera", tuple(hock), 0.15, "pata", espejo=True, seg=8, anillos=6)
    c.entre(tuple(hock), tuple(tobillo), 0.12, "pata", tipo="cilindro", lados=8, espejo=True)
    # tobillera Tesla: banda de acero, bobinas de cobre y anillo que brilla
    inclin = -math.degrees(math.atan2(hock.y - tobillo.y, hock.z - tobillo.z))
    c.entre(eje(0.68), eje(1.12), 0.18, "acero", tipo="cilindro", lados=10, espejo=True)
    for z, col, gros in ((1.12, "acero_osc", 0.045), (0.68, "acero_osc", 0.045), (1.0, "cobre", 0.04),
                         (0.8, "cobre", 0.04)):
        c.pieza("toro", eje(z), 1, col, rot=(inclin, 0, 0), espejo=True, radio=0.195, grosor=gros, seg=14,
                seg_menor=5)
    c.pieza("toro", eje(0.9), 1, "cian_brillo", rot=(inclin, 0, 0), espejo=True, brillo=True, radio=0.2,
            grosor=0.035, seg=14, seg_menor=5)
    for lado in (-1, 1):  # electrodos al frente y por fuera
        p = Vector(eje(0.9))
        c.pieza("ico", (p.x + 0.21 * (lado > 0), p.y - 0.21 * (lado < 0), p.z), 0.055, "cian_brillo", espejo=True,
                brillo=True, subdiv=1)
    # espolon de acero
    p = Vector(eje(0.5))
    c.entre((p.x, p.y + 0.06, p.z), (p.x, p.y + 0.42, p.z + 0.1), 0.055, "acero", lados=6, espejo=True)
    # dedos y garras
    pie = Vector((0.5, 0.05, 0.08))
    for ang in (-28, 0, 28):
        a = math.radians(ang)
        d = Vector((math.sin(a), -math.cos(a), 0))
        fin = pie + d * 0.55
        c.entre(tuple(pie), tuple(fin), 0.085, "pata", tipo="cilindro", lados=6, espejo=True)
        c.entre(tuple(fin - d * 0.02), tuple(fin + d * 0.16 + Vector((0, 0, -0.06))), 0.055, "gris_osc", lados=5,
                espejo=True)
    c.entre(tuple(pie), (0.5, 0.42, 0.07), 0.065, "pata", tipo="cilindro", lados=6, espejo=True)
    c.entre((0.5, 0.4, 0.07), (0.5, 0.55, 0.01), 0.05, "gris_osc", lados=5, espejo=True)

    # ---------------- cola: plumas cobertoras (Cola1) y hoces (Cola1 -> Cola2) con puntas de rayo
    c.usar("Cola1")
    for k, x in enumerate((-0.3, -0.15, 0.0, 0.15, 0.3)):
        a = (x * 0.5, 1.25, 3.35)
        b = (x * 1.3, 2.05 + abs(x) * 0.3, 4.3 - abs(x) * 1.2)
        tramo(c, a, b, 0.22, 0.05, 0.06, (1, 0, 0), "azul_rayo" if k % 2 == 0 else "azul_ala")
    hoces = [  # (x0, x1, puntos de control y-z), color
        ((0.0, 0.0), ((1.45, 3.5), (2.0, 5.3), (3.3, 5.6), (3.85, 4.0)), 0.21, "marino"),
        ((0.12, 0.38), ((1.45, 3.45), (2.0, 4.95), (3.1, 5.2), (3.55, 3.7)), 0.19, "marino"),
        ((-0.12, -0.38), ((1.45, 3.45), (2.0, 4.95), (3.1, 5.2), (3.55, 3.7)), 0.19, "marino"),
        ((0.2, 0.7), ((1.4, 3.4), (1.95, 4.5), (2.8, 4.7), (3.15, 3.45)), 0.17, "azul_ala"),
        ((-0.2, -0.7), ((1.4, 3.4), (1.95, 4.5), (2.8, 4.7), (3.15, 3.45)), 0.17, "azul_ala"),
    ]
    n = 8
    for (x0, x1), ctrl, ancho, col in hoces:
        pts = []
        for i in range(n + 1):
            t = i / n
            y, z = bezier(*ctrl, t)
            pts.append(Vector((x0 + (x1 - x0) * t, y, z)))
        for i in range(n):
            parte = "Cola1" if i < 2 else "Cola2"
            w0 = ancho * (1 - 0.35 * i / n)
            w1 = ancho * (1 - 0.35 * (i + 1) / n)
            tramo(c, pts[i], pts[i + 1], w0, w1, 0.055, (1, 0, 0), col, extra=0.05, parte=parte)
        # punta en zigzag que brilla cian
        d = (pts[-1] - pts[-2]).normalized()
        lado = Vector((1, 0, 0)).cross(d).normalized()
        p1 = pts[-1] + d * 0.25 + lado * 0.12
        p2 = p1 + d * 0.06 - lado * 0.22
        p3 = p2 + d * 0.32 + lado * 0.1
        linea(c, [pts[-1] - d * 0.08, p1, p2, p3], [ancho * 0.7, ancho * 0.6, ancho * 0.55, 0.0], 0.05, (1, 0, 0),
              "cian_brillo", extra=ancho * 0.3, brillo=True, parte="Cola2")


# ------------------------------------------------------------------ estadisticas y habilidades

CONFIG = {
    "nombre": "Gallo Relámpago",
    "vida": 260,
    "velocidad": 22,
    "comportamiento": "normal",
    "radioDeteccion": 40,
    "radioPatrulla": 18,
    "radioPersecucion": 80,
    "reaparecer": 25,
    "colorUI": ("rgb", 70, 215, 255),
    "habilidades": [
        {"nombre": "Picotazo Eléctrico", "tipo": "Golpe", "anim": "Picotazo", "rango": 6, "alcance": 6,
         "angulo": 70, "danio": 10, "empuje": 25, "aturdir": 0.2, "cooldown": 1.5, "retraso": 0.2,
         "color": ("rgb", 120, 235, 255)},
        {"nombre": "Rayo Encadenado", "tipo": "Cadena", "anim": "RayoEncadenado", "rango": 30, "danio": 16,
         "saltos": 3, "radioSalto": 15, "cooldown": 7, "retraso": 0.4, "color": ("rgb", 255, 230, 70)},
        {"nombre": "Embestida Relámpago", "tipo": "Embestida", "anim": "Embestida", "rango": 28, "distancia": 26,
         "velocidad": 90, "danio": 20, "empuje": 40, "ancho": 5, "cooldown": 6, "retraso": 0.3,
         "color": ("rgb", 80, 220, 255)},
    ],
}

# ------------------------------------------------------------------ animaciones

ANIMACIONES = {
    "Idle": {
        "Raiz": [("py", 0.04, 1.2, 0), ("rx", 1.5, 0.6, 0.3)],
        "Cabeza": [("rx", 4, 0.6, 0), ("ry", 14, 0.35, 0.1)],
        "Cresta": [("rz", 4, 3.5, 0), ("rx", 3, 2.1, 0.3)],
        "AlaIzq": [("rz", -4, 1.2, 0)],
        "Cola1": [("rx", 3, 0.6, 0.2), ("ry", 3, 0.4, 0)],
        "Cola2": [("rx", 5, 0.6, 0.4), ("ry", 4, 0.4, 0.25)],
    },
    "Caminar": {
        "Raiz": [("py", 0.15, 5.2, 0.25), ("rz", 3, 2.6, 0)],
        "Cabeza": [("pz", 0.15, 5.2, 0), ("rx", 5, 5.2, 0.25)],
        "Cresta": [("rx", 6, 5.2, 0.4)],
        "AlaIzq": [("rz", -8, 2.6, 0.25)],
        "PataIzq": [("rx", 32, 2.6, 0)],
        "PataDer": [("rx", 32, 2.6, 0.5)],
        "Cola1": [("rx", 5, 5.2, 0.1), ("ry", 4, 2.6, 0)],
        "Cola2": [("rx", 6, 5.2, 0.3), ("ry", 5, 2.6, 0.2)],
    },
    "clips": {
        # Golpe al tiempo 0.2 (retraso)
        "Picotazo": {"duracion": 0.6, "claves": [
            (0.0, {}),
            (0.11, {"Raiz": {"rx": 6, "pz": 0.25}, "Cabeza": {"rx": 25, "pz": 0.15}, "Cresta": {"rx": 15},
                    "AlaIzq": {"rz": -15}, "Cola1": {"rx": -6}}),
            (0.2, {"Raiz": {"rx": -14, "pz": -0.35}, "Cabeza": {"rx": -45, "pz": -0.3}, "Cresta": {"rx": -12},
                   "AlaIzq": {"rz": -30}, "Cola1": {"rx": 8}, "Cola2": {"rx": 10}}),
            (0.32, {"Raiz": {"rx": -10, "pz": -0.25}, "Cabeza": {"rx": -35, "pz": -0.2}, "AlaIzq": {"rz": -20},
                    "Cola2": {"rx": -6}}),
            (0.6, {}),
        ]},
        # Descarga al tiempo 0.4: alza alas y cresta
        "RayoEncadenado": {"duracion": 1.1, "claves": [
            (0.0, {}),
            (0.28, {"Raiz": {"py": -0.1, "rx": -6}, "Cabeza": {"rx": -12}, "Cresta": {"rx": -12},
                    "AlaIzq": {"rz": -40}, "Cola1": {"rx": 6}}),
            (0.4, {"Raiz": {"py": 0.35, "rx": 10}, "Cabeza": {"rx": 22}, "Cresta": {"rx": 20},
                   "AlaIzq": {"rz": -80, "ry": -15}, "Cola1": {"rx": -15}, "Cola2": {"rx": -10}}),
            (0.65, {"Raiz": {"py": 0.25, "rx": 8}, "Cabeza": {"rx": 16}, "Cresta": {"rx": 14},
                    "AlaIzq": {"rz": -70, "ry": -12}, "Cola1": {"rx": -12}, "Cola2": {"rx": 6}}),
            (1.1, {}),
        ]},
        # Se lanza al tiempo 0.3
        "Embestida": {"duracion": 1.15, "claves": [
            (0.0, {}),
            (0.2, {"Raiz": {"py": -0.3, "rx": -12, "pz": 0.35}, "Cabeza": {"rx": 15}, "AlaIzq": {"rz": -30},
                   "PataIzq": {"rx": 40}, "PataDer": {"rx": -16}, "Cola1": {"rx": -12}}),
            (0.3, {"Raiz": {"py": -0.15, "rx": -28, "pz": -0.6}, "Cabeza": {"rx": -20, "pz": -0.2},
                   "Cresta": {"rx": 25}, "AlaIzq": {"rz": -55, "ry": -30}, "Cola1": {"rx": 20}, "Cola2": {"rx": 15},
                   "PataIzq": {"rx": -10}, "PataDer": {"rx": -10}}),
            (0.55, {"Raiz": {"py": -0.1, "rx": -25, "pz": -0.5}, "Cabeza": {"rx": -18, "pz": -0.2},
                    "Cresta": {"rx": 22}, "AlaIzq": {"rz": -60, "ry": -30}, "Cola1": {"rx": 18},
                    "Cola2": {"rx": 20}, "PataIzq": {"rx": -12}, "PataDer": {"rx": -12}}),
            (0.8, {"Raiz": {"py": -0.25, "rx": -8}, "Cabeza": {"rx": 10}, "AlaIzq": {"rz": -35},
                   "PataIzq": {"rx": 33}, "PataDer": {"rx": -17}, "Cola2": {"rx": -8}}),
            (1.15, {}),
        ]},
        "Golpeado": {"duracion": 0.35, "claves": [
            (0.0, {}),
            (0.08, {"Raiz": {"rx": 10, "pz": 0.25}, "Cabeza": {"rx": 20}, "Cresta": {"rx": 15}, "AlaIzq": {"rz": -25}}),
            (0.35, {}),
        ]},
        "Derrota": {"duracion": 1.3, "claves": [
            (0.0, {}),
            (0.25, {"Raiz": {"rx": 12, "py": 0.1}, "Cabeza": {"rx": 30}, "Cresta": {"rx": 20}, "AlaIzq": {"rz": -50}}),
            (0.55, {"Raiz": {"rx": 5, "rz": -10}, "Cabeza": {"rx": -20, "ry": 20}, "AlaIzq": {"rz": -30}}),
            (1.3, {"Raiz": {"rz": -85, "py": -2.25}, "Cabeza": {"rx": -25, "rz": -20}, "Cresta": {"rx": 15},
                   "AlaIzq": {"rz": -35}, "AlaDer": {"rz": -10}, "PataIzq": {"rx": 25}, "PataDer": {"rx": -15},
                   "Cola1": {"rx": 15}}),
        ]},
    },
}
