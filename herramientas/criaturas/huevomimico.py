"""Huevo Mimico: un huevo de oro gigante que parece un tesoro... pero es un monstruo trampa.

Disfraz: un huevo de oro tipo joya (estilo huevo de Faberge) con bandas de oro, gemas turquesa, un remate
con gema en la punta y una grieta en zigzag que brilla, como si estuviera por eclosionar.
Cuando un ladron de huevos se acerca, la mitad de arriba de la cascara (Cabeza) se abre como una mandibula
sobre una bisagra trasera y deja ver filas de dientes blancos, una boca roja oscura, una lengua morada
bifurcada (Lengua -> PuntaLengua) y un gran ojo rojo que brilla dentro de la tapa (Ojo, mira para todos lados).
Patitas cortas de pollo anaranjadas con garras que salen de dos agujeros en la cascara.
"""
import math

from mathutils import Matrix, Vector

NOMBRE = "HuevoMimico"
COLORES_EXTRA = {
    "oro_huevo": (1.00, 0.72, 0.14),     # cascara
    "oro_borde": (0.72, 0.43, 0.05),     # bandas, bisagra, labio de la cascara
    "oro_claro": (1.00, 0.88, 0.45),     # remates
    "boca": (0.30, 0.02, 0.06),          # interior de la boca
    "encia": (0.62, 0.08, 0.16),         # encias y parpado
    "diente": (0.98, 0.96, 0.88),
    "lengua": (0.62, 0.22, 0.76),
    "lengua_osc": (0.36, 0.08, 0.48),
    "ojo_rojo": (1.00, 0.10, 0.06),      # brilla
    "grieta": (1.00, 0.88, 0.40),        # brilla (grietas e iris)
    "gema": (0.08, 0.78, 0.74),          # turquesa
    "gema_osc": (0.02, 0.45, 0.48),
    "pata": (1.00, 0.55, 0.12),
    "pata_osc": (0.85, 0.36, 0.06),
    "garra": (0.16, 0.10, 0.10),
}

# ------------------------------------------------------------------ medidas del huevo
R = 1.5      # radio horizontal
RB = 1.75    # alto de la mitad de abajo (desde la boca)
RT = 2.3     # alto de la mitad de arriba
ZC = 2.3     # altura de la boca (linea de la grieta)
PROF = 0.8   # hondura de la boca (mitad de abajo)
DOMO = 1.3   # hondura del paladar (dentro de la tapa)
ZIG = 0.17   # alto del zigzag de la grieta
SEG = 24     # lados de la cascara (cada 15 grados)
ANILLOS = 16
PASO = 360 / SEG
# perfil del interior: radio relativo de cada anillo, desde el borde (0) hasta el centro (8)
PERFIL = [1.0, 0.92, 0.80, 0.67, 0.53, 0.40, 0.27, 0.13, 0.0]
PESO_ZIG = {0: 1.0, 1: 1.0, 2: 0.7, 3: 0.3, -1: 0.45, -2: 0.1}
BISAGRA = (0, R + 0.07, ZC)
OJO = (0, -0.08, ZC + 1.02)
MIRADA = Vector((0, -0.42, -0.91)).normalized()   # hacia donde mira el ojo con la boca cerrada
ARRIBA_OJO = Vector((0, -0.91, 0.42)).normalized()  # "arriba" del ojo (la pupila es una rendija en esta direccion)
CADERA = (0.62, 0.05, 0.84)


def V(p):
    return Vector(p)


def desvanecer(theta):
    """El zigzag desaparece cerca de la bisagra (atras, 90 grados)."""
    dist = abs((theta - 90 + 180) % 360 - 180)
    return min(1.0, max(0.0, (dist - 15) / 45))


def zig(k):
    """Altura del zigzag en el vertice k (angulo k*15 grados)."""
    k %= SEG
    return ZIG * (1 if k % 2 == 0 else -1) * desvanecer(k * PASO)


def prof_interior(j, hondo):
    if j <= 0:
        return 0.0
    if j == 1:
        return 0.04
    s = PERFIL[j]
    return hondo * (1 - s * s) ** 0.75


