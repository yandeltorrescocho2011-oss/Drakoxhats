"""Gallo Catrín: gallo calavera de Día de Muertos, elegante y espectral.

Cabeza de calavera de azúcar (pétalos rosa, turquesa y naranja alrededor de las cuencas, ojos de brillo
morado, pico de hueso con puntadas), sombrero charro negro de ala ancha levantada con borde dorado y flores
de cempasúchil en la banda. Plumaje morado oscuro casi negro con costillas de hueso en el pecho y un corazón
de alma que brilla adentro, collar de cempasúchil, cola de plumas fantasmales con fuego de alma en las
puntas y patas de hueso con espuelas charras de oro.
"""
import math
import random

from mathutils import Euler, Matrix, Vector

from motor import alargar

NOMBRE = "GalloCatrin"
COLORES_EXTRA = {
    "pluma_noche": (0.14, 0.07, 0.22),      # plumaje principal (morado casi negro)
    "pluma_morada": (0.32, 0.12, 0.50),     # capas de plumas
    "pluma_violeta": (0.50, 0.25, 0.72),    # puntas claras de la golilla
    "calavera": (0.97, 0.95, 0.90),         # calavera de azucar y costillas
    "cuenca": (0.04, 0.015, 0.06),          # cuencas, cavidad del pecho, puntadas
    "alma_morada": (0.80, 0.38, 1.00),      # brillo: ojos, corazon, fuego de alma
    "alma_turquesa": (0.25, 1.00, 0.88),    # brillo: fuego de alma de la cola
    "turquesa": (0.05, 0.74, 0.74),         # decoracion de la calavera
    "rosa_mex": (1.00, 0.22, 0.58),         # rosa mexicano
    "cempasuchil": (1.00, 0.52, 0.04),
    "cempasuchil_cl": (1.00, 0.72, 0.14),
    "cempasuchil_osc": (0.82, 0.28, 0.02),
    "fantasma": (0.62, 0.52, 1.00),         # plumas fantasma (semitransparentes)
    "sombrero": (0.07, 0.05, 0.08),
    "hoja": (0.16, 0.55, 0.24),
}

RND = random.Random(1102)  # 2 de noviembre


# ------------------------------------------------------------------ utilidades

def _grados(m):
    return tuple(math.degrees(a) for a in m.to_euler("XYZ"))


def _rot_base(eje_y, eje_z):
    """Euler (grados) que lleva el eje local Y hacia eje_y y el Z lo mas cerca posible de eje_z."""
    y = Vector(eje_y).normalized()
    z = Vector(eje_z)
    z = (z - y * z.dot(y)).normalized()
    x = y.cross(z)
    return _grados(Matrix((x, y, z)).transposed())


def _rot_zy(eje_z, eje_y):
    """Euler (grados) que lleva el eje local Z hacia eje_z y el Y lo mas cerca posible de eje_y."""
    z = Vector(eje_z).normalized()
    y = Vector(eje_y)
    y = (y - z * y.dot(z)).normalized()
    x = y.cross(z)
    return _grados(Matrix((x, y, z)).transposed())


def _tangentes(n):
    """Base tangente (horizontal, vertical) de una superficie con normal n."""
    n = Vector(n).normalized()
    e1 = Vector((0, 0, 1)).cross(n)
    e1 = e1.normalized() if e1.length > 1e-4 else Vector((1, 0, 0))
    return e1, n.cross(e1)


def _lerp(a, b, t):
    return Vector(a) + (Vector(b) - Vector(a)) * t


class Elip:
    """Elipsoide (opcionalmente girado) para pegar piezas sobre su superficie."""

    def __init__(self, centro, radios, rot=(0, 0, 0)):
        self.c, self.r = Vector(centro), Vector(radios)
        self.m = Euler(tuple(math.radians(a) for a in rot), "XYZ").to_matrix()

    def punto(self, u, v, salir=0.0):
        """u = azimut en grados (0 = frente -Y, +90 = izquierda +X), v = elevacion en grados.
        Devuelve (punto, normal)."""
        u, v = math.radians(u), math.radians(v)
        d = Vector((math.sin(u) * math.cos(v), -math.cos(u) * math.cos(v), math.sin(v)))
        return self._sobre(Vector((d.x * self.r.x, d.y * self.r.y, d.z * self.r.z)), salir)

    def proyectar(self, p, salir=0.0):
        """Lleva p a la superficie (por el rayo desde el centro)."""
        q = self.m.transposed() @ (Vector(p) - self.c)
        s = 1 / math.sqrt(sum((q[i] / self.r[i]) ** 2 for i in range(3)))
        return self._sobre(q * s, salir)

    def _sobre(self, q, salir):
        n = Vector((q.x / self.r.x ** 2, q.y / self.r.y ** 2, q.z / self.r.z ** 2)).normalized()
        return self.c + self.m @ (q + n * salir), self.m @ n


class _Girado:
    """Construye piezas en un marco local girado (el sombrero ladeado). Coordenadas locales con Z = arriba
    del sombrero y el origen en el centro de su base."""

    def __init__(self, c, origen, rot):
        self.c, self.o = c, Vector(origen)
        self.m = Euler(tuple(math.radians(a) for a in rot), "XYZ").to_matrix()

    def p(self, local):
        return tuple(self.o + self.m @ Vector(local))

    def pieza(self, tipo, pos, esc=1, color="negro", rot=(0, 0, 0), **kw):
        m = self.m @ Euler(tuple(math.radians(a) for a in rot), "XYZ").to_matrix()
        return self.c.pieza(tipo, self.p(pos), esc, color, rot=_grados(m), **kw)

    def orientada(self, tipo, pos, eje_z, eje_y, esc, color, **kw):
        rot = _rot_zy(self.m @ Vector(eje_z), self.m @ Vector(eje_y))
        return self.c.pieza(tipo, self.p(pos), esc, color, rot=rot, **kw)

    def entre(self, a, b, radio, color="negro", **kw):
        return self.c.entre(self.p(a), self.p(b), radio, color, **kw)


