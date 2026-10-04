-- Generado por herramientas/criaturas/generar.py. No lo edites a mano: cambia el archivo
-- herramientas/criaturas/gallosamurai.py y vuelve a generar.
return {
	nombre = "Gallo Samurái",
	vida = 320,
	velocidad = 18,
	comportamiento = "normal",
	radioDeteccion = 40,
	radioPatrulla = 18,
	radioPersecucion = 75,
	reaparecer = 30,
	colorUI = Color3.fromRGB(215, 30, 35),
	habilidades = {
		{
			nombre = "Corte Veloz",
			tipo = "Golpe",
			anim = "CorteVeloz",
			rango = 8,
			cooldown = 2.5,
			retraso = 0.3,
			danio = 18,
			alcance = 9,
			angulo = 120,
			empuje = 35,
			color = Color3.fromRGB(225, 235, 255),
		},
		{
			nombre = "Tajo Giratorio",
			tipo = "Onda",
			anim = "TajoGiratorio",
			rango = 10,
			cooldown = 8,
			retraso = 0.45,
			danio = 22,
			radio = 12,
			empuje = 55,
			color = Color3.fromRGB(210, 225, 255),
		},
		{
			nombre = "Defensa de Acero",
			tipo = "Escudo",
			anim = "DefensaAcero",
			rango = 20,
			cooldown = 12,
			retraso = 0.2,
			duracion = 3,
			reduccion = 0.7,
			color = Color3.fromRGB(200, 210, 230),
		},
	},
	tipo = "GalloSamurai",
	rig = {
		marcador = 2.0,
		suelo = -3.0944,
		partes = {
			Cabeza = {
				padre = "Cuerpo",
				union = { 1.0589, 0.1672, 1.2055 },
			},
			AlaIzq = {
				padre = "Cuerpo",
				union = { 0.4589, -0.8328, 1.1055 },
			},
			AlaDer = {
				padre = "Cuerpo",
				union = { 0.4589, 1.1672, 1.1055 },
			},
			PataIzq = {
				padre = "Cuerpo",
				union = { -0.1611, -0.3328, -0.6445 },
			},
			PataDer = {
				padre = "Cuerpo",
				union = { -0.1611, 0.6672, -0.6445 },
			},
			Cola = {
				padre = "Cuerpo",
				union = { -1.2411, 0.1672, 0.6555 },
			},
			Bandera = {
				padre = "Cuerpo",
				union = { -0.7411, 0.1672, 1.1555 },
			},
		},
		adjuntos = {
			AlaDer__Brillo_filo = "AlaDer",
		},
	},
	coloresBrillo = {
		AlaDer__Brillo_filo = Color3.fromRGB(199, 237, 255),
	},
	animaciones = {
		ciclos = {
			Idle = {
				Raiz = {
					{ "py", 0.04, 1.2, 0 },
				},
				Cabeza = {
					{ "rx", 4, 0.6, 0 },
					{ "ry", 10, 0.3, 0.1 },
				},
				AlaIzq = {
					{ "rz", -3, 1.2, 0 },
				},
				AlaDer = {
					{ "rz", 3, 1.2, 0 },
					{ "rx", 3, 0.6, 0.25 },
				},
				Bandera = {
					{ "rx", 3, 0.9, 0 },
					{ "rz", 4, 0.6, 0.3 },
				},
				Cola = {
					{ "rz", 3, 0.7, 0 },
					{ "rx", 2, 0.9, 0.5 },
				},
			},
			Caminar = {
				Raiz = {
					{ "py", 0.08, 5.0, 0.25 },
					{ "rz", 3, 2.5, 0 },
					{ "ry", 3, 2.5, 0.25 },
				},
				Cabeza = {
					{ "rx", 6, 5.0, 0.0 },
				},
				AlaIzq = {
					{ "rz", -5, 2.5, 0 },
				},
				AlaDer = {
					{ "rz", 5, 2.5, 0.5 },
					{ "rx", 5, 2.5, 0.25 },
				},
				PataIzq = {
					{ "rx", 28, 2.5, 0 },
				},
				PataDer = {
					{ "rx", 28, 2.5, 0.5 },
				},
				Bandera = {
					{ "rx", 6, 2.5, 0.3 },
					{ "rz", 5, 2.5, 0.1 },
				},
				Cola = {
					{ "rx", 5, 5.0, 0.4 },
					{ "rz", 5, 2.5, 0.2 },
				},
			},
		},
		clips = {
			CorteVeloz = {
				duracion = 0.75,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.15,
						pose = {
							Raiz = {
								ry = -20,
								rx = 3,
							},
							AlaDer = {
								rx = 55,
								rz = 30,
								ry = -10,
							},
							AlaIzq = {
								rz = -12,
								rx = 5,
							},
							Cabeza = {
								ry = -8,
								rx = 5,
							},
							Bandera = {
								rx = -4,
							},
							Cola = {
								rx = 4,
							},
						},
					},
					{
						t = 0.3,
						pose = {
							Raiz = {
								ry = 22,
								pz = -0.55,
								rx = -8,
								py = 0.02,
							},
							AlaDer = {
								rx = -42,
								ry = 25,
								rz = 8,
							},
							AlaIzq = {
								rz = -28,
								rx = -10,
							},
							Cabeza = {
								rx = -8,
								ry = 6,
							},
							Bandera = {
								rx = 9,
							},
							Cola = {
								rx = -8,
							},
							PataIzq = {
								rx = 10,
							},
							PataDer = {
								rx = -8,
							},
						},
					},
					{
						t = 0.45,
						pose = {
							Raiz = {
								ry = 26,
								pz = -0.45,
								rx = -6,
								py = 0.02,
							},
							AlaDer = {
								rx = -52,
								ry = 28,
								rz = 5,
							},
							AlaIzq = {
								rz = -22,
								rx = -6,
							},
							Cabeza = {
								rx = -5,
								ry = 6,
							},
							Bandera = {
								rx = 5,
							},
							Cola = {
								rx = -5,
							},
							PataIzq = {
								rx = 8,
							},
							PataDer = {
								rx = -7,
							},
						},
					},
					{
						t = 0.75,
						pose = {},
					},
				},
			},
			TajoGiratorio = {
				duracion = 1.0,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.2,
						pose = {
							Raiz = {
								ry = 35,
								py = -0.03,
							},
							AlaDer = {
								rz = 55,
								ry = -70,
								rx = -50,
							},
							AlaIzq = {
								rz = -55,
								rx = -10,
							},
							Cabeza = {
								ry = -15,
							},
							Bandera = {
								rz = -6,
							},
							Cola = {
								rz = -6,
							},
						},
					},
					{
						t = 0.2,
						pose = {
							Raiz = {
								ry = 395,
								py = -0.03,
							},
							AlaDer = {
								rz = 55,
								ry = -70,
								rx = -50,
							},
							AlaIzq = {
								rz = -55,
								rx = -10,
							},
							Cabeza = {
								ry = -15,
							},
							Bandera = {
								rz = -6,
							},
							Cola = {
								rz = -6,
							},
						},
					},
					{
						t = 0.62,
						pose = {
							Raiz = {
								ry = 0,
								py = -0.02,
							},
							AlaDer = {
								rz = 55,
								ry = -70,
								rx = -50,
							},
							AlaIzq = {
								rz = -55,
								rx = -10,
							},
							Cabeza = {
								ry = 12,
							},
							Bandera = {
								rz = 12,
							},
							Cola = {
								rz = 12,
							},
						},
					},
					{
						t = 1.0,
						pose = {},
					},
				},
			},
			DefensaAcero = {
				duracion = 1.0,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.2,
						pose = {
							Raiz = {
								ry = -12,
							},
							AlaDer = {
								rx = 25,
								ry = 25,
							},
							AlaIzq = {
								rz = -25,
								rx = 10,
							},
							Cabeza = {
								rx = -6,
								ry = 6,
							},
							PataIzq = {
								rx = 8,
							},
							PataDer = {
								rx = -8,
							},
							Bandera = {
								rx = 4,
							},
						},
					},
					{
						t = 0.8,
						pose = {
							Raiz = {
								ry = -12,
							},
							AlaDer = {
								rx = 27,
								ry = 25,
							},
							AlaIzq = {
								rz = -25,
								rx = 10,
							},
							Cabeza = {
								rx = -6,
								ry = 6,
							},
							PataIzq = {
								rx = 8,
							},
							PataDer = {
								rx = -8,
							},
							Bandera = {
								rx = 4,
							},
						},
					},
					{
						t = 1.0,
						pose = {},
					},
				},
			},
			Golpeado = {
				duracion = 0.4,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.1,
						pose = {
							Raiz = {
								rx = 8,
								pz = 0.25,
							},
							Cabeza = {
								rx = 15,
							},
							AlaIzq = {
								rz = -15,
							},
							AlaDer = {
								rz = 10,
							},
							Bandera = {
								rx = -8,
							},
						},
					},
					{
						t = 0.4,
						pose = {},
					},
				},
			},
			Derrota = {
				duracion = 1.2,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.35,
						pose = {
							Raiz = {
								py = -0.05,
								rx = -12,
							},
							Cabeza = {
								rx = -20,
							},
							AlaDer = {
								rx = -30,
								rz = 10,
							},
							AlaIzq = {
								rz = -10,
							},
							PataIzq = {
								rx = 15,
							},
							PataDer = {
								rx = 15,
							},
							Bandera = {
								rx = 8,
							},
						},
					},
					{
						t = 1.2,
						pose = {
							Raiz = {
								py = -1.36,
								rz = 82,
								rx = -8,
							},
							Cabeza = {
								rx = 25,
								rz = -20,
							},
							AlaDer = {
								rz = 45,
								rx = -20,
							},
							AlaIzq = {
								rz = -20,
							},
							PataIzq = {
								rx = 30,
							},
							PataDer = {
								rx = -15,
							},
							Bandera = {
								rz = -15,
							},
							Cola = {
								rz = -10,
							},
						},
					},
				},
			},
		},
	},
}
