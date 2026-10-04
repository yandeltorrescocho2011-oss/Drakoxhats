--[[
	Habilidades: los 10 tipos que pueden usar las criaturas (Golpe, Embestida, Onda, Proyectil, Cadena,
	Escudo, Fantasma, Teletransporte, Invocar, Explotar). Los valores vienen de la configuracion de cada criatura.
]]

local RunService = game:GetService("RunService")

local Efectos = require(script.Parent.Efectos)
local Objetivos = require(script.Parent.Objetivos)
local Registro = require(script.Parent.Registro)

local Habilidades = {}

local BLANCO = Color3.new(1, 1, 1)

local function colorDe(hab, criatura): Color3
	return hab.color or criatura.config.colorUI or BLANCO
end

local function plano(v: Vector3): Vector3
	local p = Vector3.new(v.X, 0, v.Z)
	return if p.Magnitude > 1e-3 then p.Unit else Vector3.new(0, 0, -1)
end

-- Gira la criatura hacia una posicion (solo en horizontal).
function Habilidades.mirarA(criatura, posicion: Vector3)
	local r = criatura.raiz
	local destino = Vector3.new(posicion.X, r.Position.Y, posicion.Z)
	if (destino - r.Position).Magnitude > 0.1 then
		r.CFrame = CFrame.lookAt(r.Position, destino)
	end
end

-- Punto desde donde salen proyectiles y rayos (la cabeza si existe).
local function boca(criatura): Vector3
	local cabeza = criatura.partes.Cabeza
	if cabeza then
		return cabeza.Position + criatura.raiz.CFrame.LookVector * (criatura.alto * 0.1)
	end
	return criatura.raiz.Position + criatura.raiz.CFrame.LookVector * criatura.alto * 0.3
end

-- Golpe: cono al frente.
local function golpe(criatura, hab)
	local esc = criatura.escala
	local alcance = (hab.alcance or 6) * esc
	local angulo = hab.angulo or 100
	local r = criatura.raiz
	local base = CFrame.lookAt(r.Position, r.Position + r.CFrame.LookVector)
	Efectos.arco(base, alcance, angulo, colorDe(hab, criatura))
	Efectos.sonido("golpe", r)
	local coseno = math.cos(math.rad(angulo / 2))
	for _, e in Objetivos.enRadio(criatura, r.Position, alcance + 1.5) do
		local hacia = e.raiz.Position - r.Position
		if plano(hacia):Dot(plano(r.CFrame.LookVector)) >= coseno or Objetivos.distanciaPlana(e.raiz.Position, r.Position) < 2.5 then
			Objetivos.danar(criatura, e, hab.danio or 10)
			Objetivos.empujar(e, hacia, hab.empuje or 25)
			Objetivos.aturdir(e, hab.aturdir or 0)
		end
	end
end

-- Embestida: corre en linea recta golpeando a todo lo que toca.
local function embestida(criatura, hab, objetivo)
	local esc = criatura.escala
	local r = criatura.raiz
	local direccion = plano((if objetivo then objetivo.raiz.Position else r.Position + r.CFrame.LookVector) - r.Position)
	Habilidades.mirarA(criatura, r.Position + direccion)
	local velocidad = (hab.velocidad or 70) * esc
	local duracion = ((hab.distancia or 20) * esc) / velocidad
	local ancho = (hab.ancho or 4) * esc
	local color = colorDe(hab, criatura)
	local quitarEstela = Efectos.estela(r, criatura.alto, color)
	Efectos.sonido("embestida", r)
	local adjunto = Instance.new("Attachment")
	adjunto.Parent = r
	local lv = Instance.new("LinearVelocity")
	lv.Attachment0 = adjunto
	lv.VelocityConstraintMode = Enum.VelocityConstraintMode.Plane
	lv.PrimaryTangentAxis = Vector3.xAxis
	lv.SecondaryTangentAxis = Vector3.zAxis
	lv.PlaneVelocity = Vector2.new(direccion.X, direccion.Z) * velocidad
	lv.MaxForce = 1e6
	lv.RelativeTo = Enum.ActuatorRelativeTo.World
	lv.Parent = adjunto
	local golpeados = {}
	local inicio = os.clock()
	while os.clock() - inicio < duracion and criatura.vivo do
		for _, e in Objetivos.enRadio(criatura, r.Position, ancho) do
			if not golpeados[e.modelo] then
				golpeados[e.modelo] = true
				Objetivos.danar(criatura, e, hab.danio or 15)
				Objetivos.empujar(e, e.raiz.Position - r.Position + direccion * 2, hab.empuje or 40)
				Efectos.poof(e.raiz.Position, color, 2)
			end
		end
		RunService.Heartbeat:Wait()
	end
	adjunto:Destroy()
	r.AssemblyLinearVelocity = Vector3.zero
	quitarEstela()
