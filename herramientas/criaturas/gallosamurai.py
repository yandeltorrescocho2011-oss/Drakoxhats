"""Gallo Samurái: gallo blanco noble con armadura de laca roja, kabuto negro con media luna dorada,
katana en el ala derecha y bandera sashimono en la espalda."""
import math

from motor import alargar

NOMBRE = "GalloSamurai"
COLORES_EXTRA = {
    "pluma": (0.97, 0.97, 0.95),          # plumaje blanco noble
    "pluma_sombra": (0.78, 0.80, 0.86),   # capas de plumas (sombra fria)
    "laca": (0.72, 0.05, 0.05),           # laca roja de la armadura
    "laca_osc": (0.36, 0.02, 0.03),       # cordones / juntas de las laminas
    "laca_negra": (0.07, 0.06, 0.08),     # casco y vaina
    "cresta": (0.95, 0.14, 0.12),
    "pico": (1.00, 0.80, 0.25),
    "pata": (0.98, 0.78, 0.28),
    "cola_verde": (0.03, 0.20, 0.13),
    "cola_tornasol": (0.05, 0.42, 0.33),
    "hoja": (0.84, 0.88, 0.94),           # acero de la katana
    "filo": (0.78, 0.93, 1.00),           # filo brillante (hamon)
    "trenza": (0.92, 0.90, 0.86),         # trenzado del mango
}


# ------------------------------------------------------------------ utilidades vectoriales simples

