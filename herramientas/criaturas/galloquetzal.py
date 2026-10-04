"""Gallo Quetzal (JEFE): gallo gigante inspirado en Quetzalcoatl, la serpiente emplumada azteca.

Plumaje verde esmeralda y turquesa, pecho rojo y joyeria azteca de oro: un gran disco solar (piedra del sol)
en el pecho con centro de jade que brilla, collar y brazaletes de oro. En la cabeza lleva un penacho de plumas
de quetzal abierto en abanico (como el de Moctezuma) con banda de oro y gemas de jade. Su cola es una SERPIENTE
de escamas verdes con anillos de oro (Cola1 -> Cola4) que ondula y termina en un abanico de plumas largas.
Garras y espolones de obsidiana.
"""
import math

from mathutils import Matrix, Vector

import motor

NOMBRE = "GalloQuetzal"
COLORES_EXTRA = {
    "esmeralda": (0.04, 0.58, 0.34),      # plumaje principal
    "esmeralda_osc": (0.02, 0.34, 0.24),  # sombras del plumaje, muslos
    "turquesa": (0.06, 0.74, 0.70),       # plumas iridiscentes
    "azul_quetzal": (0.05, 0.36, 0.66),   # plumas de vuelo
    "pecho_rojo": (0.86, 0.09, 0.12),     # pecho
    "rojo_pluma": (0.96, 0.20, 0.14),     # puntas rojas de las alas, plumas internas del penacho
    "escama": (0.10, 0.50, 0.30),         # cola de serpiente
    "escama_osc": (0.03, 0.24, 0.16),     # rombos de la serpiente
    "vientre": (0.96, 0.84, 0.42),        # vientre de la serpiente
    "jade": (0.18, 0.72, 0.48),           # jade sin brillo
    "jade_brillo": (0.30, 1.00, 0.62),    # ojos, centro del disco, gemas (brillan)
    "pata_q": (0.22, 0.30, 0.29),         # patas
    "obsidiana": (0.07, 0.05, 0.10),      # garras y espolones
}

X = Vector((1, 0, 0))
Y = Vector((0, 1, 0))
Z = Vector((0, 0, 1))

# ------------------------------------------------------------------ utilidades propias


def V(p):
    return Vector(p)


def orientada(c, tipo, centro, eje_z, eje_y, esc, color, giro=0.0, **kw):
    """Pieza con su eje local Z a lo largo de eje_z y su eje local Y lo mas cerca posible de eje_y
    (girada 'giro' grados alrededor de eje_z)."""
    z = Vector(eje_z).normalized()
    y = Vector(eje_y)
    y = (y - z * y.dot(z))
    if y.length < 1e-6:
        y = Vector((1, 0, 0)) if abs(z.x) < 0.9 else Vector((0, 1, 0))
        y = y - z * y.dot(z)
    y.normalize()
    if giro:
        y = (Matrix.Rotation(math.radians(giro), 3, z) @ y).normalized()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed()
    rot = tuple(math.degrees(a) for a in m.to_euler("XYZ"))
    return c.pieza(tipo, tuple(centro), esc, color, rot=rot, **kw)


def hoja(c, a, b, ancho, grosor, normal, color, seg=8, anillos=5, **kw):
    """Pluma/hoja: elipsoide aplanado de a hasta b; su cara plana mira hacia 'normal'."""
    a, b = V(a), V(b)
    return orientada(c, "esfera", (a + b) / 2, b - a, normal, (ancho, grosor, (b - a).length / 2), color,
                     seg=seg, anillos=anillos, **kw)


def punta(c, a, b, ancho, grosor, normal, color, lados=4, fin=0.0, **kw):
    """Pieza plana y afilada (cono de 4 lados) de a hasta b; cara plana hacia 'normal'."""
    a, b = V(a), V(b)
    return orientada(c, "cono", (a + b) / 2, b - a, normal, (ancho, grosor, (b - a).length), color, lados=lados,
                     punta=fin, **kw)


def pluma(c, a, b, ancho, grosor, normal, color, color_punta=None, corte=0.66, **kw):
    """Pluma lanceolada: cuerpo ovalado + punta afilada. Con color_punta la punta (desde 'corte') es de
    otro color y un poco mas gruesa para que se vea por los dos lados."""
    a, b = V(a), V(b)
    hoja(c, a, a + (b - a) * 0.8, ancho, grosor, normal, color, **kw)
    if color_punta:
        punta(c, a + (b - a) * corte, b, ancho * 0.92, grosor * 1.3, normal, color_punta, **kw)
    else:
        punta(c, a + (b - a) * 0.55, b, ancho * 0.86, grosor * 0.95, normal, color, **kw)