end

-- Onda: golpe en area alrededor de la criatura.
local function onda(criatura, hab)
	local esc = criatura.escala
	local radio = (hab.radio or 10) * esc
	local r = criatura.raiz
	local piso = r.Position - Vector3.new(0, criatura.alto * 0.5 - 0.2, 0)
	Efectos.anillo(piso, radio, colorDe(hab, criatura))
	Efectos.sonido("onda", r, 0.8)
	for _, e in Objetivos.enRadio(criatura, r.Position, radio) do
		Objetivos.danar(criatura, e, hab.danio or 15)
		Objetivos.empujar(e, e.raiz.Position - r.Position, hab.empuje or 40)
		Objetivos.aturdir(e, hab.aturdir or 0)
	end
end

-- Proyectil: uno o varios disparos hacia el objetivo.
local function proyectil(criatura, hab, objetivo)
	local esc = criatura.escala
	local cantidad = hab.cantidad or 1
	local dispersion = hab.dispersion or 0
	local velocidad = (hab.velocidad or 60) * esc
	local tamano = (hab.tamano or 1) * esc
	local alcanceMax = (hab.alcanceMax or (hab.rango or 30) * 1.6) * esc
	local radioExplosion = (hab.radioExplosion or 0) * esc
	local color = colorDe(hab, criatura)
	local origen = boca(criatura)
	local destino = if objetivo then objetivo.raiz.Position else origen + criatura.raiz.CFrame.LookVector * 20
	local base = (destino - origen)
	base = if base.Magnitude > 1e-3 then base.Unit else criatura.raiz.CFrame.LookVector
	Efectos.sonido("disparo", criatura.raiz, 0.5)

	local parametros = RaycastParams.new()
	parametros.FilterType = Enum.RaycastFilterType.Exclude
	parametros.FilterDescendantsInstances = { criatura.modelo, workspace:FindFirstChild("EfectosCriaturas") }

	for i = 1, cantidad do
		local angulo = if cantidad > 1 then -dispersion / 2 + dispersion * (i - 1) / (cantidad - 1) else 0
		local dir = (CFrame.fromAxisAngle(Vector3.yAxis, math.rad(angulo)) * base)
		local bala = Efectos.proyectil(hab.forma or "bola", color, tamano)
		local pos = origen
		bala.CFrame = CFrame.lookAt(pos, pos + dir)
		task.spawn(function()
			local recorrido = 0
			local giro = 0
			while recorrido < alcanceMax and bala.Parent do
				local dt = RunService.Heartbeat:Wait()
				local paso = dir * velocidad * dt
				local impacto = workspace:Raycast(pos, paso, parametros)
				local siguiente = if impacto then impacto.Position else pos + paso
				giro += dt * 12
				bala.CFrame = CFrame.lookAt(siguiente, siguiente + dir) * (if hab.forma == "hueso" then CFrame.Angles(0, 0, giro) else CFrame.identity)
				recorrido += (siguiente - pos).Magnitude
				pos = siguiente
				local tocado = nil
				for _, e in Objetivos.validos(criatura) do
					if (e.raiz.Position - pos).Magnitude < 2.5 * tamano + 1 then
						tocado = e
						break
					end
				end
				if tocado or impacto then
					if radioExplosion > 0 then
						Efectos.explosion(pos, radioExplosion, color)
						for _, e in Objetivos.enRadio(criatura, pos, radioExplosion) do
							Objetivos.danar(criatura, e, hab.danio or 10)
							Objetivos.empujar(e, e.raiz.Position - pos, hab.empuje or 30)
						end
					elseif tocado then
						Objetivos.danar(criatura, tocado, hab.danio or 10)
						Objetivos.empujar(tocado, dir, hab.empuje or 15)
						Efectos.poof(pos, color, 1.5)
					else
						Efectos.poof(pos, color, 1)
					end
					break
				end
			end
			bala:Destroy()
		end)
		task.wait(0.06)
	end
end