def _sum(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _res(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _mul(a, k):
    return tuple(x * k for x in a)


def _norm(a):
    l = math.sqrt(sum(x * x for x in a))
    return tuple(x / l for x in a)


def _rotar(v, rx=0.0, ry=0.0, rz=0.0):
    """Gira v igual que una pieza con rot=(rx, ry, rz) (Euler XYZ de Blender, en grados)."""
    x, y, z = v
    a = math.radians(rx)
    y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
    a = math.radians(ry)
    x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
    a = math.radians(rz)
    x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
    return (x, y, z)


def _cadena(c, puntos, r0, r1, color, aplanar=1.0, lados=6, **kw):
    """Tubo que se adelgaza siguiendo varios puntos (plumas en hoz, media luna)."""
    n = len(puntos) - 1
    for i in range(n):
        ra = r0 + (r1 - r0) * i / n
        rb = r0 + (r1 - r0) * (i + 1) / n
        a, b = puntos[i], puntos[i + 1]
        ultimo = i == n - 1
        if not ultimo:
            b = alargar(a, b, ra * 0.9)  # solapa un poco para que no queden huecos en los codos
        c.entre(a, b, ra, color, tipo="cono", punta=0.0 if ultimo else rb / ra, aplanar=aplanar, lados=lados, **kw)


def _placa(c, centro, ancho, alto, grosor, color, tilt=0.0, giro=0.0, franjas=(), borde=None, parte=None):
    """Lamina de armadura (cubo) mirando hacia afuera en el angulo 'giro' (0 = al frente, 90 = izquierda),
    inclinada 'tilt' grados (negativo = la parte de abajo sale hacia afuera). franjas = alturas locales de
    lineas oscuras; borde = color del ribete inferior."""
    rot = (tilt, 0, giro)
    c.pieza("cubo", centro, (ancho, grosor, alto), color, rot=rot, parte=parte)
    for dz in franjas:
        p = _sum(centro, _rotar((0, -0.012, dz), *rot))
        c.pieza("cubo", p, (ancho * 1.01, grosor, 0.04), "laca_osc", rot=rot, parte=parte)
    if borde:
        p = _sum(centro, _rotar((0, -0.01, -alto / 2 + 0.025), *rot))
        c.pieza("cubo", p, (ancho * 1.03, grosor * 1.25, 0.06), borde, rot=rot, parte=parte)


# ------------------------------------------------------------------ geometria

CUERPO_C = (0.0, 0.35, 3.35)
CUERPO_R = (1.05, 1.45, 1.1)
G_KATANA = (-1.5, -1.15, 3.15)                 # puno del ala derecha
U_KATANA = _norm((-0.3, -0.7, 0.65))           # direccion de la hoja (adelante, arriba, afuera)


def construir(c):
    c.parte("Cabeza", "Cuerpo", (0, -0.8, 4.3))
    c.parte("AlaIzq", "Cuerpo", (1.0, -0.2, 4.2), espejo=True)
    c.parte("PataIzq", "Cuerpo", (0.5, 0.42, 2.45), espejo=True)
    c.parte("Cola", "Cuerpo", (0, 1.5, 3.75))
    c.parte("Bandera", "Cuerpo", (0, 1.0, 4.25))

    _cuerpo(c)
    _cabeza(c)
    _alas(c)
    _katana(c)
    _patas(c)
    _cola(c)
    _bandera(c)


# Perfil de la pechera (do): (z, radio_x, radio_y, corrimiento al frente). Ancha en el pecho, angosta en la cintura.
PERFIL_DO = [(2.5, 0.9, 1.12, 0.12), (2.85, 0.99, 1.26, 0.15), (3.2, 1.07, 1.37, 0.19), (3.55, 1.12, 1.43, 0.23),
             (3.88, 1.11, 1.41, 0.27), (4.1, 1.0, 1.28, 0.3)]


def _perfil(z):
    for (z0, *a), (z1, *b) in zip(PERFIL_DO, PERFIL_DO[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return tuple(x + (y - x) * t for x, y in zip(a, b))
    return tuple(PERFIL_DO[-1][1:]) if z > PERFIL_DO[-1][0] else tuple(PERFIL_DO[0][1:])


def _banda(c, z0, z1, color, margen=0.0, lados=24):
    """Lamina de la pechera: tronco de cono entre z0 y z1 siguiendo PERFIL_DO."""
    ax, ay, ac = _perfil(z0)
    bx, _, bc = _perfil(z1)
    ac = (ac + bc) / 2
    c.pieza("cono", (0, CUERPO_C[1] - ac, (z0 + z1) / 2), (ax + margen, ay + margen, z1 - z0), color, lados=lados,
            punta=(bx + margen) / (ax + margen))


def _cuerpo(c):
    c.usar("Cuerpo")
    cy = CUERPO_C[1]
    c.pieza("esfera", CUERPO_C, CUERPO_R, "pluma", seg=18, anillos=12)
    # plumas del lomo (silla) que bajan hacia la cola
    for k, x in enumerate((-0.45, -0.15, 0.15, 0.45)):
        c.entre((x, 0.9, 4.3), (x * 1.3, 1.85, 3.9 - 0.05 * (k % 2)), 0.2, "pluma" if k % 2 else "pluma_sombra",
                tipo="esfera", aplanar=0.45)

    # --- do (pechera) de laminas de laca: pecho ancho y cintura angosta
    cortes = [2.5, 2.82, 3.14, 3.46, 3.78]
    for z0, z1 in zip(cortes, cortes[1:]):
        _banda(c, z0, z1, "laca")
        _banda(c, z1 - 0.025, z1 + 0.025, "laca_osc", margen=0.025)   # cordon entre laminas
    _banda(c, 3.78, 4.08, "laca_negra", margen=0.01)                    # munaita (placa del pecho)
    _banda(c, 4.06, 4.12, "oro", margen=0.03)
    _banda(c, 2.46, 2.54, "oro", margen=0.03)

    # mon (emblema) dorado al frente
    zm = 3.3
    _, py_, pc = _perfil(zm)
    yf = cy - pc - py_ - 0.03
    c.pieza("cilindro", (0, yf, zm), (0.4, 0.4, 0.06), "oro", rot=(90, 0, 0), lados=20)
    c.pieza("cilindro", (0, yf - 0.03, zm), (0.31, 0.31, 0.04), "laca", rot=(90, 0, 0), lados=20)
    c.pieza("cilindro", (0, yf - 0.06, zm), (0.11, 0.11, 0.04), "oro", rot=(90, 0, 0), lados=12)
    for k in range(6):
        a = math.radians(60 * k + 30)
        p = (0.2 * math.cos(a), yf - 0.05, zm + 0.2 * math.sin(a))
        c.pieza("esfera", p, (0.065, 0.03, 0.065), "oro", seg=8, anillos=5)

    # cinturon (obi) negro
    _banda(c, 2.3, 2.47, "laca_negra", margen=0.04)
    # kusazuri (faldones) colgando bajo la cintura, abiertos hacia afuera
    px, py_, pc = _perfil(2.4)
    for giro in (-125, -82, -41, 0, 41, 82, 125):
        a = math.radians(giro)
        centro = ((px + 0.12) * math.sin(a), cy - pc - (py_ + 0.1) * math.cos(a), 2.03)
        _placa(c, centro, 0.62, 0.58, 0.07, "laca", tilt=-18, giro=giro, franjas=(0.0,), borde="oro")

    # vaina (saya) vacia en la cadera izquierda
    a, b = (1.22, -1.0, 2.72), (1.42, 1.85, 2.15)
    c.entre(a, b, 0.095, "laca_negra", tipo="cilindro", lados=8)
    c.entre(a, alargar(b, a, -0.16), 0.115, "oro", tipo="cilindro", lados=8)          # boca (koiguchi)
    c.entre(alargar(a, b, -0.14), b, 0.11, "oro", tipo="cilindro", lados=8)          # punta (kojiri)
    c.entre((1.26, -0.6, 2.66), (1.33, -0.45, 2.3), 0.035, "laca_osc", tipo="cilindro", lados=5)  # cordon
    c.entre((1.33, -0.45, 2.3), (1.38, -0.2, 2.05), 0.035, "laca_osc", tipo="cilindro", lados=5)


class _Escalado:
    """Envuelve la criatura para construir una parte escalada k veces alrededor de 'centro'
    (asi la cabeza se puede agrandar o achicar con un solo numero)."""

    def __init__(self, c, centro, k):
        self.c, self.centro, self.k = c, centro, k

    def _p(self, p):
        return tuple(cc + (x - cc) * self.k for x, cc in zip(p, self.centro))

    def pieza(self, tipo, pos, esc=(1, 1, 1), *args, **kw):
        if isinstance(esc, (int, float)):
            esc = (esc, esc, esc)
        return self.c.pieza(tipo, self._p(pos), tuple(e * self.k for e in esc), *args, **kw)

    def entre(self, a, b, radio, *args, **kw):
        return self.c.entre(self._p(a), self._p(b), radio * self.k, *args, **kw)


ESCALA_CABEZA = 1.15


def _cabeza(c):
    c.usar("Cabeza")
    # golilla: plumas del cuello que caen sobre los hombros y la parte alta de la pechera
    for k in range(13):
        ang = math.radians(-165 + 27.5 * k)
        sx, sy = math.sin(ang), -math.cos(ang)
        a = (0.32 * sx, -0.95 + 0.34 * sy, 4.95)
        b = (0.88 * sx, -0.82 + 0.86 * sy, 3.98)
        c.entre(a, b, 0.22, "pluma" if k % 2 else "pluma_sombra", tipo="esfera", aplanar=0.5)

    c = _Escalado(c, (0, -1.1, 5.0), ESCALA_CABEZA)
    H = (0, -1.32, 5.5)
    c.entre((0, -0.72, 4.2), (0, -1.22, 5.4), 0.47, "pluma", tipo="esfera")  # cuello
    c.pieza("esfera", H, (0.56, 0.62, 0.6), "pluma", seg=16, anillos=10)

    # cara: piel roja alrededor de los ojos, ojos serios a medio cerrar, cejas duras
    c.pieza("esfera", (0.26, -1.74, 5.57), (0.2, 0.15, 0.19), "cresta", espejo=True)
    c.pieza("esfera", (0.26, -1.86, 5.59), (0.125, 0.06, 0.095), "ojo_blanco", seg=10, anillos=7, espejo=True)
    c.pieza("esfera", (0.24, -1.91, 5.6), (0.06, 0.03, 0.065), "negro", seg=8, anillos=6, espejo=True)
    c.pieza("cubo", (0.26, -1.92, 5.68), (0.34, 0.08, 0.085), "negro", rot=(0, -24, 0), espejo=True)
    # pico
    c.entre((0, -1.78, 5.47), (0, -2.36, 5.31), 0.17, "pico", lados=6, aplanar=0.8)
    c.entre((0, -1.78, 5.34), (0, -2.12, 5.25), 0.1, "oro_osc", lados=6, aplanar=0.8)
    # barbillas
    c.pieza("esfera", (0.08, -1.88, 5.07), (0.1, 0.09, 0.2), "cresta", seg=8, anillos=6, espejo=True)

    # --- kabuto
    D, R = (0, -1.12, 5.92), (0.64, 0.7, 0.47)
    c.pieza("esfera", D, R, "laca_negra", seg=18, anillos=10)
    for k in range(12):  # nervaduras doradas (suji) siguiendo la curva del casco
        a = math.radians(15 + 30 * k)
        pts = []
        for t in (0.3, 0.65, 1.0, 1.35):
            pts.append((D[0] + R[0] * 1.02 * math.sin(a) * math.cos(t), D[1] - R[1] * 1.02 * math.cos(a) * math.cos(t),
                        D[2] + R[2] * 1.02 * math.sin(t)))
        _cadena(c, pts, 0.022, 0.018, "oro", lados=4)
    c.pieza("toro", (0, D[1], 5.77), (0.61, 0.665, 1.0), "oro", radio=1.0, grosor=0.045, seg=20, seg_menor=4)
    c.pieza("toro", (0, D[1], 6.37), (1, 1, 0.7), "oro", radio=0.13, grosor=0.04, seg=10, seg_menor=4)  # tehen
    # cresta que asoma por la coronilla del casco
    for y, z, r in ((-1.4, 6.38, 0.15), (-1.17, 6.48, 0.18), (-0.92, 6.43, 0.16), (-0.72, 6.34, 0.12)):
        c.pieza("esfera", (0, y, z), (0.07, r, r * 1.1), "cresta", seg=8, anillos=6)
    # visera (mabizashi) con ribete dorado
    c.pieza("esfera", (0, -1.68, 5.84), (0.6, 0.35, 0.04), "oro", rot=(15, 0, 0), seg=16, anillos=6)
    c.pieza("esfera", (0, -1.66, 5.86), (0.57, 0.33, 0.05), "laca_negra", rot=(15, 0, 0), seg=16, anillos=6)
    # shikoro: laminas que protegen nuca y lados
    for capa in range(3):
        rxs, rys = 0.62 + 0.1 * capa, 0.66 + 0.1 * capa
        z = 5.57 - 0.17 * capa
        color = "laca" if capa == 1 else "laca_negra"
        for k in range(9):
            giro = 75 + (210 / 8) * k
            a = math.radians(giro)
            centro = (rxs * math.sin(a), -1.07 - rys * math.cos(a), z)
            _placa(c, centro, 0.46, 0.2, 0.06, color, tilt=-28 - 6 * capa, giro=giro,
                   borde="oro" if capa == 2 else None)
    # fukigaeshi (orejeras dobladas hacia afuera), negras con ribete dorado
    c.pieza("cubo", (0.68, -1.33, 5.56), (0.04, 0.3, 0.27), "oro", rot=(0, -12, 35), espejo=True)
    c.pieza("cubo", (0.68, -1.33, 5.56), (0.07, 0.25, 0.22), "laca_negra", rot=(0, -12, 35), espejo=True)
    # maedate: media luna dorada al frente
    puntos = []
    for k in range(13):
        th = math.radians(-78 + 13 * k)
        puntos.append((0.95 * math.sin(th), -1.98 + 0.28 * math.sin(th) ** 2, 5.86 + 0.8 * (1 - math.cos(th))))
    _cadena(c, puntos[6:], 0.035, 0.02, "oro", aplanar=3.2, lados=6)
    _cadena(c, puntos[:7][::-1], 0.035, 0.02, "oro", aplanar=3.2, lados=6)
    c.pieza("ico", (0, -1.98, 5.84), 0.1, "oro", subdiv=1)


def _alas(c):
    c.usar("AlaIzq")
    c.pieza("esfera", (1.3, 0.2, 3.55), (0.27, 1.12, 0.7), "pluma", rot=(-12, 0, 0), espejo=True)
    c.pieza("esfera", (1.38, -0.15, 3.72), (0.22, 0.7, 0.48), "pluma_sombra", rot=(-12, 0, 0), espejo=True)
    for k in range(5):
        a = (1.32 - 0.01 * k, 0.6 + 0.08 * k, 3.45 - 0.1 * k)
        b = (1.27 - 0.02 * k, 1.85 + 0.05 * k, 3.25 - 0.14 * k)
        c.entre(a, b, 0.055, "pluma" if k % 2 else "pluma_sombra", tipo="esfera", aplanar=3.4, espejo=True)
    # sode: hombreras anchas de laminas rojas con ribete dorado, abiertas hacia afuera
    inc = -32
    c.pieza("cubo", (1.18, -0.2, 4.42), (0.12, 1.05, 0.14), "laca_negra", rot=(0, inc, 0), espejo=True)
    for k in range(3):
        centro = (1.3 + 0.17 * k, -0.2, 4.25 - 0.27 * k)
        c.pieza("cubo", centro, (0.08, 1.0, 0.3), "laca", rot=(0, inc, 0), espejo=True)
        borde = _sum(centro, _rotar((0.0, 0, -0.14), 0, inc, 0))
        c.pieza("cubo", borde, (0.1, 1.02, 0.055), "oro", rot=(0, inc, 0), espejo=True)
    c.pieza("toro", (1.13, -0.2, 4.5), (1, 1, 1), "oro", rot=(0, 72, 0), radio=0.09, grosor=0.03, seg=8,
            seg_menor=4, espejo=True)

    # ala derecha: antebrazo de plumas hasta el puno que sujeta la katana
    c.usar("AlaDer")
    c.entre((-1.22, -0.4, 3.6), G_KATANA, 0.2, "pluma", tipo="esfera")
    c.pieza("esfera", G_KATANA, (0.24, 0.26, 0.24), "pluma", seg=12, anillos=8)
    for k in range(3):
        base = _sum(G_KATANA, (0.05, 0.05 - 0.1 * k, 0.12 - 0.1 * k))
        c.entre(base, _sum(base, (0.17, -0.12, -0.12)), 0.09, "pluma_sombra", tipo="esfera", aplanar=0.6)


def _katana(c):
    c.usar("AlaDer")
    G, u = G_KATANA, U_KATANA
    n = _norm(_res((0, 0, 1), _mul(u, u[2])))  # perpendicular "arriba" (lomo); el filo mira a -n

    def P(s, sori=0.0):
        return _sum(_sum(G, _mul(u, s)), _mul(n, sori))

    # mango (tsuka) negro con trenzado claro, pomo dorado
    c.entre(P(-0.52), P(0.42), 0.075, "laca_negra", tipo="cilindro", lados=6)
    for k in range(5):
        s = -0.4 + 0.18 * k
        c.entre(P(s - 0.035), P(s + 0.035), 0.085, "trenza", tipo="cilindro", lados=4)
    c.entre(P(-0.58), P(-0.5), 0.085, "oro", tipo="cilindro", lados=6)
    # guarda (tsuba) y collar (habaki)
    c.entre(P(0.42), P(0.48), 0.22, "oro", tipo="cilindro", lados=10)
    c.entre(P(0.48), P(0.62), 0.06, "oro_osc", tipo="cilindro", lados=4, aplanar=2.0)
    # hoja curvada (sori), seccion de rombo
    L, sori = 3.0, 0.16
    pasos = [0.48, 1.2, 1.9, 2.6, 3.1]

    def B(s):
        t = (s - 0.48) / L
        return P(s, sori * t * t)

    for s0, s1 in zip(pasos, pasos[1:]):
        c.entre(B(s0), alargar(B(s0), B(s1), 0.03), 0.032, "hoja", tipo="cono", punta=1.0, lados=4, aplanar=3.0)
        # filo brillante (hamon) en el lado del filo
        a = _sum(B(s0 + 0.06), _mul(n, -0.08))
        b = _sum(B(s1), _mul(n, -0.08))
        c.entre(a, b, 0.018, "filo", tipo="cubo", aplanar=1.4, brillo=True)
    c.entre(B(3.1), B(L + 0.48), 0.032, "hoja", tipo="cono", lados=4, aplanar=3.0)  # kissaki


def _patas(c):
    c.usar("PataIzq")
    c.pieza("esfera", (0.5, 0.42, 2.0), (0.34, 0.4, 0.55), "pluma", espejo=True)
    c.entre((0.5, 0.45, 1.65), (0.5, 0.5, 0.12), 0.11, "pata", tipo="cilindro", lados=8, espejo=True)
    # suneate (espinillera) negra con ribete dorado
    c.pieza("cubo", (0.5, 0.37, 0.95), (0.26, 0.08, 0.9), "laca_negra", rot=(-3, 0, 0), espejo=True)
    c.pieza("cubo", (0.5, 0.37, 1.39), (0.28, 0.09, 0.06), "oro", rot=(-3, 0, 0), espejo=True)
    c.pieza("cubo", (0.5, 0.36, 0.52), (0.28, 0.09, 0.05), "oro", rot=(-3, 0, 0), espejo=True)
    # dedos con garras
    for ang in (-32, 0, 32):
        a = math.radians(ang)
        fin = (0.5 + 0.55 * math.sin(a), 0.48 - 0.55 * math.cos(a), 0.07)
        c.entre((0.5, 0.48, 0.1), fin, 0.07, "pata", tipo="cilindro", lados=6, espejo=True)
        c.entre(fin, (fin[0] + 0.12 * math.sin(a), fin[1] - 0.12 * math.cos(a), 0.03), 0.05, "gris_osc", lados=5,
                espejo=True)
    c.entre((0.5, 0.48, 0.1), (0.5, 0.9, 0.06), 0.06, "pata", tipo="cilindro", lados=6, espejo=True)
    c.entre((0.5, 0.58, 0.45), (0.5, 0.86, 0.36), 0.05, "hueso", lados=5, espejo=True)  # espolon


def _cola(c):
    c.usar("Cola")

    def hoz(x, escala, color, alto=1.0, abre=0.6):
        base = [(1.45, 3.85), (2.05, 4.85), (2.85, 5.4), (3.6, 5.25), (4.05, 4.6), (4.2, 3.9)]
        pts = []
        for i, (y, z) in enumerate(base):
            yy = 1.45 + (y - 1.45) * escala
            zz = 3.8 + (z - 3.8) * escala * alto
            pts.append((x * (1 + abre * i / 5), yy, zz))
        _cadena(c, pts, 0.085, 0.03, color, aplanar=3.0, lados=6)

    hoz(0.1, 1.0, "cola_verde")
    hoz(-0.1, 0.97, "laca_negra")
    hoz(0.28, 0.88, "laca_negra", 0.92, 1.0)
    hoz(-0.28, 0.86, "cola_tornasol", 0.92, 1.0)
    hoz(0.42, 0.74, "cola_tornasol", 0.78, 1.2)
    hoz(-0.44, 0.72, "cola_verde", 0.78, 1.2)
    hoz(0.0, 0.64, "cola_tornasol", 0.62)
    # plumas cobertoras blancas en la base
    for k, x in enumerate((-0.3, 0.0, 0.3)):
        c.entre((x, 1.4, 3.9), (x * 1.4, 2.25, 4.1 + 0.1 * (k == 1)), 0.2, "pluma", tipo="esfera", aplanar=0.55)


def _bandera(c):
    c.usar("Bandera")
    c.pieza("cubo", (0, 1.05, 4.4), (0.22, 0.2, 0.4), "laca_negra")             # soporte en la espalda
    c.pieza("cubo", (0, 1.05, 4.59), (0.25, 0.23, 0.05), "oro")
    abajo, arriba = (0, 1.0, 4.1), (0, 1.27, 7.85)
    c.entre(abajo, arriba, 0.05, "laca_negra", tipo="cilindro", lados=6)       # asta
    c.entre((-0.68, 1.26, 7.75), (0.68, 1.26, 7.75), 0.04, "laca_negra", tipo="cilindro", lados=6)  # travesano
    c.pieza("cono", (0, 1.275, 7.95), (0.07, 0.07, 0.22), "oro", lados=6)          # remate
    for x in (-0.68, 0.68):
        c.pieza("esfera", (x, 1.26, 7.75), 0.06, "oro", seg=8, anillos=6)
    tilt = -math.degrees(math.atan2(0.27, 3.75))
    centro = (0, 1.16, 6.97)
    c.pieza("cubo", centro, (1.3, 0.05, 1.5), "laca", rot=(tilt, 0, 0))
    c.pieza("cubo", _sum(centro, _rotar((0, 0, -0.72), tilt)), (1.32, 0.06, 0.08), "oro", rot=(tilt, 0, 0))
    c.pieza("cilindro", centro, (0.38, 0.38, 0.08), "oro", rot=(90 + tilt, 0, 0), lados=20)   # circulo dorado
    c.pieza("cilindro", centro, (0.27, 0.27, 0.1), "laca", rot=(90 + tilt, 0, 0), lados=20)


CONFIG = {
    "nombre": "Gallo Samurái",
    "vida": 320,
    "velocidad": 18,
    "comportamiento": "normal",
    "radioDeteccion": 40,
    "radioPatrulla": 18,
    "radioPersecucion": 75,
    "reaparecer": 30,
    "colorUI": ("rgb", 215, 30, 35),
    "habilidades": [
        {"nombre": "Corte Veloz", "tipo": "Golpe", "anim": "CorteVeloz", "rango": 8, "cooldown": 2.5, "retraso": 0.3,
         "danio": 18, "alcance": 9, "angulo": 120, "empuje": 35, "color": ("rgb", 225, 235, 255)},
        {"nombre": "Tajo Giratorio", "tipo": "Onda", "anim": "TajoGiratorio", "rango": 10, "cooldown": 8,
         "retraso": 0.45, "danio": 22, "radio": 12, "empuje": 55, "color": ("rgb", 210, 225, 255)},
        {"nombre": "Defensa de Acero", "tipo": "Escudo", "anim": "DefensaAcero", "rango": 20, "cooldown": 12,
         "retraso": 0.2, "duracion": 3, "reduccion": 0.7, "color": ("rgb", 200, 210, 230)},
    ],
}

# Ojo: el ala derecha lleva la katana, asi que en los clips siempre se escriben las dos alas
# (si solo se escribe una, el motor copia la otra en espejo).
ANIMACIONES = {
    "Idle": {
        "Raiz": [("py", 0.04, 1.2, 0)],
        "Cabeza": [("rx", 4, 0.6, 0), ("ry", 10, 0.3, 0.1)],
        "AlaIzq": [("rz", -3, 1.2, 0)],
        "AlaDer": [("rz", 3, 1.2, 0), ("rx", 3, 0.6, 0.25)],
        "Bandera": [("rx", 3, 0.9, 0), ("rz", 4, 0.6, 0.3)],
        "Cola": [("rz", 3, 0.7, 0), ("rx", 2, 0.9, 0.5)],
    },
    "Caminar": {
        "Raiz": [("py", 0.08, 5.0, 0.25), ("rz", 3, 2.5, 0), ("ry", 3, 2.5, 0.25)],
        "Cabeza": [("rx", 6, 5.0, 0.0)],
        "AlaIzq": [("rz", -5, 2.5, 0)],
        "AlaDer": [("rz", 5, 2.5, 0.5), ("rx", 5, 2.5, 0.25)],
        "PataIzq": [("rx", 28, 2.5, 0)],
        "PataDer": [("rx", 28, 2.5, 0.5)],
        "Bandera": [("rx", 6, 2.5, 0.3), ("rz", 5, 2.5, 0.1)],
        "Cola": [("rx", 5, 5.0, 0.4), ("rz", 5, 2.5, 0.2)],
    },
    "clips": {
        # Tajo de arriba hacia abajo con giro de cadera: alza la katana (0.15) y corta al frente a los 0.3 s.
        "CorteVeloz": {"duracion": 0.75, "claves": [
            (0.0, {}),
            (0.15, {"Raiz": {"ry": -20, "rx": 3},
                    "AlaDer": {"rx": 55, "rz": 30, "ry": -10}, "AlaIzq": {"rz": -12, "rx": 5},
                    "Cabeza": {"ry": -8, "rx": 5}, "Bandera": {"rx": -4}, "Cola": {"rx": 4}}),
            (0.3, {"Raiz": {"ry": 22, "pz": -0.55, "rx": -8, "py": 0.02},
                   "AlaDer": {"rx": -42, "ry": 25, "rz": 8}, "AlaIzq": {"rz": -28, "rx": -10},
                   "Cabeza": {"rx": -8, "ry": 6}, "Bandera": {"rx": 9}, "Cola": {"rx": -8},
                   "PataIzq": {"rx": 10}, "PataDer": {"rx": -8}}),
            (0.45, {"Raiz": {"ry": 26, "pz": -0.45, "rx": -6, "py": 0.02},
                    "AlaDer": {"rx": -52, "ry": 28, "rz": 5}, "AlaIzq": {"rz": -22, "rx": -6},
                    "Cabeza": {"rx": -5, "ry": 6}, "Bandera": {"rx": 5}, "Cola": {"rx": -5},
                    "PataIzq": {"rx": 8}, "PataDer": {"rx": -7}}),
            (0.75, {}),
        ]},
        # Se carga a la izquierda (0.2) y da una vuelta completa a la derecha con la katana extendida;
        # la onda sale a mitad del giro (0.45). La clave repetida en 0.2 cambia 35 por 395 (es la misma pose).
        "TajoGiratorio": {"duracion": 1.0, "claves": [
            (0.0, {}),
            (0.2, {"Raiz": {"ry": 35, "py": -0.03}, "AlaDer": {"rz": 55, "ry": -70, "rx": -50},
                   "AlaIzq": {"rz": -55, "rx": -10}, "Cabeza": {"ry": -15}, "Bandera": {"rz": -6},
                   "Cola": {"rz": -6}}),
            (0.2, {"Raiz": {"ry": 395, "py": -0.03}, "AlaDer": {"rz": 55, "ry": -70, "rx": -50},
                   "AlaIzq": {"rz": -55, "rx": -10}, "Cabeza": {"ry": -15}, "Bandera": {"rz": -6},
                   "Cola": {"rz": -6}}),
            (0.62, {"Raiz": {"ry": 0, "py": -0.02}, "AlaDer": {"rz": 55, "ry": -70, "rx": -50},
                    "AlaIzq": {"rz": -55, "rx": -10}, "Cabeza": {"ry": 12}, "Bandera": {"rz": 12},
                    "Cola": {"rz": 12}}),
            (1.0, {}),
        ]},
        # Guardia: katana vertical al frente, se agacha un poco y abre las patas.
        "DefensaAcero": {"duracion": 1.0, "claves": [
            (0.0, {}),
            (0.2, {"Raiz": {"ry": -12}, "AlaDer": {"rx": 25, "ry": 25},
                   "AlaIzq": {"rz": -25, "rx": 10}, "Cabeza": {"rx": -6, "ry": 6},
                   "PataIzq": {"rx": 8}, "PataDer": {"rx": -8}, "Bandera": {"rx": 4}}),
            (0.8, {"Raiz": {"ry": -12}, "AlaDer": {"rx": 27, "ry": 25},
                   "AlaIzq": {"rz": -25, "rx": 10}, "Cabeza": {"rx": -6, "ry": 6},
                   "PataIzq": {"rx": 8}, "PataDer": {"rx": -8}, "Bandera": {"rx": 4}}),
            (1.0, {}),
        ]},
        "Golpeado": {"duracion": 0.4, "claves": [
            (0.0, {}),
            (0.1, {"Raiz": {"rx": 8, "pz": 0.25}, "Cabeza": {"rx": 15}, "AlaIzq": {"rz": -15}, "AlaDer": {"rz": 10},
                   "Bandera": {"rx": -8}}),
            (0.4, {}),
        ]},
        # Se tambalea hacia adelante y cae de lado (sobre el ala izquierda), la bandera queda en el piso.
        "Derrota": {"duracion": 1.2, "claves": [
            (0.0, {}),
            (0.35, {"Raiz": {"py": -0.05, "rx": -12}, "Cabeza": {"rx": -20}, "AlaDer": {"rx": -30, "rz": 10},
                    "AlaIzq": {"rz": -10}, "PataIzq": {"rx": 15}, "PataDer": {"rx": 15}, "Bandera": {"rx": 8}}),
            (1.2, {"Raiz": {"py": -1.36, "rz": 82, "rx": -8}, "Cabeza": {"rx": 25, "rz": -20},
                   "AlaDer": {"rz": 45, "rx": -20}, "AlaIzq": {"rz": -20}, "PataIzq": {"rx": 30},
                   "PataDer": {"rx": -15}, "Bandera": {"rz": -15}, "Cola": {"rz": -10}}),
        ]},
    },
}
