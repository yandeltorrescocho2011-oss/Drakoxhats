"""Arena del Palenque: el redondel donde pelean los gallos, en estilo fiesta mexicana caricatura.

Piso de arena con el circulo de careo y las dos rayas de salida, barrera baja de madera pintada en rojo y
blanco con dos puertas opuestas, gradas de madera escalonadas (3/4 del circulo) con pasillos, cojines y
sombreros olvidados, y una pared de respaldo rosa mexicano. Al fondo, la Puerta de los Gallos: pilares
turquesa, letrero "PALENQUE" con marco de oro y un copete con un gallo y un sol, con foquitos de marquesina
y macetas de cempasuchil. Ocho postes altos con faroles sostienen cuerdas de papel picado que bajan
hacia el centro, donde cuelga un aro con foquitos y una pinata de estrella. Entre poste y poste cuelgan
series de foquitos de colores. Antorchas en la entrada principal.

Escenario estatico: no se anima. Las partes solo sirven para no pasar el limite de triangulos por objeto.
"""
import math
import random

from mathutils import Euler, Vector

from motor import lerp

NOMBRE = "ArenaPalenque"
ESTATICO = True

COLORES_EXTRA = {
    "arena": (0.91, 0.73, 0.47),          # piso del redondel
    "arena_osc": (0.80, 0.60, 0.37),      # orilla del redondel
    "arena_media": (0.86, 0.67, 0.42),    # manchas de arena removida
    "piedra": (0.64, 0.58, 0.52),         # base de toda la arena
    "terracota": (0.78, 0.36, 0.20),      # zapatas de los postes, camino, macetas
    "madera_clara": (0.74, 0.52, 0.29),   # asientos y pasamanos
    "rosa_mex": (0.93, 0.12, 0.50),       # pared de las gradas, letrero
    "turquesa": (0.05, 0.70, 0.72),       # pilares y remates
    "picado_rosa": (1.00, 0.32, 0.66),
    "picado_naranja": (1.00, 0.52, 0.08),
    "picado_verde": (0.25, 0.85, 0.30),
    "picado_morado": (0.62, 0.30, 0.95),
    "picado_amarillo": (1.00, 0.88, 0.18),
    "picado_azul": (0.15, 0.65, 1.00),
    "foco": (1.00, 0.86, 0.45),           # foquitos y faroles (brillan)
    "foco_rosa": (1.00, 0.45, 0.75),
    "foco_verde": (0.45, 1.00, 0.55),
    "foco_azul": (0.45, 0.75, 1.00),
    "fuego": (1.00, 0.42, 0.06),          # llamas (brillan)
    "llama": (1.00, 0.86, 0.30),
    "cempasuchil": (1.00, 0.55, 0.04),
    "hoja": (0.20, 0.55, 0.18),
}

PICADO = ["picado_rosa", "picado_naranja", "picado_verde", "picado_morado", "picado_amarillo", "picado_azul"]
FOCOS = ["foco", "foco_rosa", "foco_verde", "foco_azul"]

# Medidas generales (studs). El centro de la arena es (0, 0); la entrada principal mira a -Y y la
# Puerta de los Gallos (con el letrero) esta en +Y.
R_ARENA = 17.45          # cara interior de la barrera
R_GRADA = 18.6           # primer escalon
PASO_GRADA = 1.6         # profundidad de cada escalon
N_GRADAS = 4
R_PARED = R_GRADA + PASO_GRADA * N_GRADAS   # 25.0
R_POSTE = 26.3
ALTO_POSTE = 14.0
ANG_POSTES = [22.5 + 45 * k for k in range(8)]
# Gradas en dos arcos: dejan libre la entrada principal (-123 a -57) y el pasillo de la puerta (79 a 101).
ARCOS_GRADA = [(-57.0, 79.0, 20), (101.0, 237.0, 20)]
Y_PUERTA = 19.0          # plano del letrero de la Puerta de los Gallos
X_PILAR = 4.1


# ------------------------------------------------------------------ utilidades

def polar(r, ang, z):
    a = math.radians(ang)
    return (r * math.cos(a), r * math.sin(a), z)


def caja_arco(c, r_in, r_out, z0, z1, ang, d_ang, color, extra=0.04, **kw):
    """Caja tangente al circulo que cubre la rebanada [ang - d_ang/2, ang + d_ang/2] entre r_in y r_out."""
    rc = (r_in + r_out) / 2
    largo = 2 * r_out * math.sin(math.radians(d_ang / 2)) + extra
    return c.pieza("cubo", polar(rc, ang, (z0 + z1) / 2), (largo, r_out - r_in, z1 - z0), color,
                   rot=(0, 0, ang + 90), **kw)


