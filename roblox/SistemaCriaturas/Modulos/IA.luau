--[[
	IA: el cerebro de cada criatura. Corre en el servidor unas 7 veces por segundo.

	Atributo "Modo" del modelo (se puede cambiar en cualquier momento):
	  "Guardian" (por defecto): patrulla su zona, persigue a los jugadores que se acercan y vuelve a casa.
	  "Pelea":   pelea contra otras criaturas en modo Pelea (usa el atributo "Equipo" para bandos).
	  "Mascota": sigue al jugador cuyo nombre esta en el atributo "Dueno" (o al mas cercano).
	  "Estatua": se queda quieta, solo con su animacion de reposo.
	Comportamientos especiales (config.comportamiento): "emboscada" (disfrazada hasta que alguien se acerca)
	y "kamikaze" (corre hacia el objetivo y explota).
]]

local Players = game:GetService("Players")

local Habilidades = require(script.Parent.Habilidades)
local Interfaz = require(script.Parent.Interfaz)
local Objetivos = require(script.Parent.Objetivos)

local IA = {}

local TICK = 0.15
local MODOS = { Guardian = true, Pelea = true, Mascota = true, Estatua = true }

local function ahora(): number
	return os.clock()
end

-- Distancia a la que la criatura prefiere quedarse para pelear cuerpo a cuerpo.
local function distanciaCerca(criatura): number
	local mejor = math.huge
	for _, hab in criatura.config.habilidades or {} do
		if hab.tipo == "Golpe" or hab.tipo == "Explotar" then
			mejor = math.min(mejor, (hab.rango or 6) * 0.75)
		end
	end
	if mejor == math.huge then
		mejor = 6
	end
	return mejor * criatura.escala + criatura.alto * 0.2
end

