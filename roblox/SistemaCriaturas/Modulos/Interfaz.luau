--[[
	Interfaz: barra de vida con el nombre de la criatura.
]]

local TweenService = game:GetService("TweenService")

local Interfaz = {}

function Interfaz.crear(criatura)
	local config = criatura.config
	local color = config.colorUI or Color3.fromRGB(255, 80, 80)
	local gui = Instance.new("BillboardGui")
	gui.Name = "BarraCriatura"
	gui.Size = UDim2.fromOffset(170, 40)
	gui.StudsOffset = Vector3.new(0, criatura.alto * 0.5 + 1.5, 0)
	gui.MaxDistance = 90
	gui.Adornee = criatura.raiz
	gui.ResetOnSpawn = false

	local nombre = Instance.new("TextLabel")
	nombre.Size = UDim2.new(1, 0, 0.55, 0)
	nombre.BackgroundTransparency = 1
	nombre.Text = config.nombre or criatura.tipo
	nombre.TextColor3 = Color3.new(1, 1, 1)
	nombre.TextStrokeTransparency = 0.2
	nombre.TextScaled = true
	nombre.Font = Enum.Font.FredokaOne
	nombre.Parent = gui

	local fondo = Instance.new("Frame")
	fondo.Position = UDim2.new(0.1, 0, 0.62, 0)
	fondo.Size = UDim2.new(0.8, 0, 0.28, 0)
	fondo.BackgroundColor3 = Color3.fromRGB(25, 20, 30)
	fondo.BorderSizePixel = 0
	fondo.Parent = gui
	local esquina = Instance.new("UICorner")
	esquina.CornerRadius = UDim.new(0.5, 0)
	esquina.Parent = fondo
	local borde = Instance.new("UIStroke")
	borde.Color = Color3.new(0, 0, 0)
	borde.Thickness = 1.5
	borde.Parent = fondo

	local relleno = Instance.new("Frame")
	relleno.Size = UDim2.fromScale(1, 1)
	relleno.BackgroundColor3 = color
	relleno.BorderSizePixel = 0
	relleno.Parent = fondo
	local esquina2 = esquina:Clone()
	esquina2.Parent = relleno

	gui.Parent = criatura.raiz
	criatura.barra = gui

	local function actualizar()
		local h = criatura.humanoid
		local frac = if h.MaxHealth > 0 then math.clamp(h.Health / h.MaxHealth, 0, 1) else 0
		TweenService:Create(relleno, TweenInfo.new(0.2), { Size = UDim2.fromScale(frac, 1) }):Play()
	end
	criatura.humanoid.HealthChanged:Connect(actualizar)
	actualizar()
end

function Interfaz.visible(criatura, visible: boolean)
	if criatura.barra then
		criatura.barra.Enabled = visible
	end
end

return Interfaz
