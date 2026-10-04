--[[
	Construye roblox/SistemaCriaturas.rbxmx a partir de los archivos de roblox/SistemaCriaturas/.
	Uso (desde la carpeta del repositorio):  lune run roblox/construir.luau
	Necesita Lune (https://github.com/lune-org/lune):  cargo install lune
]]

local fs = require("@lune/fs")
local roblox = require("@lune/roblox")
local Instance = roblox.Instance

local BASE = "roblox/SistemaCriaturas"

local function leer(ruta: string): string
	return fs.readFile(ruta)
end

local function crear(clase: string, nombre: string, padre: any?, fuente: string?)
	local i = Instance.new(clase)
	i.Name = nombre
	if fuente then
		i.Source = fuente
	end
	if padre then
		i.Parent = padre
	end
	return i
end

local function nombreSinExtension(archivo: string): string
	return (archivo:gsub("%.server%.luau$", ""):gsub("%.client%.luau$", ""):gsub("%.luau$", ""):gsub("%.lua$", ""))
end

local function modulosDe(carpeta: string, padre)
	local archivos = fs.readDir(carpeta)
	table.sort(archivos)
	for _, archivo in archivos do
		local ruta = `{carpeta}/{archivo}`
		if fs.isFile(ruta) and (archivo:match("%.luau$") or archivo:match("%.lua$")) then
			crear("ModuleScript", nombreSinExtension(archivo), padre, leer(ruta))
		end
	end
end

local raiz = crear("Folder", "SistemaCriaturas")
crear("Script", "Servidor", raiz, leer(`{BASE}/Servidor.server.luau`))
crear("ModuleScript", "API", raiz, leer(`{BASE}/API.luau`))
crear("LocalScript", "AnimadorCliente", raiz, leer(`{BASE}/AnimadorCliente.client.luau`))
local modulos = crear("Folder", "Modulos", raiz)
modulosDe(`{BASE}/Modulos`, modulos)
local compartido = crear("Folder", "Compartido", raiz)
crear("ModuleScript", "Animacion", compartido, leer(`{BASE}/Compartido/Animacion.luau`))
local configs = crear("Folder", "Configs", compartido)
modulosDe(`{BASE}/Compartido/Configs`, configs)

-- Roblox Studio guarda el codigo de los scripts como ProtectedString.
local xml = roblox.serializeModel({ raiz }, true)
xml = xml:gsub('<string name="Source">(.-)</string>', '<ProtectedString name="Source">%1</ProtectedString>')
fs.writeFile("roblox/SistemaCriaturas.rbxmx", xml)
local total = 0
for _ in raiz:GetDescendants() do
	total += 1
end
print(`roblox/SistemaCriaturas.rbxmx creado ({total} objetos)`)
