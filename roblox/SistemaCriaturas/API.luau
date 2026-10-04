--[[
	API del sistema de criaturas para usar desde tus propios scripts del servidor:

	  local Criaturas = require(game.ServerScriptService.SistemaCriaturas.API)
	  local gallo = Criaturas.aparecer("GalloSamurai", CFrame.new(0, 5, 0), { Modo = "Pelea", Equipo = "Rojo" })
	  Criaturas.cambiarModo(gallo, "Mascota")
	  gallo:SetAttribute("Dueno", jugador.Name)

	Para "aparecer" necesitas el modelo de esa criatura en ServerStorage (o una en el mapa).
]]

local Registro = require(script.Parent.Modulos.Registro)

local API = {}

-- Hace aparecer una criatura nueva. atributos es opcional (Modo, Equipo, Dueno...).
function API.aparecer(tipo: string, donde: CFrame, atributos: { [string]: any }?, padre: Instance?): Model?
	local plantilla = Registro.plantilla(tipo)
	if not plantilla then
		warn(`[Criaturas] No hay plantilla para "{tipo}". Pon el modelo en ServerStorage o en el mapa.`)
		return nil
	end
	local nuevo = plantilla:Clone()
	for nombre, valor in atributos or {} do
		nuevo:SetAttribute(nombre, valor)
	end
	nuevo:PivotTo(donde)
	nuevo.Parent = padre or workspace
	if Registro.activar then
		Registro.activar(nuevo)
	end
	return nuevo
end

function API.cambiarModo(modelo: Model, modo: string)
	modelo:SetAttribute("Modo", modo)
end

-- Devuelve todas las criaturas vivas (modelos), opcionalmente de un tipo.
function API.lista(tipo: string?): { Model }
	local lista = {}
	for modelo, criatura in Registro.criaturas do
		if criatura.vivo and (tipo == nil or criatura.tipo == tipo) then
			table.insert(lista, modelo)
		end
	end
	return lista
end

return API