def _cadena(c, puntos, r0, r1, color, aplanar=1.0, lados=6, **kw):
    """Tubo que se adelgaza siguiendo varios puntos (costillas, plumas en hoz)."""
    n = len(puntos) - 1
    for i in range(n):
        ra = r0 + (r1 - r0) * i / n
        rb = r0 + (r1 - r0) * (i + 1) / n
        a, b = tuple(puntos[i]), tuple(puntos[i + 1])
        ultimo = i == n - 1
        if not ultimo:
            b = alargar(a, b, ra * 0.9)  # solapa un poco para que no queden huecos en los codos
        c.entre(a, b, ra, color, tipo="cono", punta=(rb / ra) if not ultimo else 0.0, aplanar=aplanar,
                lados=lados, **kw)


def _flor(c, centro, r, normal, **kw):
    """Cempasuchil: pompon de petalos (icosaedros girados al azar en tres tonos)."""
    n = Vector(normal).normalized()
    p = Vector(centro)

    def giro():
        return (RND.uniform(0, 360), RND.uniform(0, 360), RND.uniform(0, 360))

    c.pieza("ico", tuple(p), r, "cempasuchil_osc", rot=giro(), subdiv=1, **kw)
    c.pieza("ico", tuple(p + n * r * 0.3), r * 0.9, "cempasuchil", rot=giro(), subdiv=1, **kw)
    c.pieza("ico", tuple(p + n * r * 0.62), r * 0.6, "cempasuchil_cl", rot=giro(), subdiv=1, **kw)


def _florecita(c, centro, normal, r, petalo, centro_color, n_petalos=6, superficie=None, **kw):
    """Florecita plana pintada (decoracion de la calavera y del sombrero)."""
    n = Vector(normal).normalized()
    e1, e2 = _tangentes(n)
    for k in range(n_petalos):
        a = 2 * math.pi * k / n_petalos
        radial = e1 * math.cos(a) + e2 * math.sin(a)
        p, nn = Vector(centro) + radial * r * 0.95, n
        if superficie:
            p, nn = superficie.proyectar(p, 0.0)
        c.pieza("esfera", tuple(p), (r * 0.42, r * 0.22, r * 0.8), petalo, rot=_rot_base(nn, radial), seg=8,
                anillos=5, **kw)
    c.pieza("esfera", tuple(Vector(centro) + n * r * 0.12), (r * 0.42, r * 0.3, r * 0.42), centro_color,
            rot=_rot_base(n, e2), seg=8, anillos=5, **kw)