def anillo(c, centro, eje, radio, grosor, color, seg=14, **kw):
    """Toro con su eje a lo largo de 'eje'."""
    return orientada(c, "toro", centro, eje, (0, 0, 1) if abs(V(eje).normalized().z) < 0.9 else (0, 1, 0), 1,
                     color, radio=radio, grosor=grosor, seg=seg, seg_menor=5, **kw)


class Elipsoide:
    """Elipsoide girado en X (grados) para pegar piezas en su superficie."""

    def __init__(self, centro, radios, rot_x=0.0):
        self.c, self.r, self.rot_x = V(centro), radios, rot_x
        self.m = Matrix.Rotation(math.radians(rot_x), 3, "X")

    def poner(self, c, color, **kw):
        return c.pieza("esfera", tuple(self.c), self.r, color, rot=(self.rot_x, 0, 0), **kw)

    def rayo(self, d, dentro=0.0):
        """Punto de la superficie en la direccion d (mundo) desde el centro, y su normal."""
        dl = self.m.inverted() @ V(d).normalized()
        rx, ry, rz = self.r
        t = 1 / math.sqrt((dl.x / rx) ** 2 + (dl.y / ry) ** 2 + (dl.z / rz) ** 2)
        p = dl * t
        n = Vector((p.x / rx ** 2, p.y / ry ** 2, p.z / rz ** 2)).normalized()
        p = p - n * dentro
        return self.c + self.m @ p, self.m @ n

    def lado(self, u, v, signo=1, dentro=0.0):
        """Punto y normal en la cara lateral (+X si signo=1). u = largo local (Y), v = alto local (Z)."""
        rx, ry, rz = self.r
        x = signo * rx * math.sqrt(max(1 - (u / ry) ** 2 - (v / rz) ** 2, 0.0))
        p = Vector((x, u, v))
        n = Vector((p.x / rx ** 2, p.y / ry ** 2, p.z / rz ** 2)).normalized()
        p = p - n * dentro
        return self.c + self.m @ p, self.m @ n


def rot_eje(v, eje, grados):
    return Matrix.Rotation(math.radians(grados), 3, V(eje)) @ V(v)


# ------------------------------------------------------------------ medidas principales

TORSO = Elipsoide((0, 0.4, 4.95), (1.4, 1.88, 1.42), -30)
PECHO = Elipsoide((0, -0.72, 5.3), (1.2, 1.1, 1.42))
CABEZA = Elipsoide((0, -1.55, 7.7), (0.66, 0.74, 0.66))
ALA = Elipsoide((1.42, 0.5, 5.3), (0.3, 1.55, 0.82), -22)

U_CABEZA = (0, -0.72, 6.1)       # base del cuello
U_PENACHO = (0, -1.32, 7.93)     # centro del abanico del penacho
U_ALA = (1.12, -0.5, 5.95)       # hombro
U_PATA = (0.66, 0.3, 4.05)       # cadera
# cola de serpiente: articulaciones y punta (curva en S que se levanta detras del gallo)
COLA = [V((0, 1.95, 5.05)), V((0, 3.15, 4.55)), V((0, 4.3, 5.0)), V((0, 4.85, 6.12)), V((0, 4.8, 7.32))]
RADIOS_COLA = [0.68, 0.6, 0.5, 0.41]

DISCO_C = V((0, -1.82, 5.2))     # centro del disco solar
DISCO_INCL = 80                  # rot X del disco (90 = mira al frente)


def construir(c):
    c.parte("Cabeza", "Cuerpo", U_CABEZA)
    c.parte("Penacho", "Cabeza", U_PENACHO)
    c.parte("AlaIzq", "Cuerpo", U_ALA, espejo=True)
    c.parte("PataIzq", "Cuerpo", U_PATA, espejo=True)
    padre = "Cuerpo"
    for i in range(4):
        c.parte(f"Cola{i + 1}", padre, tuple(COLA[i]))
        padre = f"Cola{i + 1}"

    cuerpo(c)
    cabeza(c)
    penacho(c)
    ala(c)
    pata(c)
    cola(c)


# ------------------------------------------------------------------ cuerpo, pecho y disco solar

