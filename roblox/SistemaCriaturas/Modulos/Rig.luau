--[[
	Rig: convierte el modelo importado (MeshParts sueltas) en una criatura armada:
	  - Usa los marcadores _Frente y _Arriba para saber hacia donde mira y su escala, aunque el
	    importador lo haya girado o escalado.
	  - Crea HumanoidRootPart + Humanoid y un Motor6D llamado "Articulacion" dentro de cada parte movible.
	  - Pone en Neon las piezas "__Brillo_" y semitransparentes las "__Vidrio".
]]

local CollectionService = game:GetService("CollectionService")

local Rig = {}

local function partesPorNombre(modelo: Model): { [string]: BasePart }
	local mapa = {}
	for _, d in modelo:GetDescendants() do
		if d:IsA("BasePart") and not mapa[d.Name] then
			mapa[d.Name] = d
		end
	end
	return mapa
end

-- Ordena las partes para que cada padre se arme antes que sus hijos.
local function ordenar(partesRig): { string }
	local orden, visitado = {}, {}
	local function visitar(nombre: string)
		if visitado[nombre] or nombre == "Cuerpo" then
			return
		end
		visitado[nombre] = true
		local datos = partesRig[nombre]
		if datos and datos.padre and partesRig[datos.padre] then
			visitar(datos.padre)
		end
		table.insert(orden, nombre)
	end
	local nombres = {}
	for nombre in partesRig do
		table.insert(nombres, nombre)
	end
	table.sort(nombres)
	for _, nombre in nombres do
		visitar(nombre)
	end
	return orden
end

local function motor(nombre: string, parte0: BasePart, parte1: BasePart, union: CFrame): Motor6D
	local m = Instance.new("Motor6D")
	m.Name = nombre
	m.Part0 = parte0
	m.Part1 = parte1
	m.C0 = parte0.CFrame:Inverse() * union
	m.C1 = parte1.CFrame:Inverse() * union
	m.Parent = parte1
	return m
end

local function soldar(a: BasePart, b: BasePart)
	local w = Instance.new("WeldConstraint")
	w.Part0, w.Part1 = a, b
	w.Parent = b
end

-- Limites del modelo en el marco de la criatura (adelante, derecha, arriba) relativos al centro del cuerpo.
local function limites(partes: { BasePart }, centro: Vector3, adelante: Vector3, derecha: Vector3, arriba: Vector3)
	local minimo = Vector3.new(math.huge, math.huge, math.huge)
	local maximo = -minimo
	for _, p in partes do
		local m = p.Size / 2
		for _, sx in { -1, 1 } do
			for _, sy in { -1, 1 } do
				for _, sz in { -1, 1 } do
					local w = p.CFrame:PointToWorldSpace(Vector3.new(m.X * sx, m.Y * sy, m.Z * sz)) - centro
					local v = Vector3.new(w:Dot(adelante), w:Dot(derecha), w:Dot(arriba))
					minimo = Vector3.new(math.min(minimo.X, v.X), math.min(minimo.Y, v.Y), math.min(minimo.Z, v.Z))
					maximo = Vector3.new(math.max(maximo.X, v.X), math.max(maximo.Y, v.Y), math.max(maximo.Z, v.Z))
				end
			end
		end
	end
	return minimo, maximo
end