def orientada(c, tipo, centro, eje_z, eje_y, esc, color, **kw):
    """Pieza con su eje local Z a lo largo de eje_z y su eje local Y lo mas cerca posible de eje_y."""
    z = V(eje_z).normalized()
    y = V(eje_y)
    y = y - z * y.dot(z)
    if y.length < 1e-6:
        y = V((1, 0, 0)) if abs(z.x) < 0.9 else V((0, 1, 0))
        y = y - z * y.dot(z)
    y.normalize()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed()
    rot = tuple(math.degrees(a) for a in m.to_euler("XYZ"))
    return c.pieza(tipo, tuple(centro), esc, color, rot=rot, **kw)


def punta(c, a, b, ancho, grosor, normal, color, lados=4, **kw):
    """Cono afilado de a hasta b; su lado delgado mira hacia 'normal'."""
    a, b = V(a), V(b)
    return orientada(c, "cono", (a + b) / 2, b - a, normal, (ancho, grosor, (b - a).length), color, lados=lados, **kw)


def superficie(theta, z, fuera=0.03):
    """Punto sobre la cascara exterior (angulo theta en grados, altura z) y su normal."""
    rz = RT if z >= ZC else RB
    k = max(-1.0, min(1.0, (z - ZC) / rz))
    r = R * math.sqrt(1 - k * k)
    t = math.radians(theta)
    p = V((r * math.cos(t), r * math.sin(t), z))
    n = V((p.x / R ** 2, p.y / R ** 2, (z - ZC) / rz ** 2)).normalized()
    return p + n * fuera, n


# ------------------------------------------------------------------ cascaras

def cascara(c, arriba):
    """Media cascara: por fuera mitad de elipsoide de oro; por dentro boca (abajo) o paladar (arriba)."""
    parte = "Cabeza" if arriba else "Cuerpo"
    rz = RT if arriba else RB
    obj = c.pieza("esfera", (0, 0, ZC), (R, R, rz), "oro_huevo", parte=parte, seg=SEG, anillos=ANILLOS)
    me = obj.data
    paso_lat = 180 / ANILLOS
    indice = {}
    for v in me.vertices:
        x, y, z = v.co
        lat = math.degrees(math.asin(max(-1.0, min(1.0, z / rz))))
        anillo = round(lat / paso_lat)
        d = -anillo if arriba else anillo  # d > 0: interior; d = 0: borde; d < 0: exterior
        theta = math.degrees(math.atan2(y, x)) % 360
        k = round(theta / PASO) % SEG
        w = PESO_ZIG.get(d, 0.0)
        r = math.hypot(x, y)
        if d > 0:
            nuevo = R * PERFIL[d]
            if r > 1e-6:
                x, y = x * nuevo / r, y * nuevo / r
            z = (1 if arriba else -1) * prof_interior(d, DOMO if arriba else PROF)
        v.co = (x, y, z + zig(k) * w)
        indice[v.index] = d
    capa = me.uv_layers.active
    colores = {"labio": "oro_borde", "encia": "encia", "boca": "boca"}
    for p in me.polygons:
        ds = [indice[i] for i in p.vertices]
        if max(ds) <= 0:
            continue
        if max(ds) <= 1:
            nombre = "labio"
        elif min(ds) >= 1 and max(ds) <= 2:
            nombre = "encia"
        else:
            nombre = "boca"
        u, vv = c.paleta.uv(colores[nombre])
        for li in p.loop_indices:
            capa.data[li].uv = (u, vv)
    return obj


def borde(k, d=0, arriba=False):
    """Punto del anillo d (0 = borde) en el angulo k*15 (coordenadas del mundo)."""
    s = PERFIL[d] if d > 0 else 1.0
    t = math.radians(k * PASO)
    z = ZC + (1 if arriba else -1) * prof_interior(d, DOMO if arriba else PROF) + zig(k) * PESO_ZIG.get(d, 0.0)
    return V((R * s * math.cos(t), R * s * math.sin(t), z))


