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


def _cruz(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


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


def _radio(z):
    cz, rz = CUERPO_C[2], CUERPO_R[2]
    return math.sqrt(max(0.04, 1 - ((z - cz) / rz) ** 2))


def _banda(c, z0, z1, corr, color, margen=0.06, lados=24):
    """Lamina de la pechera: tronco de cono que sigue la curva del cuerpo, corrido 'corr' hacia el frente."""
    rx, ry = CUERPO_R[0], CUERPO_R[1]
    f0, f1 = _radio(z0), _radio(z1)
    fm = _radio((z0 + z1) / 2)
    fb = max(f0, fm - (f1 - f0) / 2 * 0) if False else f0
    k = max(fm - (f0 + f1) / 2, 0)  # flecha de la curva entre z0 y z1
    r0x, r0y = rx * (f0 + k) + margen, ry * (f0 + k) + margen
    r1x = rx * (f1 + k) + margen
    c.pieza("cono", (0, CUERPO_C[1] - corr, (z0 + z1) / 2), (r0x, r0y, z1 - z0), color, lados=lados,
            punta=r1x / r0x)


def _cuerpo(c):
    c.usar("Cuerpo")
    cx, cy, cz = CUERPO_C
    rx, ry, rz = CUERPO_R
    c.pieza("esfera", CUERPO_C, CUERPO_R, "pluma", seg=18, anillos=12)
    # plumas del lomo (silla) que bajan hacia la cola
    for k, x in enumerate((-0.45, -0.15, 0.15, 0.45)):
        c.entre((x, 0.9, 4.3), (x * 1.3, 1.85, 3.9 - 0.05 * (k % 2)), 0.2, "pluma" if k % 2 else "pluma_sombra",
                tipo="esfera", aplanar=0.45)

    # --- do (pechera) de laminas de laca, abultada al frente como pecho orgulloso
    cortes = [2.55, 2.88, 3.21, 3.54, 3.87]
    for i, (z0, z1) in enumerate(zip(cortes, cortes[1:])):
        corr = 0.12 + 0.06 * i
        _banda(c, z0, z1, corr, "laca")
        _banda(c, z1 - 0.025, z1 + 0.025, corr + 0.02, "laca_osc", margen=0.075)   # cordon entre laminas
    _banda(c, 3.87, 4.07, 0.36, "laca_negra")                                      # munaita (placa del pecho)
    _banda(c, 4.05, 4.11, 0.38, "oro", margen=0.08)
    _banda(c, 2.47, 2.57, 0.12, "oro", margen=0.09)

    # mon (emblema) dorado al frente
    yf, zm = cy - 0.24 - (ry * _radio(3.3) + 0.06) - 0.03, 3.3
    c.pieza("cilindro", (0, yf, zm), (0.4, 0.4, 0.06), "oro", rot=(90, 0, 0), lados=20)
    c.pieza("cilindro", (0, yf - 0.03, zm), (0.31, 0.31, 0.04), "laca", rot=(90, 0, 0), lados=20)
    c.pieza("cilindro", (0, yf - 0.06, zm), (0.11, 0.11, 0.04), "oro", rot=(90, 0, 0), lados=12)
    for k in range(6):
        a = math.radians(60 * k + 30)
        p = (0.2 * math.cos(a), yf - 0.05, zm + 0.2 * math.sin(a))
        c.pieza("esfera", p, (0.065, 0.03, 0.065), "oro", seg=8, anillos=5)

    # cinturon (obi) negro
    _banda(c, 2.32, 2.5, 0.12, "laca_negra", margen=0.1)
    # kusazuri (faldones) colgando bajo la pechera
    f = _radio(2.4)
    for giro in (-120, -80, -40, 0, 40, 80, 120):
        a = math.radians(giro)
        centro = ((rx * f + 0.1) * math.sin(a), cy - 0.12 - (ry * f + 0.1) * math.cos(a), 2.08)
        _placa(c, centro, 0.6, 0.55, 0.07, "laca", tilt=-14, giro=giro, franjas=(0.0,), borde="oro")

    # vaina (saya) vacia en la cadera izquierda
    a, b = (1.22, -1.0, 2.72), (1.42, 1.85, 2.15)
    c.entre(a, b, 0.095, "laca_negra", tipo="cilindro", lados=8)
    c.entre(a, alargar(b, a, -0.16), 0.115, "oro", tipo="cilindro", lados=8)          # boca (koiguchi)
    c.entre(alargar(a, b, -0.14), b, 0.11, "oro", tipo="cilindro", lados=8)          # punta (kojiri)
    c.entre((1.26, -0.6, 2.66), (1.33, -0.45, 2.3), 0.035, "laca_osc", tipo="cilindro", lados=5)  # cordon
    c.entre((1.33, -0.45, 2.3), (1.38, -0.2, 2.05), 0.035, "laca_osc", tipo="cilindro", lados=5)


def _cabeza(c):
    c.usar("Cabeza")
    H = (0, -1.32, 5.5)
    c.entre((0, -0.72, 4.2), (0, -1.22, 5.4), 0.47, "pluma", tipo="esfera")  # cuello
    c.pieza("esfera", H, (0.56, 0.62, 0.6), "pluma", seg=16, anillos=10)
    # golilla de plumas que cae sobre los hombros y la pechera
    for k in range(11):
        ang = math.radians(-150 + 30 * k)
        sx, sy = math.sin(ang), -math.cos(ang)
        a = (0.3 * sx, -0.95 + 0.32 * sy, 4.95)
        b = (0.7 * sx, -0.85 + 0.72 * sy, 4.22)
        c.entre(a, b, 0.2, "pluma" if k % 2 else "pluma_sombra", tipo="esfera", aplanar=0.5)

    # cara: piel roja, ojos serios, cejas duras
    c.pieza("esfera", (0.29, -1.66, 5.47), (0.19, 0.18, 0.21), "cresta", espejo=True)
    c.pieza("esfera", (0.27, -1.82, 5.6), (0.12, 0.07, 0.11), "ojo_blanco", seg=10, anillos=7, espejo=True)
    c.pieza("esfera", (0.25, -1.88, 5.59), (0.06, 0.035, 0.07), "negro", seg=8, anillos=6, espejo=True)
    c.pieza("cubo", (0.27, -1.87, 5.71), (0.32, 0.09, 0.08), "negro", rot=(0, -24, 0), espejo=True)
    # pico
    c.entre((0, -1.78, 5.47), (0, -2.36, 5.31), 0.17, "pico", lados=6, aplanar=0.8)
    c.entre((0, -1.78, 5.34), (0, -2.12, 5.25), 0.1, "oro_osc", lados=6, aplanar=0.8)
    # barbillas
    c.pieza("esfera", (0.08, -1.88, 5.07), (0.1, 0.09, 0.2), "cresta", seg=8, anillos=6, espejo=True)

    # --- kabuto
    D = (0, -1.12, 5.92)
    c.pieza("esfera", D, (0.64, 0.7, 0.47), "laca_negra", seg=18, anillos=10)
    for k in range(5):  # nervaduras doradas del casco
        ang = math.radians(-50 + 25 * k)
        p = (0.6 * math.sin(ang), D[1] - 0.64 * math.cos(ang), 6.08)
        c.entre(p, (0, D[1], 6.38), 0.025, "oro", tipo="cilindro", lados=4)
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
    # fukigaeshi (orejeras dobladas hacia afuera)
    c.pieza("cubo", (0.7, -1.38, 5.5), (0.05, 0.34, 0.36), "oro", rot=(0, -10, 30), espejo=True)
    c.pieza("cubo", (0.72, -1.37, 5.5), (0.05, 0.3, 0.3), "laca_negra", rot=(0, -10, 30), espejo=True)
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
    c.pieza("esfera", (1.22, 0.25, 3.58), (0.24, 1.0, 0.62), "pluma", rot=(-12, 0, 0), espejo=True)
    c.pieza("esfera", (1.29, -0.1, 3.75), (0.2, 0.62, 0.42), "pluma_sombra", rot=(-12, 0, 0), espejo=True)
    for k in range(5):
        a = (1.23 - 0.01 * k, 0.55 + 0.08 * k, 3.5 - 0.1 * k)
        b = (1.19 - 0.02 * k, 1.75 + 0.05 * k, 3.3 - 0.13 * k)
        c.entre(a, b, 0.05, "pluma" if k % 2 else "pluma_sombra", tipo="esfera", aplanar=3.4, espejo=True)
    # sode: hombreras de laminas rojas con ribete dorado
    c.pieza("cubo", (1.2, -0.2, 4.33), (0.1, 1.0, 0.12), "laca_negra", rot=(0, -18, 0), espejo=True)
    for k in range(3):
        centro = (1.28 + 0.06 * k, -0.2, 4.15 - 0.26 * k)
        c.pieza("cubo", centro, (0.08, 0.95, 0.28), "laca", rot=(0, -18, 0), espejo=True)
        c.pieza("cubo", _sum(centro, (0.0, 0, -0.13)), (0.095, 0.97, 0.05), "oro", rot=(0, -18, 0), espejo=True)
    c.pieza("toro", (1.16, -0.2, 4.4), (1, 1, 1), "oro", rot=(0, 72, 0), radio=0.09, grosor=0.03, seg=8,
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
    abajo, arriba = (0, 1.0, 4.1), (0, 1.25, 7.65)
    c.entre(abajo, arriba, 0.05, "laca_negra", tipo="cilindro", lados=6)       # asta
    c.entre((-0.68, 1.24, 7.55), (0.68, 1.24, 7.55), 0.04, "laca_negra", tipo="cilindro", lados=6)  # travesano
    c.pieza("cono", (0, 1.255, 7.75), (0.07, 0.07, 0.22), "oro", lados=6)          # remate
    for x in (-0.68, 0.68):
        c.pieza("esfera", (x, 1.24, 7.55), 0.06, "oro", seg=8, anillos=6)
    tilt = -math.degrees(math.atan2(0.25, 3.55))
    centro = (0, 1.15, 6.77)
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
        "CorteVeloz": {"duracion": 0.75, "claves": [
            (0.0, {}),
            (0.15, {"Raiz": {"ry": -18, "py": -0.05},
                    "AlaDer": {"rx": 55, "rz": 35, "ry": -15}, "AlaIzq": {"rz": -10},
                    "Cabeza": {"ry": -10}, "Bandera": {"rx": -4}}),
            (0.3, {"Raiz": {"ry": 20, "pz": -0.5, "rx": -8},
                   "AlaDer": {"rx": -55, "rz": -10, "ry": 35}, "AlaIzq": {"rz": -25, "rx": 10},
                   "Cabeza": {"rx": -10, "ry": 10}, "Bandera": {"rx": 8}, "Cola": {"rx": -8}}),
            (0.45, {"Raiz": {"ry": 24, "pz": -0.4, "rx": -6},
                    "AlaDer": {"rx": -62, "rz": -15, "ry": 45}, "AlaIzq": {"rz": -20, "rx": 8},
                    "Cabeza": {"rx": -6, "ry": 8}, "Bandera": {"rx": 5}, "Cola": {"rx": -5}}),
            (0.75, {}),
        ]},
        "TajoGiratorio": {"duracion": 1.0, "claves": [
            (0.0, {}),
            (0.2, {"Raiz": {"ry": 35, "py": -0.15}, "AlaDer": {"rz": 70, "rx": -20, "ry": -10},
                   "AlaIzq": {"rz": -50}, "Cabeza": {"ry": -15}, "Bandera": {"rz": -6}}),
            # mismo giro +360 (se ve igual): desde aqui da una vuelta completa hasta 0
            (0.2, {"Raiz": {"ry": 395, "py": -0.15}, "AlaDer": {"rz": 70, "rx": -20, "ry": -10},
                   "AlaIzq": {"rz": -50}, "Cabeza": {"ry": -15}, "Bandera": {"rz": -6}}),
            (0.62, {"Raiz": {"ry": 0, "py": -0.1}, "AlaDer": {"rz": 70, "rx": -20, "ry": -10},
                    "AlaIzq": {"rz": -50}, "Cabeza": {"ry": 10}, "Bandera": {"rz": 10}}),
            (1.0, {}),
        ]},
        "DefensaAcero": {"duracion": 1.0, "claves": [
            (0.0, {}),
            (0.2, {"Raiz": {"py": -0.08, "rx": 4}, "AlaDer": {"rx": 35, "ry": 40, "rz": 10},
                   "AlaIzq": {"rx": 15, "ry": -25, "rz": -15}, "Cabeza": {"rx": -8},
                   "PataIzq": {"rx": -10}, "PataDer": {"rx": 10}}),
            (0.75, {"Raiz": {"py": -0.08, "rx": 4}, "AlaDer": {"rx": 35, "ry": 40, "rz": 10},
                    "AlaIzq": {"rx": 15, "ry": -25, "rz": -15}, "Cabeza": {"rx": -8},
                    "PataIzq": {"rx": -10}, "PataDer": {"rx": 10}}),
            (1.0, {}),
        ]},
        "Golpeado": {"duracion": 0.4, "claves": [
            (0.0, {}),
            (0.1, {"Raiz": {"rx": 8, "pz": 0.25}, "Cabeza": {"rx": 15}, "AlaIzq": {"rz": -15}, "AlaDer": {"rz": 10}}),
            (0.4, {}),
        ]},
        "Derrota": {"duracion": 1.2, "claves": [
            (0.0, {}),
            (0.35, {"Raiz": {"py": -0.2, "rx": -12}, "Cabeza": {"rx": -20}, "AlaDer": {"rx": -40, "rz": -10},
                    "AlaIzq": {"rz": 10}, "PataIzq": {"rx": -20}, "PataDer": {"rx": -20}}),
            (1.2, {"Raiz": {"py": -1.55, "rz": 82, "rx": -8}, "Cabeza": {"rx": 25, "rz": -20},
                   "AlaDer": {"rz": 45, "rx": -20}, "AlaIzq": {"rz": 15}, "PataIzq": {"rx": -30},
                   "PataDer": {"rx": 15}, "Bandera": {"rz": -15}, "Cola": {"rz": -10}}),
        ]},
    },
}