-- Cadena: rayo que salta entre enemigos.
local function cadena(criatura, hab, objetivo)
	local esc = criatura.escala
	local color = colorDe(hab, criatura)
	local radioSalto = (hab.radioSalto or 15) * esc
	local danio = hab.danio or 15
	local golpeados = {}
	local desde = boca(criatura)
	local actual = objetivo
	Efectos.sonido("rayo", criatura.raiz, 0.8)
	for _ = 0, (hab.saltos or 2) do
		if not actual or not Objetivos.sigueValido(criatura, actual) then
			break
		end
		golpeados[actual.modelo] = true
		Efectos.rayo(desde, actual.raiz.Position, color)
		Objetivos.danar(criatura, actual, danio)
		Objetivos.aturdir(actual, 0.3)
		desde = actual.raiz.Position
		danio *= 0.8
		local siguiente, mejor = nil, radioSalto
		for _, e in Objetivos.validos(criatura) do
			local d = (e.raiz.Position - desde).Magnitude
			if not golpeados[e.modelo] and d <= mejor then
				siguiente, mejor = e, d
			end
		end
		actual = siguiente
		task.wait(0.08)
	end
end

-- Escudo: reduce el dano un tiempo (no bloquea a la criatura).
local function escudo(criatura, hab)
	local modelo = criatura.modelo
	modelo:SetAttribute("Reduccion", hab.reduccion or 0.6)
	Efectos.sonido("escudo", criatura.raiz)
	local quitar = Efectos.escudo(criatura.raiz, criatura.alto * 1.25, colorDe(hab, criatura))
	task.delay(hab.duracion or 3, function()
		quitar()
		if modelo.Parent then
			modelo:SetAttribute("Reduccion", nil)
		end
	end)
end

-- Fantasma: transparente, intocable y mas rapida por un tiempo.
local function fantasma(criatura, hab)
	local modelo = criatura.modelo
	local originales = {}
	for _, d in modelo:GetDescendants() do
		if d:IsA("BasePart") and d ~= criatura.raiz then
			originales[d] = d.Transparency
			d.Transparency = 0.5 + d.Transparency * 0.5
		end
	end
	modelo:SetAttribute("Intocable", true)
	local velocidadBase = criatura.velocidadBase
	criatura.humanoid.WalkSpeed = velocidadBase * (hab.velocidadExtra or 1.5)
	Efectos.poof(criatura.raiz.Position, colorDe(hab, criatura), criatura.alto)
	task.delay(hab.duracion or 3, function()
		for parte, t in originales do
			if parte.Parent then
				parte.Transparency = t
			end
		end
		if modelo.Parent then
			modelo:SetAttribute("Intocable", nil)
			if criatura.vivo then
				criatura.humanoid.WalkSpeed = velocidadBase
				Efectos.poof(criatura.raiz.Position, colorDe(hab, criatura), criatura.alto)
			end
		end
	end)
end

-- Teletransporte: aparece detras del objetivo y golpea alrededor.
local function teletransporte(criatura, hab, objetivo)
	if not objetivo then
		return
	end
	local esc = criatura.escala
	local color = colorDe(hab, criatura)
	local r = criatura.raiz
	Efectos.poof(r.Position, color, criatura.alto)
	local atras = objetivo.raiz.CFrame.LookVector * -((hab.distanciaDetras or 4) * esc + criatura.alto * 0.3)
	local destino = Vector3.new(objetivo.raiz.Position.X + atras.X, r.Position.Y, objetivo.raiz.Position.Z + atras.Z)
	criatura.modelo:PivotTo(CFrame.lookAt(destino, Vector3.new(objetivo.raiz.Position.X, destino.Y, objetivo.raiz.Position.Z)))
	Efectos.sonido("aparecer", r)
	Efectos.poof(destino, color, criatura.alto)
	local radio = (hab.radio or 8) * esc
	Efectos.anillo(destino - Vector3.new(0, criatura.alto * 0.5 - 0.2, 0), radio, color)
	for _, e in Objetivos.enRadio(criatura, destino, radio) do
		Objetivos.danar(criatura, e, hab.danio or 10)
		Objetivos.empujar(e, e.raiz.Position - destino, hab.empuje or 30)
	end
end