def cuerpo(c):
    c.usar("Cuerpo")
    TORSO.poner(c, "esmeralda", seg=20, anillos=12)
    PECHO.poner(c, "pecho_rojo", seg=18, anillos=12)
    # vientre oscuro entre las patas
    c.pieza("esfera", (0, 0.45, 4.05), (1.05, 1.3, 0.7), "esmeralda_osc", seg=14, anillos=8)
    # plumas del lomo (silla) que caen sobre la base de la cola
    for k, (x, col) in enumerate(((0.0, "turquesa"), (0.36, "esmeralda"), (0.68, "turquesa"))):
        a = V((x, 0.85 - 0.1 * k, 6.15 - 0.15 * k))
        b = V((x * 1.25, 2.45 - 0.12 * k, 5.4 - 0.25 * k))
        n = V((x * 0.8, 0.3, 1)).normalized()
        punta(c, a, b, 0.38, 0.08, n, col, espejo=x > 0)

    # collar de oro en la base del cuello (placas sobre el pecho y los hombros)
    for k in range(-4, 5):
        ang = math.radians(k * 22)
        p, n = PECHO.rayo(V((math.sin(ang), -math.cos(ang), 1.05)))
        q, _ = PECHO.rayo(V((math.sin(ang) * 1.05, -math.cos(ang) * 1.05, 0.72)))
        orientada(c, "cubo", (p + q) / 2 + n * 0.03, q - p, n, (0.3, 0.09, (q - p).length + 0.14), "oro")
        if k % 2 == 0:
            c.pieza("ico", tuple((p + q) / 2 + n * 0.1), 0.085, "jade", subdiv=1)

    # disco solar (piedra del sol) colgado del collar
    m = Matrix.Rotation(math.radians(DISCO_INCL), 3, "X")
    nrm = m @ Z  # hacia el frente (y un poco arriba)
    ux, uy = m @ X, m @ Y

    def en_disco(r, ang, h=0.0):
        a = math.radians(ang)
        return DISCO_C + ux * (r * math.cos(a)) + uy * (r * math.sin(a)) + nrm * h

    rot = (DISCO_INCL, 0, 0)
    c.pieza("cilindro", tuple(DISCO_C), (0.68, 0.68, 0.16), "oro", rot=rot, lados=18)
    c.pieza("cilindro", tuple(DISCO_C + nrm * 0.03), (0.52, 0.52, 0.16), "oro_osc", rot=rot, lados=18)
    c.pieza("cilindro", tuple(DISCO_C + nrm * 0.06), (0.44, 0.44, 0.16), "turquesa", rot=rot, lados=18)
    c.pieza("cilindro", tuple(DISCO_C + nrm * 0.09), (0.31, 0.31, 0.16), "oro", rot=rot, lados=12)
    # rayos del sol alrededor
    for k in range(8):
        ang = 90 + k * 45
        punta(c, en_disco(0.62, ang), en_disco(0.98, ang), 0.18, 0.09, nrm, "oro")
    # cuatro marcas (ollin) en el anillo turquesa
    for k in range(4):
        orientada(c, "cubo", en_disco(0.48, 45 + k * 90, 0.11), nrm, uy, (0.13, 0.13, 0.05), "oro")
    # centro de jade que brilla
    c.pieza("ico", tuple(DISCO_C + nrm * 0.2), (0.21, 0.21, 0.21), "jade_brillo", brillo=True, subdiv=2)
    # tiras que lo cuelgan del collar
    for s in (-1, 1):
        a = en_disco(0.62, 90 + s * 32, 0.0)
        p, _ = PECHO.rayo(V((s * 0.32, -1.0, 0.85)))
        c.entre(tuple(p), tuple(a), 0.055, "oro_osc", tipo="cilindro", lados=6)


# ------------------------------------------------------------------ cabeza

def cabeza(c):
    c.usar("Cabeza")
    # cuello
    c.entre((0, -0.62, 5.8), (0, -1.42, 7.5), 0.6, "esmeralda", tipo="esfera", seg=14, anillos=10)
    CABEZA.poner(c, "esmeralda", seg=16, anillos=10)
    # melena del cuello: dos capas de plumas que caen sobre los hombros
    for capa, (alto, ancho, cols) in enumerate(((7.35, 0.34, ("turquesa", "esmeralda")),
                                                (7.62, 0.28, ("esmeralda", "turquesa")))):
        for i, th in enumerate(range(50, 311, 26)):
            t = math.radians(th)
            r = V((math.sin(t), -math.cos(t), 0))
            a = V((0, -1.38 + 0.05 * capa, alto)) + r * 0.44
            b = V((0, -0.9 + 0.12 * capa, alto - 1.45 + 0.25 * capa)) + r * (0.95 - 0.12 * capa) + Y * 0.15
            punta(c, a, b, ancho, 0.07, r + Y * 0.2, cols[i % 2])
    # oreja roja de gallo detras del ojo
    c.pieza("esfera", (0.46, -1.62, 7.42), (0.15, 0.24, 0.2), "pecho_rojo", rot=(-25, 0, 0), espejo=True, seg=10,
            anillos=7)
    # ojo: cuenca de obsidiana, ojo de jade que brilla y pupila
    c.pieza("esfera", (0.5, -1.98, 7.8), (0.16, 0.19, 0.17), "obsidiana", espejo=True, seg=10, anillos=7)
    c.pieza("ico", (0.56, -2.02, 7.8), 0.125, "jade_brillo", espejo=True, brillo=True, subdiv=2)
    c.pieza("esfera", (0.635, -2.08, 7.8), (0.04, 0.05, 0.08), "obsidiana", espejo=True, seg=6, anillos=4)
    # ceja de obsidiana enojada (baja hacia el pico)
    punta(c, (0.2, -2.22, 7.98), (0.7, -1.86, 8.14), 0.12, 0.08, (0.3, -0.5, 1), "obsidiana", espejo=True,
          fin=0.35)
    # pico de oro ganchudo
    c.entre((0, -2.08, 7.7), (0, -2.93, 7.52), 0.21, "oro", lados=6, aplanar=0.85)
    c.entre((0, -2.82, 7.58), (0, -2.98, 7.3), 0.075, "oro", lados=5)
    c.entre((0, -2.06, 7.52), (0, -2.62, 7.42), 0.14, "oro_osc", lados=6, aplanar=0.8)
    # barbillas rojas
    c.pieza("esfera", (0.09, -2.17, 7.18), (0.11, 0.12, 0.24), "pecho_rojo", espejo=True, seg=8, anillos=6)
    # diadema de oro con jade en la frente
    anillo(c, (0, -1.55, 8.17), (0, 0.3, 1), 0.47, 0.075, "oro", seg=18)
    c.pieza("cilindro", (0, -2.0, 8.08), (0.15, 0.15, 0.08), "oro", rot=(72, 0, 0), lados=10)
    c.pieza("ico", (0, -2.06, 8.1), 0.095, "jade_brillo", brillo=True, subdiv=1)