def _hueso(c, a, b, r, color="hueso", nudo=1.45, lado=None, puntas=(True, True), **kw):
    """Hueso de caricatura: cana con dos nudos en cada punta."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    if lado is None:
        lado = d.cross(Vector((0, 0, 1)))
        lado = lado.normalized() if lado.length > 1e-3 else Vector((1, 0, 0))
    c.entre(tuple(a), tuple(b), r, color, tipo="cilindro", lados=8, **kw)
    for p, si in zip((a, b), puntas):
        if si:
            for s in (-1, 1):
                c.pieza("esfera", tuple(p + Vector(lado) * s * r * 0.85), r * nudo, color, seg=8, anillos=6, **kw)


# ------------------------------------------------------------------ geometria

CUERPO = Elip((0, 0.2, 2.95), (0.92, 1.25, 0.98), rot=(-12, 0, 0))
CRANEO = Elip((0, -1.05, 4.92), (0.6, 0.6, 0.55))
U_OJO, V_OJO = 31, 3              # cuenca izquierda (la derecha es espejo)
SOMBRERO_O = (0, -1.0, 5.3)       # centro de la base del sombrero (articulacion)
SOMBRERO_ROT = (-15, 7, 0)        # ladeado hacia atras (se ve la cara) y un poco de lado
CUELLO_EJE = Vector((0, -0.42, 1.0)).normalized()
CUELLO_BASE = Vector((0, -0.6, 3.86))


def construir(c):
    RND.seed(1102)  # mismas flores aunque se construya varias veces (poster)
    c.parte("Cabeza", "Cuerpo", (0, -0.55, 3.78))
    c.parte("Mandibula", "Cabeza", (0, -1.5, 4.55))
    c.parte("Sombrero", "Cabeza", SOMBRERO_O)
    c.parte("AlaIzq", "Cuerpo", (0.8, -0.35, 3.42), espejo=True)
    c.parte("PataIzq", "Cuerpo", (0.42, 0.35, 2.2), espejo=True)
    c.parte("Cola", "Cuerpo", (0, 1.3, 3.45))

    _cuerpo(c)
    _pecho(c)
    _collar(c)
    _cabeza(c)
    _mandibula(c)
    _sombrero(c)
    _alas(c)
    _patas(c)
    _cola(c)


def _cuerpo(c):
    c.usar("Cuerpo")
    c.pieza("esfera", tuple(CUERPO.c), tuple(CUERPO.r), "pluma_noche", rot=(-12, 0, 0), seg=18, anillos=12)
    # plumas de los costados (escamas un poco mas claras)
    for u, v in ((66, 6), (60, -24), (80, 26), (84, -6), (78, -34)):
        p, n = CUERPO.punto(u, v, 0.0)
        e1, e2 = _tangentes(n)
        c.pieza("esfera", tuple(p), (0.24, 0.07, 0.3), "pluma_morada", rot=_rot_base(n, e2), seg=8, anillos=6,
                espejo=True)
    # silla: plumas del lomo que caen hacia la cola
    for k, x in enumerate((-0.42, -0.14, 0.14, 0.42)):
        c.entre((x, 0.85, 3.85), (x * 1.35, 1.75, 3.55 - 0.06 * (k % 2)), 0.2,
                "pluma_morada" if k % 2 else "pluma_noche", tipo="esfera", aplanar=0.45, seg=10, anillos=6)
    # columna: vertebras de hueso asomando por el lomo
    for k in range(4):
        p, n = CUERPO.punto(180, 84 - 12 * k, 0.0)
        c.pieza("esfera", tuple(p + n * 0.02), (0.13, 0.1, 0.07), "hueso", rot=_rot_base(n, (0, 1, 0)), seg=8,
                anillos=6)
        c.entre(tuple(p), tuple(p + n * 0.2), 0.05, "hueso", lados=5)


def _pecho(c):
    """Cavidad oscura del pecho, costillas de hueso y el corazon de alma que brilla adentro."""
    c.usar("Cuerpo")
    p, n = CUERPO.punto(0, -8, -0.035)
    c.pieza("esfera", tuple(p), (0.68, 0.055, 0.58), "cuenca", rot=_rot_base(n, (0, 0, 1)), seg=14, anillos=8)
    p, n = CUERPO.punto(19, -5, 0.07)
    e1, e2 = _tangentes(n)
    for s in (-1, 1):
        c.pieza("esfera", tuple(p + e1 * s * 0.09 + e2 * 0.06), (0.12, 0.06, 0.12), "alma_morada",
                rot=_rot_base(n, e2), seg=8, anillos=6, brillo=True)
    c.entre(tuple(p + e2 * 0.04), tuple(p - e2 * 0.24), 0.17, "alma_morada", tipo="cono", lados=6, aplanar=0.4,
            brillo=True)
    costillas = ((18, 70, 0.078), (4, 76, 0.074), (-10, 74, 0.068), (-24, 64, 0.06))
    for v0, umax, r in costillas:
        pts = []
        for i in range(7):
            u = umax * i / 6
            v = v0 - 14 * (u / 75) ** 1.4
            pts.append(CUERPO.punto(u, v, 0.06)[0])
        _cadena(c, pts, r, r * 0.5, "calavera", lados=6, espejo=True)
    pts = [CUERPO.punto(0, v, 0.08)[0] for v in (28, 14, 0, -14, -28, -38)]
    _cadena(c, pts, 0.095, 0.07, "calavera", lados=6)                 # esternon
    c.pieza("esfera", tuple(pts[-1]), 0.08, "calavera", seg=8, anillos=6)


def _collar(c):
    c.usar("Cuerpo")
    eje, centro = CUELLO_EJE, CUELLO_BASE
    e1, e2 = _tangentes(eje)          # e1 = izquierda, e2 = atras/arriba; el frente es -e2
    # golilla: plumas del cuello que caen sobre los hombros (mas cortas al frente para que se vea el pecho)
    for k in range(14):
        a = 2 * math.pi * (k + 0.5) / 14
        radial = e1 * math.cos(a) + e2 * math.sin(a)
        frente = max(-math.sin(a), 0.0)
        ini = centro + eje * 0.2 + radial * 0.3
        fin = centro - eje * (0.5 - 0.3 * frente) + radial * (0.95 - 0.3 * frente)
        c.entre(tuple(ini), tuple(fin), 0.2, "pluma_violeta" if k % 2 else "pluma_morada", tipo="esfera",
                aplanar=0.45, seg=8, anillos=6)
    # collar de cempasuchil con hojitas
    for k in range(11):
        a = 2 * math.pi * k / 11 + math.pi / 2
        radial = e1 * math.cos(a) + e2 * math.sin(a)
        _flor(c, centro + radial * 0.52, 0.17, radial * 0.6 + eje * 0.8)
        b = 2 * math.pi * (k + 0.5) / 11 + math.pi / 2
        rad2 = e1 * math.cos(b) + e2 * math.sin(b)
        q = centro + rad2 * 0.6 - eje * 0.08
        c.entre(tuple(q - rad2 * 0.1), tuple(q + rad2 * 0.2 - eje * 0.08), 0.07, "hoja", tipo="esfera",
                aplanar=0.4, seg=6, anillos=4)


def _cabeza(c):
    c.usar("Cabeza")
    # cuello de plumas (sale de adentro del collar)
    c.entre((0, -0.52, 3.6), (0, -0.98, 4.62), 0.34, "pluma_noche", tipo="esfera", seg=10, anillos=8)
    # calavera: craneo redondo, hocico y pomulos
    c.pieza("esfera", tuple(CRANEO.c), tuple(CRANEO.r), "calavera", seg=18, anillos=12)
    c.pieza("esfera", (0, -1.36, 4.62), (0.42, 0.4, 0.32), "calavera", seg=14, anillos=9)
    p, n = CRANEO.punto(52, -22, -0.06)
    c.pieza("esfera", tuple(p), (0.17, 0.12, 0.13), "calavera", rot=_rot_base(n, (0, 0, 1)), seg=8, anillos=6,
            espejo=True)

    # cuencas con ojos de brillo morado, petalos alrededor y ceja enojada
    S, n = CRANEO.punto(U_OJO, V_OJO, -0.02)
    e1, e2 = _tangentes(n)
    c.pieza("esfera", tuple(S), (0.2, 0.09, 0.22), "cuenca", rot=_rot_base(n, e2), seg=12, anillos=8, espejo=True)
    c.pieza("esfera", tuple(S + n * 0.035), (0.085, 0.06, 0.1), "alma_morada", rot=_rot_base(n, e2),
            seg=10, anillos=6, brillo=True, espejo=True)
    colores = ("rosa_mex", "cempasuchil", "rosa_mex", "turquesa")
    npet = 10
    for k in range(npet):
        a = 2 * math.pi * k / npet + 0.2
        radial = e1 * math.cos(a) + e2 * math.sin(a)
        p, nn = CRANEO.proyectar(S + radial * 0.32, 0.0)
        c.pieza("esfera", tuple(p), (0.055, 0.028, 0.1), colores[k % 4], rot=_rot_base(nn, radial), seg=8, anillos=5,
                espejo=True)
        if k % 2 == 0:
            p2, nn2 = CRANEO.proyectar(S + radial * 0.46, 0.0)
            c.pieza("esfera", tuple(p2), (0.035, 0.02, 0.035), "turquesa", rot=_rot_base(nn2, radial), seg=6,
                    anillos=4, espejo=True)
    # monoculo dorado en el ojo izquierdo con su cadenita que cuelga hacia la nuca
    centro_mono = S + n * 0.08
    c.pieza("toro", tuple(centro_mono), 1, "oro", rot=_rot_zy(n, e2), radio=0.27, grosor=0.032, seg=16, seg_menor=4)
    inicio = centro_mono - e2 * 0.2 + e1 * 0.18
    fin, _ = CRANEO.punto(96, -28, 0.03)
    for k in range(9):
        t = k / 8
        p = _lerp(inicio, fin, t) - Vector((0, 0, 0.2 * math.sin(math.pi * t)))
        p, _ = CRANEO.proyectar(p, 0.035) if t > 0.15 else (p, None)
        c.pieza("ico", tuple(p), 0.03, "oro", subdiv=1)
    # ceja enojada (baja hacia el centro)
    pts = [CRANEO.proyectar(S + e1 * dx + e2 * dy, 0.035)[0] for dx, dy in ((-0.3, 0.2), (-0.05, 0.34), (0.26, 0.4))]
    _cadena(c, pts, 0.055, 0.03, "cuenca", lados=5, aplanar=0.7, espejo=True)

    # flor en la frente, flores en las sienes y puntitos bajo los ojos
    p, n = CRANEO.punto(0, 34, 0.0)
    _florecita(c, p, n, 0.11, "rosa_mex", "oro", superficie=CRANEO)
    p, n = CRANEO.punto(78, 12, 0.0)
    _florecita(c, p, n, 0.1, "turquesa", "rosa_mex", n_petalos=5, superficie=CRANEO, espejo=True)
    for k in range(4):
        p, n = CRANEO.punto(50 + 9 * k, -20 + 6 * k, 0.0)
        c.pieza("esfera", tuple(p), (0.03, 0.02, 0.03), "rosa_mex" if k % 2 else "cempasuchil",
                rot=_rot_base(n, (0, 0, 1)), seg=6, anillos=4, espejo=True)

    # pico de hueso (de arriba): ganchudo, con fosas nasales y puntadas
    _cadena(c, [(0, -1.58, 4.68), (0, -2.0, 4.6), (0, -2.28, 4.44)], 0.2, 0.03, "hueso", lados=6, aplanar=0.78)
    c.pieza("esfera", (0.055, -1.86, 4.71), (0.05, 0.03, 0.06), "cuenca", rot=(20, 0, 25), seg=6, anillos=4,
            espejo=True)
    for k in range(5):  # puntadas de la boca (mitad de arriba)
        c.pieza("cubo", (0.0, -1.7 - 0.11 * k, 4.555 - 0.012 * k), (0.36 - 0.05 * k, 0.025, 0.06), "cuenca")


def _mandibula(c):
    c.usar("Mandibula")
    c.entre((0, -1.52, 4.5), (0, -2.06, 4.47), 0.13, "hueso", lados=6, aplanar=0.62)
    c.pieza("esfera", (0, -1.55, 4.5), (0.22, 0.12, 0.08), "hueso", seg=10, anillos=6)
    for k in range(4):  # puntadas (mitad de abajo)
        c.pieza("cubo", (0.0, -1.7 - 0.11 * k, 4.5), (0.24 - 0.04 * k, 0.025, 0.06), "cuenca")
    # barbillas de petalos de cempasuchil
    c.entre((0.07, -1.72, 4.42), (0.1, -1.66, 4.12), 0.1, "cempasuchil", tipo="esfera", aplanar=0.6, seg=8,
            anillos=6, espejo=True)
    c.entre((0.07, -1.7, 4.3), (0.12, -1.66, 4.05), 0.06, "cempasuchil_osc", tipo="esfera", aplanar=0.6, seg=8,
            anillos=6, espejo=True)


def _sombrero(c):
    c.usar("Sombrero")
    h = _Girado(c, SOMBRERO_O, SOMBRERO_ROT)
    N = 24
    # ala ancha: parte plana y dos aros de tablitas que se levantan hacia el borde dorado
    h.pieza("cilindro", (0, 0, 0.03), (1.02, 1.02, 0.06), "sombrero", lados=N)
    aros = ((0.98, 0.04, 1.2, 0.13), (1.16, 0.1, 1.44, 0.4))
    for r0, z0, r1, z1 in aros:
        dr, dz = r1 - r0, z1 - z0
        for k in range(N):
            a = 2 * math.pi * (k + 0.5) / N
            ca, sa = math.cos(a), math.sin(a)
            centro = ((r0 + r1) / 2 * ca, (r0 + r1) / 2 * sa, (z0 + z1) / 2)
            h.orientada("cono", centro, (ca * dr, sa * dr, dz), (-ca * dz, -sa * dz, dr),
                        (math.pi * r0 / N * 1.06, 0.035, math.hypot(dr, dz) * 1.03), "sombrero", lados=4,
                        punta=r1 / r0)
    h.pieza("toro", (0, 0, 0.4), 1, "oro", radio=1.44, grosor=0.06, seg=N * 2, seg_menor=5)
    for k in range(12):  # bordado dorado: rombos en el ala levantada y puntitos en la parte plana
        a = 2 * math.pi * k / 12
        ca, sa = math.cos(a), math.sin(a)
        h.orientada("cono", (1.3 * ca, 1.3 * sa, 0.275), (ca * 0.28, sa * 0.28, 0.3), (-ca * 0.3, -sa * 0.3, 0.28),
                    (0.06, 0.03, 0.13), "oro", lados=4, punta=0.01)
        b = a + math.pi / 12
        h.pieza("esfera", (0.82 * math.cos(b), 0.82 * math.sin(b), 0.065), (0.05, 0.05, 0.02), "oro", seg=6,
                anillos=4)

    # copa alta en punta redondeada
    def radio_copa(z):
        return 0.52 - 0.28 * (z - 0.02) / 1.1

    h.pieza("cono", (0, 0, 0.57), (0.52, 0.52, 1.1), "sombrero", punta=0.46, lados=12)
    h.pieza("esfera", (0, 0, 1.12), (0.24, 0.24, 0.13), "sombrero", seg=12, anillos=6)
    # banda: dos lineas doradas, rombos y flores
    h.pieza("toro", (0, 0, 0.09), 1, "oro", radio=radio_copa(0.09) + 0.01, grosor=0.045, seg=20, seg_menor=4)
    h.pieza("toro", (0, 0, 0.32), 1, "oro", radio=radio_copa(0.32) + 0.005, grosor=0.035, seg=20, seg_menor=4)
    for k in range(10):
        a = 2 * math.pi * k / 10 + 0.31
        r = radio_copa(0.62)
        h.pieza("cubo", (r * math.cos(a), r * math.sin(a), 0.62), (0.055, 0.055, 0.055), "oro",
                rot=(0, 45, math.degrees(a)))
    for ang, r in ((-20, 0.17), (15, 0.2), (50, 0.17), (195, 0.15)):
        a = math.radians(ang)
        d = Vector((math.cos(a), math.sin(a), 0))
        p = d * (radio_copa(0.2) + 0.06) + Vector((0, 0, 0.2))
        _flor(c, h.p(p), r, h.m @ (d + Vector((0, 0, 0.3))))   # _flor trabaja en coordenadas del mundo
    for ang in (-2, 33, 65):  # hojitas entre las flores
        a = math.radians(ang)
        d = (math.cos(a), math.sin(a))
        h.entre((0.48 * d[0], 0.48 * d[1], 0.2), (0.75 * d[0], 0.75 * d[1], 0.3), 0.07, "hoja", tipo="esfera",
                aplanar=0.4, seg=6, anillos=4)
    a = math.radians(-42)
    p = Vector(((radio_copa(0.21) + 0.02) * math.cos(a), (radio_copa(0.21) + 0.02) * math.sin(a), 0.21))
    _florecita(c, h.p(p), h.m @ Vector((math.cos(a), math.sin(a), 0.2)), 0.08, "rosa_mex", "oro")


def _alas(c):
    c.usar("AlaIzq")
    c.pieza("esfera", (1.02, 0.2, 2.95), (0.22, 0.95, 0.58), "pluma_noche", rot=(-20, 0, 0), espejo=True)
    c.pieza("esfera", (1.12, -0.08, 3.12), (0.16, 0.64, 0.38), "pluma_morada", rot=(-20, 0, 0), espejo=True)
    for k in range(3):  # cobertoras en capas
        c.pieza("esfera", (1.16, 0.25 + 0.05 * k, 2.95 - 0.16 * k), (0.12, 0.55, 0.13),
                "pluma_violeta" if k == 0 else "pluma_morada", rot=(-18, 0, 0), seg=10, anillos=6, espejo=True)
    for k in range(5):  # primarias
        a = (1.08 - 0.01 * k, 0.55 + 0.06 * k, 2.85 - 0.09 * k)
        b = (1.02 - 0.02 * k, 1.78 + 0.05 * k, 2.52 - 0.15 * k)
        c.entre(a, b, 0.06, "pluma_noche" if k % 2 else "pluma_morada", tipo="esfera", aplanar=3.4, seg=8,
                anillos=6, espejo=True)
    # hueso del ala por el borde de arriba (hombro a muneca)
    _hueso(c, (0.98, -0.5, 3.38), (1.2, 0.3, 3.42), 0.055, color="hueso", lado=(0, 0, 1), espejo=True)


def _patas(c):
    c.usar("PataIzq")
    # muslo de plumas tipo pantalon charro con botonadura dorada
    c.pieza("esfera", (0.42, 0.35, 1.85), (0.32, 0.38, 0.5), "pluma_noche", seg=12, anillos=8, espejo=True)
    for k in range(3):
        c.pieza("esfera", (0.72, 0.3 + 0.03 * k, 2.05 - 0.22 * k), 0.055, "oro", seg=8, anillos=6, espejo=True)
    for k in range(6):  # volante de plumas abajo del muslo
        a = 2 * math.pi * k / 6
        c.entre((0.42, 0.37, 1.55), (0.42 + 0.3 * math.cos(a), 0.37 + 0.3 * math.sin(a), 1.32), 0.11,
                "pluma_morada", tipo="esfera", aplanar=0.5, seg=8, anillos=5, espejo=True)
    # canilla de hueso
    _hueso(c, (0.42, 0.42, 1.4), (0.42, 0.47, 0.2), 0.085, nudo=1.35, lado=(1, 0, 0), espejo=True)
    # dedos de hueso con garras negras
    tob = (0.42, 0.47, 0.12)
    for ang in (-34, 0, 34):
        a = math.radians(ang)
        medio = (0.42 + 0.3 * math.sin(a), 0.47 - 0.3 * math.cos(a), 0.08)
        fin = (0.42 + 0.55 * math.sin(a), 0.47 - 0.55 * math.cos(a), 0.06)
        c.entre(tob, medio, 0.06, "hueso", tipo="cilindro", lados=6, espejo=True)
        c.entre(medio, fin, 0.05, "hueso", tipo="cilindro", lados=6, espejo=True)
        c.pieza("esfera", medio, 0.07, "hueso", seg=8, anillos=5, espejo=True)
        c.entre(fin, (fin[0] + 0.14 * math.sin(a), fin[1] - 0.14 * math.cos(a), 0.02), 0.05, "negro", lados=5,
                espejo=True)
    c.entre(tob, (0.42, 0.85, 0.06), 0.05, "hueso", tipo="cilindro", lados=6, espejo=True)
    c.entre((0.42, 0.85, 0.06), (0.42, 0.97, 0.02), 0.045, "negro", lados=5, espejo=True)
    # espolon de hueso y espuela charra de oro en el talon
    c.entre((0.42, 0.52, 0.55), (0.42, 0.82, 0.48), 0.05, "hueso", lados=5, espejo=True)
    c.entre((0.42, 0.52, 0.28), (0.42, 0.72, 0.28), 0.03, "oro", tipo="cilindro", lados=5, espejo=True)
    c.pieza("cilindro", (0.42, 0.76, 0.28), (0.11, 0.11, 0.03), "oro", rot=(0, 90, 0), lados=10, espejo=True)
    for k in range(6):
        a = 2 * math.pi * k / 6
        d = (0, math.cos(a), math.sin(a))
        c.entre((0.42, 0.76 + 0.08 * d[1], 0.28 + 0.08 * d[2]), (0.42, 0.76 + 0.17 * d[1], 0.28 + 0.17 * d[2]),
                0.03, "oro", lados=4, espejo=True)


COLA_BASE = [(1.35, 3.6), (1.85, 4.55), (2.55, 5.2), (3.35, 5.28), (3.9, 4.85), (4.12, 4.1)]


def _cola(c):
    c.usar("Cola")

    def hoz(x, escala, color, alto=1.0, abre=0.6, fuego="alma_turquesa"):
        pts = []
        for i, (y, z) in enumerate(COLA_BASE):
            pts.append(Vector((x * (1 + abre * i / 5), 1.35 + (y - 1.35) * escala, 3.6 + (z - 3.6) * escala * alto)))
        _cadena(c, pts[:5], 0.1, 0.055, color, aplanar=2.6, lados=6)
        # ultimo tramo y punta: fuego de alma que sube
        a, b = pts[4], pts[5]
        c.entre(tuple(_lerp(a, b, -0.05)), tuple(b), 0.06, fuego, tipo="cono", aplanar=2.4, lados=6, brillo=True)
        c.pieza("esfera", tuple(b), 0.13, fuego, seg=8, anillos=6, brillo=True)
        _cadena(c, [b + Vector((0, 0.0, 0.04)), b + Vector((0, 0.07, 0.3)), b + Vector((0, 0.22, 0.6))], 0.125,
                0.0, fuego, lados=6, brillo=True)

    hoz(0.1, 1.0, "pluma_noche", fuego="alma_turquesa")
    hoz(-0.1, 0.96, "pluma_morada", fuego="alma_morada")
    hoz(0.3, 0.86, "pluma_morada", 0.92, 1.0, fuego="alma_morada")
    hoz(-0.3, 0.84, "pluma_noche", 0.92, 1.0, fuego="alma_turquesa")
    hoz(0.46, 0.72, "pluma_noche", 0.78, 1.2, fuego="alma_turquesa")
    hoz(-0.46, 0.7, "pluma_morada", 0.78, 1.2, fuego="alma_morada")
    # plumas fantasma semitransparentes entre las hoces
    for x, esc, alto in ((0.2, 0.93, 0.96), (-0.2, 0.9, 0.96), (0.0, 0.8, 0.86)):
        pts = [Vector((x * (1 + 0.8 * i / 5), 1.35 + (y - 1.35) * esc, 3.6 + (z - 3.6) * esc * alto))
               for i, (y, z) in enumerate(COLA_BASE)]
        for a, b in zip(pts[1:4], pts[2:5]):
            c.entre(tuple(a), tuple(b), 0.16, "fantasma", tipo="esfera", aplanar=0.35, seg=8, anillos=6, vidrio=True)
    # plumas cobertoras en la base
    for k, x in enumerate((-0.3, 0.0, 0.3)):
        c.entre((x, 1.3, 3.75), (x * 1.4, 2.2, 3.98 + 0.1 * (k == 1)), 0.22, "pluma_morada" if k != 1 else
                "pluma_noche", tipo="esfera", aplanar=0.55, seg=10, anillos=6)


# ------------------------------------------------------------------ configuracion

CONFIG = {
    "nombre": "Gallo Catrín",
    "vida": 240,
    "velocidad": 20,
    "comportamiento": "normal",
    "radioDeteccion": 38,
    "radioPatrulla": 16,
    "radioPersecucion": 75,
    "reaparecer": 25,
    "colorUI": ("rgb", 170, 80, 255),
    "habilidades": [
        {"nombre": "Picotazo de Hueso", "tipo": "Golpe", "anim": "PicotazoHueso", "rango": 6, "cooldown": 1.8,
         "retraso": 0.2, "danio": 10, "alcance": 6, "angulo": 90, "empuje": 20, "color": ("rgb", 245, 235, 215)},
        {"nombre": "Huesos Malditos", "tipo": "Proyectil", "anim": "HuesosMalditos", "rango": 35, "cooldown": 4,
         "retraso": 0.35, "danio": 12, "cantidad": 3, "dispersion": 20, "velocidad": 60, "forma": "hueso",
         "tamano": 1, "radioExplosion": 0, "color": ("rgb", 180, 80, 255)},
        {"nombre": "Forma Fantasma", "tipo": "Fantasma", "anim": "FormaFantasma", "rango": 40, "cooldown": 14,
         "retraso": 0.3, "duracion": 3, "velocidadExtra": 1.6, "color": ("rgb", 150, 110, 255)},
        {"nombre": "Grito del Más Allá", "tipo": "Onda", "anim": "GritoMasAlla", "rango": 10, "cooldown": 10,
         "retraso": 0.5, "danio": 10, "radio": 14, "empuje": 30, "aturdir": 1.5, "color": ("rgb", 60, 240, 220)},
    ],
}

ANIMACIONES = {
    "Idle": {
        "Raiz": [("py", 0.05, 0.8, 0), ("rz", 1.5, 0.4, 0.2)],
        "Cabeza": [("rx", 4, 0.8, 0.1), ("ry", 9, 0.3, 0)],
        "Mandibula": [("rx", 2, 0.8, 0.6)],
        "Sombrero": [("rz", 2, 0.4, 0.5)],
        "AlaIzq": [("rz", -4, 0.8, 0)],
        "Cola": [("rz", 4, 0.5, 0), ("rx", 3, 0.8, 0.3)],
    },
    "Caminar": {
        "Raiz": [("py", 0.08, 5.0, 0.25), ("rz", 3, 2.5, 0), ("ry", 4, 2.5, 0.25)],
        "Cabeza": [("rx", 7, 5.0, 0.0), ("pz", 0.08, 5.0, 0.25)],
        "Sombrero": [("rx", 3, 5.0, 0.1)],
        "AlaIzq": [("rz", -6, 2.5, 0)],
        "PataIzq": [("rx", 30, 2.5, 0)],
        "PataDer": [("rx", 30, 2.5, 0.5)],
        "Cola": [("rz", 6, 2.5, 0.2), ("rx", 4, 5.0, 0.4)],
    },
    "clips": {
        # Se echa para atras con el pico abierto (0.1) y lo cierra de golpe al frente a los 0.2 s.
        "PicotazoHueso": {"duracion": 0.6, "claves": [
            (0.0, {}),
            (0.1, {"Raiz": {"rx": 5, "pz": 0.15}, "Cabeza": {"rx": 12, "pz": 0.1}, "Mandibula": {"rx": -32},
                   "Sombrero": {"rx": -3}, "AlaIzq": {"rz": -15}, "Cola": {"rx": 4}}),
            (0.2, {"Raiz": {"rx": -8, "pz": -0.4, "py": -0.05}, "Cabeza": {"rx": -20, "pz": -0.3, "py": -0.08},
                   "Mandibula": {"rx": 0}, "Sombrero": {"rx": 6}, "AlaIzq": {"rz": -28, "rx": -10},
                   "Cola": {"rx": -8}, "PataIzq": {"rx": 10}, "PataDer": {"rx": -10}}),
            (0.32, {"Raiz": {"rx": -6, "pz": -0.35, "py": -0.04}, "Cabeza": {"rx": -15, "pz": -0.25, "py": -0.06},
                    "Sombrero": {"rx": 4}, "AlaIzq": {"rz": -20, "rx": -6}, "Cola": {"rx": -6},
                    "PataIzq": {"rx": 8}, "PataDer": {"rx": -8}}),
            (0.6, {}),
        ]},
        # Alza las alas (0.2) y las avienta hacia adelante soltando los huesos malditos a los 0.35 s.
        "HuesosMalditos": {"duracion": 0.8, "claves": [
            (0.0, {}),
            (0.2, {"Raiz": {"rx": 8, "pz": 0.2, "py": 0.05}, "Cabeza": {"rx": 10}, "Mandibula": {"rx": -12},
                   "AlaIzq": {"rz": -100, "ry": 15, "rx": 15}, "Cola": {"rx": -10}, "Sombrero": {"rx": -4}}),
            (0.35, {"Raiz": {"rx": -9, "pz": -0.35}, "Cabeza": {"rx": -12, "pz": -0.1}, "Mandibula": {"rx": -34},
                    "AlaIzq": {"rz": -20, "ry": -85, "rx": -20}, "Cola": {"rx": 8}, "Sombrero": {"rx": 7},
                    "PataIzq": {"rx": 8}, "PataDer": {"rx": -8}}),
            (0.5, {"Raiz": {"rx": -7, "pz": -0.3}, "Cabeza": {"rx": -9, "pz": -0.08}, "Mandibula": {"rx": -22},
                   "AlaIzq": {"rz": -15, "ry": -72, "rx": -14}, "Cola": {"rx": 5}, "Sombrero": {"rx": 4},
                   "PataIzq": {"rx": 6}, "PataDer": {"rx": -6}}),
            (0.8, {}),
        ]},
        # Se encoge escondiendo la cara bajo el sombrero (0.15), se eleva con las alas abiertas (0.3: se vuelve
        # fantasma) y da una vuelta flotando. La clave repetida en 0.65 cambia 360 por 0 (es la misma pose).
        "FormaFantasma": {"duracion": 0.9, "claves": [
            (0.0, {}),
            (0.15, {"Raiz": {"py": -0.25, "rx": -6}, "Cabeza": {"rx": -22}, "Sombrero": {"rx": -10},
                    "AlaIzq": {"ry": 18, "rz": 8}, "Cola": {"rx": 12}, "PataIzq": {"rx": -8}, "PataDer": {"rx": -8}}),
            (0.3, {"Raiz": {"py": 0.45, "rx": 4}, "Cabeza": {"rx": 20}, "Mandibula": {"rx": -30},
                   "Sombrero": {"py": 0.15, "rx": 8}, "AlaIzq": {"rz": -70, "ry": -10}, "Cola": {"rx": -25},
                   "PataIzq": {"rx": 20}, "PataDer": {"rx": 20}}),
            (0.65, {"Raiz": {"py": 0.4, "ry": 360}, "Cabeza": {"rx": 10}, "Mandibula": {"rx": -15},
                    "Sombrero": {"py": 0.05}, "AlaIzq": {"rz": -55}, "Cola": {"rx": -15},
                    "PataIzq": {"rx": 15}, "PataDer": {"rx": 15}}),
            (0.65, {"Raiz": {"py": 0.4, "ry": 0}, "Cabeza": {"rx": 10}, "Mandibula": {"rx": -15},
                    "Sombrero": {"py": 0.05}, "AlaIzq": {"rz": -55}, "Cola": {"rx": -15},
                    "PataIzq": {"rx": 15}, "PataDer": {"rx": 15}}),
            (0.9, {}),
        ]},
        # Toma aire mirando arriba (0.3) y grita con la mandibula abierta a los 0.5 s: el sombrero sale volando
        # un poco y la calavera vibra.
        "GritoMasAlla": {"duracion": 1.15, "claves": [
            (0.0, {}),
            (0.3, {"Raiz": {"rx": 12, "pz": 0.15, "py": 0.08}, "Cabeza": {"rx": 28}, "Mandibula": {"rx": -10},
                   "AlaIzq": {"rz": -35, "rx": 8}, "Cola": {"rx": -12}, "Sombrero": {"rx": -6}}),
            (0.5, {"Raiz": {"rx": -7, "pz": -0.25, "py": -0.12}, "Cabeza": {"rx": 6, "pz": -0.2}, "Mandibula": {"rx": -50},
                   "AlaIzq": {"rz": -75, "ry": -25}, "Cola": {"rx": -22}, "Sombrero": {"py": 0.35, "rx": 18},
                   "PataIzq": {"rx": 8}, "PataDer": {"rx": -8}}),
            (0.62, {"Raiz": {"rx": -7, "pz": -0.25, "py": -0.12}, "Cabeza": {"rx": 6, "ry": 7, "pz": -0.2},
                    "Mandibula": {"rx": -45}, "AlaIzq": {"rz": -72, "ry": -25}, "Cola": {"rx": -22},
                    "Sombrero": {"py": 0.45, "rx": 22}, "PataIzq": {"rx": 8}, "PataDer": {"rx": -8}}),
            (0.74, {"Raiz": {"rx": -6, "pz": -0.22, "py": -0.1}, "Cabeza": {"rx": 6, "ry": -7, "pz": -0.2},
                    "Mandibula": {"rx": -45}, "AlaIzq": {"rz": -70, "ry": -22}, "Cola": {"rx": -20},
                    "Sombrero": {"py": 0.4, "rx": 18}, "PataIzq": {"rx": 8}, "PataDer": {"rx": -8}}),
            (0.86, {"Raiz": {"rx": -4, "pz": -0.15, "py": -0.06}, "Cabeza": {"rx": 4, "ry": 5, "pz": -0.12},
                    "Mandibula": {"rx": -35}, "AlaIzq": {"rz": -50, "ry": -15}, "Cola": {"rx": -12},
                    "Sombrero": {"py": 0.15, "rx": 8}, "PataIzq": {"rx": 5}, "PataDer": {"rx": -5}}),
            (1.15, {}),
        ]},
        "Golpeado": {"duracion": 0.4, "claves": [
            (0.0, {}),
            (0.1, {"Raiz": {"rx": 8, "pz": 0.25}, "Cabeza": {"rx": 16, "rz": 8}, "Mandibula": {"rx": -20},
                   "Sombrero": {"py": 0.15, "rz": -10}, "AlaIzq": {"rz": -18}}),
            (0.4, {}),
        ]},
        # Se le sale el alma: el sombrero sale volando, los huesos se desarman y se desploma abierto de patas
        # con la calavera en el piso; el sombrero cae junto a el (canales calculados para que quede en el piso).
        "Derrota": {"duracion": 1.5, "claves": [
            (0.0, {}),
            (0.3, {"Raiz": {"py": 0.15, "rx": 6}, "Cabeza": {"rx": 15, "ry": 10}, "Mandibula": {"rx": -35},
                   "Sombrero": {"py": 0.5, "rx": -10, "rz": 12}, "AlaIzq": {"rz": -45}, "Cola": {"rx": -10},
                   "PataIzq": {"rx": -5}, "PataDer": {"rx": -5}}),
            (0.8, {"Raiz": {"py": -1.0, "rx": -6, "rz": 5}, "Cabeza": {"rx": -20, "rz": 10}, "Mandibula": {"rx": -25},
                   "AlaIzq": {"rz": 15}, "PataIzq": {"rz": -45, "rx": -15}, "PataDer": {"rz": 45, "rx": -15},
                   "Cola": {"rx": 10},
                   "Sombrero": {"rx": -63.2, "ry": 18.9, "rz": 83.0, "px": 2.24, "py": 0.07, "pz": 0.66}}),
            (1.5, {"Raiz": {"py": -1.95, "rx": -10, "rz": 8}, "Cabeza": {"rx": -10, "ry": 32, "rz": 10, "py": -1.92, "pz": -0.6},
                   "Mandibula": {"rx": -30}, "AlaIzq": {"rz": 30, "ry": 10}, "PataIzq": {"rz": -84, "rx": -10},
                   "PataDer": {"rz": 84, "rx": -10}, "Cola": {"rx": 20, "rz": 12},
                   "Sombrero": {"rx": 0.4, "ry": 2.1, "rz": -12.2, "px": 1.87, "py": -1.5, "pz": 1.06}}),
        ]},
    },
}