def diente(c, k, alto, ancho, arriba):
    t = math.radians(k * PASO)
    e = V((math.cos(t), math.sin(t), 0))
    # base en la encia, entre el anillo 1 y el 2
    base = (borde(k, 1, arriba) * 0.55 + borde(k, 2, arriba) * 0.45)
    arr = V((0, 0, -1 if arriba else 1))
    direccion = (arr * math.cos(math.radians(14)) - e * math.sin(math.radians(14))).normalized()
    base = base - direccion * 0.06
    punta(c, base, base + direccion * alto, ancho, ancho * 0.45, e, "diente", parte="Cabeza" if arriba else "Cuerpo")


def linea(c, puntos, radio, color, **kw):
    for a, b in zip(puntos, puntos[1:]):
        c.entre(a, b, radio, color, tipo="cilindro", lados=4, **kw)
    for p in puntos[1:-1]:
        c.pieza("ico", tuple(p), radio * 1.05, color, subdiv=1, **kw)


def grieta(c, trazo, parte, radio=0.03):
    """Grieta brillante sobre la cascara: trazo = [(theta, z), ...]."""
    puntos = [superficie(t, z, 0.025)[0] for t, z in trazo]
    linea(c, puntos, radio, "grieta", parte=parte, brillo=True)


def gema(c, theta, z, tam, parte):
    p, n = superficie(theta, z, 0.0)
    orientada(c, "cilindro", p + n * 0.03, n, (0, 0, 1), (tam * 1.35, tam * 1.35, 0.1), "oro_claro", lados=8,
              parte=parte)
    orientada(c, "esfera", p + n * 0.09, n, (0, 0, 1), (tam, tam, tam * 0.75), "gema", seg=8, anillos=5,
              parte=parte)


# ------------------------------------------------------------------ construir

