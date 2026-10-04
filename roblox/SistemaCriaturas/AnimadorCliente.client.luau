--[[
	ANIMADOR DE CRIATURAS (cliente)
	Mueve las articulaciones (Motor6D.Transform) de cada criatura cerca de la camara, en cada cuadro.
	Es suave y no gasta red: el servidor solo avisa que accion hacer con atributos del modelo:
	  "Accion" = "NombreDelClip#numero", "Estado" = "Vivo"/"Derrotado", "Disfrazado", "Golpe".
]]

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local compartido = ReplicatedStorage:WaitForChild("SistemaCriaturasCompartido")
local Animacion = require(compartido:WaitForChild("Animacion"))
local carpetaConfigs = compartido:WaitForChild("Configs")

local DISTANCIA_MAXIMA = 220

local configs = {}
local activas = {}

local function configDe(tipo: string?)
	if not tipo then
		return nil
	end
	if configs[tipo] == nil then
		local modulo = carpetaConfigs:FindFirstChild(tipo)
		local ok, config = false, nil
		if modulo then
			ok, config = pcall(require, modulo)
		end
		configs[tipo] = if ok then config else false
	end
	return configs[tipo] or nil
end

local function buscarMotores(estado)
	local modelo = estado.modelo
	local motores = {}
	local function motorDe(nombreParte: string)
		local parte = modelo:FindFirstChild(nombreParte, true)
		local m = parte and parte:FindFirstChild("Articulacion")
		if m and m:IsA("Motor6D") then
			return m
		end
		return nil
	end
	motores.Raiz = motorDe("Cuerpo")
	for nombre in estado.config.rig.partes do
		motores[nombre] = motorDe(nombre)
	end
	estado.motores = motores
	estado.raiz = modelo:FindFirstChild("HumanoidRootPart")
	estado.humanoid = modelo:FindFirstChildOfClass("Humanoid")
	estado.ultimaBusqueda = os.clock()
end

local function iniciarClip(estado, nombre: string?, ranura: string)
	local clips = estado.config.animaciones.clips
	local clip = nombre and clips[nombre]
	if clip then
		estado[ranura] = { clip = clip, t = 0, nombre = nombre }
	end
end

local function registrar(modelo: Instance)
	if activas[modelo] or not modelo:IsA("Model") then
		return
	end
	local config = configDe(modelo:GetAttribute("Tipo"))
	if not config then
		return
	end
	local estado = {
		modelo = modelo,
		config = config,
		t = math.random() * 10, -- para que no se muevan todas igual
		pesoCaminar = 0,
		pesoVida = 1,
		principal = nil,
		golpe = nil,
		conexiones = {},
	}
	buscarMotores(estado)
	table.insert(estado.conexiones, modelo:GetAttributeChangedSignal("Accion"):Connect(function()
		local accion = modelo:GetAttribute("Accion")
		if type(accion) == "string" then
			iniciarClip(estado, string.match(accion, "^(.-)#") or accion, "principal")
		end
	end))
	table.insert(estado.conexiones, modelo:GetAttributeChangedSignal("Golpe"):Connect(function()
		if not (estado.principal and estado.principal.clip) then
			iniciarClip(estado, "Golpeado", "golpe")
		end
	end))
	table.insert(estado.conexiones, modelo:GetAttributeChangedSignal("Estado"):Connect(function()
		if modelo:GetAttribute("Estado") == "Derrotado" then
			iniciarClip(estado, "Derrota", "principal")
		end
	end))
	if modelo:GetAttribute("Estado") == "Derrotado" then
		iniciarClip(estado, "Derrota", "principal")
	end
	activas[modelo] = estado
end

local function quitar(modelo: Instance)
	local estado = activas[modelo]
	if estado then
		for _, c in estado.conexiones do
			c:Disconnect()
		end
		activas[modelo] = nil
	end
end

for _, modelo in CollectionService:GetTagged("Criatura") do
	task.spawn(registrar, modelo)
end
CollectionService:GetInstanceAddedSignal("Criatura"):Connect(registrar)
CollectionService:GetInstanceRemovedSignal("Criatura"):Connect(quitar)

local function avanzarClip(ranura, dt: number, pose, mantener: boolean)
	if not ranura then
		return nil
	end
	ranura.t += dt
	Animacion.evaluarClip(ranura.clip, math.min(ranura.t, ranura.clip.duracion), pose, 1)
	if ranura.t >= ranura.clip.duracion and not mantener then
		return nil
	end
	return ranura
end

local evento = RunService.PreSimulation or RunService.Stepped
evento:Connect(function(a, b)
	local dt = if typeof(a) == "number" and typeof(b) == "number" then b else a
	local camara = workspace.CurrentCamera
	local posCamara = camara and camara.CFrame.Position
	for modelo, estado in activas do
		if not modelo.Parent then
			quitar(modelo)
			continue
		end
		-- Con StreamingEnabled las partes pueden llegar tarde: se vuelven a buscar cada segundo.
		if (not estado.raiz or not estado.motores.Raiz) and os.clock() - estado.ultimaBusqueda > 1 then
			buscarMotores(estado)
		end
		local raiz = estado.raiz
		if not raiz or not raiz.Parent then
			continue
		end
		if posCamara and (raiz.Position - posCamara).Magnitude > DISTANCIA_MAXIMA then
			continue
		end

		local derrotado = modelo:GetAttribute("Estado") == "Derrotado"
		local ciclos = estado.config.animaciones.ciclos
		estado.t += dt
		local velocidad = raiz.AssemblyLinearVelocity
		local plana = Vector3.new(velocidad.X, 0, velocidad.Z).Magnitude
		local caminar = if derrotado then 0 else math.clamp(plana / 6, 0, 1)
		estado.pesoCaminar += (caminar - estado.pesoCaminar) * math.min(1, dt * 8)
		estado.pesoVida += ((if derrotado then 0 else 1) - estado.pesoVida) * math.min(1, dt * 6)

		local pose = {}
		local reposo = if modelo:GetAttribute("Disfrazado") and ciclos.Disfrazado then ciclos.Disfrazado else ciclos.Idle
		Animacion.evaluarCiclo(reposo, estado.t, pose, (1 - estado.pesoCaminar) * estado.pesoVida)
		Animacion.evaluarCiclo(ciclos.Caminar, estado.t, pose, estado.pesoCaminar * estado.pesoVida)
		estado.principal = avanzarClip(estado.principal, dt, pose, derrotado)
		estado.golpe = avanzarClip(estado.golpe, dt, pose, false)

		local escala = modelo:GetAttribute("Escala") or 1
		for nombre, motor in estado.motores do
			local canales = pose[nombre]
			motor.Transform = if canales then Animacion.aCFrame(canales, escala) else CFrame.identity
		end
	end
end)