def arco_cajas(c, r_in, r_out, z0, z1, ang0, ang1, n, colores, extra=0.04):
    d = (ang1 - ang0) / n
    for i in range(n):
        caja_arco(c, r_in, r_out, z0, z1, ang0 + d * (i + 0.5), d, colores[i % len(colores)], extra)


def cuerda(a, b, comba, n):
    """Puntos de una cuerda que cuelga de a a b (comba = cuanto baja en medio)."""
    return [_punto_cuerda(a, b, comba, i / n) for i in range(n + 1)]


def _punto_cuerda(a, b, comba, t):
    p = lerp(a, b, t)
    return (p[0], p[1], p[2] - comba * 4 * t * (1 - t))


def dibujar_cuerda(c, pts, color="blanco", radio=0.045):
    for q0, q1 in zip(pts, pts[1:]):
        c.entre(q0, q1, radio, color, tipo="cilindro", lados=4)


def barra_xz(c, p0, p1, y, ancho, grosor, color):
    """Trazo recto en el plano XZ (para las letras del letrero), visto desde -Y."""
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    largo = math.hypot(dx, dz) + ancho
    ang = -math.degrees(math.atan2(dz, dx))
    c.pieza("cubo", ((p0[0] + p1[0]) / 2, y, (p0[1] + p1[1]) / 2), (largo, grosor, ancho), color, rot=(0, ang, 0))


def rayo_xz(c, centro, ang, r0, r1, ancho, grosor, color, **kw):
    """Cono plano que sale del centro (en el plano XZ) en direccion ang (grados, 0 = +X, 90 = arriba)."""
    a = math.radians(ang)
    d = (math.cos(a), math.sin(a))
    m = (r0 + r1) / 2
    pos = (centro[0] + d[0] * m, centro[1], centro[2] + d[1] * m)
    c.pieza("cono", pos, (ancho, grosor, r1 - r0), color, rot=(0, 90 - ang, 0), lados=4, **kw)


# ------------------------------------------------------------------ piso y barrera (Cuerpo)

def _cuerpo(c):
    c.usar("Cuerpo")
    # Base de piedra de toda la arena y el redondel de arena.
    c.pieza("cilindro", (0, 0, -0.15), (27.4, 27.4, 0.3), "piedra", lados=48)
    c.pieza("cilindro", (0, 0, 0.025), (R_ARENA + 0.05, R_ARENA + 0.05, 0.05), "arena_osc", lados=48)
    c.pieza("cilindro", (0, 0, 0.045), (15.6, 15.6, 0.09), "arena", lados=48)
    rnd = random.Random(7)
    for _ in range(7):  # manchas de arena removida
        r, a = rnd.uniform(4, 13), rnd.uniform(0, 360)
        c.pieza("esfera", polar(r, a, 0.09), (rnd.uniform(1.0, 1.8), rnd.uniform(0.7, 1.2), 0.025), "arena_media",
                rot=(0, 0, rnd.uniform(0, 180)), seg=8, anillos=4)
    # Circulo de careo, centro y rayas de salida (pintados con cal).
    c.pieza("toro", (0, 0, 0.09), (1, 1, 0.25), "blanco", radio=5.2, grosor=0.17, seg=40, seg_menor=4)
    c.pieza("cilindro", (0, 0, 0.1), (0.6, 0.6, 0.05), "rojo", lados=12)
    for y in (-3.0, 3.0):
        c.pieza("cubo", (0, y, 0.1), (2.0, 0.22, 0.05), "blanco")

    # Barrera: 40 tableros de 9 grados, menos los 4 de las puertas (+Y y -Y).
    puertas = (9, 10, 29, 30)
    for i in range(40):
        if i in puertas:
            continue
        a = 4.5 + 9 * i
        rojo = i % 2 == 0
        caja_arco(c, R_ARENA, 17.8, 0, 2.35, a, 9, "rojo" if rojo else "blanco", extra=0.0)
        caja_arco(c, 17.3, 17.95, 2.35, 2.6, a, 9, "madera_clara", extra=0.02)
        # rombo pintado en la cara de adentro
        c.pieza("cubo", polar(R_ARENA - 0.02, a, 1.2), (0.72, 0.06, 0.72), "amarillo" if rojo else "rosa_mex",
                rot=(0, 45, a + 90))
    # Postes de la barrera en cada union, con remate de piramide.
    for i in range(40):
        if i in (9, 10, 11, 29, 30, 31):
            continue
        a = 9 * i
        c.pieza("cubo", polar(17.62, a, 1.35), (0.32, 0.62, 2.7), "madera", rot=(0, 0, a + 90))
        c.pieza("cono", polar(17.62, a, 2.85), (0.32, 0.32, 0.3), "amarillo", rot=(0, 0, a + 45), lados=4)
    # Postes de las puertas (mas gruesos).
    for a in (81, 99, 261, 279):
        c.pieza("cubo", polar(17.62, a, 1.6), (0.62, 0.78, 3.2), "cafe_osc", rot=(0, 0, a + 90))
        c.pieza("cubo", polar(17.62, a, 3.3), (0.82, 0.98, 0.2), "amarillo", rot=(0, 0, a + 90))
    for a in (81, 99):  # la puerta de los gallos lleva bolas de oro (la principal lleva antorchas)
        c.pieza("esfera", polar(17.62, a, 3.65), 0.3, "oro", seg=8, anillos=6)
    # Camino de losetas en la entrada principal.
    for k in range(5):
        r = 19.0 + k * 1.65
        c.pieza("cubo", polar(r, -90, 0.03), (2.6, 1.3, 0.06), "terracota")


