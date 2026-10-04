--[[
	Pruebas del sistema de criaturas. Uso (desde la carpeta del repositorio):
	  python3 roblox/pruebas/referencia_python.py PollitoBomba > /tmp/ref.json
	  lune run roblox/pruebas/probar.luau /tmp/ref.json PollitoBomba
]]

local fs = require("@lune/fs")
local serde = require("@lune/serde")
local process = require("@lune/process")
local roblox = require("@lune/roblox")

local Entorno = require("./entorno")

local Vector3, CFrame, Instance = roblox.Vector3, roblox.CFrame, roblox.Instance

local rutaReferencia, tipo = process.args[1], process.args[2] or "PollitoBomba"
local fallos, pruebas = 0, 0

local function revisar(condicion: boolean, mensaje: string)
	pruebas += 1
	if not condicion then
		fallos += 1
		print("FALLO: " .. mensaje)
	end
end

local function cerca(a: number, b: number, tol: number?): boolean
	return math.abs(a - b) <= (tol or 1e-4)
end

local function cercaV(a, b, tol: number?): boolean
	return (a - b).Magnitude <= (tol or 1e-3)
end

local function cercaCF(a, b, tol: number?): boolean
	local t = tol or 1e-3
	local ca, cb = { a:GetComponents() }, { b:GetComponents() }
	for i = 1, 12 do
		if math.abs(ca[i] - cb[i]) > t then
			return false
		end
	end
	return true
end

local arbol = Entorno.arbol()
local Animacion = Entorno.requerir(arbol.Compartido.Animacion)
local config = Entorno.requerir(arbol.Compartido.Configs:FindFirstChild(tipo))

-------------------------------------------------------------- 1. animaciones iguales a las de Python
local referencia = serde.decode("json", fs.readFile(rutaReferencia))

local function compararPose(pose, esperado, contexto)
	for parte, canales in esperado do
		for canal, valor in canales do
			local obtenido = pose[parte] and pose[parte][canal] or 0
			revisar(cerca(obtenido, valor), `{contexto} {parte}.{canal}: Luau {obtenido} vs Python {valor}`)
		end
	end
	for parte, canales in pose do
		for canal, valor in canales do
			local e = esperado[parte] and esperado[parte][canal] or 0
			revisar(cerca(valor, e), `{contexto} {parte}.{canal} sobra en Luau: {valor} vs {e}`)
		end
	end
end

for _, caso in referencia.ciclos do
	local pose = {}
	Animacion.evaluarCiclo(config.animaciones.ciclos[caso.ciclo], caso.t, pose, 1)
	compararPose(pose, caso.pose, `ciclo {caso.ciclo} t={caso.t}`)
end
for _, caso in referencia.clips do
	local pose = {}
	Animacion.evaluarClip(config.animaciones.clips[caso.clip], caso.t, pose, 1)
	compararPose(pose, caso.pose, `clip {caso.clip} t={caso.t}`)
end
for i, caso in referencia.matrices do
	local cf = Animacion.aCFrame(caso.canales, 1)
	local c = { cf:GetComponents() }
	-- GetComponents: x, y, z, R00, R01, R02, R10, R11, R12, R20, R21, R22
	local m = caso.m
	local esperado = { m[1][4], m[2][4], m[3][4], m[1][1], m[1][2], m[1][3], m[2][1], m[2][2], m[2][3], m[3][1], m[3][2], m[3][3] }
	for k = 1, 12 do
		revisar(cerca(c[k], esperado[k]), `matriz {i} componente {k}: {c[k]} vs {esperado[k]}`)
	end
end

-------------------------------------------------------------- 2. el rig respeta articulaciones con giro y escala
local Rig = Entorno.requerir(arbol.Modulos.Rig)
local rig = config.rig

local escalaImport = 1.7
-- El "importador" gira el modelo 137 grados, lo inclina un poco y lo mueve.
local transformacion = CFrame.new(10, 5, -3) * CFrame.Angles(0, math.rad(137), 0)
local adelanteW = transformacion:VectorToWorldSpace(Vector3.new(0, 0, -1))
local arribaW = transformacion:VectorToWorldSpace(Vector3.new(0, 1, 0))
local derechaW = adelanteW:Cross(arribaW)
local centroW = transformacion.Position
local function mundo(v): any
	return centroW + adelanteW * (v[1] * escalaImport) + derechaW * (v[2] * escalaImport) + arribaW * (v[3] * escalaImport)
end

local modelo = Instance.new("Model")
modelo.Name = tipo
local function parte(nombre: string, posicion, tamano)
	local p = Instance.new("MeshPart")
	p.Name = nombre
	p.Size = tamano or Vector3.new(0.6, 0.6, 0.6)
	p.CFrame = transformacion.Rotation + posicion
	p.Position = posicion -- Lune no calcula Position desde CFrame: se guarda a mano
	p.Parent = modelo
	return p