--[[
	Arma el modelo. Devuelve una tabla con lo necesario para la IA, o nil si el modelo no sirve.
]]
function Rig.armar(modelo: Model, tipo: string, config)
	local rig = config.rig
	local partes = partesPorNombre(modelo)
	local cuerpo = partes.Cuerpo
	if not cuerpo then
		warn(`[Criaturas] {modelo:GetFullName()} no tiene una parte llamada "Cuerpo". ¿Es el FBX correcto?`)
		return nil
	end
	if modelo:FindFirstChild("HumanoidRootPart") then
		warn(`[Criaturas] {modelo:GetFullName()} ya estaba armado; se ignora.`)
		return nil
	end

	-- Marco de la criatura a partir de los marcadores.
	local centro = cuerpo.Position
	local frente, arribaM = partes._Frente, partes._Arriba
	local adelante, arriba, escala
	if frente and arribaM then
		local f = frente.Position - centro
		escala = f.Magnitude / rig.marcador
		adelante = f.Unit
		local u = (arribaM.Position - centro).Unit
		arriba = (u - adelante * u:Dot(adelante)).Unit
	else
		warn(`[Criaturas] {modelo.Name}: faltan los marcadores _Frente/_Arriba; se usa la orientacion del modelo.`)
		local pivote = modelo:GetPivot()
		adelante, arriba, escala = pivote.LookVector, pivote.UpVector, 1
	end
	local derecha = adelante:Cross(arriba)
	if frente then
		frente:Destroy()
	end
	if arribaM then
		arribaM:Destroy()
	end
	partes._Frente, partes._Arriba = nil, nil

	local function aMundo(v): Vector3
		return centro + adelante * (v[1] * escala) + derecha * (v[2] * escala) + arriba * (v[3] * escala)
	end
	local function marco(posicion: Vector3): CFrame
		-- Columnas: derecha (X), arriba (Y), atras (Z) -> LookVector = adelante.
		return CFrame.fromMatrix(posicion, derecha, arriba, -adelante)
	end

	local lista = {}
	for _, p in partes do
		table.insert(lista, p)
	end
	local minimo, maximo = limites(lista, centro, adelante, derecha, arriba)
	local alto = maximo.Z - minimo.Z
	local largo = maximo.X - minimo.X
	local ancho = maximo.Y - minimo.Y

	-- HumanoidRootPart invisible en el centro, con la mitad del alto.
	local raiz = Instance.new("Part")
	raiz.Name = "HumanoidRootPart"
	raiz.Transparency = 1
	raiz.CanCollide = true -- las demas piezas no chocan; la raiz hace que la criatura sea solida
	raiz.CanTouch = false
	raiz.Size = Vector3.new(math.max(ancho * 0.5, 1), math.max(alto * 0.5, 1), math.max(largo * 0.5, 1))
	raiz.CFrame = marco(centro + arriba * (minimo.Z + alto * 0.5))
	raiz.Parent = modelo

	motor("Articulacion", raiz, cuerpo, marco(centro))
	local armadas = { Cuerpo = cuerpo }
	for _, nombre in ordenar(rig.partes) do
		local datos = rig.partes[nombre]
		local parte = partes[nombre]
		if parte then
			local padre = armadas[datos.padre] or cuerpo
			motor("Articulacion", padre, parte, marco(aMundo(datos.union)))
			armadas[nombre] = parte
		end
	end

	-- Piezas de brillo/vidrio y cualquier otra pieza: soldadas a su parte.
	local brillos = config.coloresBrillo or {}
	for nombre, p in partes do
		if not armadas[nombre] then
			local duena = rig.adjuntos and rig.adjuntos[nombre]
			soldar(armadas[duena] or cuerpo, p)
		end
		if brillos[nombre] then
			p.Material = Enum.Material.Neon
			p.Color = brillos[nombre]
			pcall(function()
				(p :: any).TextureID = ""
			end)
		elseif string.find(nombre, "__Vidrio", 1, true) then
			p.Transparency = 0.4
			p.CastShadow = false
		end
	end

	for _, p in partes do
		p.Anchored = false
		p.CanCollide = false
		p.CanTouch = false
		p.Massless = true
	end
	raiz.Massless = false

	local humanoid = Instance.new("Humanoid")
	humanoid.RigType = Enum.HumanoidRigType.R15
	humanoid.RequiresNeck = false
	humanoid.BreakJointsOnDeath = false
	humanoid.HipHeight = alto * 0.25
	humanoid.MaxHealth = config.vida or 100
	humanoid.Health = humanoid.MaxHealth
	humanoid.WalkSpeed = config.velocidad or 16
	humanoid.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	humanoid.HealthDisplayType = Enum.HumanoidHealthDisplayType.AlwaysOff
	humanoid.Parent = modelo

	modelo.PrimaryPart = raiz
	modelo:SetAttribute("Tipo", tipo)
	modelo:SetAttribute("Escala", escala)
	modelo:SetAttribute("Estado", "Vivo")
	pcall(function()
		raiz:SetNetworkOwner(nil)
	end)
	CollectionService:AddTag(modelo, "Criatura")

	return {
		raiz = raiz,
		cuerpo = cuerpo,
		humanoid = humanoid,
		escala = escala,
		alto = alto,
		partes = armadas,
	}
end

return Rig