def construir(c):
    c.parte("Cabeza", "Cuerpo", BISAGRA)
    c.parte("Ojo", "Cabeza", OJO)
    c.parte("Lengua", "Cuerpo", (0, 0.62, ZC - 0.52))
    c.parte("PuntaLengua", "Lengua", (0, -0.2, ZC - 0.47))
    c.parte("PataIzq", "Cuerpo", CADERA, espejo=True)

    # ---------------- Cuerpo: mitad de abajo de la cascara
    c.usar("Cuerpo")
    cascara(c, arriba=False)
    # banda de oro con cuentas
    zb = ZC - 0.95
    rb = R * math.sqrt(1 - ((zb - ZC) / RB) ** 2)
    c.pieza("toro", (0, 0, zb), 1, "oro_borde", radio=rb + 0.01, grosor=0.06, seg=SEG, seg_menor=5)
    for i in range(12):
        p, n = superficie(i * 30 + 15, zb, 0.04)
        c.pieza("ico", tuple(p), 0.065, "oro_claro", subdiv=1)
    # grieta en zigzag de la boca (brilla, como huevo a punto de eclosionar)
    puntos = []
    for k in range(SEG + 1):
        p = borde(k)
        n = V((p.x, p.y, 0)).normalized()
        puntos.append(p + n * 0.035 - V((0, 0, 0.02)))
    linea(c, puntos, 0.028, "grieta", brillo=True)
    # grietas que bajan
    grieta(c, [(300, ZC - 0.1), (306, ZC - 0.45), (298, ZC - 0.7), (304, ZC - 1.05)], "Cuerpo")
    grieta(c, [(306, ZC - 0.45), (318, ZC - 0.62)], "Cuerpo", 0.03)
    grieta(c, [(232, ZC - 0.1), (226, ZC - 0.5), (234, ZC - 0.8)], "Cuerpo")
    grieta(c, [(160, ZC - 0.1), (153, ZC - 0.4), (161, ZC - 0.75)], "Cuerpo")
    # agujeros por donde salen las patas (con grietas alrededor)
    for sx in (1, -1):
        cx, cy = CADERA[0] * sx, CADERA[1]
        r2 = (cx ** 2 + cy ** 2) / R ** 2
        z = ZC - RB * math.sqrt(1 - r2)
        n = V((cx / R ** 2, cy / R ** 2, (z - ZC) / RB ** 2)).normalized()
        orientada(c, "esfera", V((cx, cy, z)) + n * 0.0, n, (0, 1, 0), (0.24, 0.24, 0.05), "boca", seg=10,
                  anillos=4)
        theta = math.degrees(math.atan2(cy, cx))
        grieta(c, [(theta - 14 * sx, z + 0.12), (theta - 24 * sx, z + 0.3), (theta - 18 * sx, z + 0.45)], "Cuerpo",
               0.028)
    # bisagra de joyero atras
    for sx in (1, -1):
        c.pieza("cilindro", (0.33 * sx, BISAGRA[1], BISAGRA[2]), (0.1, 0.1, 0.24), "oro_borde", rot=(0, 90, 0),
                lados=8)
        c.pieza("cubo", (0.33 * sx, BISAGRA[1] - 0.05, BISAGRA[2] - 0.2), (0.2, 0.06, 0.36), "oro_borde",
                rot=(-6, 0, 0))
    # monedas de oro dentro de la boca (la carnada)
    for x, y, giro in ((0.55, -0.55, 20), (-0.6, -0.4, -15), (0.62, 0.25, 35), (-0.5, 0.45, 10), (0.35, -0.95, 50)):
        r = math.hypot(x, y) / R
        z = ZC - PROF * (1 - r * r) ** 0.75 + 0.06
        c.pieza("cilindro", (x, y, z), (0.16, 0.16, 0.04), "oro_claro", rot=(math.atan2(-x, 1) * 25, giro, 0),
                lados=10)
    # dientes de abajo (en los picos del zigzag)
    for k, alto, ancho in ((16, 0.6, 0.17), (20, 0.6, 0.17), (14, 0.5, 0.15),
                           (22, 0.5, 0.15), (12, 0.42, 0.13), (0, 0.42, 0.13), (10, 0.36, 0.12), (2, 0.36, 0.12)):
        diente(c, k, alto, ancho, arriba=False)

    # ---------------- Cabeza: tapa / mandibula de arriba
    c.usar("Cabeza")
    cascara(c, arriba=True)
    zt = ZC + 0.85
    rt = R * math.sqrt(1 - ((zt - ZC) / RT) ** 2)
    c.pieza("toro", (0, 0, zt), 1, "oro_borde", radio=rt + 0.01, grosor=0.065, seg=SEG, seg_menor=5)
    for ang in (330, 30, 90, 150, 210):
        gema(c, ang, zt, 0.09, "Cabeza")
    gema(c, 270, zt, 0.17, "Cabeza")  # gema grande al frente
    # remate de la punta
    top = ZC + RT
    c.pieza("cilindro", (0, 0, top + 0.02), (0.24, 0.24, 0.14), "oro_borde", lados=10)
    c.pieza("esfera", (0, 0, top + 0.12), (0.2, 0.2, 0.08), "oro_claro", seg=10, anillos=5)
    c.pieza("ico", (0, 0, top + 0.3), (0.17, 0.17, 0.22), "gema", subdiv=1)
    c.pieza("ico", (0, 0, top + 0.52), 0.06, "oro_claro", subdiv=1)
    for i in range(4):
        a = math.radians(i * 90 + 45)
        c.entre((0.16 * math.cos(a), 0.16 * math.sin(a), top + 0.12),
                (0.1 * math.cos(a), 0.1 * math.sin(a), top + 0.36), 0.035, "oro_claro", lados=4)
    # grietas que suben
    grieta(c, [(285, ZC + 0.1), (279, ZC + 0.4), (287, ZC + 0.62)], "Cabeza")
    grieta(c, [(287, ZC + 1.05), (280, ZC + 1.35), (288, ZC + 1.6), (283, ZC + 1.85)], "Cabeza")
    grieta(c, [(280, ZC + 1.35), (296, ZC + 1.5)], "Cabeza", 0.03)
    grieta(c, [(350, ZC + 1.0), (343, ZC + 1.35), (352, ZC + 1.6)], "Cabeza")
    grieta(c, [(225, ZC + 0.1), (231, ZC + 0.42), (223, ZC + 0.66)], "Cabeza")
    grieta(c, [(20, ZC + 0.1), (14, ZC + 0.42), (22, ZC + 0.66)], "Cabeza")
    # bisagra (nudillo del centro)
    c.pieza("cilindro", BISAGRA, (0.1, 0.1, 0.4), "oro_borde", rot=(0, 90, 0), lados=8)
    c.pieza("cubo", (0, BISAGRA[1] - 0.05, BISAGRA[2] + 0.2), (0.34, 0.06, 0.36), "oro_borde", rot=(6, 0, 0))
    # dientes de arriba (en los valles del zigzag); los dos del frente son colmillos
    for k, alto, ancho in ((17, 0.66, 0.17), (19, 0.66, 0.17), (15, 0.5, 0.14), (21, 0.5, 0.14),
                           (13, 0.42, 0.13), (23, 0.42, 0.13), (11, 0.36, 0.12), (1, 0.36, 0.12)):
        diente(c, k, alto, ancho, arriba=True)
    # parpado alrededor del ojo
    c.pieza("toro", (OJO[0], OJO[1], OJO[2] + 0.2), (1, 1, 0.8), "encia", radio=0.47, grosor=0.1, seg=16,
            seg_menor=6)

    # ---------------- Ojo
    c.usar("Ojo")
    o = V(OJO)
    c.pieza("esfera", OJO, 0.5, "ojo_rojo", seg=16, anillos=10, brillo=True)
    orientada(c, "esfera", o + MIRADA * 0.43, MIRADA, ARRIBA_OJO, (0.28, 0.28, 0.1), "grieta", seg=12, anillos=6,
              brillo=True)
    orientada(c, "esfera", o + MIRADA * 0.5, MIRADA, ARRIBA_OJO, (0.065, 0.23, 0.06), "negro", seg=8, anillos=6)

    # ---------------- Lengua morada (dos partes) con punta bifurcada
    c.usar("Lengua")
    zl = ZC - 0.5
    c.entre((0, 0.85, zl - 0.06), (0, -0.32, zl + 0.02), 0.34, "lengua", tipo="esfera", aplanar=0.42, seg=14,
            anillos=8)
    c.entre((0, 0.55, zl + 0.1), (0, -0.25, zl + 0.14), 0.035, "lengua_osc", tipo="cilindro", lados=4)
    # raiz: entra en el piso de la boca, para que la lengua nunca se vea suelta al estirarse
    c.entre((0, 0.75, zl - 0.02), (0, 0.55, zl - 0.6), 0.3, "lengua", tipo="esfera", aplanar=0.75, seg=10,
            anillos=6)
    c.usar("PuntaLengua")
    c.entre((0, -0.12, zl + 0.0), (0, -1.08, zl + 0.14), 0.29, "lengua", tipo="esfera", aplanar=0.42, seg=14,
            anillos=8)
    c.entre((0, -0.2, zl + 0.12), (0, -0.88, zl + 0.22), 0.03, "lengua_osc", tipo="cilindro", lados=4)
    for sx in (1, -1):  # punta bifurcada de serpiente
        c.entre((0.05 * sx, -0.9, zl + 0.13), (0.15 * sx, -1.36, zl + 0.2), 0.075, "lengua", lados=6, aplanar=0.55)

    # ---------------- Patas de pollo
    c.usar("PataIzq")
    x0, y0 = CADERA[0], CADERA[1]
    tob = V((x0 + 0.05, y0 - 0.04, 0.2))
    c.entre((x0, y0, CADERA[2] + 0.15), tob, 0.12, "pata", tipo="cilindro", lados=8, espejo=True)
    for zz in (0.42, 0.56):
        c.pieza("toro", (x0 + 0.03, y0 - 0.02, zz), (1, 1, 0.7), "pata_osc", radio=0.12, grosor=0.03, seg=8,
                seg_menor=4, espejo=True)
    c.pieza("esfera", tuple(tob), 0.13, "pata", seg=8, anillos=6, espejo=True)
    for dx, dy in ((-0.24, -0.4), (0.0, -0.5), (0.24, -0.4), (0.0, 0.3)):
        dedo = V((tob.x + dx, tob.y + dy, 0.07))
        c.entre(tob - V((0, 0, 0.06)), dedo, 0.06, "pata", tipo="cilindro", lados=6, espejo=True)
        c.pieza("ico", tuple(dedo), 0.065, "pata", subdiv=1, espejo=True)
        uni = (dedo - tob).normalized()
        uni.z = 0
        uni.normalize()
        c.entre(dedo, dedo + uni * 0.17 - V((0, 0, 0.03)), 0.055, "garra", lados=5, espejo=True)