-- Invocar: hace aparecer otras criaturas (necesita la plantilla en ServerStorage o en el mapa).
local function invocar(criatura, hab)
	local tipo = hab.criatura
	local plantilla = tipo and Registro.plantilla(tipo)
	if not plantilla then
		warn(`[Criaturas] {criatura.tipo} quiere invocar "{tipo}" pero no hay ningun modelo {tipo} en el mapa ni en ServerStorage.`)
		return
	end
	local vivos = 0
	for modelo in criatura.invocados do
		if modelo.Parent and Registro.de(modelo) and Registro.de(modelo).vivo then
			vivos += 1
		else
			criatura.invocados[modelo] = nil
		end
	end
	local cuantos = math.min(hab.cantidad or 1, (hab.maximo or 4) - vivos)
	local r = criatura.raiz
	for i = 1, cuantos do
		local angulo = math.rad(-50 + 100 * (if cuantos > 1 then (i - 1) / (cuantos - 1) else 0.5))
		local dir = CFrame.fromAxisAngle(Vector3.yAxis, angulo) * plano(r.CFrame.LookVector)
		local posicion = r.Position + dir * (criatura.alto * 0.6 + 2)
		local nuevo = plantilla:Clone()
		nuevo:SetAttribute("Modo", criatura.modo)
		nuevo:SetAttribute("Invocado", true)
		local equipo = criatura.modelo:GetAttribute("Equipo")
		if equipo then
			nuevo:SetAttribute("Equipo", equipo)
		end
		local _, tamano = nuevo:GetBoundingBox()
		local piso = r.Position.Y - criatura.alto * 0.5
		nuevo:PivotTo(CFrame.lookAt(Vector3.new(posicion.X, piso + tamano.Y / 2, posicion.Z), Vector3.new(posicion.X, piso + tamano.Y / 2, posicion.Z) + dir))
		criatura.invocados[nuevo] = true
		nuevo:SetAttribute("Invocador", criatura.modelo.Name)
		nuevo.Parent = criatura.modelo.Parent or workspace
		Efectos.poof(posicion, colorDe(hab, criatura), 3)
		if Registro.activar then
			Registro.activar(nuevo)
		end
		local nueva = Registro.de(nuevo)
		if nueva then
			nueva.invocador = criatura
		end
	end
end

-- Explotar: dano en area y la criatura desaparece.
local function explotar(criatura, hab)
	local esc = criatura.escala
	local radio = (hab.radio or 10) * esc
	local centro = criatura.raiz.Position
	Efectos.explosion(centro, radio, colorDe(hab, criatura))
	for _, e in Objetivos.enRadio(criatura, centro, radio) do
		local d = (e.raiz.Position - centro).Magnitude
		local factor = 1 - 0.5 * math.clamp(d / radio, 0, 1)
		Objetivos.danar(criatura, e, (hab.danio or 20) * factor)
		Objetivos.empujar(e, e.raiz.Position - centro, (hab.empuje or 60) * factor)
	end
	criatura.explotado = true
	criatura.humanoid.Health = 0
end

local TIPOS = {
	Golpe = golpe,
	Embestida = embestida,
	Onda = onda,
	Proyectil = proyectil,
	Cadena = cadena,
	Escudo = escudo,
	Fantasma = fantasma,
	Teletransporte = teletransporte,
	Invocar = invocar,
	Explotar = explotar,
}
Habilidades.TIPOS = TIPOS

-- Le dice a los clientes que reproduzcan un clip de animacion.
function Habilidades.animar(criatura, clip: string)
	criatura.contadorAccion += 1
	criatura.modelo:SetAttribute("Accion", `{clip}#{criatura.contadorAccion}`)
end

function Habilidades.duracionClip(criatura, clip: string?): number
	local clips = criatura.config.animaciones and criatura.config.animaciones.clips
	local datos = clip and clips and clips[clip]
	return if datos then datos.duracion else 0.5
end

-- Usa una habilidad completa: anima, espera el momento del golpe, aplica el efecto y termina la animacion.
function Habilidades.usar(criatura, hab, objetivo)
	local funcion = TIPOS[hab.tipo]
	if not funcion then
		warn(`[Criaturas] Tipo de habilidad desconocido: {hab.tipo}`)
		return
	end
	criatura.cooldowns[hab.nombre] = os.clock() + (hab.cooldown or 3)
	criatura.ocupado = true
	criatura.humanoid:MoveTo(criatura.raiz.Position)
	if objetivo then
		Habilidades.mirarA(criatura, objetivo.raiz.Position)
	end
	local duracion = Habilidades.duracionClip(criatura, hab.anim)
	if hab.anim then
		Habilidades.animar(criatura, hab.anim)
	end
	Efectos.texto(criatura.raiz, hab.nombre, colorDe(hab, criatura), criatura.alto * 0.5 + 3)
	local retraso = hab.retraso or 0.3
	task.wait(retraso)
	if criatura.vivo then
		if objetivo and Objetivos.sigueValido(criatura, objetivo) and hab.tipo ~= "Embestida" then
			Habilidades.mirarA(criatura, objetivo.raiz.Position)
		end
		local ok, err = pcall(funcion, criatura, hab, objetivo)
		if not ok then
			warn(`[Criaturas] Error en la habilidad {hab.nombre}: {err}`)
		end
	end
	local resto = duracion - retraso
	if resto > 0 and criatura.vivo then
		task.wait(resto)
	end
	criatura.ocupado = false
end

return Habilidades