# ------------------------------------------------------------------ penacho de plumas de quetzal

def penacho(c):
    c.usar("Penacho")
    F = V(U_PENACHO)
    tau = math.radians(16)  # el abanico se inclina un poco hacia atras
    arriba = V((0, math.sin(tau), math.cos(tau)))
    frente = V((0, -math.cos(tau), math.sin(tau)))

    def dirf(phi):
        p = math.radians(phi)
        return (X * math.sin(p) + arriba * math.cos(p)).normalized()

    # capa de atras: plumas largas de quetzal
    for i, phi in enumerate(range(-80, 81, 16)):
        d = dirf(phi)
        largo = 2.15 - 0.3 * abs(phi) / 80
        a = F + d * 0.3 - frente * 0.12
        b = F + d * (0.3 + largo) - frente * 0.12
        pluma(c, a, b, 0.27, 0.06, frente, "esmeralda" if i % 2 == 0 else "turquesa")
    # capa del medio
    for i, phi in enumerate(range(-72, 73, 16)):
        d = dirf(phi)
        a = F + d * 0.3 - frente * 0.04
        b = F + d * 1.5 - frente * 0.04
        pluma(c, a, b, 0.22, 0.06, frente, "azul_quetzal")
    # capa de adelante: plumas rojas cortas
    for phi in range(-64, 65, 16):
        d = dirf(phi)
        pluma(c, F + d * 0.3 + frente * 0.04, F + d * 1.0 + frente * 0.04, 0.17, 0.06, frente, "rojo_pluma",
              seg=6, anillos=4)
    # banda de oro con gemas de jade
    for i, phi in enumerate(range(-90, 91, 18)):
        d = dirf(phi)
        p = F + d * 0.52 + frente * 0.1
        orientada(c, "cilindro", p, frente, d, (0.14, 0.14, 0.08), "oro", lados=8)
        if i % 2 == 1:
            c.pieza("ico", tuple(p + frente * 0.07), 0.08, "jade_brillo", brillo=True, subdiv=1)


# ------------------------------------------------------------------ alas