# ------------------------------------------------------------------ estadisticas y habilidades

CONFIG = {
    "nombre": "Huevo Mímico",
    "vida": 280,
    "velocidad": 14,
    "comportamiento": "emboscada",
    "radioDeteccion": 14,
    "radioPatrulla": 6,
    "radioPersecucion": 45,
    "reaparecer": 40,
    "colorUI": ("rgb", 255, 190, 40),
    "habilidades": [
        {"nombre": "Mordisco", "tipo": "Golpe", "anim": "Mordisco", "rango": 7, "alcance": 7, "angulo": 90,
         "danio": 20, "empuje": 30, "cooldown": 2, "retraso": 0.25, "color": ("rgb", 255, 60, 50)},
        {"nombre": "Nidada Explosiva", "tipo": "Invocar", "anim": "NidadaExplosiva", "rango": 40,
         "criatura": "PollitoBomba", "cantidad": 3, "maximo": 6, "cooldown": 12, "retraso": 0.6,
         "color": ("rgb", 255, 200, 40)},
        {"nombre": "Aplastón", "tipo": "Onda", "anim": "Aplaston", "rango": 9, "radio": 10, "danio": 18,
         "empuje": 50, "cooldown": 7, "retraso": 0.6, "color": ("rgb", 255, 215, 90)},
    ],
}

