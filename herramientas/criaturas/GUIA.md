# Guía para crear criaturas animadas

Cada criatura es un archivo `herramientas/criaturas/<nombre_en_minusculas>.py`. Ejemplo completo:
`pollitobomba.py`. El motor compartido es `motor.py` y el generador es `generar.py`. **No modifiques
`motor.py` ni `generar.py`**; si te falta algo, avísalo en tu respuesta.

## Comandos

```bash
cd /home/user/Drakoxhats
python3 herramientas/criaturas/generar.py MiCriatura --rapido   # solo imagen (≈30 s), para probar formas
python3 herramientas/criaturas/generar.py MiCriatura            # imagen + GIF de animación (varios minutos)
python3 herramientas/criaturas/hoja_contacto.py MiCriatura      # hoja con 24 cuadros del GIF para revisarlo
```

Salidas: `modelos/criaturas/<Nombre>/` (`<Nombre>.fbx`, `paleta.png`, `vista_previa.png`, `animacion.gif`,
`_hoja_contacto.png`) y `roblox/SistemaCriaturas/Compartido/Configs/<Nombre>.lua`. Mira las imágenes con la herramienta Read.

## Estructura del archivo

```python
NOMBRE = "GalloEjemplo"                  # igual que el nombre del archivo pero en CamelCase
COLORES_EXTRA = {"azul_rayo": (0.2, 0.5, 1.0)}   # colores RGB 0-1 además de motor.COLORES_BASE (máx. 64 en total)

def construir(c):        # c es motor.Criatura
    c.parte("Cabeza", "Cuerpo", (0, -1.2, 4.6))          # parte, padre, punto de unión (articulación)
    c.parte("AlaIzq", "Cuerpo", (1.1, 0.0, 3.6), espejo=True)   # crea también AlaDer reflejada
    c.usar("Cuerpo")                                     # las piezas siguientes van a esta parte
    c.pieza("esfera", (0, 0, 3), (1.3, 1.7, 1.4), "rojo", seg=16, anillos=10)
    c.entre((0, -1.8, 4.7), (0, -2.4, 4.6), 0.2, "amarillo", lados=6)   # pieza del punto a al b
    c.pieza("ico", (0.3, -1.8, 4.9), 0.12, "cian", brillo=True, espejo=True, parte="Cabeza")
    ...

CONFIG = {...}           # estadísticas y habilidades (ver abajo)
ANIMACIONES = {...}      # ciclos y clips (ver abajo)
```

Para escenarios sin animación (por ejemplo una arena) pon `ESTATICO = True` y omite `CONFIG` y `ANIMACIONES`.

### Piezas
- `c.pieza(tipo, pos, esc, color, rot=(0,0,0), espejo=False, parte=None, brillo=False, vidrio=False, **kw)`
  - `tipo`: `"esfera"` (kw `seg`, `anillos`), `"ico"` (`subdiv`), `"cubo"`, `"cilindro"` (`lados`),
    `"cono"` (`lados`, `punta` = radio de la punta 0-1), `"toro"` (`radio`, `grosor`, `seg`, `seg_menor`).
  - `esc`: número o (x, y, z). Una esfera de esc 1 tiene radio 1; un cubo de esc 1 mide 1; el cilindro y el cono
    tienen radio 1 y alto 1 (a lo largo de Z) antes de escalar. `rot` en grados (X, Y, Z).
- `c.entre(a, b, radio, color, tipo="cono", aplanar=1.0, ...)`: pieza alineada de `a` a `b` (cuernos, plumas,
  garras, picos, palos, hojas de espada). Con `tipo="esfera"` hace una pluma/hoja alargada.
- `espejo=True` copia la pieza al otro lado (x → -x). Si la parte termina en `Izq`, la copia va a la parte `Der`.
- `brillo=True`: la pieza será **Neon** en Roblox (ojos, energía, gemas, fuego). Úsalo como acento, no en todo.
- `vidrio=True`: pieza semitransparente (alas de insecto, cristal).
- Utilidades en `motor`: `lerp(a, b, t)`, `alargar(a, b, extra)`, `sobre_elipsoide(centro, radios, x, z)`.