def ala(c):
    c.usar("AlaIzq")
    ALA.poner(c, "esmeralda_osc", espejo=True, seg=16, anillos=10)
    # hombro y brazalete de oro con jade
    c.pieza("esfera", (1.3, -0.35, 5.62), (0.35, 0.62, 0.58), "turquesa", espejo=True, seg=12, anillos=8)
    c.pieza("cilindro", (1.31, -0.2, 5.6), (0.39, 0.61, 0.24), "oro", rot=(90, 0, 0), espejo=True, lados=12)
    c.pieza("cilindro", (1.31, -0.2, 5.6), (0.41, 0.63, 0.08), "oro_osc", rot=(90, 0, 0), espejo=True, lados=12)
    c.pieza("ico", (1.71, -0.24, 5.6), 0.11, "jade_brillo", espejo=True, brillo=True, subdiv=1)
    # filas de plumas como tejas: las de arriba cortas y encima, las de abajo largas con puntas rojas
    filas = [  # (v, u inicial, cantidad, paso, largo, ancho, direccion, colores, punta roja, afuera)
        (-0.28, -0.95, 7, 0.3, 1.45, 0.25, (0, 0.55, -0.83), ("azul_quetzal", "esmeralda"), True, 0.0),
        (0.08, -1.0, 6, 0.32, 1.0, 0.24, (0, 0.72, -0.7), ("esmeralda", "turquesa"), False, 0.05),
        (0.42, -0.9, 5, 0.32, 0.68, 0.22, (0, 0.8, -0.6), ("turquesa", "esmeralda"), False, 0.1),
    ]
    for v, u0, n, paso, largo, ancho, dirr, cols, roja, afuera in filas:
        for k in range(n):
            p, nrm = ALA.lado(u0 + paso * k, v, dentro=0.08)
            p = p + nrm * afuera
            q = p + V(dirr).normalized() * largo + nrm * 0.04
            pluma(c, p, q, ancho, 0.065, nrm, cols[k % 2], "rojo_pluma" if roja else None, corte=0.72,
                  espejo=True)
    # primarias largas hacia atras con puntas rojas
    for k in range(5):
        a = V((1.45, 1.05 + 0.12 * k, 5.5 - 0.2 * k))
        b = V((1.42 - 0.03 * k, 3.3 + 0.05 * k, 5.0 - 0.36 * k))
        pluma(c, a, b, 0.27, 0.07, (1, 0, 0.12), "azul_quetzal" if k % 2 == 0 else "esmeralda", "rojo_pluma",
              corte=0.72, espejo=True)


# ------------------------------------------------------------------ patas

def pata(c):
    c.usar("PataIzq")
    c.entre((0.72, 0.28, 4.3), (0.86, 0.45, 2.5), 0.6, "esmeralda_osc", tipo="esfera", espejo=True, seg=12,
            anillos=8)
    for i, th in enumerate(range(0, 360, 40)):  # flecos de plumas del muslo
        t = math.radians(th)
        r = V((math.sin(t), -math.cos(t), 0))
        a = V((0.86, 0.45, 2.95)) + r * 0.46
        b = V((0.86, 0.5, 2.15)) + r * 0.42
        punta(c, a, b, 0.22, 0.06, r, "esmeralda" if i % 2 else "turquesa", espejo=True)
    hock, tob = V((0.86, 0.48, 2.25)), V((0.86, 0.16, 0.28))

    def eje(z):
        return tuple(motor.lerp(tuple(tob), tuple(hock), (z - tob.z) / (hock.z - tob.z)))

    c.pieza("esfera", tuple(hock), 0.27, "pata_q", espejo=True, seg=8, anillos=6)
    c.entre(tuple(hock), tuple(tob), 0.24, "pata_q", tipo="cilindro", lados=8, espejo=True)
    # brazaletes de oro con jade
    for z0, z1, r in ((0.72, 1.08, 0.33), (1.36, 1.5, 0.31)):
        c.entre(eje(z0), eje(z1), r, "oro", tipo="cilindro", lados=10, espejo=True)
    p = V(eje(0.9))
    c.pieza("ico", (p.x + 0.32, p.y - 0.04, p.z), 0.09, "jade_brillo", espejo=True, brillo=True, subdiv=1)
    c.pieza("ico", (p.x, p.y - 0.33, p.z), 0.09, "jade_brillo", espejo=True, brillo=True, subdiv=1)
    # espolon de obsidiana
    p = V(eje(0.5))
    c.entre((p.x - 0.05, p.y + 0.15, p.z), (p.x - 0.1, p.y + 0.72, p.z + 0.14), 0.1, "obsidiana", lados=6,
            espejo=True)
    # dedos con garras de obsidiana
    pie = V((0.86, 0.14, 0.14))
    for ang in (-32, 0, 32):
        a = math.radians(ang)
        d = V((math.sin(a), -math.cos(a), 0))
        fin = pie + d * 0.88
        c.entre(tuple(pie), tuple(fin), 0.14, "pata_q", tipo="cilindro", lados=6, espejo=True)
        c.entre(tuple(fin - d * 0.03), tuple(fin + d * 0.28 + V((0, 0, -0.1))), 0.095, "obsidiana", lados=5,
                espejo=True)
    c.entre(tuple(pie), (0.86, 0.68, 0.14), 0.12, "pata_q", tipo="cilindro", lados=6, espejo=True)
    c.entre((0.86, 0.66, 0.14), (0.86, 0.9, 0.04), 0.085, "obsidiana", lados=5, espejo=True)


# ------------------------------------------------------------------ cola de serpiente emplumada