# ------------------------------------------------------------------ animaciones
# Constante en un ciclo: amplitud * sin(2*pi*(0*t + 0.25)) = amplitud.
FIJO = 0.25

ANIMACIONES = {
    # Despierto: la boca "respira" (abierta de 10 a 18 grados), la lengua se mueve y el ojo mira a todos lados.
    "Idle": {
        "Raiz": [("py", 0.04, 1.0, 0), ("rz", 2, 0.5, 0)],
        "Cabeza": [("rx", 14, 0, FIJO), ("rx", 4, 0.9, 0)],
        "Ojo": [("ry", 9, 0.45, 0), ("rz", -16, 0.45, 0), ("rx", 8, 0.7, 0.3)],
        "Lengua": [("rx", 8, 0, FIJO), ("py", 0.08, 0, FIJO), ("rx", 8, 1.1, 0), ("ry", 8, 0.6, 0)],
        "PuntaLengua": [("rx", 15, 1.1, 0.3), ("ry", 14, 0.6, 0.25)],
        "PataIzq": [("rx", 3, 1.0, 0)],
        "PataDer": [("rx", 3, 1.0, 0.5)],
    },
    # Disfrazado: huevo de oro casi quieto, boca cerrada y patitas escondidas dentro de la cascara.
    "Disfrazado": {
        "Raiz": [("py", -0.45, 0, FIJO), ("rz", 1.0, 0.3, 0)],
        "Cabeza": [("rx", 0.6, 0, FIJO), ("rx", 0.6, 0.2, 0)],
        "PataIzq": [("py", 0.45, 0, FIJO)],
        "PataDer": [("py", 0.45, 0, FIJO)],
    },
    # Caminar: saltitos con las patas (alternadas), se tambalea y mastica en cada salto.
    "Caminar": {
        "Raiz": [("py", 0.14, 0, FIJO), ("py", 0.14, 5.2, 0.75), ("rz", 6, 2.6, 0), ("rx", -4, 5.2, 0)],
        "Cabeza": [("rx", 14, 0, FIJO), ("rx", 7, 5.2, 0)],
        "Ojo": [("ry", 6, 1.3, 0)],
        "Lengua": [("rx", 8, 0, FIJO), ("py", 0.08, 0, FIJO), ("rx", 6, 5.2, 0.2)],
        "PuntaLengua": [("rx", 14, 5.2, 0.45), ("ry", 10, 2.6, 0)],
        "PataIzq": [("rx", 34, 2.6, 0)],
        "PataDer": [("rx", 34, 2.6, 0.5)],
    },
    # Los clips se suman encima del ciclo: Idle ya deja la tapa abierta ~14 grados, por eso "cerrar" es rx -14.
    "clips": {
        # Mordisco: abre de golpe y muerde hacia adelante (la mordida cierra en t = 0.25 = retraso).
        "Mordisco": {"duracion": 0.7, "claves": [
            (0.0, {}),
            (0.13, {"Raiz": {"rx": 8, "pz": 0.25}, "Cabeza": {"rx": 52}, "Lengua": {"rx": 20, "py": 0.1, "ry": 12},
                    "PuntaLengua": {"rx": 15, "ry": 15}, "PataIzq": {"rx": -10}, "PataDer": {"rx": -10}}),
            (0.25, {"Raiz": {"rx": -12, "pz": -0.8, "py": 0.2}, "Cabeza": {"rx": -14}, "Lengua": {"rx": -8},
                    "PataIzq": {"rx": 22}, "PataDer": {"rx": 22}}),
            (0.42, {"Raiz": {"rx": -6, "pz": -0.45, "py": 0.05}, "Cabeza": {"rx": -10}, "PataIzq": {"rx": 10},
                    "PataDer": {"rx": 10}}),
            (0.7, {}),
        ]},
        # Nidada Explosiva: se infla, abre la boca enorme y escupe pollitos bomba con la lengua (t = 0.6).
        "NidadaExplosiva": {"duracion": 1.25, "claves": [
            (0.0, {}),
            (0.25, {"Raiz": {"rx": 10, "py": -0.2}, "Cabeza": {"rx": -6}, "PataIzq": {"py": 0.2},
                    "PataDer": {"py": 0.2}}),
            (0.45, {"Raiz": {"rx": 16, "py": -0.1}, "Cabeza": {"rx": 22}, "Lengua": {"rx": -6},
                    "PataIzq": {"py": 0.1}, "PataDer": {"py": 0.1}}),
            (0.6, {"Raiz": {"rx": -12, "py": 0.35, "pz": -0.2}, "Cabeza": {"rx": 62},
                   "Lengua": {"rx": 12, "pz": -0.55, "py": 0.2}, "PuntaLengua": {"rx": 15}, "Ojo": {"rx": -10},
                   "PataIzq": {"rx": 15}, "PataDer": {"rx": 15}}),
            (0.85, {"Raiz": {"rx": -6, "py": 0.1}, "Cabeza": {"rx": 56}, "Lengua": {"rx": 10, "pz": -0.45, "py": 0.15},
                    "PuntaLengua": {"rx": -10}}),
            (1.25, {}),
        ]},
        # Aplaston: se agacha, salta alto con la boca abierta y cae de golpe cerrando la boca (t = 0.6).
        "Aplaston": {"duracion": 1.1, "claves": [
            (0.0, {}),
            (0.2, {"Raiz": {"py": -0.35, "rx": 4}, "PataIzq": {"py": 0.35}, "PataDer": {"py": 0.35},
                   "Cabeza": {"rx": -10}}),
            (0.42, {"Raiz": {"py": 1.7, "rx": -6}, "PataIzq": {"rx": 28}, "PataDer": {"rx": 28},
                    "Cabeza": {"rx": 32}, "Lengua": {"rx": 25, "ry": -20, "pz": -0.2},
                    "PuntaLengua": {"rx": 10, "ry": -18}}),
            (0.53, {"Raiz": {"py": 0.6, "rx": 0}, "PataIzq": {"rx": 10}, "PataDer": {"rx": 10},
                    "Cabeza": {"rx": 20}, "Lengua": {"rx": 10}}),
            (0.6, {"Raiz": {"py": -0.3}, "PataIzq": {"py": 0.3}, "PataDer": {"py": 0.3}, "Cabeza": {"rx": -14},
                   "Lengua": {"rx": -6}}),
            (0.75, {"Raiz": {"py": 0.12}, "Cabeza": {"rx": 10}}),
            (1.1, {}),
        ]},
        # Despertar: empieza en la pose del disfraz, tiembla, salta, abre la boca de golpe y saca la lengua.
        "Despertar": {"duracion": 1.4, "claves": [
            (0.0, {"Raiz": {"py": -0.45}, "PataIzq": {"py": 0.45}, "PataDer": {"py": 0.45}, "Cabeza": {"rx": -14}}),
            (0.12, {"Raiz": {"py": -0.45, "rz": 4}, "PataIzq": {"py": 0.45}, "PataDer": {"py": 0.45},
                    "Cabeza": {"rx": -12}}),
            (0.24, {"Raiz": {"py": -0.45, "rz": -4}, "PataIzq": {"py": 0.45}, "PataDer": {"py": 0.45},
                    "Cabeza": {"rx": -10}}),
            (0.34, {"Raiz": {"py": -0.5, "rz": 3}, "PataIzq": {"py": 0.5}, "PataDer": {"py": 0.5},
                    "Cabeza": {"rx": -14}}),
            (0.55, {"Raiz": {"py": 1.3, "rx": 6}, "PataIzq": {"rx": 30}, "PataDer": {"rx": 30},
                    "Cabeza": {"rx": 60}, "Lengua": {"rx": 32, "ry": 22, "pz": -0.25},
                    "PuntaLengua": {"rx": -8, "ry": 25},
                    "Ojo": {"rx": -8}}),
            (0.8, {"Raiz": {"py": -0.15, "rx": 4}, "PataIzq": {"py": 0.15}, "PataDer": {"py": 0.15},
                   "Cabeza": {"rx": 40}, "Lengua": {"rx": 26, "ry": 5, "pz": -0.3}, "PuntaLengua": {"rx": -5}}),
            (1.0, {"Raiz": {"rx": 12, "py": 0.1}, "Cabeza": {"rx": 58},
                   "Lengua": {"rx": 16, "ry": -16, "pz": -0.5, "py": 0.2}, "PuntaLengua": {"rx": -12, "ry": -22},
                   "Ojo": {"ry": 15}}),
            (1.4, {}),
        ]},
        "Golpeado": {"duracion": 0.4, "claves": [
            (0.0, {}),
            (0.1, {"Raiz": {"rz": 7, "rx": 6}, "Cabeza": {"rx": 18}, "Ojo": {"rx": 15}}),
            (0.22, {"Raiz": {"rz": -5}, "Cabeza": {"rx": -8}}),
            (0.4, {}),
        ]},
        # Derrota: se tambalea, se cae de lado con la tapa abierta, la lengua de fuera y las patas al aire.
        "Derrota": {"duracion": 1.3, "claves": [
            (0.0, {}),
            (0.3, {"Raiz": {"py": 0.3, "rz": -14}, "Cabeza": {"rx": 20}, "Ojo": {"ry": 20}}),
            (0.55, {"Raiz": {"py": 0.2, "rz": 18}, "Cabeza": {"rx": 0}}),
            (1.0, {"Raiz": {"py": -0.15, "rz": 88}, "Cabeza": {"rx": 42}, "Lengua": {"rx": 12, "pz": -0.5, "py": 0.2},
                   "PuntaLengua": {"rx": -40}, "PataIzq": {"rx": -30}, "PataDer": {"rx": 25},
                   "Ojo": {"rx": 25}}),
            (1.3, {"Raiz": {"py": -0.12, "rz": 84}, "Cabeza": {"rx": 36}, "Lengua": {"rx": 10, "pz": -0.55, "py": 0.2},
                   "PuntaLengua": {"rx": -50}, "PataIzq": {"rx": -36}, "PataDer": {"rx": 30},
                   "Ojo": {"rx": 30}}),
        ]},
    },
}