### Coordenadas (Blender, 1 unidad = 1 stud)
- El **frente** mira a **-Y**, **arriba** es **+Z**, el **piso** es **Z = 0**: las patas deben tocar Z ≈ 0.
- El lado **izquierdo de la criatura es +X**. Construye las partes `...Izq` con X positiva y usa `espejo=True`.

### Partes y articulaciones
- `Cuerpo` siempre existe y es la raíz. Cada parte necesita al menos una pieza.
- El punto de unión es donde la parte **gira**: base del cuello, raíz del ala (hombro), cadera,
  base de la cola. Si está mal puesto, la animación se ve rota.
- Todas las piezas de una parte deben estar pegadas a esa parte (el ala completa en `AlaIzq`, la espada en la
  parte de la mano/ala que la sostiene, la cresta en `Cabeza`, etc.).
- Cadenas: una cola de serpiente puede ser `Cola1` (padre `Cuerpo`) → `Cola2` (padre `Cola1`) → `Cola3`.
- Partes típicas: `Cabeza`, `AlaIzq/AlaDer`, `PataIzq/PataDer`, `Cola`. Extras opcionales: `Cresta`, `Mandibula`,
  `Bandera`, `Lengua`...
- Límite: cada parte/objeto **< 10 000 triángulos** y la criatura completa **< 25 000** (el generador los imprime).
  Usa `seg`/`anillos` moderados (esferas pequeñas: `seg=8, anillos=6`).

## Animaciones

Los ejes de cada articulación son los mismos que `Motor6D.Transform` en Roblox:
**X = derecha de la criatura, Y = arriba, Z = atrás.** Canales: `rx`, `ry`, `rz` (grados) y `px`, `py`, `pz` (studs).

| canal | positivo significa |
|---|---|
| `rx` | la parte se inclina hacia **atrás** (cabeza mira arriba, pata se va hacia atrás) |
| `ry` | gira hacia la **izquierda** de la criatura |
| `rz` | rueda: el lado **derecho sube**. Ala **izquierda arriba = rz negativo**; ala derecha arriba = rz positivo |
| `py` | sube |

`"Raiz"` mueve todo el `Cuerpo` (y todo lo que cuelga de él) respecto al piso: úsalo para rebotar,
agacharse, inclinarse o saltar.

```python
ANIMACIONES = {
    "Idle":    {"Raiz": [("py", 0.05, 1.5, 0)], "Cabeza": [("rx", 5, 0.8, 0)], "AlaIzq": [("rz", -6, 1.5, 0)]},
    "Caminar": {"PataIzq": [("rx", 30, 2.5, 0)], "PataDer": [("rx", 30, 2.5, 0.5)], ...},
    "clips": {
        "Picotazo": {"duracion": 0.6, "claves": [
            (0.0, {}),
            (0.2, {"Cabeza": {"rx": 25}, "Raiz": {"pz": 0.3}}),        # se prepara (hacia atrás)
            (0.3, {"Cabeza": {"rx": -45, "pz": -0.4}}),                 # golpe
            (0.6, {}),                                                    # termina en reposo
        ]},
        "Derrota": {...},
    },
}
```

- **Ciclos** (`Idle`, `Caminar`, y `Disfrazado` solo para comportamiento `emboscada`): listas de osciladores
  `(canal, amplitud, frecuencia_Hz, fase_0_a_1)` = amplitud·sin(2π(frecuencia·t + fase)). Se repiten siempre.
  `Idle` y `Caminar` son obligatorios.
- **Clips**: poses clave `(tiempo, {parte: {canal: valor}})` con interpolación suave. Se **suman** encima del ciclo.
  Empiezan en `{}` y **terminan en `{}`** (reposo), salvo `Derrota`, que termina en la pose de caída.
- Espejo automático: si animas `AlaIzq` y no `AlaDer`, se crea la del otro lado (ry, rz y px cambian de signo).
  Para patas al caminar escribe las dos con fases opuestas (0 y 0.5).
- Clips especiales: `Derrota` (obligatorio: se cae o se desploma), `Despertar` (comportamiento `emboscada`),
  `Golpeado` (opcional, sacudida corta al recibir daño).