def cola(c):
    for i in range(4):
        parte = f"Cola{i + 1}"
        c.usar(parte)
        p, q, r = COLA[i], COLA[i + 1], RADIOS_COLA[i]
        r1 = RADIOS_COLA[i + 1] if i < 3 else r * 0.85
        d = (q - p).normalized()
        arr = X.cross(d).normalized()  # lado de arriba (lomo) del segmento
        largo = (q - p).length
        # cuerpo del segmento y bola de la articulacion
        c.entre(tuple(p - d * 0.1), tuple(q + d * 0.2), (r + r1) / 2 * 1.02, "escama", tipo="esfera", seg=12,
                anillos=8)
        c.pieza("esfera", tuple(p), r * 1.04, "escama", seg=12, anillos=8)
        # anillo de oro en la articulacion
        anillo(c, p + d * 0.14, d, r * 1.03, 0.09, "oro")
        # vientre de escamas claras
        for k in (0.32, 0.7):
            rr = r + (r1 - r) * k
            pc = p + d * (largo * k) - arr * rr * 0.84
            orientada(c, "cubo", pc, d, arr, (rr * 1.15, 0.12, largo * 0.34), "vientre")
        # rombos oscuros a los lados
        for k in (0.3, 0.68):
            rr = r + (r1 - r) * k
            base = p + d * (largo * k)
            for lado in (-1, 1):
                n = (X * lado + arr * 0.4).normalized()
                orientada(c, "cubo", base + n * rr * 0.95, n, d, (rr * 0.45, rr * 0.45, 0.05), "escama_osc",
                          giro=45)
        # cresta de plumitas en el lomo (serpiente emplumada)
        for k, col in ((0.3, "rojo_pluma"), (0.72, "turquesa")):
            rr = r + (r1 - r) * k
            base = p + d * (largo * k) + arr * rr * 0.8
            tip = base + (d * 0.85 + arr * 1.0).normalized() * (0.38 + r * 0.6)
            punta(c, base, tip, 0.16, 0.05, X, col)
    # abanico de plumas al final de la cola
    c.usar("Cola4")
    E = COLA[4]
    c.pieza("esfera", tuple(E), 0.36, "escama", seg=10, anillos=7)
    anillo(c, E + V((0, 0, -0.08)), (0, 0.1, 1), 0.36, 0.1, "oro")
    for capa, (angs, largo0, ancho, cols, x) in enumerate((
            (range(-30, 131, 20), 2.6, 0.32, ("esmeralda", "turquesa"), 0.0),
            (range(-20, 121, 20), 1.7, 0.27, ("azul_quetzal", "turquesa"), 0.1),
    )):
        for k, ang in enumerate(angs):
            a = math.radians(ang)
            d = (Z * math.cos(a) + Y * math.sin(a)).normalized()
            largo = largo0 * (1 - 0.18 * abs(ang - 50) / 80)
            for s in ((1, -1) if capa == 1 else (0,)):
                off = X * x * s
                m = E + off + d * largo * 0.55
                d2 = rot_eje(d, X, 18).normalized()
                b = m + d2 * largo * 0.5
                col = cols[k % 2]
                hoja(c, E + off + d * 0.1, m + d * 0.15, ancho, 0.07, X, col)
                pluma(c, m - d2 * 0.1, b, ancho * 0.92, 0.065, X, col)


# ------------------------------------------------------------------ estadisticas y habilidades

CONFIG = {
    "nombre": "Gallo Quetzal",
    "vida": 900,
    "velocidad": 16,
    "comportamiento": "normal",
    "radioDeteccion": 50,
    "radioPatrulla": 20,
    "radioPersecucion": 100,
    "reaparecer": 120,
    "colorUI": ("rgb", 60, 215, 140),
    "habilidades": [
        {"nombre": "Mordida de Serpiente", "tipo": "Golpe", "anim": "MordidaSerpiente", "rango": 9, "alcance": 10,
         "angulo": 140, "danio": 22, "empuje": 35, "cooldown": 3, "retraso": 0.35,
         "color": ("rgb", 80, 240, 150)},
        {"nombre": "Lluvia de Plumas", "tipo": "Proyectil", "anim": "LluviaPlumas", "rango": 45, "cantidad": 7,
         "dispersion": 50, "forma": "pluma", "velocidad": 70, "tamano": 1.3, "radioExplosion": 0, "danio": 10,
         "cooldown": 6, "retraso": 0.4, "color": ("rgb", 40, 220, 110)},
        {"nombre": "Viento Divino", "tipo": "Onda", "anim": "VientoDivino", "rango": 14, "radio": 18, "danio": 25,
         "empuje": 90, "cooldown": 9, "retraso": 0.6, "color": ("rgb", 150, 255, 210)},
        {"nombre": "Paso Sagrado", "tipo": "Teletransporte", "anim": "PasoSagrado", "rango": 50, "danio": 15,
         "radio": 8, "cooldown": 12, "retraso": 0.3, "color": ("rgb", 255, 205, 60)},
    ],
}

# ------------------------------------------------------------------ animaciones

