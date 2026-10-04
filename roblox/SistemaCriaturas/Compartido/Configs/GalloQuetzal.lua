-- Generado por herramientas/criaturas/generar.py. No lo edites a mano: cambia el archivo
-- herramientas/criaturas/galloquetzal.py y vuelve a generar.
return {
	nombre = "Gallo Quetzal",
	vida = 900,
	velocidad = 16,
	comportamiento = "normal",
	radioDeteccion = 50,
	radioPatrulla = 20,
	radioPersecucion = 100,
	reaparecer = 120,
	colorUI = Color3.fromRGB(60, 215, 140),
	habilidades = {
		{
			nombre = "Mordida de Serpiente",
			tipo = "Golpe",
			anim = "MordidaSerpiente",
			rango = 9,
			alcance = 10,
			angulo = 140,
			danio = 22,
			empuje = 35,
			cooldown = 3,
			retraso = 0.35,
			color = Color3.fromRGB(80, 240, 150),
		},
		{
			nombre = "Lluvia de Plumas",
			tipo = "Proyectil",
			anim = "LluviaPlumas",
			rango = 45,
			cantidad = 7,
			dispersion = 50,
			forma = "pluma",
			velocidad = 70,
			tamano = 1.3,
			radioExplosion = 0,
			danio = 10,
			cooldown = 6,
			retraso = 0.4,
			color = Color3.fromRGB(40, 220, 110),
		},
		{
			nombre = "Viento Divino",
			tipo = "Onda",
			anim = "VientoDivino",
			rango = 14,
			radio = 18,
			danio = 25,
			empuje = 90,
			cooldown = 9,
			retraso = 0.6,
			color = Color3.fromRGB(150, 255, 210),
		},
		{
			nombre = "Paso Sagrado",
			tipo = "Teletransporte",
			anim = "PasoSagrado",
			rango = 50,
			danio = 15,
			radio = 8,
			cooldown = 12,
			retraso = 0.3,
			color = Color3.fromRGB(255, 205, 60),
		},
	},
	tipo = "GalloQuetzal",
	rig = {
		marcador = 2.0,
		suelo = -5.035,
		partes = {
			Cabeza = {
				padre = "Cuerpo",
				union = { 0.9244, -0.0, 1.065 },
			},
			Penacho = {
				padre = "Cabeza",
				union = { 1.5244, -0.0, 2.895 },
			},
			AlaIzq = {
				padre = "Cuerpo",
				union = { 0.7044, -1.12, 0.915 },
			},
			AlaDer = {
				padre = "Cuerpo",
				union = { 0.7044, 1.12, 0.915 },
			},
			PataIzq = {
				padre = "Cuerpo",
				union = { -0.0956, -0.66, -0.985 },
			},
			PataDer = {
				padre = "Cuerpo",
				union = { -0.0956, 0.66, -0.985 },
			},
			Cola1 = {
				padre = "Cuerpo",
				union = { -1.7456, -0.0, 0.015 },
			},
			Cola2 = {
				padre = "Cola1",
				union = { -2.9456, -0.0, -0.485 },
			},
			Cola3 = {
				padre = "Cola2",
				union = { -4.0956, -0.0, -0.035 },
			},
			Cola4 = {
				padre = "Cola3",
				union = { -4.6456, -0.0, 1.085 },
			},
		},
		adjuntos = {
			Cuerpo__Brillo_jade_brillo = "Cuerpo",
			Cabeza__Brillo_jade_brillo = "Cabeza",
			Penacho__Brillo_jade_brillo = "Penacho",
			AlaIzq__Brillo_jade_brillo = "AlaIzq",
			AlaDer__Brillo_jade_brillo = "AlaDer",
			PataIzq__Brillo_jade_brillo = "PataIzq",
			PataDer__Brillo_jade_brillo = "PataDer",
		},
	},
	coloresBrillo = {
		Cuerpo__Brillo_jade_brillo = Color3.fromRGB(76, 255, 158),
		Cabeza__Brillo_jade_brillo = Color3.fromRGB(76, 255, 158),
		Penacho__Brillo_jade_brillo = Color3.fromRGB(76, 255, 158),
		AlaIzq__Brillo_jade_brillo = Color3.fromRGB(76, 255, 158),
		AlaDer__Brillo_jade_brillo = Color3.fromRGB(76, 255, 158),
		PataIzq__Brillo_jade_brillo = Color3.fromRGB(76, 255, 158),
		PataDer__Brillo_jade_brillo = Color3.fromRGB(76, 255, 158),
	},
	animaciones = {
		ciclos = {
			Idle = {
				Raiz = {
					{ "py", 0.06, 0.8, 0 },
					{ "rx", 1.5, 0.4, 0.3 },
				},
				Cabeza = {
					{ "rx", 4, 0.8, 0.1 },
					{ "ry", 10, 0.3, 0 },
				},
				Penacho = {
					{ "rx", 3, 0.8, 0.35 },
					{ "rz", 2, 0.5, 0 },
				},
				AlaIzq = {
					{ "rz", -3, 0.8, 0 },
				},
				PataIzq = {
					{ "rx", -1.5, 0.4, 0.3 },
				},
				PataDer = {
					{ "rx", -1.5, 0.4, 0.3 },
				},
				Cola1 = {
					{ "ry", 6.0, 0.6, 0.0 },
					{ "rx", 3, 0.6, 0.25 },
				},
				Cola2 = {
					{ "ry", 10, 0.6, 0.17 },
					{ "rx", 3, 0.6, 0.42 },
				},
				Cola3 = {
					{ "ry", 6.0, 0.6, 0.34 },
					{ "rz", -7.0, 0.6, 0.34 },
					{ "rx", 3, 0.6, 0.59 },
				},
				Cola4 = {
					{ "rz", -12.0, 0.6, 0.51 },
					{ "rx", 3.9, 0.6, 0.76 },
				},
				AlaDer = {
					{ "rz", 3, 0.8, 0 },
				},
			},
			Caminar = {
				Raiz = {
					{ "py", 0.14, 3.2, 0.25 },
					{ "rz", 3, 1.6, 0 },
					{ "ry", 3, 1.6, 0.25 },
				},
				Cabeza = {
					{ "pz", 0.18, 3.2, 0 },
					{ "rx", 5, 3.2, 0.25 },
				},
				Penacho = {
					{ "rx", 5, 3.2, 0.4 },
					{ "rz", 3, 1.6, 0.1 },
				},
				AlaIzq = {
					{ "rz", -7, 1.6, 0.25 },
				},
				PataIzq = {
					{ "rx", 27, 1.6, 0 },
				},
				PataDer = {
					{ "rx", 27, 1.6, 0.5 },
				},
				Cola1 = {
					{ "ry", 7.2, 1.6, 0.0 },
					{ "rx", 3, 1.6, 0.25 },
				},
				Cola2 = {
					{ "ry", 12, 1.6, 0.17 },
					{ "rx", 3, 1.6, 0.42 },
				},
				Cola3 = {
					{ "ry", 7.2, 1.6, 0.34 },
					{ "rz", -8.4, 1.6, 0.34 },
					{ "rx", 3, 1.6, 0.59 },
				},
				Cola4 = {
					{ "rz", -14.4, 1.6, 0.51 },
					{ "rx", 3.9, 1.6, 0.76 },
				},
				AlaDer = {
					{ "rz", 7, 1.6, 0.25 },
				},
			},
		},
		clips = {
			MordidaSerpiente = {
				duracion = 0.95,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.18,
						pose = {
							Cabeza = {
								rx = 25,
								pz = 0.1,
							},
							Penacho = {
								rx = -8,
							},
							AlaIzq = {
								rz = -18,
							},
							Cola1 = {
								rx = 14,
							},
							Cola2 = {
								rx = 12,
								ry = 8,
							},
							Cola3 = {
								rx = 10,
							},
							Cola4 = {
								rx = 10,
							},
							Raiz = {
								rx = 8,
								pz = 0.3,
							},
							PataIzq = {
								rx = -8,
							},
							PataDer = {
								rx = -8,
							},
							AlaDer = {
								rz = 18,
							},
						},
					},
					{
						t = 0.35,
						pose = {
							Cabeza = {
								rx = -40,
								pz = -0.3,
							},
							Penacho = {
								rx = 15,
							},
							AlaIzq = {
								rz = -35,
								ry = -15,
							},
							Cola1 = {
								rx = -18,
							},
							Cola2 = {
								rx = -24,
							},
							Cola3 = {
								rx = -28,
							},
							Cola4 = {
								rx = -32,
							},
							Raiz = {
								rx = -12,
								pz = -0.5,
							},
							PataIzq = {
								rx = 12,
							},
							PataDer = {
								rx = 12,
							},
							AlaDer = {
								rz = 35,
								ry = 15,
							},
						},
					},
					{
						t = 0.5,
						pose = {
							Cabeza = {
								rx = -25,
								pz = -0.2,
							},
							Penacho = {
								rx = 8,
							},
							AlaIzq = {
								rz = -22,
							},
							Cola1 = {
								rx = -12,
							},
							Cola2 = {
								rx = -16,
							},
							Cola3 = {
								rx = -18,
							},
							Cola4 = {
								rx = -12,
							},
							Raiz = {
								rx = -8,
								pz = -0.35,
							},
							PataIzq = {
								rx = 8,
							},
							PataDer = {
								rx = 8,
							},
							AlaDer = {
								rz = 22,
							},
						},
					},
					{
						t = 0.95,
						pose = {},
					},
				},
			},
			LluviaPlumas = {
				duracion = 1.1,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.25,
						pose = {
							Cabeza = {
								rx = 18,
							},
							Penacho = {
								rx = -14,
							},
							AlaIzq = {
								rx = -60,
								ry = -30,
								rz = -75,
							},
							Cola1 = {
								rx = -8,
							},
							Cola3 = {
								rx = -8,
							},
							Cola4 = {
								rx = -18,
							},
							Raiz = {
								py = 0.12,
								rx = 8,
								pz = 0.2,
							},
							PataIzq = {
								rx = -8,
							},
							PataDer = {
								rx = -8,
							},
							AlaDer = {
								rx = -60,
								ry = 30,
								rz = 75,
							},
						},
					},
					{
						t = 0.4,
						pose = {
							Cabeza = {
								rx = -18,
								pz = -0.15,
							},
							Penacho = {
								rx = 16,
							},
							AlaIzq = {
								rx = 5,
								ry = -100,
								rz = -45,
							},
							Cola1 = {
								rx = 6,
							},
							Cola2 = {
								rx = 4,
							},
							Cola4 = {
								rx = 12,
							},
							Raiz = {
								rx = -10,
								pz = -0.25,
							},
							PataIzq = {
								rx = 10,
							},
							PataDer = {
								rx = 10,
							},
							AlaDer = {
								rx = 5,
								ry = 100,
								rz = 45,
							},
						},
					},
					{
						t = 0.6,
						pose = {
							Cabeza = {
								rx = -8,
							},
							Penacho = {
								rx = 6,
							},
							AlaIzq = {
								rx = 0,
								ry = -65,
								rz = -25,
							},
							Raiz = {
								rx = -6,
								pz = -0.12,
							},
							PataIzq = {
								rx = 6,
							},
							PataDer = {
								rx = 6,
							},
							AlaDer = {
								rx = 0,
								ry = 65,
								rz = 25,
							},
						},
					},
					{
						t = 1.1,
						pose = {},
					},
				},
			},
			VientoDivino = {
				duracion = 1.4,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.2,
						pose = {
							Cabeza = {
								rx = -10,
							},
							AlaIzq = {
								rz = -25,
								ry = -15,
							},
							Raiz = {
								py = -0.1,
								rx = -6,
							},
							PataIzq = {
								rx = 6,
							},
							PataDer = {
								rx = 6,
							},
							AlaDer = {
								rz = 25,
								ry = 15,
							},
						},
					},
					{
						t = 0.42,
						pose = {
							Cabeza = {
								rx = 20,
							},
							Penacho = {
								rx = -12,
							},
							AlaIzq = {
								rx = -75,
								ry = -30,
								rz = -85,
							},
							Cola1 = {
								rx = -10,
							},
							Cola2 = {
								rx = -8,
							},
							Cola3 = {
								rx = -8,
							},
							Cola4 = {
								rx = -12,
							},
							Raiz = {
								py = 0.55,
								rx = 10,
							},
							PataIzq = {
								rx = -10,
							},
							PataDer = {
								rx = -10,
							},
							AlaDer = {
								rx = -75,
								ry = 30,
								rz = 85,
							},
						},
					},
					{
						t = 0.6,
						pose = {
							Cabeza = {
								rx = -20,
							},
							Penacho = {
								rx = 22,
							},
							AlaIzq = {
								rx = 25,
								ry = -45,
								rz = -50,
							},
							Cola1 = {
								rx = 10,
							},
							Cola2 = {
								rx = 10,
							},
							Cola3 = {
								rx = 8,
							},
							Cola4 = {
								rx = 14,
							},
							Raiz = {
								py = -0.1,
								rx = -8,
							},
							PataIzq = {
								rx = 8,
							},
							PataDer = {
								rx = 8,
							},
							AlaDer = {
								rx = 25,
								ry = 45,
								rz = 50,
							},
						},
					},
					{
						t = 0.85,
						pose = {
							Cabeza = {
								rx = -10,
							},
							Penacho = {
								rx = 10,
							},
							AlaIzq = {
								rx = 10,
								ry = -25,
								rz = -25,
							},
							Cola4 = {
								rx = 5,
							},
							Raiz = {
								py = -0.06,
								rx = -5,
							},
							PataIzq = {
								rx = 5,
							},
							PataDer = {
								rx = 5,
							},
							AlaDer = {
								rx = 10,
								ry = 25,
								rz = 25,
							},
						},
					},
					{
						t = 1.4,
						pose = {},
					},
				},
			},
			PasoSagrado = {
				duracion = 1.0,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.15,
						pose = {
							Cabeza = {
								rx = -25,
								pz = -0.15,
							},
							Penacho = {
								rx = 20,
							},
							AlaIzq = {
								rz = 8,
								ry = 8,
							},
							Cola1 = {
								rx = 10,
							},
							Cola2 = {
								rx = 12,
							},
							Cola3 = {
								rx = 10,
							},
							Cola4 = {
								rx = 8,
							},
							Raiz = {
								py = -0.08,
								rx = -10,
							},
							PataIzq = {
								rx = 10,
							},
							PataDer = {
								rx = 10,
							},
							AlaDer = {
								rz = -8,
								ry = -8,
							},
						},
					},
					{
						t = 0.3,
						pose = {
							Cabeza = {
								rx = 22,
							},
							Penacho = {
								rx = -18,
							},
							AlaIzq = {
								rx = -50,
								ry = -45,
								rz = -75,
							},
							Cola1 = {
								rx = -12,
							},
							Cola2 = {
								rx = -14,
							},
							Cola3 = {
								rx = -10,
							},
							Cola4 = {
								rx = -18,
							},
							Raiz = {
								py = 0.3,
								rx = 6,
							},
							PataIzq = {
								rx = -6,
							},
							PataDer = {
								rx = -6,
							},
							AlaDer = {
								rx = -50,
								ry = 45,
								rz = 75,
							},
						},
					},
					{
						t = 0.55,
						pose = {
							Cabeza = {
								rx = 10,
							},
							Penacho = {
								rx = -8,
							},
							AlaIzq = {
								rx = -30,
								ry = -30,
								rz = -45,
							},
							Cola4 = {
								rx = -8,
							},
							Raiz = {
								py = 0.12,
								rx = 3,
							},
							PataIzq = {
								rx = -3,
							},
							PataDer = {
								rx = -3,
							},
							AlaDer = {
								rx = -30,
								ry = 30,
								rz = 45,
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
							Cabeza = {
								rx = 20,
							},
							Penacho = {
								rx = -10,
							},
							AlaIzq = {
								rz = -20,
							},
							Cola2 = {
								ry = 10,
							},
							Cola4 = {
								rz = -12,
							},
							Raiz = {
								rx = 8,
								pz = 0.3,
							},
							PataIzq = {
								rx = -8,
							},
							PataDer = {
								rx = -8,
							},
							AlaDer = {
								rz = 20,
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
				duracion = 1.6,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.3,
						pose = {
							Cabeza = {
								rx = 30,
							},
							Penacho = {
								rx = -10,
							},
							AlaIzq = {
								rz = -50,
							},
							Cola4 = {
								rx = -15,
							},
							Raiz = {
								rx = 12,
								py = 0.1,
							},
							PataIzq = {
								rx = -12,
							},
							PataDer = {
								rx = -12,
							},
							AlaDer = {
								rz = 50,
							},
						},
					},
					{
						t = 0.65,
						pose = {
							Cabeza = {
								rx = -20,
								ry = 20,
							},
							Penacho = {
								rx = 20,
							},
							AlaIzq = {
								rz = -25,
							},
							Raiz = {
								rx = 4,
								rz = -10,
							},
							PataIzq = {
								rx = -4,
							},
							PataDer = {
								rx = -4,
							},
							AlaDer = {
								rz = 25,
							},
						},
					},
					{
						t = 1.05,
						pose = {
							Raiz = {
								rx = -10,
								py = -1.0,
							},
							PataIzq = {
								rx = -55,
							},
							PataDer = {
								rx = -55,
							},
							Cabeza = {
								rx = -10,
								ry = 25,
							},
							Penacho = {
								rx = 25,
							},
							AlaIzq = {
								rz = -35,
								ry = -15,
							},
							Cola3 = {
								rx = 15,
							},
							Cola4 = {
								rx = 10,
							},
							AlaDer = {
								rz = 35,
								ry = 15,
							},
						},
					},
					{
						t = 1.6,
						pose = {
							Raiz = {
								rx = -18,
								py = -3.3,
							},
							PataIzq = {
								rx = -72,
							},
							PataDer = {
								rx = -72,
							},
							Cabeza = {
								rx = -35,
								ry = 35,
							},
							Penacho = {
								rx = 40,
							},
							AlaIzq = {
								rz = -15,
								ry = -35,
							},
							Cola1 = {
								rx = 12,
							},
							Cola2 = {
								rx = 15,
								ry = -12,
							},
							Cola3 = {
								rx = 45,
								ry = -10,
							},
							Cola4 = {
								rx = 45,
							},
							AlaDer = {
								rz = 15,
								ry = 35,
							},
						},
					},
				},
			},
		},
	},
}