# ------------------------------------------------------------------ gradas

def _gradas(c):
    c.usar("Gradas")
    for k in range(N_GRADAS):
        r0 = R_GRADA + PASO_GRADA * k
        h = 1.0 * (k + 1)
        for a0, a1, n in ARCOS_GRADA:
            arco_cajas(c, r0, r0 + PASO_GRADA, 0, h, a0, a1, n, ["madera"])
            arco_cajas(c, r0 - 0.08, r0 + 0.55, h, h + 0.14, a0, a1, n, ["madera_clara"], extra=0.02)
    # Pared de respaldo rosa con remate turquesa.
    for a0, a1, n in ARCOS_GRADA:
        arco_cajas(c, R_PARED, R_PARED + 0.45, 0, 5.6, a0, a1, n, ["rosa_mex"])
        arco_cajas(c, R_PARED - 0.1, R_PARED + 0.55, 5.6, 5.85, a0, a1, n, ["turquesa"])
    # Por fuera: zoclo terracota y pilastras turquesa con remate amarillo.
    for a0, a1, n in ARCOS_GRADA:
        arco_cajas(c, R_PARED + 0.4, R_PARED + 0.52, 0, 1.0, a0, a1, n, ["terracota"])
        d = (a1 - a0) / n
        for i in range(0, n + 1, 2):
            a = a0 + d * i
            c.pieza("cubo", polar(R_PARED + 0.55, a, 2.95), (0.6, 0.3, 5.9), "turquesa", rot=(0, 0, a + 90))
            c.pieza("cubo", polar(R_PARED + 0.4, a, 6.0), (0.8, 0.75, 0.3), "amarillo", rot=(0, 0, a + 90))
    # Muros laterales escalonados donde terminan las gradas.
    for a0, a1, n in ARCOS_GRADA:
        for borde, signo in ((a0, -1), (a1, 1)):
            for k in range(N_GRADAS):
                r0 = R_GRADA + PASO_GRADA * k
                d = math.degrees(0.35 / (r0 + 0.8))
                caja_arco(c, r0 - 0.05, r0 + PASO_GRADA + 0.05, 0, k + 1.3, borde + signo * d / 2, d, "rosa_mex",
                          extra=0.0)
                caja_arco(c, r0 - 0.1, r0 + PASO_GRADA + 0.05, k + 1.3, k + 1.45, borde + signo * d / 2, d * 1.4,
                          "amarillo", extra=0.0)
    # Pasillos: medios escalones color crema para subir.
    for a in (-12, 34, 146, 192):
        for k in range(-1, N_GRADAS - 1):
            r_fin = R_GRADA + PASO_GRADA * (k + 1)
            r_ini = r_fin - 0.75
            d = math.degrees(1.5 / r_fin)
            caja_arco(c, r_ini, r_fin, 0, (k + 1) + 0.5, a, d, "crema", extra=0.0)
    # Cojines de colores y sombreros olvidados en los asientos.
    rnd = random.Random(3)
    sitios = []
    for k in range(N_GRADAS):
        for a0, a1, n in ARCOS_GRADA:
            for i in range(n):
                sitios.append((k, a0 + (a1 - a0) * (i + 0.5) / n))
    rnd.shuffle(sitios)
    for j, (k, a) in enumerate(sitios[:34]):
        if any(abs(a - p) < 4 for p in (-12, 34, 146, 192)):
            continue
        r = R_GRADA + PASO_GRADA * k + 0.9
        h = k + 1.0
        if j < 6:
            _sombrero(c, polar(r, a + rnd.uniform(-1, 1), h), rnd.uniform(0, 360))
        else:
            c.pieza("cubo", polar(r, a + rnd.uniform(-1.5, 1.5), h + 0.1), (0.95, 0.8, 0.2), PICADO[j % 6],
                    rot=(0, 0, a + 90 + rnd.uniform(-15, 15)))