# Onda de la cola de serpiente: todos los segmentos con la misma frecuencia y la fase desplazada, asi la onda
# viaja de la base a la punta. Cola1/Cola2 van hacia atras (se mueven de lado con ry); Cola3/Cola4 suben, asi
# que se mueven de lado con rz (con signo contrario para ir al mismo lado).


def onda_cola(frec, amp, alto=0.0, paso=0.17):
    return {
        "Cola1": [("ry", amp * 0.6, frec, 0.0), ("rx", alto, frec, 0.25)],
        "Cola2": [("ry", amp, frec, paso), ("rx", alto, frec, 0.25 + paso)],
        "Cola3": [("ry", amp * 0.6, frec, 2 * paso), ("rz", -amp * 0.7, frec, 2 * paso),
                  ("rx", alto, frec, 0.25 + 2 * paso)],
        "Cola4": [("rz", -amp * 1.2, frec, 3 * paso), ("rx", alto * 1.3, frec, 0.25 + 3 * paso)],
    }


def patas(rx):
    """Las patas giran al reves que el cuerpo para que los pies se queden en el piso."""
    return {"PataIzq": {"rx": -rx}, "PataDer": {"rx": -rx}}


def pose(raiz=None, **partes):
    p = dict(partes)
    if raiz:
        p["Raiz"] = raiz
        if "rx" in raiz and "PataIzq" not in partes:
            p.update(patas(raiz["rx"]))
    return p