end
parte("Cuerpo", centroW, Vector3.new(1.5, 1.4, 1.6) * escalaImport)
parte("_Frente", mundo({ rig.marcador, 0, 0 }))
parte("_Arriba", mundo({ 0, 0, rig.marcador }))
for nombre, datos in rig.partes do
	-- Cada parte queda un poco desplazada de su articulacion, como en el modelo real.
	parte(nombre, mundo({ datos.union[1] + 0.1, datos.union[2] * 1.2, datos.union[3] + 0.2 }))
end
for nombre in rig.adjuntos or {} do
	parte(nombre, mundo({ 0.3, 0.1, 1.5 }))
end
local antes = {}
for _, p in modelo:GetChildren() do
	antes[p.Name] = p.CFrame
end

local armado = Rig.armar(modelo, tipo, config)
revisar(armado ~= nil, "Rig.armar devolvio nil")
if armado then
	revisar(cerca(armado.escala, escalaImport), `escala {armado.escala} vs {escalaImport}`)
	revisar(cercaV(armado.raiz.CFrame.LookVector, adelanteW), "la raiz no mira hacia adelante")
	revisar(cercaV(armado.raiz.CFrame.UpVector, arribaW), "la raiz no mira hacia arriba")
	revisar(modelo:FindFirstChild("_Frente") == nil and modelo:FindFirstChild("_Arriba") == nil, "los marcadores no se borraron")
	revisar(modelo.PrimaryPart == armado.raiz, "PrimaryPart no es la raiz")
	revisar(armado.humanoid.HipHeight > 0, "HipHeight debe ser positivo")
	revisar(#Entorno.etiquetas == 1, "debe agregar la etiqueta Criatura")
	-- El suelo del modelo de prueba: la parte mas baja.
	local cuerpo = armado.cuerpo
	local raizMotor = cuerpo:FindFirstChild("Articulacion")
	revisar(raizMotor ~= nil and raizMotor.Part0 == armado.raiz, "falta el motor Raiz (Cuerpo -> HumanoidRootPart)")
	for nombre, datos in rig.partes do
		local p = modelo:FindFirstChild(nombre)
		local m = p and p:FindFirstChild("Articulacion")
		revisar(m ~= nil, `falta la articulacion de {nombre}`)
		if m then
			local union = m.Part0.CFrame * m.C0
			revisar(cercaV(union.Position, mundo(datos.union)), `articulacion de {nombre} en lugar incorrecto`)
			revisar(cercaV(union.LookVector, adelanteW) and cercaV(union.UpVector, arribaW), `ejes de la articulacion de {nombre}`)
			revisar(m.Part0.Name == datos.padre, `{nombre}: padre {m.Part0.Name} vs {datos.padre}`)
			-- En reposo (Transform = identidad) la parte queda donde estaba.
			revisar(cercaCF(m.Part0.CFrame * m.C0 * m.C1:Inverse(), antes[nombre]), `{nombre} se mueve en reposo`)
			-- Con rx = 90 la parte gira sobre el eje derecho de la criatura, alrededor de la articulacion.
			local girada = m.Part0.CFrame * m.C0 * CFrame.Angles(math.rad(90), 0, 0) * m.C1:Inverse()
			local relativo = antes[nombre].Position - union.Position
			local esperado = union.Position + (CFrame.fromAxisAngle(derechaW, math.rad(90)) * relativo)
			revisar(cercaV(girada.Position, esperado), `{nombre}: el giro rx no es alrededor del eje derecho`)
		end
	end
	for nombre in rig.adjuntos or {} do
		local p = modelo:FindFirstChild(nombre)
		revisar(p and p:FindFirstChildOfClass("WeldConstraint") ~= nil, `{nombre} no quedo soldado`)
		if config.coloresBrillo and config.coloresBrillo[nombre] then
			revisar(p.Material == roblox.Enum.Material.Neon, `{nombre} no quedo en Neon`)
		end
	end
	for _, p in modelo:GetDescendants() do
		if p:IsA("BasePart") then
			revisar(p.Anchored == false, `{p.Name} quedo anclada`)
		end
	end
end

-------------------------------------------------------------- 3. tipos por nombre
local Registro = Entorno.requerir(arbol.Modulos.Registro)
Registro.configs = { GalloSamurai = {}, PollitoBomba = {} }
local function m(nombre, atributo)
	local x = Instance.new("Model")
	x.Name = nombre
	if atributo then
		x:SetAttribute("Tipo", atributo)
	end
	return x
end
revisar(Registro.tipoDe(m("GalloSamurai")) == "GalloSamurai", "nombre exacto")
revisar(Registro.tipoDe(m("GalloSamurai2")) == "GalloSamurai", "nombre con numero")
revisar(Registro.tipoDe(m("GalloSamurai (1)")) == "GalloSamurai", "nombre con (1)")
revisar(Registro.tipoDe(m("Cualquiera", "PollitoBomba")) == "PollitoBomba", "atributo Tipo")
revisar(Registro.tipoDe(m("Arbol")) == nil, "modelo que no es criatura")

for _, aviso in Entorno.avisos do
	print("aviso: " .. aviso)
end
print(`{tipo}: {pruebas - fallos}/{pruebas} pruebas correctas`)
if fallos > 0 then
	process.exit(1)
end