def _sombrero(c, base, giro):
    x, y, z = base
    c.pieza("cilindro", (x, y, z + 0.05), (0.75, 0.75, 0.08), "paja", lados=12)
    c.pieza("cono", (x, y, z + 0.32), (0.34, 0.34, 0.5), "paja", lados=8, punta=0.55, rot=(0, 0, giro))
    c.pieza("cilindro", (x, y, z + 0.17), (0.35, 0.35, 0.1), "rojo", lados=8)


# ------------------------------------------------------------------ postes, faroles y foquitos

def _postes(c):
    c.usar("Postes")
    for k, a in enumerate(ANG_POSTES):
        x, y, _ = polar(R_POSTE, a, 0)
        c.pieza("cubo", (x, y, 0.3), (1.0, 1.0, 0.6), "terracota", rot=(0, 0, a))
        c.pieza("cilindro", (x, y, ALTO_POSTE / 2), (0.28, 0.28, ALTO_POSTE), "madera", lados=8)
        c.pieza("cilindro", (x, y, ALTO_POSTE - 0.5), (0.34, 0.34, 0.3), "rosa_mex", lados=8)
        c.pieza("cilindro", (x, y, 9.3), (0.34, 0.34, 0.25), "turquesa", lados=8)
        c.pieza("esfera", (x, y, ALTO_POSTE + 0.2), 0.38, "oro", seg=8, anillos=6)
        # banderita en la punta
        c.entre((x, y, ALTO_POSTE + 0.4), (x, y, ALTO_POSTE + 1.6), 0.05, "negro", tipo="cilindro", lados=4)
        tx, ty = -math.sin(math.radians(a)) * 0.42, math.cos(math.radians(a)) * 0.42
        c.pieza("cono", (x + tx, y + ty, ALTO_POSTE + 1.3), (0.32, 0.06, 0.8), PICADO[k % 6], lados=3,
                rot=(0, 90, a + 90))
        # farol colgado de un brazo hacia el centro
        c.entre(polar(R_POSTE, a, 8.5), polar(R_POSTE - 1.1, a, 8.5), 0.06, "negro", tipo="cilindro", lados=4)
        xf, yf, _ = polar(R_POSTE - 1.05, a, 0)
        c.entre((xf, yf, 8.5), (xf, yf, 8.15), 0.03, "negro", tipo="cilindro", lados=4)
        c.pieza("cono", (xf, yf, 8.0), (0.45, 0.45, 0.32), "negro", lados=6)
        c.pieza("cilindro", (xf, yf, 7.5), (0.3, 0.3, 0.7), "foco", lados=6, brillo=True)
        c.pieza("cilindro", (xf, yf, 7.1), (0.36, 0.36, 0.12), "negro", lados=6)
    # Series de foquitos de colores entre poste y poste.
    for k, a in enumerate(ANG_POSTES):
        p0 = polar(R_POSTE, a, 13.0)
        p1 = polar(R_POSTE, a + 45, 13.0)
        dibujar_cuerda(c, cuerda(p0, p1, 1.6, 8), "negro", 0.04)
        n = 9
        for j in range(n):
            t = (j + 0.5) / n
            px, py, pz = _punto_cuerda(p0, p1, 1.6, t)
            c.pieza("ico", (px, py, pz - 0.22), 0.2, FOCOS[(j + k) % 4], brillo=True, subdiv=1)


# ------------------------------------------------------------------ papel picado y pinata