- Cada habilidad usa un clip con `"anim"`. El efecto ocurre a los `retraso` segundos del inicio del clip,
  así que el momento del golpe en el clip debe coincidir con `retraso`.
- Amplitudes razonables: cabeza 5–15° en reposo, alas que aletean 20–60°, patas 25–40° al caminar.
  Nada debe atravesarse de forma fea ni separarse del cuerpo.

## CONFIG

```python
CONFIG = {
    "nombre": "Gallo Ejemplo",        # nombre visible (con acentos)
    "vida": 250, "velocidad": 20,      # velocidad en studs/s (un jugador camina a 16)
    "comportamiento": "normal",        # "normal" | "emboscada" (se queda quieto disfrazado) | "kamikaze"
    "radioDeteccion": 35, "radioPatrulla": 16, "radioPersecucion": 70,
    "reaparecer": 20,                  # segundos para volver a aparecer después de morir (0 = no reaparece)
    "colorUI": ("rgb", 80, 200, 255), # color de la barra de vida
    "habilidades": [ {...}, {...} ],
}
```

Los colores en CONFIG se escriben `("rgb", r, g, b)` con valores 0-255.

### Habilidades disponibles (el sistema de Roblox ya sabe hacerlas)
Campos comunes: `nombre` (se muestra al usarla), `tipo`, `anim` (clip), `rango` (la IA la usa si el objetivo
está a esa distancia o menos), `cooldown` (s), `retraso` (s desde que empieza el clip hasta el efecto), `color`.

| tipo | qué hace | campos propios |
|---|---|---|
| `Golpe` | ataque cuerpo a cuerpo en un cono al frente | `danio`, `alcance`, `angulo` (°), `empuje`, `aturdir` (s) |
| `Embestida` | se lanza hacia adelante y golpea a todo lo que toca | `danio`, `distancia`, `velocidad`, `empuje`, `ancho` |
| `Onda` | onda expansiva alrededor (pisotón, grito, viento) | `danio`, `radio`, `empuje`, `aturdir` |
| `Proyectil` | dispara proyectiles al objetivo | `danio`, `cantidad`, `dispersion` (°), `velocidad`, `forma` (`"bola"`, `"pluma"`, `"hueso"`, `"rayo"`, `"cristal"`), `tamano`, `radioExplosion` (0 = sin explosión) |
| `Cadena` | rayo que salta entre enemigos cercanos | `danio`, `saltos`, `radioSalto` |
| `Escudo` | reduce el daño recibido por un tiempo | `duracion`, `reduccion` (0-1) |
| `Fantasma` | se vuelve transparente, intocable y más rápido | `duracion`, `velocidadExtra` (multiplicador) |
| `Teletransporte` | aparece detrás del objetivo y golpea alrededor | `danio`, `radio` |
| `Invocar` | invoca otras criaturas (por ejemplo `"PollitoBomba"`) | `criatura`, `cantidad`, `maximo` |
| `Explotar` | explota y desaparece (kamikaze) | `danio`, `radio`, `empuje` |

Valores de referencia: daño 8–30 por golpe (un jugador tiene 100 de vida), cooldown 1.5–14 s,
empuje 20–90. Una criatura normal tiene 2–3 habilidades; un jefe 3–4. Incluye al menos un ataque básico de
cooldown corto (`Golpe`) para que siempre tenga algo que hacer de cerca.

## Calidad que se espera
- Diseño **único y épico**, con silueta clara y reconocible a distancia. Estilo low-poly caricatura, sin sangre.
- **No repitas** a las criaturas que ya existen: Gallo Infernal (fuego, cuernos de oro), OsoGallo, Oso Titán,
  Nido Dorado, Abeja Cristal, Abeja Guerrera, Abeja Eclipse, Gallo Guardián (casco de acero),
  Oso Guardián, Pollito Bomba.
- Paleta de 3–4 colores principales + 1–2 de brillo. Detalles: ojos expresivos, cejas, accesorios temáticos.
- Revisa `vista_previa.png` y la hoja de contacto **mirándolas de verdad**: busca piezas flotando, piezas
  que atraviesan mal, patas que no tocan el piso, caras raras, partes que se separan al animar.
  Itera hasta que se vea bien.
