--[[
	Eventos para conectar el sistema con el resto de tu juego (desde cualquier Script del servidor):

	  local eventos = game.ServerStorage:WaitForChild("EventosCriaturas")
	  eventos.CriaturaDerrotada.Event:Connect(function(modelo, tipo, ultimoAtacante)
	      print(tipo, "fue derrotada")   -- por ejemplo, dar monedas o un huevo especial
	  end)
	  eventos.CriaturaAparecio.Event:Connect(function(modelo, tipo) end)
]]

local ServerStorage = game:GetService("ServerStorage")

local carpeta = ServerStorage:FindFirstChild("EventosCriaturas")
if not carpeta then
	carpeta = Instance.new("Folder")
	carpeta.Name = "EventosCriaturas"
	carpeta.Parent = ServerStorage
end

local function evento(nombre: string): BindableEvent
	local e = carpeta:FindFirstChild(nombre)
	if not e then
		e = Instance.new("BindableEvent")
		e.Name = nombre
		e.Parent = carpeta
	end
	return e :: BindableEvent
end

return {
	CriaturaDerrotada = evento("CriaturaDerrotada"),
	CriaturaAparecio = evento("CriaturaAparecio"),
}