local function elegirHabilidad(criatura, distancia: number)
	local listas = {}
	for _, hab in criatura.config.habilidades or {} do
		local rango = (hab.rango or 8) * criatura.escala + criatura.alto * 0.2
		if (criatura.cooldowns[hab.nombre] or 0) <= ahora() and distancia <= rango then
			table.insert(listas, hab)
		end
	end
	if #listas == 0 then
		return nil
	end
	-- Prefiere las habilidades fuertes (cooldown largo); a veces elige al azar para variar.
	table.sort(listas, function(a, b)
		return (a.cooldown or 0) > (b.cooldown or 0)
	end)
	if #listas > 1 and math.random() < 0.3 then
		return listas[math.random(1, #listas)]
	end
	return listas[1]
end

local function mover(criatura, destino: Vector3)
	criatura.humanoid:MoveTo(destino)
end

local function detener(criatura)
	criatura.humanoid:MoveTo(criatura.raiz.Position)
end

local function posicionCasa(criatura): Vector3
	return criatura.casa.Position
end

function IA.disfrazar(criatura, disfrazado: boolean)
	criatura.disfrazado = disfrazado
	criatura.modelo:SetAttribute("Disfrazado", disfrazado)
	Interfaz.visible(criatura, not disfrazado)
	criatura.humanoid.WalkSpeed = if disfrazado then 0 else criatura.velocidadBase
end

local function despertar(criatura)
	IA.disfrazar(criatura, false)
	criatura.humanoid.WalkSpeed = 0
	Habilidades.animar(criatura, "Despertar")
	task.wait(Habilidades.duracionClip(criatura, "Despertar"))
	if criatura.vivo then
		criatura.humanoid.WalkSpeed = criatura.velocidadBase
	end
end

local function patrullar(criatura)
	local radio = (criatura.config.radioPatrulla or 12) * criatura.escala
	if radio <= 0 then
		return
	end
	if ahora() >= criatura.siguientePatrulla then
		local angulo = math.random() * math.pi * 2
		local d = math.random() * radio
		local casa = posicionCasa(criatura)
		mover(criatura, casa + Vector3.new(math.cos(angulo) * d, 0, math.sin(angulo) * d))
		criatura.siguientePatrulla = ahora() + 3 + math.random() * 4
	end
end

local function pasoCombate(criatura)
	local config = criatura.config
	local esc = criatura.escala
	local casa = posicionCasa(criatura)

	if config.comportamiento == "emboscada" and criatura.disfrazado then
		local intruso = Objetivos.masCercano(criatura, (config.radioDeteccion or 14) * esc)
		if not intruso then
			return
		end
		criatura.objetivo = intruso
		despertar(criatura)
		return
	end

	if criatura.objetivo and not Objetivos.sigueValido(criatura, criatura.objetivo) then
		criatura.objetivo = nil
	end
	if criatura.objetivo and criatura.modo == "Guardian" then
		local lejos = (criatura.objetivo.raiz.Position - casa).Magnitude > (config.radioPersecucion or 70) * esc
		if lejos then
			criatura.objetivo = nil
			criatura.regresando = true
		end
	end
	if not criatura.objetivo and not criatura.regresando then
		criatura.objetivo = Objetivos.masCercano(criatura, (config.radioDeteccion or 35) * esc)
	end

	local objetivo = criatura.objetivo
	if objetivo then
		criatura.regresando = false
		criatura.ultimoCombate = ahora()
		local distancia = Objetivos.distanciaPlana(objetivo.raiz.Position, criatura.raiz.Position)
		local hab = elegirHabilidad(criatura, distancia)
		if hab then
			Habilidades.usar(criatura, hab, objetivo)
			return
		end
		if distancia > distanciaCerca(criatura) then
			mover(criatura, objetivo.raiz.Position)
		else
			detener(criatura)
			Habilidades.mirarA(criatura, objetivo.raiz.Position)
		end
		return
	end

	if criatura.regresando then
		mover(criatura, casa)
		if Objetivos.distanciaPlana(casa, criatura.raiz.Position) < 4 * esc then
			criatura.regresando = false
			criatura.humanoid.Health = criatura.humanoid.MaxHealth
		end
		return
	end

	if config.comportamiento == "emboscada" then
		-- Vuelve a disfrazarse si pasa un rato tranquila cerca de casa.
		if ahora() - criatura.ultimoCombate > 4 then
			if Objetivos.distanciaPlana(casa, criatura.raiz.Position) > 2 * esc then
				mover(criatura, casa)
			else
				detener(criatura)
				IA.disfrazar(criatura, true)
			end
		end
		return
	end
	patrullar(criatura)
end

local function pasoMascota(criatura)
	local dueno = Players:FindFirstChild(criatura.modelo:GetAttribute("Dueno") or "")
	local personaje
	if dueno and dueno:IsA("Player") then
		personaje = dueno.Character
	else
		-- Sin dueno: sigue al jugador mas cercano.
		local mejor = math.huge
		for _, jugador in Players:GetPlayers() do
			local raiz = jugador.Character and jugador.Character:FindFirstChild("HumanoidRootPart")
			if raiz then
				local d = (raiz.Position - criatura.raiz.Position).Magnitude
				if d < mejor then
					mejor, personaje = d, jugador.Character
				end
			end
		end
	end
	local raiz = personaje and personaje:FindFirstChild("HumanoidRootPart")
	if not raiz then
		return
	end
	local d = Objetivos.distanciaPlana(raiz.Position, criatura.raiz.Position)
	local cerca = 6 * criatura.escala + criatura.alto * 0.3
	if d > 80 then
		-- Muy lejos: aparece junto al dueno.
		local destino = raiz.Position - raiz.CFrame.LookVector * cerca
		criatura.modelo:PivotTo(CFrame.lookAt(destino, raiz.Position))
	elseif d > cerca then
		criatura.humanoid.WalkSpeed = if d > 25 then criatura.velocidadBase * 1.6 else criatura.velocidadBase
		mover(criatura, raiz.Position - (raiz.Position - criatura.raiz.Position).Unit * cerca * 0.8)
	else
		detener(criatura)
	end
end

function IA.cambiarModo(criatura, modo: string)
	if not MODOS[modo] then
		warn(`[Criaturas] Modo desconocido "{modo}" en {criatura.modelo.Name}; se usa Guardian.`)
		modo = "Guardian"
	end
	criatura.modo = modo
	criatura.objetivo = nil
	criatura.regresando = false
	if criatura.disfrazado and modo ~= "Guardian" then
		IA.disfrazar(criatura, false)
	end
	criatura.humanoid.WalkSpeed = if modo == "Estatua" then 0 else criatura.velocidadBase
	if modo == "Estatua" then
		detener(criatura)
	end
end

function IA.iniciar(criatura)
	criatura.modelo:GetAttributeChangedSignal("Modo"):Connect(function()
		IA.cambiarModo(criatura, criatura.modelo:GetAttribute("Modo") or "Guardian")
	end)
	task.spawn(function()
		while criatura.vivo and criatura.modelo.Parent do
			if not criatura.ocupado then
				local ok, err = pcall(function()
					if criatura.modo == "Mascota" then
						pasoMascota(criatura)
					elseif criatura.modo == "Guardian" or criatura.modo == "Pelea" then
						pasoCombate(criatura)
					end
				end)
				if not ok then
					warn(`[Criaturas] Error en la IA de {criatura.modelo.Name}: {err}`)
					task.wait(1)
				end
			end
			task.wait(TICK)
		end
	end)
end

return IA
