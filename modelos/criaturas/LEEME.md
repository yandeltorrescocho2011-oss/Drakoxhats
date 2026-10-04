# Criaturas animadas con habilidades

![Poster](poster.png)

Estas criaturas **se mueven, caminan, atacan con habilidades, tienen barra de vida y piensan solas**.
Cada carpeta tiene el modelo (`.fbx`), su imagen (`vista_previa.png`) y un GIF con sus animaciones (`animacion.gif`).

<!-- TABLA_CRIATURAS -->

## Instalación (una sola vez)

1. **El sistema.** Descarga [`roblox/SistemaCriaturas.rbxmx`](../../roblox/SistemaCriaturas.rbxmx).
   En Roblox Studio, en el **Explorer**, haz clic derecho en **ServerScriptService** →
   **Insertar desde archivo…** (*Insert from File…*) y elige ese archivo.
   Debe quedar una carpeta `SistemaCriaturas` dentro de `ServerScriptService`.
2. **Las criaturas.** Importa el `.fbx` de cada criatura con **Importar 3D** (igual que antes) y déjala en el mapa.
   - **No le cambies el nombre** al modelo (por ejemplo debe llamarse `GalloSamurai`). Si haces copias,
     `GalloSamurai2` o `GalloSamurai (1)` también funcionan.
   - **No borres ni renombres sus piezas** (`Cuerpo`, `Cabeza`, `AlaIzq`, `_Frente`, `_Arriba`...).
     Las piezas `_Frente` y `_Arriba` son unos cubitos que le dicen al sistema hacia dónde mira la criatura;
     el sistema las borra solo al empezar.
   - Ya **no** hace falta ponerles Neon, transparencia ni colores: el sistema lo hace solo.
3. **El Huevo Mímico invoca Pollitos Bomba**: importa también `PollitoBomba.fbx` y pon una copia en
   **ServerStorage** (así el huevo tiene de dónde sacar pollitos aunque no haya ninguno en el mapa).
4. Dale a **Jugar** (F5). En la ventana **Output** debe salir: `[Criaturas] Sistema listo: ...`

## Modos

Cada criatura tiene un **modo**. Para cambiarlo: selecciona el modelo → **Propiedades** → abajo en
**Atributos** haz clic en **+** → Nombre `Modo`, Tipo **string**, y escribe el valor.

| Modo | Qué hace |
|---|---|
| `Guardian` (si no pones nada) | Patrulla su zona, persigue y ataca a los jugadores que se acercan y vuelve a su lugar. |
| `Pelea` | Pelea contra las otras criaturas que estén en modo `Pelea`. ¡Ideal para la arena del palenque! |
| `Mascota` | Sigue al jugador cuyo nombre pongas en el atributo `Dueno` (o al más cercano). No ataca. |
| `Estatua` | Se queda en su lugar moviéndose un poquito (para decorar, tiendas, menús). |

Otros atributos:
- `Equipo` (string): en modo `Pelea`, las criaturas del mismo equipo no se atacan entre ellas.
- `Dueno` (string): en modo `Mascota`, el nombre del jugador al que sigue.

**Pelea en la arena:** pon dos gallos dentro de la arena, a los dos ponles `Modo = Pelea`, y a uno
`Equipo = Rojo` y al otro `Equipo = Azul`. Al darle a Jugar pelean con todas sus habilidades.

## Cambiar vida, velocidad o daño

En el Explorer abre `ServerScriptService → SistemaCriaturas → Compartido → Configs` y abre el de la criatura.
Ahí puedes cambiar `vida`, `velocidad`, `reaparecer` (segundos para volver a aparecer) y en `habilidades`
el `danio`, `cooldown`, `rango`, etc. No cambies la parte `rig` ni `animaciones`.

## Para programar (opcional)

```lua
-- En un Script del servidor:
local Criaturas = require(game.ServerScriptService.SistemaCriaturas.API)

-- Hacer aparecer una criatura (su modelo debe estar en ServerStorage o en el mapa):
local gallo = Criaturas.aparecer("GalloSamurai", CFrame.new(0, 5, 0), { Modo = "Pelea", Equipo = "Rojo" })

-- Saber cuándo derrotan a una criatura (por ejemplo para dar monedas):
local eventos = game.ServerStorage:WaitForChild("EventosCriaturas")
eventos.CriaturaDerrotada.Event:Connect(function(modelo, tipo, ultimoAtacante)
	print(tipo .. " fue derrotada")
end)
```

## Si algo no funciona

- **No se mueve:** revisa la ventana **Output**. Los mensajes del sistema empiezan con `[Criaturas]`.
  Lo más común es que el modelo tenga otro nombre o que falte la pieza `Cuerpo`.
- **Mira hacia atrás o está acostada:** no pasa nada, el sistema usa las piezas `_Frente` y `_Arriba` para
  orientarla. No las borres antes de darle a Jugar.
- **Es muy grande o muy chica:** cambia la escala en el importador; el sistema se ajusta solo.
- **El Huevo Mímico no invoca pollitos:** falta el `PollitoBomba` en ServerStorage (paso 3).

## Para crear más criaturas

Las criaturas se hacen con código en `herramientas/criaturas/` (Blender desde Python). Lee
[`herramientas/criaturas/GUIA.md`](../../herramientas/criaturas/GUIA.md). Después de generar, vuelve a
construir el sistema con `lune run roblox/construir.luau` para que incluya la configuración nueva.