ANIMACIONES = {
    "Idle": {
        "Raiz": [("py", 0.06, 0.8, 0), ("rx", 1.5, 0.4, 0.3)],
        "Cabeza": [("rx", 4, 0.8, 0.1), ("ry", 10, 0.3, 0)],
        "Penacho": [("rx", 3, 0.8, 0.35), ("rz", 2, 0.5, 0)],
        "AlaIzq": [("rz", -3, 0.8, 0)],
        "PataIzq": [("rx", -1.5, 0.4, 0.3)],
        "PataDer": [("rx", -1.5, 0.4, 0.3)],
        **onda_cola(0.6, 10, 3),
    },
    "Caminar": {
        "Raiz": [("py", 0.14, 3.2, 0.25), ("rz", 3, 1.6, 0), ("ry", 3, 1.6, 0.25)],
        "Cabeza": [("pz", 0.18, 3.2, 0), ("rx", 5, 3.2, 0.25)],
        "Penacho": [("rx", 5, 3.2, 0.4), ("rz", 3, 1.6, 0.1)],
        "AlaIzq": [("rz", -7, 1.6, 0.25)],
        "PataIzq": [("rx", 27, 1.6, 0)],
        "PataDer": [("rx", 27, 1.6, 0.5)],
        **onda_cola(1.6, 12, 3),
    },
    "clips": {
        # Golpe a los 0.35 s: se echa atras, lanza un picotazo y la cola-serpiente da un latigazo por encima
        "MordidaSerpiente": {"duracion": 0.95, "claves": [
            (0.0, {}),
            (0.18, pose({"rx": 8, "pz": 0.3}, Cabeza={"rx": 25, "pz": 0.1}, Penacho={"rx": -8},
                        AlaIzq={"rz": -18}, Cola1={"rx": 14}, Cola2={"rx": 12, "ry": 8}, Cola3={"rx": 10},
                        Cola4={"rx": 10})),
            (0.35, pose({"rx": -12, "pz": -0.5}, Cabeza={"rx": -40, "pz": -0.3}, Penacho={"rx": 15},
                        AlaIzq={"rz": -35, "ry": -15}, Cola1={"rx": -18}, Cola2={"rx": -24}, Cola3={"rx": -28},
                        Cola4={"rx": -32})),
            (0.5, pose({"rx": -8, "pz": -0.35}, Cabeza={"rx": -25, "pz": -0.2}, Penacho={"rx": 8},
                       AlaIzq={"rz": -22}, Cola1={"rx": -12}, Cola2={"rx": -16}, Cola3={"rx": -18},
                       Cola4={"rx": -12})),
            (0.95, {}),
        ]},
        # Lanza las plumas a los 0.4 s: abre las alas en alto y las sacude hacia adelante
        "LluviaPlumas": {"duracion": 1.1, "claves": [
            (0.0, {}),
            (0.25, pose({"py": 0.12, "rx": 8, "pz": 0.2}, Cabeza={"rx": 18}, Penacho={"rx": -14},
                        AlaIzq={"rx": -60, "ry": -30, "rz": -75}, Cola1={"rx": -8}, Cola3={"rx": -8},
                        Cola4={"rx": -18})),
            (0.4, pose({"rx": -10, "pz": -0.25}, Cabeza={"rx": -18, "pz": -0.15}, Penacho={"rx": 16},
                       AlaIzq={"rx": 5, "ry": -100, "rz": -45}, Cola1={"rx": 6}, Cola2={"rx": 4},
                       Cola4={"rx": 12})),
            (0.6, pose({"rx": -6, "pz": -0.12}, Cabeza={"rx": -8}, Penacho={"rx": 6},
                       AlaIzq={"rx": 0, "ry": -65, "rz": -25})),
            (1.1, {}),
        ]},
        # Onda a los 0.6 s: se eleva con las alas en alto y da un aletazo enorme hacia abajo
        "VientoDivino": {"duracion": 1.4, "claves": [
            (0.0, {}),
            (0.2, pose({"py": -0.1, "rx": -6}, Cabeza={"rx": -10}, AlaIzq={"rz": -25, "ry": -15})),
            (0.42, pose({"py": 0.55, "rx": 10}, Cabeza={"rx": 20}, Penacho={"rx": -12},
                        AlaIzq={"rx": -75, "ry": -30, "rz": -85}, Cola1={"rx": -10}, Cola2={"rx": -8},
                        Cola3={"rx": -8}, Cola4={"rx": -12})),
            (0.6, pose({"py": -0.1, "rx": -8}, Cabeza={"rx": -20}, Penacho={"rx": 22},
                       AlaIzq={"rx": 25, "ry": -45, "rz": -50}, Cola1={"rx": 10}, Cola2={"rx": 10},
                       Cola3={"rx": 8}, Cola4={"rx": 14})),
            (0.85, pose({"py": -0.06, "rx": -5}, Cabeza={"rx": -10}, Penacho={"rx": 10},
                        AlaIzq={"rx": 10, "ry": -25, "rz": -25}, Cola4={"rx": 5})),
            (1.4, {}),
        ]},
        # Teletransporte a los 0.3 s: se encoge y estalla abriendo alas, penacho y cola
        "PasoSagrado": {"duracion": 1.0, "claves": [
            (0.0, {}),
            (0.15, pose({"py": -0.08, "rx": -10}, Cabeza={"rx": -25, "pz": -0.15}, Penacho={"rx": 20},
                        AlaIzq={"rz": 8, "ry": 8}, Cola1={"rx": 10}, Cola2={"rx": 12}, Cola3={"rx": 10},
                        Cola4={"rx": 8})),
            (0.3, pose({"py": 0.3, "rx": 6}, Cabeza={"rx": 22}, Penacho={"rx": -18},
                       AlaIzq={"rx": -50, "ry": -45, "rz": -75}, Cola1={"rx": -12}, Cola2={"rx": -14},
                       Cola3={"rx": -10}, Cola4={"rx": -18})),
            (0.55, pose({"py": 0.12, "rx": 3}, Cabeza={"rx": 10}, Penacho={"rx": -8},
                        AlaIzq={"rx": -30, "ry": -30, "rz": -45}, Cola4={"rx": -8})),
            (1.0, {}),
        ]},
        "Golpeado": {"duracion": 0.4, "claves": [
            (0.0, {}),
            (0.1, pose({"rx": 8, "pz": 0.3}, Cabeza={"rx": 20}, Penacho={"rx": -10}, AlaIzq={"rz": -20},
                       Cola2={"ry": 10}, Cola4={"rz": -12})),
            (0.4, {}),
        ]},
        # Se tambalea hacia atras y se desploma de pecho con las alas abiertas en el piso
        "Derrota": {"duracion": 1.6, "claves": [
            (0.0, {}),
            (0.3, pose({"rx": 12, "py": 0.1}, Cabeza={"rx": 30}, Penacho={"rx": -10}, AlaIzq={"rz": -50},
                       Cola4={"rx": -15})),
            (0.65, pose({"rx": 4, "rz": -10}, Cabeza={"rx": -20, "ry": 20}, Penacho={"rx": 20},
                        AlaIzq={"rz": -25})),
            (1.05, {"Raiz": {"rx": -10, "py": -1.0}, "PataIzq": {"rx": -55}, "PataDer": {"rx": -55},
                    "Cabeza": {"rx": -10, "ry": 25}, "Penacho": {"rx": 25}, "AlaIzq": {"rz": -35, "ry": -15},
                    "Cola3": {"rx": 15}, "Cola4": {"rx": 10}}),
            (1.6, {"Raiz": {"rx": -18, "py": -3.3}, "PataIzq": {"rx": -72}, "PataDer": {"rx": -72},
                   "Cabeza": {"rx": -35, "ry": 35}, "Penacho": {"rx": 40},
                   "AlaIzq": {"rz": -15, "ry": -35}, "Cola1": {"rx": 12}, "Cola2": {"rx": 15, "ry": -12},
                   "Cola3": {"rx": 45, "ry": -10}, "Cola4": {"rx": 45}}),
        ]},
    },
}
