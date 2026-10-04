--[[
	SISTEMA DE CRIATURAS (servidor)

	Instalacion: pon la carpeta "SistemaCriaturas" en ServerScriptService. Despues importa los modelos FBX
	de las criaturas y ponlos en el mapa (Workspace). El sistema los encuentra solo por su nombre
	(o por el atributo "Tipo"), les pone articulaciones, animaciones, barra de vida, IA y habilidades.

	Atributos que puedes poner en el modelo (Propiedades -> Atributos -> +):
	  Modo   (string): "Guardian" (por defecto), "Pelea", "Mascota" o "Estatua".
	  Equipo (string): en modo Pelea, las criaturas del mismo equipo no se atacan.
	  Dueno  (string): en modo Mascota, el nombre del jugador al que sigue.
	Los modelos que pongas en ServerStorage se usan como plantillas (por ejemplo PollitoBomba para el Huevo Mimico).
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local StarterPlayer = game:GetService("StarterPlayer")
local Players = game:GetService("Players")

local carpeta = script.Parent
local modulos = carpeta:WaitForChild("Modulos")

-- Lo compartido (animaciones y configuraciones) va a ReplicatedStorage para que lo lean los clientes.
local compartido = carpeta:FindFirstChild("Compartido")
if compartido then
	local viejo = ReplicatedStorage:FindFirstChild("SistemaCriaturasCompartido")
	if viejo then
		viejo:Destroy()
	end
	compartido.Name = "SistemaCriaturasCompartido"
	compartido.Parent = ReplicatedStorage
else
	compartido = ReplicatedStorage:WaitForChild("SistemaCriaturasCompartido")
end

-- El animador corre en cada jugador.
local animador = carpeta:FindFirstChild("AnimadorCliente")
if animador then
	local scripts = StarterPlayer:WaitForChild("StarterPlayerScripts")
	if not scripts:FindFirstChild("AnimadorCriaturas") then
		local copia = animador:Clone()
		copia.Name = "AnimadorCriaturas"
		copia.Parent = scripts
		-- Los jugadores que ya entraron (por ejemplo al probar en Studio) lo reciben en su PlayerGui.
		for _, jugador in Players:GetPlayers() do
			local gui = jugador:FindFirstChildOfClass("PlayerGui")
			if gui then
				animador:Clone().Parent = gui
			end
		end
	end
end

local Registro = require(modulos.Registro)
local Rig = require(modulos.Rig)
local IA = require(modulos.IA)
local Interfaz = require(modulos.Interfaz)
local Efectos = require(modulos.Efectos)
local Eventos = require(modulos.Eventos)
local Habilidades = require(modulos.Habilidades)

Registro.cargarConfigs(compartido:WaitForChild("Configs"))
Registro.buscarPlantillas()

local activar

local function morir(criatura)
	if not criatura.vivo then
		return
	end
	criatura.vivo = false
	local modelo = criatura.modelo
	-- Al morir el Humanoid deja de sostenerla: se ancla para que no atraviese el piso mientras cae.
	criatura.raiz.Anchored = true
	modelo:SetAttribute("Estado", "Derrotado")
	Interfaz.visible(criatura, false)
	Eventos.CriaturaDerrotada:Fire(modelo, criatura.tipo, modelo:GetAttribute("UltimoAtacante"))
	local color = criatura.config.colorUI or Color3.new(1, 1, 1)
	local espera = if criatura.explotado then 0 else Habilidades.duracionClip(criatura, "Derrota") + 1.2
	task.delay(espera, function()
		if criatura.raiz.Parent then
			Efectos.poof(criatura.raiz.Position, color, criatura.alto)
		end
		Registro.quitar(modelo)
		modelo:Destroy()
	end)
	local segundos = criatura.config.reaparecer or 0
	if segundos > 0 and not criatura.invocado then
		local plantilla = Registro.plantilla(criatura.tipo)
		if plantilla then
			task.delay(espera + segundos, function()
				local nuevo = plantilla:Clone()
				for nombre, valor in criatura.atributosIniciales do
					nuevo:SetAttribute(nombre, valor)
				end
				nuevo:PivotTo(criatura.pivoteInicial)
				nuevo.Parent = criatura.padreInicial and criatura.padreInicial.Parent and criatura.padreInicial or workspace
				activar(nuevo)
				Efectos.poof(criatura.pivoteInicial.Position, color, criatura.alto)
			end)
		end
	end
end

activar = function(modelo: Instance)
	if not modelo:IsA("Model") or Registro.de(modelo) or not modelo:IsDescendantOf(workspace) then
		return
	end
	if modelo:FindFirstChild("HumanoidRootPart") then
		return
	end
	-- Ignora modelos dentro de otra criatura (el importador a veces anida modelos).
	local ancestro = modelo:FindFirstAncestorOfClass("Model")
	while ancestro do
		if Registro.de(ancestro) or Registro.tipoDe(ancestro) then
			return
		end
		ancestro = ancestro:FindFirstAncestorOfClass("Model")
	end
	local tipo = Registro.tipoDe(modelo)
	if not tipo then
		return
	end
	local config = Registro.configs[tipo]
	local atributosIniciales = modelo:GetAttributes()
	local pivoteInicial = modelo:GetPivot()
	local padreInicial = modelo.Parent
	Registro.guardarPlantilla(tipo, modelo)

	local armado = Rig.armar(modelo, tipo, config)
	if not armado then
		return
	end
	local modo = modelo:GetAttribute("Modo") or "Guardian"
	local criatura = {
		modelo = modelo,
		tipo = tipo,
		config = config,
		raiz = armado.raiz,
		cuerpo = armado.cuerpo,
		humanoid = armado.humanoid,
		escala = armado.escala,
		alto = armado.alto,
		partes = armado.partes,
		casa = armado.raiz.CFrame,
		modo = "Guardian",
		vivo = true,
		ocupado = false,
		disfrazado = false,
		regresando = false,
		objetivo = nil,
		cooldowns = {},
		invocados = {},
		invocado = modelo:GetAttribute("Invocado") == true,
		invocador = nil,
		contadorAccion = 0,
		siguientePatrulla = 0,
		ultimoCombate = 0,
		velocidadBase = config.velocidad or 16,
		atributosIniciales = atributosIniciales,
		pivoteInicial = pivoteInicial,
		padreInicial = padreInicial,
	}
	Registro.agregar(criatura)
	Interfaz.crear(criatura)
	IA.cambiarModo(criatura, modo)
	if config.comportamiento == "emboscada" and criatura.modo == "Guardian" then
		IA.disfrazar(criatura, true)
	end
	criatura.humanoid.Died:Connect(function()
		morir(criatura)
	end)
	modelo.AncestryChanged:Connect(function()
		if not modelo:IsDescendantOf(workspace) then
			criatura.vivo = false
			Registro.quitar(modelo)
		end
	end)
	if criatura.invocado then
		-- Las criaturas invocadas desaparecen solas despues de un rato.
		task.delay(45, function()
			if criatura.vivo then
				criatura.humanoid.Health = 0
			end
		end)
	end
	IA.iniciar(criatura)
	Eventos.CriaturaAparecio:Fire(modelo, tipo)
end
Registro.activar = activar

for _, d in workspace:GetDescendants() do
	if d:IsA("Model") then
		activar(d)
	end
end
workspace.DescendantAdded:Connect(function(d)
	if d:IsA("Model") then
		task.defer(activar, d)
	end
end)

local cuantas = 0
for _ in Registro.criaturas do
	cuantas += 1
end
local tipos = {}
for tipo in Registro.configs do
	table.insert(tipos, tipo)
end
table.sort(tipos)
print(`[Criaturas] Sistema listo: {cuantas} criaturas en el mapa. Tipos: {table.concat(tipos, ", ")}`)
