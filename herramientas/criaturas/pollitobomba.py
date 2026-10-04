"""Pollito Bomba: pollito kamikaze con mecha encendida. Corre hacia el enemigo y explota."""
NOMBRE = "PollitoBomba"
COLORES_EXTRA = {"pollito": (1.00, 0.86, 0.25), "pollito_osc": (0.95, 0.68, 0.12), "chispa": (1.00, 0.75, 0.15),
                 "mejilla": (1.00, 0.45, 0.45)}


def construir(c):
    c.parte("Cabeza", "Cuerpo", (0, -0.2, 1.4))
    c.parte("Mecha", "Cabeza", (0, -0.3, 2.3))
    c.parte("AlaIzq", "Cuerpo", (0.62, 0.0, 1.25), espejo=True)
    c.parte("PataIzq", "Cuerpo", (0.25, 0.0, 0.6), espejo=True)

    c.usar("Cuerpo")
    c.pieza("esfera", (0, 0, 1.0), (0.75, 0.8, 0.7), "pollito", seg=14, anillos=9)
    c.pieza("esfera", (0, -0.35, 0.95), (0.5, 0.5, 0.45), "crema")
    for k in range(3):  # colita de plumitas
        c.entre((0, 0.6, 1.15), ((k - 1) * 0.18, 1.0, 1.45 + (k % 2) * 0.1), 0.12, "pollito_osc", tipo="esfera")
    c.pieza("toro", (0, -0.15, 1.38), (1, 1, 0.8), "rojo", radio=0.5, grosor=0.09)  # bandana
    c.entre((0.1, 0.3, 1.38), (0.25, 0.65, 1.15), 0.12, "rojo")

    c.usar("Cabeza")
    c.pieza("esfera", (0, -0.35, 1.78), 0.58, "pollito", seg=14, anillos=9)
    c.pieza("esfera", (0.22, -0.84, 1.88), (0.17, 0.08, 0.21), "ojo_blanco", espejo=True)
    c.pieza("esfera", (0.2, -0.9, 1.85), (0.09, 0.04, 0.11), "negro", espejo=True)
    c.pieza("cubo", (0.22, -0.9, 2.1), (0.26, 0.05, 0.06), "negro", rot=(0, -20, 0), espejo=True)  # cejas enojadas
    c.pieza("esfera", (0.4, -0.75, 1.62), (0.1, 0.04, 0.07), "mejilla", espejo=True)
    c.entre((0, -0.85, 1.7), (0, -1.2, 1.64), 0.13, "naranja", lados=6)
    c.entre((0, -0.85, 1.6), (0, -1.05, 1.57), 0.08, "naranja", lados=6)

    c.usar("Mecha")
    c.pieza("cilindro", (0, -0.3, 2.33), (0.22, 0.22, 0.14), "gris_osc", lados=10)
    c.entre((0, -0.3, 2.38), (0.05, -0.25, 2.6), 0.04, "beige", tipo="cilindro")
    c.entre((0.05, -0.25, 2.6), (0.15, -0.15, 2.75), 0.04, "beige", tipo="cilindro")
    c.pieza("ico", (0.17, -0.13, 2.82), 0.11, "chispa", brillo=True)
    for k in range(4):
        c.entre((0.17, -0.13, 2.82), (0.17 + 0.18 * ((k % 2) * 2 - 1) * (k < 2), -0.13 + 0.18 * ((k % 2) * 2 - 1) * (k >= 2),
                                      2.95), 0.03, "amarillo", brillo=True)

    c.usar("AlaIzq")
    c.pieza("esfera", (0.72, 0.05, 1.05), (0.13, 0.33, 0.3), "pollito_osc", rot=(-20, 0, 0), espejo=True)

    c.usar("PataIzq")
    c.entre((0.25, 0, 0.55), (0.25, 0, 0.1), 0.06, "naranja", tipo="cilindro", espejo=True)
    for ang in (-30, 0, 30):
        import math
        a = math.radians(ang)
        c.entre((0.25, 0, 0.08), (0.25 + 0.25 * math.sin(a), -0.25 * math.cos(a), 0.05), 0.05, "naranja",
                tipo="cilindro", espejo=True)


CONFIG = {
    "nombre": "Pollito Bomba",
    "vida": 30,
    "velocidad": 24,
    "comportamiento": "kamikaze",
    "radioDeteccion": 45,
    "radioPatrulla": 10,
    "radioPersecucion": 90,
    "reaparecer": 0,  # los invoca el Huevo Mimico; no reaparecen
    "colorUI": ("rgb", 255, 200, 40),
    "habilidades": [
        {"nombre": "¡Kabum!", "tipo": "Explotar", "anim": "Explotar", "rango": 5, "cooldown": 0, "retraso": 1.1,
         "radio": 11, "danio": 25, "empuje": 70, "color": ("rgb", 255, 150, 30)},
    ],
}

ANIMACIONES = {
    "Idle": {
        "Raiz": [("py", 0.05, 2.0, 0)],
        "Cabeza": [("rx", 6, 1.0, 0), ("ry", 8, 0.4, 0.2)],
        "Mecha": [("rz", 12, 3.0, 0), ("rx", 8, 2.3, 0.3)],
        "AlaIzq": [("rz", -10, 2.0, 0)],
    },
    "Caminar": {
        "Raiz": [("rz", 9, 3.0, 0), ("py", 0.08, 6.0, 0)],
        "Cabeza": [("rx", 7, 6.0, 0.25)],
        "Mecha": [("rz", 18, 6.0, 0)],
        "AlaIzq": [("rz", -30, 8.0, 0)],
        "PataIzq": [("rx", 35, 3.0, 0)],
        "PataDer": [("rx", 35, 3.0, 0.5)],
    },
    "clips": {
        "Explotar": {"duracion": 1.1, "claves": [
            (0.0, {}),
            (0.25, {"Raiz": {"py": 0.15, "rx": -12}, "AlaIzq": {"rz": -50}}),
            (0.5, {"Raiz": {"py": -0.1, "rx": 6}, "Cabeza": {"rx": 12}, "AlaIzq": {"rz": 10}}),
            (0.8, {"Raiz": {"py": 0.35, "rx": -8}, "AlaIzq": {"rz": -70}, "Mecha": {"rz": 30}}),
            (1.1, {"Raiz": {"py": 0.5}, "AlaIzq": {"rz": -80}, "Cabeza": {"rx": 20}, "Mecha": {"rz": -30}}),
        ]},
        "Derrota": {"duracion": 0.8, "claves": [
            (0.0, {}),
            (0.3, {"Raiz": {"py": 0.3, "rz": 30}}),
            (0.8, {"Raiz": {"py": -0.25, "rz": 90}, "AlaIzq": {"rz": -40}, "PataIzq": {"rx": 40}}),
        ]},
    },
}