def _papel_picado(c):
    c.usar("PapelPicado")
    z_aro = 13.0
    r_aro = 2.2
    c.pieza("toro", (0, 0, z_aro), 1, "oro", radio=r_aro, grosor=0.12, seg=20, seg_menor=4)
    for a in (45, 135):
        c.entre(polar(r_aro, a, z_aro), polar(r_aro, a + 180, z_aro), 0.05, "madera", tipo="cilindro", lados=4)
    for k, a in enumerate(ANG_POSTES):
        p0 = polar(R_POSTE, a, 13.4)
        p1 = polar(r_aro, a, z_aro)
        comba = 2.2
        dibujar_cuerda(c, cuerda(p0, p1, comba, 10))
        horiz = R_POSTE - r_aro
        n = 17
        for j in range(n):
            t = (j + 0.5) / n
            px, py, pz = _punto_cuerda(p0, p1, comba, t)
            pendiente = ((p1[2] - p0[2]) - comba * 4 * (1 - 2 * t)) / horiz
            inclina = -math.degrees(math.atan(pendiente))
            vaiven = 18 if j % 2 else -18      # ondean un poco para que se vean tambien desde arriba
            rot = (vaiven, inclina, a + 180)
            colgar = Euler(tuple(math.radians(v) for v in rot), "XYZ").to_matrix() @ Vector((0, 0, -0.52))
            c.pieza("cubo", (px + colgar.x, py + colgar.y, pz + colgar.z), (0.86, 0.04, 1.0),
                    PICADO[(j + k * 2) % 6], rot=rot)
    # Foquitos del aro.
    for k in range(8):
        c.pieza("ico", polar(r_aro, 22.5 + 45 * k, z_aro - 0.3), 0.2, "foco", brillo=True, subdiv=1)
    # Pinata de estrella colgada del centro.
    zc = 10.9
    c.pieza("cilindro", (0, 0, (zc + z_aro) / 2), (0.04, 0.04, z_aro - zc), "blanco", lados=4)
    c.pieza("esfera", (0, 0, zc), 0.85, "rosa_mex", seg=12, anillos=8)
    c.pieza("toro", (0, 0, zc), (1, 1, 1.2), "picado_amarillo", radio=0.85, grosor=0.1, seg=12, seg_menor=4)
    colores = ["picado_amarillo", "picado_azul", "picado_naranja", "picado_verde", "picado_morado", "picado_rosa"]
    puntas = []
    for m in range(6):
        b = math.radians(30 + 60 * m)
        d = Vector((math.cos(b) * math.cos(math.radians(12)), math.sin(b) * math.cos(math.radians(12)),
                    -math.sin(math.radians(12))))
        ini = Vector((0, 0, zc)) + d * 0.55
        fin = Vector((0, 0, zc)) + d * 2.1
        c.entre(tuple(ini), tuple(fin), 0.4, colores[m], tipo="cono", lados=6)
        puntas.append((tuple(fin), colores[(m + 3) % 6]))
    fin = (0, 0, zc - 2.0)
    c.entre((0, 0, zc - 0.55), fin, 0.4, "picado_amarillo", tipo="cono", lados=6)
    puntas.append((fin, "picado_rosa"))
    for (px, py, pz), col in puntas:  # flecos de papel en las puntas
        for dx, dy in ((0.12, 0), (-0.06, 0.1), (-0.06, -0.1)):
            c.entre((px, py, pz), (px + dx, py + dy, pz - 0.7), 0.06, col, tipo="cono", lados=4)


# ------------------------------------------------------------------ puerta de los gallos, antorchas

LETRAS = {
    # trazos en una cuadricula de 0..1 (x) por 0..1 (z); se escalan al tamano de la letra
    "P": [((0, 0), (0, 1)), ((0, 1), (1, 1)), ((0, 0.5), (1, 0.5)), ((1, 0.5), (1, 1))],
    "A": [((0, 0), (0, 1)), ((1, 0), (1, 1)), ((0, 1), (1, 1)), ((0, 0.5), (1, 0.5))],
    "L": [((0, 0), (0, 1)), ((0, 0), (1, 0))],
    "E": [((0, 0), (0, 1)), ((0, 1), (1, 1)), ((0, 0.5), (0.8, 0.5)), ((0, 0), (1, 0))],
    "N": [((0, 0), (0, 1)), ((1, 0), (1, 1)), ((0, 1), (1, 0))],
    "Q": [((0, 0), (0, 1)), ((1, 0), (1, 1)), ((0, 1), (1, 1)), ((0, 0), (1, 0)), ((0.55, 0.3), (1.15, -0.15))],
    "U": [((0, 0), (0, 1)), ((1, 0), (1, 1)), ((0, 0), (1, 0))],
}


