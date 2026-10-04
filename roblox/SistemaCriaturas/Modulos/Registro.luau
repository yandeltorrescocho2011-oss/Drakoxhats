--[[
	Registro: lista de criaturas activas, plantillas para reaparecer/invocar y configuraciones.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local Registro = {}

Registro.criaturas = {} -- [Model] = criatura
Registro.configs = {} -- [tipo] = config

local carpetaPlantillas: Folder? = nil

function Registro.cargarConfigs(carpetaConfigs: Instance)
	for _, modulo in carpetaConfigs:GetChildren() do
		if modulo:IsA("ModuleScript") then
			local ok, config = pcall(require, modulo)
			if ok and type(config) == "table" then
				Registro.configs[modulo.Name] = config
			else
				warn(`[Criaturas] No se pudo cargar la configuracion {modulo.Name}: {config}`)
			end
		end
	end
end

-- Descubre el tipo de criatura de un modelo: atributo "Tipo", nombre exacto o nombre con numeros/copias al final.
function Registro.tipoDe(modelo: Instance): string?
	if not modelo:IsA("Model") then
		return nil
	end
	local tipo = modelo:GetAttribute("Tipo")
	if type(tipo) == "string" and Registro.configs[tipo] then
		return tipo
	end
	if Registro.configs[modelo.Name] then
		return modelo.Name
	end
	local limpio = modelo.Name:gsub("%s*%(%d+%)$", ""):gsub("[%s_%-]*[Cc]opy$", ""):gsub("%d+$", "")
	if Registro.configs[limpio] then
		return limpio
	end
	return nil
end

function Registro.plantillas(): Folder
	if not carpetaPlantillas then
		local carpeta = ServerStorage:FindFirstChild("PlantillasCriaturas")
		if not carpeta then
			carpeta = Instance.new("Folder")
			carpeta.Name = "PlantillasCriaturas"
			carpeta.Parent = ServerStorage
		end
		carpetaPlantillas = carpeta :: Folder
	end
	return carpetaPlantillas :: Folder
end

-- Guarda una copia limpia (sin armar) del modelo para reaparecer o invocar.
function Registro.guardarPlantilla(tipo: string, modelo: Model)
	local carpeta = Registro.plantillas()
	if carpeta:FindFirstChild(tipo) then
		return
	end
	local copia = modelo:Clone()
	copia.Name = tipo
	copia:SetAttribute("Tipo", tipo)
	copia.Parent = carpeta
end

function Registro.plantilla(tipo: string): Model?
	local p = Registro.plantillas():FindFirstChild(tipo)
	if p and p:IsA("Model") then
		return p
	end
	return nil
end

-- Busca en ServerStorage y ReplicatedStorage modelos de criaturas para usarlos como plantillas.
function Registro.buscarPlantillas()
	for _, lugar in { ServerStorage, ReplicatedStorage } do
		for _, d in lugar:GetDescendants() do
			if d:IsA("Model") and not d:IsDescendantOf(Registro.plantillas()) then
				local tipo = Registro.tipoDe(d)
				if tipo and not d:FindFirstChild("HumanoidRootPart") then
					Registro.guardarPlantilla(tipo, d)
				end
			end
		end
	end
end

function Registro.agregar(criatura)
	Registro.criaturas[criatura.modelo] = criatura
end

function Registro.quitar(modelo: Model)
	Registro.criaturas[modelo] = nil
end

function Registro.de(modelo: Instance?)
	if not modelo then
		return nil
	end
	return Registro.criaturas[modelo]
end

-- Devuelve la criatura a la que pertenece una parte (o nil).
function Registro.dePieza(pieza: Instance)
	local modelo = pieza:FindFirstAncestorOfClass("Model")
	while modelo do
		local c = Registro.criaturas[modelo]
		if c then
			return c
		end
		modelo = modelo:FindFirstAncestorOfClass("Model")
	end
	return nil
end

return Registro
