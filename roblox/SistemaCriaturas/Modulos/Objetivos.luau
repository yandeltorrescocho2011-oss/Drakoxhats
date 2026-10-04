--[[
	Objetivos: a quien puede atacar cada criatura, dano, empuje y aturdimiento.

	Modos (atributo "Modo" del modelo):
	  Guardian -> ataca a los jugadores que se acercan.
	  Pelea    -> pelea contra otras criaturas en modo Pelea (de otro "Equipo" si se usa ese atributo).
	  Mascota / Estatua -> no ataca.
]]

local Players = game:GetService("Players")

local Registro = require(script.Parent.Registro)

local Objetivos = {}

export type Objetivo = {
	modelo: Model,
	humanoid: Humanoid,
	raiz: BasePart,
	esJugador: boolean,
}

local function entradaDePersonaje(personaje: Model?): Objetivo?
	if not personaje then
		return nil
	end
	local humanoid = personaje:FindFirstChildOfClass("Humanoid")
	local raiz = personaje:FindFirstChild("HumanoidRootPart")
	if humanoid and raiz and raiz:IsA("BasePart") and humanoid.Health > 0 then
		return { modelo = personaje, humanoid = humanoid, raiz = raiz, esJugador = true }
	end
	return nil
end

local function entradaDeCriatura(c): Objetivo?
	if c and c.vivo and c.humanoid.Health > 0 and c.raiz.Parent then
		return { modelo = c.modelo, humanoid = c.humanoid, raiz = c.raiz, esJugador = false }
	end
	return nil
end

local function sonEnemigas(a, b): boolean
	if a == b then
		return false
	end
	if a.invocador == b or b.invocador == a then
		return false
	end
	local ea, eb = a.modelo:GetAttribute("Equipo"), b.modelo:GetAttribute("Equipo")
	if ea ~= nil and ea ~= "" and ea == eb then
		return false
	end
	return true
end

-- Lista de objetivos validos para una criatura segun su modo.
function Objetivos.validos(criatura): { Objetivo }
	local lista = {}
	local modo = criatura.modo
	if modo == "Guardian" then
		for _, jugador in Players:GetPlayers() do
			local e = entradaDePersonaje(jugador.Character)
			if e then
				table.insert(lista, e)
			end
		end
	elseif modo == "Pelea" then
		for _, otra in Registro.criaturas do
			if otra.modo == "Pelea" and sonEnemigas(criatura, otra) and not otra.modelo:GetAttribute("Intocable") then
				local e = entradaDeCriatura(otra)
				if e then
					table.insert(lista, e)
				end
			end
		end
	end
	return lista
end

function Objetivos.sigueValido(criatura, objetivo: Objetivo?): boolean
	if not objetivo then
		return false
	end
	if not objetivo.modelo.Parent or not objetivo.raiz.Parent or objetivo.humanoid.Health <= 0 then
		return false
	end
	if objetivo.esJugador then
		return criatura.modo == "Guardian" and Players:GetPlayerFromCharacter(objetivo.modelo) ~= nil
	end
	local otra = Registro.de(objetivo.modelo)
	return criatura.modo == "Pelea" and otra ~= nil and otra.vivo and otra.modo == "Pelea"
		and not objetivo.modelo:GetAttribute("Intocable")
end

local function distanciaPlana(a: Vector3, b: Vector3): number
	return Vector3.new(a.X - b.X, 0, a.Z - b.Z).Magnitude
end
Objetivos.distanciaPlana = distanciaPlana

function Objetivos.masCercano(criatura, radio: number, desde: Vector3?): Objetivo?
	local origen = desde or criatura.raiz.Position
	local mejor, mejorDist = nil, radio
	for _, e in Objetivos.validos(criatura) do
		local d = (e.raiz.Position - origen).Magnitude
		if d <= mejorDist then
			mejor, mejorDist = e, d
		end
	end
	return mejor
end

function Objetivos.enRadio(criatura, centro: Vector3, radio: number): { Objetivo }
	local lista = {}
	for _, e in Objetivos.validos(criatura) do
		if (e.raiz.Position - centro).Magnitude <= radio then
			table.insert(lista, e)
		end
	end
	return lista
end

-- Aplica dano respetando escudos (atributo "Reduccion") y forma fantasma (atributo "Intocable").
function Objetivos.danar(criatura, objetivo: Objetivo, cantidad: number)
	if objetivo.humanoid.Health <= 0 or objetivo.modelo:GetAttribute("Intocable") then
		return
	end
	local reduccion = objetivo.modelo:GetAttribute("Reduccion")
	if type(reduccion) == "number" then
		cantidad *= math.clamp(1 - reduccion, 0, 1)
	end
	objetivo.humanoid:TakeDamage(cantidad)
	if not objetivo.esJugador then
		objetivo.modelo:SetAttribute("Golpe", (objetivo.modelo:GetAttribute("Golpe") or 0) + 1)
		local otra = Registro.de(objetivo.modelo)
		if otra and otra.vivo and not otra.objetivo then
			-- La criatura golpeada responde al ataque.
			local atacante = { modelo = criatura.modelo, humanoid = criatura.humanoid, raiz = criatura.raiz, esJugador = false }
			otra.objetivo = atacante
		end
	end
	if criatura.modelo then
		objetivo.modelo:SetAttribute("UltimoAtacante", criatura.modelo.Name)
	end
end

-- Empuja al objetivo (funciona con jugadores porque la fuerza la simula su propio cliente).
function Objetivos.empujar(objetivo: Objetivo, direccion: Vector3, fuerza: number)
	if fuerza <= 0 or objetivo.humanoid.Health <= 0 then
		return
	end
	local plano = Vector3.new(direccion.X, 0, direccion.Z)
	if plano.Magnitude < 1e-3 then
		plano = Vector3.new(0, 0, 1)
	end
	local velocidad = plano.Unit * fuerza + Vector3.new(0, fuerza * 0.4, 0)
	local adjunto = Instance.new("Attachment")
	adjunto.Name = "EmpujeCriatura"
	adjunto.Parent = objetivo.raiz
	local lv = Instance.new("LinearVelocity")
	lv.Attachment0 = adjunto
	lv.VelocityConstraintMode = Enum.VelocityConstraintMode.Vector
	lv.VectorVelocity = velocidad
	lv.MaxForce = 1e6
	lv.RelativeTo = Enum.ActuatorRelativeTo.World
	lv.Parent = adjunto
	task.delay(0.18, function()
		adjunto:Destroy()
	end)
end

-- Deja quieto al objetivo unos segundos.
function Objetivos.aturdir(objetivo: Objetivo, segundos: number)
	if segundos <= 0 then
		return
	end
	local h = objetivo.humanoid
	local hasta = os.clock() + segundos
	local actual = h:GetAttribute("AturdidoHasta")
	if type(actual) ~= "number" or actual < os.clock() then
		h:SetAttribute("VelocidadAntesDeAturdir", h.WalkSpeed)
	end
	h:SetAttribute("AturdidoHasta", math.max(hasta, if type(actual) == "number" then actual else 0))
	h.WalkSpeed = 0
	task.delay(segundos, function()
		local limite = h:GetAttribute("AturdidoHasta")
		if h.Parent and type(limite) == "number" and os.clock() >= limite - 0.01 then
			local antes = h:GetAttribute("VelocidadAntesDeAturdir")
			h.WalkSpeed = if type(antes) == "number" then antes else 16
			h:SetAttribute("AturdidoHasta", nil)
			h:SetAttribute("VelocidadAntesDeAturdir", nil)
		end
	end)
end

return Objetivos