def _letrero(c, texto, centro, alto, ancho_letra, espacio, trazo, color):
    cx, y, cz = centro
    total = len(texto) * ancho_letra + (len(texto) - 1) * espacio
    x0 = cx - total / 2
    for i, letra in enumerate(texto):
        lx = x0 + i * (ancho_letra + espacio)
        w, h = ancho_letra - trazo, alto - trazo
        for (ax, az), (bx, bz) in LETRAS[letra]:
            p0 = (lx + trazo / 2 + ax * w, cz - alto / 2 + trazo / 2 + az * h)
            p1 = (lx + trazo / 2 + bx * w, cz - alto / 2 + trazo / 2 + bz * h)
            barra_xz(c, p0, p1, y, trazo, 0.14, color)


def _antorcha(c, base, alto, pie="madera"):
    x, y, z = base
    c.pieza("cilindro", (x, y, z + alto / 2), (0.12, 0.12, alto), pie, lados=6)
    c.pieza("cono", (x, y, z + alto + 0.15), (0.34, 0.34, 0.4), "gris_osc", rot=(180, 0, 0), lados=8, punta=0.45)
    c.pieza("cono", (x, y, z + alto + 0.72), (0.3, 0.3, 0.9), "fuego", lados=6, brillo=True)
    c.pieza("cono", (x, y + 0.04, z + alto + 0.62), (0.18, 0.18, 0.6), "llama", lados=5, brillo=True,
            rot=(0, 0, 30))


def _adornos(c):
    c.usar("Adornos")
    y = Y_PUERTA
    # Pilares turquesa con base y capitel de oro.
    for sx in (-1, 1):
        x = sx * X_PILAR
        c.pieza("cubo", (x, y, 0.25), (1.65, 1.65, 0.5), "oro_osc")
        c.pieza("cubo", (x, y, 2.85), (1.2, 1.2, 4.7), "turquesa")
        c.pieza("cubo", (x, y, 2.4), (1.3, 1.3, 0.25), "oro")
        c.pieza("cubo", (x, y - 0.6, 3.6), (0.5, 0.06, 0.5), "rosa_mex", rot=(0, 45, 0))
        # farol colgado al frente del pilar
        c.entre((x, y - 0.6, 4.6), (x, y - 1.2, 4.6), 0.05, "negro", tipo="cilindro", lados=4)
        c.pieza("cono", (x, y - 1.2, 4.4), (0.36, 0.36, 0.26), "negro", lados=6)
        c.pieza("cilindro", (x, y - 1.2, 3.98), (0.24, 0.24, 0.58), "foco", lados=6, brillo=True)
        c.pieza("cilindro", (x, y - 1.2, 3.65), (0.28, 0.28, 0.1), "negro", lados=6)
    # Letrero: marco de oro, tabla rosa y letras amarillas.
    c.pieza("cubo", (0, y, 6.6), (9.9, 0.5, 2.4), "oro")
    c.pieza("cubo", (0, y - 0.15, 6.6), (9.6, 0.4, 2.1), "rosa_mex")
    _letrero(c, "PALENQUE", (0, y - 0.4, 6.6), 1.25, 0.86, 0.26, 0.22, "amarillo")
    # Copete: medio disco crema con orilla de oro, rayos de sol y foquitos de marquesina.
    zc = 7.8
    c.pieza("cilindro", (0, y, zc), (1.9, 1.9, 0.4), "crema", rot=(90, 0, 0), lados=20)
    c.pieza("toro", (0, y, zc), 1, "oro", rot=(90, 0, 0), radio=1.9, grosor=0.13, seg=24, seg_menor=4)
    for k in range(9):
        ang = 12 + k * 19.5
        rayo_xz(c, (0, y, zc), ang, 1.95, 2.85 if k % 2 == 0 else 2.55, 0.32, 0.1,
                "amarillo" if k % 2 == 0 else "naranja")
    for k in range(9):
        ang = 22.5 * k
        if 0 < ang < 180:
            c.pieza("ico", (1.9 * math.cos(math.radians(ang)), y - 0.2, zc + 1.9 * math.sin(math.radians(ang))),
                    0.15, "foco", brillo=True, subdiv=1)
    _gallo_emblema(c, (0.05, y - 0.24, zc + 0.62))
    # Macetas con cempasuchil arriba del letrero.
    for sx in (-1, 1):
        x = sx * 4.1
        c.pieza("cono", (x, y, 8.07), (0.38, 0.38, 0.55), "terracota", rot=(180, 0, 0), lados=8, punta=0.7)
        c.pieza("esfera", (x, y, 8.4), (0.4, 0.4, 0.2), "hoja", seg=8, anillos=4)
        for dx, dy, dz in ((0, 0, 0.62), (0.28, 0.05, 0.48), (-0.28, -0.05, 0.5), (0.05, -0.3, 0.45),
                           (-0.05, 0.3, 0.47)):
            c.pieza("ico", (x + dx, y + dy, 8.0 + dz), 0.22, "cempasuchil", subdiv=1)
    # Guirnalda de cempasuchil en el borde de arriba del letrero.
    for sx in (-1, 1):
        for k in range(3):
            c.pieza("ico", (sx * (2.35 + 0.48 * k), y - 0.1, 7.85), 0.2,
                    "cempasuchil" if k % 2 == 0 else "amarillo", subdiv=1)
    # Huacales y canastos de gallos en el pasillo de la puerta.
    for sx in (-1, 1):
        _huacal(c, (sx * 3.35, 21.6, 0), sx * 8)
        _huacal(c, (sx * 3.45, 22.8, 0), -sx * 5)
        _huacal(c, (sx * 3.4, 22.2, 1.12), sx * 20)
        _canasto(c, (sx * 3.7, 24.4, 0))
    _palco(c, 170.0)
    # Macetas a los lados del camino de la entrada principal.
    for sx in (-1, 1):
        _maceta(c, (sx * 2.4, -19.3, 0))
    # Antorchas en la puerta principal (sobre los postes) y a los lados de la entrada.
    for a in (261, 279):
        _antorcha(c, polar(17.62, a, 3.4), 0.5, "cafe_osc")
    for a in (-61, -119):
        x, yy, _ = polar(19.6, a, 0)
        c.pieza("cubo", (x, yy, 0.3), (0.8, 0.8, 0.6), "terracota")
        _antorcha(c, (x, yy, 0.6), 3.6)


