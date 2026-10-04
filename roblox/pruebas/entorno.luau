--[[
	Entorno de pruebas: imita lo minimo de Roblox para cargar los modulos del sistema con Lune.
	require(script.Parent.X) funciona porque se arma el mismo arbol de instancias que en Studio.
]]

local fs = require("@lune/fs")
local luau = require("@lune/luau")
local roblox = require("@lune/roblox")
local task = require("@lune/task")

local Instance = roblox.Instance
local CFrame = roblox.CFrame

local Entorno = {}

Entorno.etiquetas = {}
Entorno.avisos = {}

local servicios = {}
local function servicio(nombre: string)
	if not servicios[nombre] then
		if nombre == "CollectionService" then
			servicios[nombre] = {
				AddTag = function(_, instancia, etiqueta)
					table.insert(Entorno.etiquetas, { instancia, etiqueta })
				end,
			}
		else
			local carpeta = Instance.new("Folder")
			carpeta.Name = nombre
			servicios[nombre] = carpeta
		end
	end
	return servicios[nombre]
end

Entorno.game = {
	GetService = function(_, nombre)
		return servicio(nombre)
	end,
}
Entorno.workspace = servicio("Workspace")

local BASE = "roblox/SistemaCriaturas"
local function crear(clase, nombre, padre, ruta)
	local i = Instance.new(clase)
	i.Name = nombre
	if ruta then
		i.Source = fs.readFile(ruta)
	end
	i.Parent = padre
	return i
end
local function sinExtension(a)
	return (a:gsub("%.server%.luau$", ""):gsub("%.client%.luau$", ""):gsub("%.luau$", ""):gsub("%.lua$", ""))
end
local function modulos(carpeta, padre)
	for _, a in fs.readDir(carpeta) do
		if a:match("%.luau?$") then
			crear("ModuleScript", sinExtension(a), padre, `{carpeta}/{a}`)
		end
	end
end

function Entorno.arbol()
	local raiz = Instance.new("Folder")
	raiz.Name = "SistemaCriaturas"
	crear("ModuleScript", "API", raiz, `{BASE}/API.luau`)
	local m = crear("Folder", "Modulos", raiz)
	modulos(`{BASE}/Modulos`, m)
	local c = crear("Folder", "Compartido", raiz)
	crear("ModuleScript", "Animacion", c, `{BASE}/Compartido/Animacion.luau`)
	local cf = crear("Folder", "Configs", c)
	modulos(`{BASE}/Compartido/Configs`, cf)
	return raiz
end

local cache = {}
local function entornoPara(instanciaScript)
	local env = {
		script = instanciaScript,
		game = Entorno.game,
		workspace = Entorno.workspace,
		task = task,
		warn = function(...)
			table.insert(Entorno.avisos, table.concat({ ... }, " "))
		end,
		Instance = Instance,
		Vector3 = roblox.Vector3,
		Vector2 = roblox.Vector2,
		CFrame = CFrame,
		Color3 = roblox.Color3,
		ColorSequence = roblox.ColorSequence,
		NumberSequence = roblox.NumberSequence,
		UDim = roblox.UDim,
		UDim2 = roblox.UDim2,
		Enum = roblox.Enum,
	}
	env.require = function(objetivo)
		if cache[objetivo] == nil then
			local fuente = objetivo.Source
			local chunk = luau.load(fuente, { debugName = objetivo:GetFullName(), environment = entornoPara(objetivo) })
			cache[objetivo] = chunk()
		end
		return cache[objetivo]
	end
	return setmetatable(env, {
		__index = function(_, k)
			local base = {
				math = math, string = string, table = table, os = os, pairs = pairs, ipairs = ipairs,
				type = type, typeof = typeof, tostring = tostring, tonumber = tonumber, print = print,
				pcall = pcall, error = error, select = select, setmetatable = setmetatable,
				getmetatable = getmetatable, next = next, assert = assert, coroutine = coroutine,
				utf8 = utf8, rawget = rawget, rawset = rawset, unpack = table.unpack,
			}
			return base[k]
		end,
	})
end

function Entorno.requerir(instancia)
	return entornoPara(instancia).require(instancia)
end

return Entorno
