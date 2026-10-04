--[[
	Efectos visuales y sonidos de las habilidades. Todo se crea en workspace.EfectosCriaturas y se borra solo.
	Puedes cambiar los sonidos por los tuyos (rbxassetid://...).
]]

local Debris = game:GetService("Debris")
local TweenService = game:GetService("TweenService")

local Efectos = {}

Efectos.sonidos = {
	golpe = "rbxasset://sounds/swordslash.wav",
	onda = "rbxasset://sounds/collide.wav",
	rayo = "rbxasset://sounds/electronicpingshort.wav",
	disparo = "rbxasset://sounds/Rocket shot.wav",
	aparecer = "rbxasset://sounds/unsheath.wav",
	escudo = "rbxasset://sounds/unsheath.wav",
	embestida = "rbxasset://sounds/swoosh.wav",
}

local function carpeta(): Folder
	local f = workspace:FindFirstChild("EfectosCriaturas")
	if not f then
		f = Instance.new("Folder")
		f.Name = "EfectosCriaturas"
		f.Parent = workspace
	end
	return f :: Folder
end

-- Parte decorativa: anclada, sin colisiones y sin afectar raycasts.
function Efectos.parte(props): BasePart
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Material = Enum.Material.Neon
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	-- La forma va primero (cambia el tamano), luego el tamano y al final la posicion.
	for _, k in { "Shape", "Size", "CFrame", "Position" } do
		if props[k] ~= nil then
			(p :: any)[k] = props[k]
		end
	end
	for k, v in props do
		if k ~= "Shape" and k ~= "Size" and k ~= "CFrame" and k ~= "Position" then
			(p :: any)[k] = v
		end
	end
	p.Parent = carpeta()
	return p
end

function Efectos.desvanecer(parte: BasePart, duracion: number, extra)
	local metas = { Transparency = 1 }
	if extra then
		for k, v in extra do
			metas[k] = v
		end
	end
	TweenService:Create(parte, TweenInfo.new(duracion, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), metas):Play()
	Debris:AddItem(parte, duracion + 0.1)
end

function Efectos.sonido(nombre: string, donde: Instance | Vector3, volumen: number?)
	local id = Efectos.sonidos[nombre]
	if not id then
		return
	end
	local padre: Instance
	if typeof(donde) == "Vector3" then
		local ancla = Efectos.parte({ Transparency = 1, Size = Vector3.one, Position = donde })
		Debris:AddItem(ancla, 3)
		padre = ancla
	else
		padre = donde
	end
	local s = Instance.new("Sound")
	s.SoundId = id
	s.Volume = volumen or 0.6
	s.RollOffMaxDistance = 120
	s.Parent = padre
	s:Play()
	Debris:AddItem(s, 3)
end

-- Anillo que crece en el piso (ondas expansivas).
function Efectos.anillo(centro: Vector3, radio: number, color: Color3, duracion: number?)
	local d = duracion or 0.45
	local anillo = Efectos.parte({
		Shape = Enum.PartType.Cylinder,
		Size = Vector3.new(0.3, 1, 1),
		CFrame = CFrame.new(centro) * CFrame.Angles(0, 0, math.rad(90)),
		Color = color,
		Transparency = 0.25,
	})
	Efectos.desvanecer(anillo, d, { Size = Vector3.new(0.3, radio * 2, radio * 2) })
	local esfera = Efectos.parte({
		Shape = Enum.PartType.Ball,
		Size = Vector3.one * 2,
		Position = centro + Vector3.new(0, 1, 0),
		Color = color,
		Transparency = 0.5,
		Material = Enum.Material.ForceField,
	})
	Efectos.desvanecer(esfera, d * 0.8, { Size = Vector3.one * radio * 1.6 })
end

-- Arco de corte al frente (golpes).
function Efectos.arco(origen: CFrame, alcance: number, angulo: number, color: Color3)
	local pasos = 7
	for i = 0, pasos - 1 do
		local a = math.rad(-angulo / 2 + angulo * i / (pasos - 1))
		local cf = origen * CFrame.Angles(0, a, 0) * CFrame.new(0, 0, -alcance * 0.7)
		local trozo = Efectos.parte({
			Size = Vector3.new(alcance * 0.35, 0.25, 0.25),
			CFrame = cf * CFrame.Angles(0, math.rad(90), 0),
			Color = color,
			Transparency = 0.15,
		})
		task.delay(i * 0.015, function()
			Efectos.desvanecer(trozo, 0.25, { Size = Vector3.new(alcance * 0.5, 0.05, 0.05) })
		end)
	end
end

-- Rayo en zigzag entre dos puntos.
function Efectos.rayo(desde: Vector3, hasta: Vector3, color: Color3)
	local segmentos = 7
	local puntos = { desde }
	local dir = hasta - desde
	local largo = dir.Magnitude
	for i = 1, segmentos - 1 do
		local base = desde + dir * (i / segmentos)
		local desvio = Vector3.new(math.random() - 0.5, math.random() - 0.5, math.random() - 0.5) * math.min(largo * 0.15, 3)
		table.insert(puntos, base + desvio)
	end
	table.insert(puntos, hasta)
	for i = 1, #puntos - 1 do
		local a, b = puntos[i], puntos[i + 1]
		local seg = Efectos.parte({
			Size = Vector3.new(0.25, 0.25, (b - a).Magnitude),
			CFrame = CFrame.lookAt((a + b) / 2, b),
			Color = color,
		})
		Efectos.desvanecer(seg, 0.3)
	end
	local destello = Efectos.parte({
		Shape = Enum.PartType.Ball,
		Size = Vector3.one * 1.5,
		Position = hasta,
		Color = color,
	})
	Efectos.desvanecer(destello, 0.3, { Size = Vector3.one * 4 })
end

-- Nube de humo/chispas (aparecer, desaparecer, teletransporte).
function Efectos.poof(posicion: Vector3, color: Color3, tamano: number?)
	local t = tamano or 4
	for _ = 1, 8 do
		local bola = Efectos.parte({
			Shape = Enum.PartType.Ball,
			Size = Vector3.one * (t * 0.35),
			Position = posicion + Vector3.new(math.random() - 0.5, math.random() * 0.6, math.random() - 0.5) * t,
			Color = color,
			Material = Enum.Material.SmoothPlastic,
			Transparency = 0.2,
		})
		local destino = bola.Position + Vector3.new(math.random() - 0.5, math.random(), math.random() - 0.5) * t
		Efectos.desvanecer(bola, 0.6, { Size = Vector3.one * t * 0.7, Position = destino })
	end
end

-- Explosion visual (el dano lo aplica la habilidad).
function Efectos.explosion(posicion: Vector3, radio: number, color: Color3)
	local e = Instance.new("Explosion")
	e.Position = posicion
	e.BlastRadius = radio
	e.BlastPressure = 0
	e.ExplosionType = Enum.ExplosionType.NoCraters
	e.DestroyJointRadiusPercent = 0
	e.Parent = carpeta()
	local bola = Efectos.parte({ Shape = Enum.PartType.Ball, Size = Vector3.one * 2, Position = posicion, Color = color })
	Efectos.desvanecer(bola, 0.4, { Size = Vector3.one * radio * 2 })
	Efectos.anillo(posicion - Vector3.new(0, 1, 0), radio, color, 0.4)
end

-- Estela detras de la criatura (embestidas). Devuelve una funcion para quitarla.
function Efectos.estela(raiz: BasePart, alto: number, color: Color3): () -> ()
	local a0 = Instance.new("Attachment")
	a0.Position = Vector3.new(0, alto * 0.3, 0)
	a0.Parent = raiz
	local a1 = Instance.new("Attachment")
	a1.Position = Vector3.new(0, -alto * 0.3, 0)
	a1.Parent = raiz
	local estela = Instance.new("Trail")
	estela.Attachment0, estela.Attachment1 = a0, a1
	estela.Color = ColorSequence.new(color)
	estela.LightEmission = 1
	estela.Lifetime = 0.35
	estela.Transparency = NumberSequence.new(0.2, 1)
	estela.Parent = raiz
	return function()
		task.delay(0.4, function()
			estela:Destroy()
			a0:Destroy()
			a1:Destroy()
		end)
	end
end

-- Burbuja de escudo pegada a la criatura. Devuelve una funcion para quitarla.
function Efectos.escudo(raiz: BasePart, tamano: number, color: Color3): () -> ()
	local burbuja = Instance.new("Part")
	burbuja.Name = "EscudoCriatura"
	burbuja.Shape = Enum.PartType.Ball
	burbuja.Size = Vector3.one * tamano
	burbuja.Material = Enum.Material.ForceField
	burbuja.Color = color
	burbuja.CanCollide = false
	burbuja.CanQuery = false
	burbuja.CanTouch = false
	burbuja.Massless = true
	burbuja.CastShadow = false
	burbuja.CFrame = raiz.CFrame
	local soldadura = Instance.new("WeldConstraint")
	soldadura.Part0, soldadura.Part1 = raiz, burbuja
	soldadura.Parent = burbuja
	burbuja.Parent = raiz
	return function()
		Efectos.desvanecer(burbuja, 0.3)
	end
end

-- Texto flotante con el nombre de la habilidad.
function Efectos.texto(adorno: BasePart, texto: string, color: Color3, altura: number)
	local gui = Instance.new("BillboardGui")
	gui.Name = "TextoHabilidad"
	gui.Size = UDim2.fromOffset(240, 40)
	gui.StudsOffset = Vector3.new(0, altura, 0)
	gui.AlwaysOnTop = true
	gui.MaxDistance = 90
	gui.Adornee = adorno
	local etiqueta = Instance.new("TextLabel")
	etiqueta.Size = UDim2.fromScale(1, 1)
	etiqueta.BackgroundTransparency = 1
	etiqueta.Text = texto
	etiqueta.TextColor3 = color
	etiqueta.TextStrokeTransparency = 0
	etiqueta.TextScaled = true
	etiqueta.Font = Enum.Font.FredokaOne
	etiqueta.Parent = gui
	gui.Parent = adorno
	TweenService:Create(gui, TweenInfo.new(1.2), { StudsOffset = Vector3.new(0, altura + 2, 0) }):Play()
	TweenService:Create(etiqueta, TweenInfo.new(1.2, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
		TextTransparency = 1,
		TextStrokeTransparency = 1,
	}):Play()
	Debris:AddItem(gui, 1.3)
end

-- Proyectil visual segun la forma.
function Efectos.proyectil(forma: string, color: Color3, tamano: number): BasePart
	local p: BasePart
	if forma == "pluma" then
		p = Efectos.parte({ Size = Vector3.new(0.2, 0.5, 1.6) * tamano, Color = color })
	elseif forma == "hueso" then
		p = Efectos.parte({
			Shape = Enum.PartType.Cylinder,
			Size = Vector3.new(1.6, 0.35, 0.35) * tamano,
			Color = Color3.fromRGB(240, 232, 210),
			Material = Enum.Material.SmoothPlastic,
		})
		local brillo = Instance.new("PointLight")
		brillo.Color = color
		brillo.Range = 6
		brillo.Parent = p
	elseif forma == "rayo" then
		p = Efectos.parte({ Size = Vector3.new(0.3, 0.3, 2.4) * tamano, Color = color })
	elseif forma == "cristal" then
		p = Efectos.parte({ Size = Vector3.new(0.7, 0.7, 1.4) * tamano, Color = color, Material = Enum.Material.Glass, Transparency = 0.2 })
	else
		p = Efectos.parte({ Shape = Enum.PartType.Ball, Size = Vector3.one * 1.2 * tamano, Color = color })
	end
	local luz = Instance.new("PointLight")
	luz.Color = color
	luz.Brightness = 2
	luz.Range = 8
	luz.Parent = p
	return p
end

return Efectos