def _huacal(c, base, giro):
    """Caja de madera con tablillas para llevar gallos."""
    x, y, z = base
    c.pieza("cubo", (x, y, z + 0.55), (1.0, 1.0, 1.08), "madera_clara", rot=(0, 0, giro))
    for dz in (0.3, 0.72):
        c.pieza("cubo", (x, y, z + dz), (1.06, 1.06, 0.12), "cafe", rot=(0, 0, giro))
    c.pieza("cubo", (x, y, z + 1.1), (1.08, 1.08, 0.06), "cafe", rot=(0, 0, giro))


def _canasto(c, base):
    x, y, z = base
    c.pieza("cilindro", (x, y, z + 0.45), (0.6, 0.6, 0.9), "paja", lados=10)
    c.pieza("toro", (x, y, z + 0.6), 1, "beige", radio=0.6, grosor=0.06, seg=10, seg_menor=3)
    c.pieza("esfera", (x, y, z + 0.9), (0.62, 0.62, 0.35), "beige", seg=10, anillos=6)
    c.pieza("esfera", (x, y, z + 1.27), 0.1, "cafe", seg=6, anillos=4)


def _maceta(c, base):
    x, y, z = base
    c.pieza("cono", (x, y, z + 0.4), (0.45, 0.45, 0.8), "terracota", rot=(180, 0, 0), lados=8, punta=0.7)
    c.pieza("esfera", (x, y, z + 0.82), (0.45, 0.45, 0.2), "hoja", seg=8, anillos=4)
    for dx, dy, dz in ((0, 0, 1.12), (0.3, 0.05, 0.98), (-0.3, -0.05, 1.0), (0.05, -0.32, 0.95), (-0.05, 0.32, 0.97)):
        c.pieza("ico", (x + dx, y + dy, z + dz), 0.24, "cempasuchil", subdiv=1)


