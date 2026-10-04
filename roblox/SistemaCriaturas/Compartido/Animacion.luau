--[[
	Animacion: matematica de animacion compartida (la misma que usa la vista previa de Blender).

	Ciclos: { [parte] = { {canal, amplitud, frecuencia, fase}, ... } }
	        valor = amplitud * sin(2*pi*(frecuencia*t + fase))
	Clips:  { duracion = n, claves = { {t = tiempo, pose = {[parte] = {[canal] = valor}}}, ... } }
	        interpolacion suave (smoothstep) entre claves.
	Canales: rx, ry, rz (grados) y px, py, pz (studs) en el marco de la articulacion:
	        X = derecha de la criatura, Y = arriba, Z = atras.
]]

local Animacion = {}

local function suave(x: number): number
	return x * x * (3 - 2 * x)
end

local function sumarCanales(origen, destino, peso: number)
	for canal, valor in origen do
		destino[canal] = (destino[canal] or 0) + valor * peso
	end
end

local function obtener(pose, parte)
	local d = pose[parte]
	if not d then
		d = {}
		pose[parte] = d
	end
	return d
end

-- Suma un ciclo de osciladores en la pose de salida.
function Animacion.evaluarCiclo(ciclo, t: number, salida, peso: number)
	if not ciclo or peso <= 0 then
		return
	end
	for parte, osciladores in ciclo do
		local d = obtener(salida, parte)
		for _, o in osciladores do
			local canal, amplitud, frecuencia, fase = o[1], o[2], o[3], o[4]
			d[canal] = (d[canal] or 0) + peso * amplitud * math.sin(2 * math.pi * (frecuencia * t + fase))
		end
	end
end

-- Suma un clip (poses clave) en la pose de salida. t se limita a [0, duracion].
function Animacion.evaluarClip(clip, t: number, salida, peso: number)
	if not clip or peso <= 0 then
		return
	end
	local claves = clip.claves
	local n = #claves
	if n == 0 then
		return
	end
	if t <= claves[1].t then
		for parte, canales in claves[1].pose do
			sumarCanales(canales, obtener(salida, parte), peso)
		end
		return
	end
	for i = 1, n - 1 do
		local a, b = claves[i], claves[i + 1]
		if t >= a.t and t <= b.t then
			local k = suave((t - a.t) / math.max(b.t - a.t, 1e-6))
			local partes = {}
			for parte in a.pose do
				partes[parte] = true
			end
			for parte in b.pose do
				partes[parte] = true
			end
			for parte in partes do
				local ca, cb = a.pose[parte] or {}, b.pose[parte] or {}
				local d = obtener(salida, parte)
				local canales = {}
				for canal in ca do
					canales[canal] = true
				end
				for canal in cb do
					canales[canal] = true
				end
				for canal in canales do
					local va, vb = ca[canal] or 0, cb[canal] or 0
					d[canal] = (d[canal] or 0) + (va + (vb - va) * k) * peso
				end
			end
			return
		end
	end
	for parte, canales in claves[n].pose do
		sumarCanales(canales, obtener(salida, parte), peso)
	end
end

-- Convierte los canales de una parte en el CFrame para Motor6D.Transform.
function Animacion.aCFrame(canales, escala: number): CFrame
	local rad = math.rad
	return CFrame.new((canales.px or 0) * escala, (canales.py or 0) * escala, (canales.pz or 0) * escala)
		* CFrame.Angles(rad(canales.rx or 0), rad(canales.ry or 0), rad(canales.rz or 0))
end

return Animacion