def _palco(c, ang):
    """Palco del juez arriba de las gradas: toldo tricolor con banderines y la campana de la pelea."""
    a0, a1 = ang - 12, ang + 12
    r_frente, r_atras = 21.4, 25.25
    z_frente, z_atras = 7.0, 8.2
    for a in (a0 + 0.8, ang, a1 - 0.8):
        c.pieza("cilindro", polar(r_frente, a, (2.0 + z_frente) / 2), (0.12, 0.12, z_frente - 2.0), "madera_clara",
                lados=6)
        c.pieza("cilindro", polar(r_atras, a, (5.85 + z_atras) / 2), (0.12, 0.12, z_atras - 5.85), "madera_clara",
                lados=6)
    n = 9
    d = (a1 - a0) / n
    largo = math.hypot(r_atras - r_frente, z_atras - z_frente) + 0.3
    incl = -math.degrees(math.atan2(z_atras - z_frente, r_atras - r_frente))
    rc, zc = (r_frente + r_atras) / 2, (z_frente + z_atras) / 2 + 0.08
    colores = ["verde", "blanco", "rojo"]
    for i in range(n):
        a = a0 + d * (i + 0.5)
        ancho = 2 * rc * math.sin(math.radians(d / 2)) + 0.03
        c.pieza("cubo", polar(rc, a, zc + (0.025 if i % 2 else 0)), (ancho, largo, 0.1), colores[i % 3],
                rot=(incl, 0, a + 90))
        # banderin del faldon
        c.pieza("cono", polar(r_frente - 0.12, a, z_frente - 0.18), (ancho * 0.48, 0.04, 0.55), colores[i % 3],
                rot=(180, 0, a + 90), lados=4)
    # Campana colgada al frente del toldo.
    x, y, _ = polar(r_frente - 0.2, ang, 0)
    c.pieza("cilindro", (x, y, 6.6), (0.03, 0.03, 0.6), "negro", lados=4)
    c.pieza("esfera", (x, y, 6.25), (0.2, 0.2, 0.16), "oro", seg=8, anillos=4)
    c.pieza("cono", (x, y, 5.95), (0.34, 0.34, 0.5), "oro", lados=10, punta=0.5)
    c.pieza("esfera", (x, y, 5.62), 0.09, "oro_osc", seg=6, anillos=4)


def _gallo_emblema(c, centro):
    """Gallo de perfil (mirando a +X) pintado en relieve sobre el copete."""
    cx, y, cz = centro
    c.pieza("esfera", (cx - 0.1, y, cz - 0.05), (0.62, 0.1, 0.44), "rojo", seg=12, anillos=6)
    c.pieza("esfera", (cx - 0.15, y - 0.06, cz - 0.02), (0.36, 0.08, 0.24), "rojo_osc", seg=10, anillos=6,
            rot=(0, 15, 0))
    c.entre((cx + 0.25, y, cz + 0.15), (cx + 0.5, y, cz + 0.55), 0.09, "naranja", tipo="esfera", aplanar=2.6)
    c.pieza("esfera", (cx + 0.55, y, cz + 0.62), (0.24, 0.1, 0.24), "naranja", seg=10, anillos=6)
    for k, dx in enumerate((-0.12, 0.04, 0.2)):
        c.pieza("esfera", (cx + 0.5 + dx, y, cz + 0.88 + (0.04 if k == 1 else 0)), (0.1, 0.08, 0.13), "rojo",
                seg=8, anillos=4)
    c.entre((cx + 0.75, y, cz + 0.64), (cx + 1.0, y, cz + 0.58), 0.08, "amarillo", tipo="cono", lados=4,
            aplanar=1.0)
    c.pieza("esfera", (cx + 0.66, y - 0.08, cz + 0.68), 0.05, "negro", seg=6, anillos=4)
    c.pieza("esfera", (cx + 0.7, y, cz + 0.42), (0.07, 0.07, 0.11), "rojo", seg=6, anillos=4)
    for (bx, bz), col in (((-1.15, 0.6), "verde_osc"), ((-1.3, 0.25), "verde"), ((-1.25, -0.08), "negro"),
                          ((-0.95, 0.8), "verde")):
        c.entre((cx - 0.55, y + 0.01, cz + 0.05), (cx + bx, y + 0.01, cz + bz), 0.07, col, tipo="esfera", aplanar=2.4)
    for dx in (-0.2, 0.08):
        c.entre((cx + dx, y, cz - 0.42), (cx + dx + 0.05, y, cz - 0.82), 0.05, "amarillo", tipo="cilindro", lados=4)


def construir(c):
    for parte in ("Gradas", "Postes", "PapelPicado", "Adornos"):
        c.parte(parte, "Cuerpo", (0, 0, 0))
    _cuerpo(c)
    _gradas(c)
    _postes(c)
    _papel_picado(c)
    _adornos(c)
