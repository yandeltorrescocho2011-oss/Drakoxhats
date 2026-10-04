-- Generado por herramientas/criaturas/generar.py. No lo edites a mano: cambia el archivo
-- herramientas/criaturas/gallorelampago.py y vuelve a generar.
return {
	nombre = "Gallo Relámpago",
	vida = 260,
	velocidad = 22,
	comportamiento = "normal",
	radioDeteccion = 40,
	radioPatrulla = 18,
	radioPersecucion = 80,
	reaparecer = 25,
	colorUI = Color3.fromRGB(70, 215, 255),
	habilidades = {
		{
			nombre = "Picotazo Eléctrico",
			tipo = "Golpe",
			anim = "Picotazo",
			rango = 6,
			alcance = 6,
			angulo = 70,
			danio = 10,
			empuje = 25,
			aturdir = 0.2,
			cooldown = 1.5,
			retraso = 0.2,
			color = Color3.fromRGB(120, 235, 255),
		},
		{
			nombre = "Rayo Encadenado",
			tipo = "Cadena",
			anim = "RayoEncadenado",
			rango = 30,
			danio = 16,
			saltos = 3,
			radioSalto = 15,
			cooldown = 7,
			retraso = 0.4,
			color = Color3.fromRGB(255, 230, 70),
		},
		{
			nombre = "Embestida Relámpago",
			tipo = "Embestida",
			anim = "Embestida",
			rango = 28,
			distancia = 26,
			velocidad = 90,
			danio = 20,
			empuje = 40,
			ancho = 5,
			cooldown = 6,
			retraso = 0.3,
			color = Color3.fromRGB(80, 220, 255),
		},
	},
	tipo = "GalloRelampago",
	rig = {
		marcador = 2.0,
		suelo = -3.2026,
		partes = {
			Cabeza = {
				padre = "Cuerpo",
				union = { 0.8509, -0.0, 0.7524 },
			},
			Cresta = {
				padre = "Cabeza",
				union = { 1.3809, -0.0, 2.6024 },
			},
			AlaIzq = {
				padre = "Cuerpo",
				union = { 0.8009, -0.62, 0.6524 },
			},
			AlaDer = {
				padre = "Cuerpo",
				union = { 0.8009, 0.62, 0.6524 },
			},
			PataIzq = {
				padre = "Cuerpo",
				union = { 0.1009, -0.42, -0.5476 },
			},
			PataDer = {
				padre = "Cuerpo",
				union = { 0.1009, 0.42, -0.5476 },
			},
			Cola1 = {
				padre = "Cuerpo",
				union = { -1.0491, -0.0, 0.0524 },
			},
			Cola2 = {
				padre = "Cola1",
				union = { -1.6991, -0.0, 1.3824 },
			},
		},
		adjuntos = {
			Cuerpo__Brillo_rayo = "Cuerpo",
			Cabeza__Brillo_cian_brillo = "Cabeza",
			Cresta__Brillo_rayo_blanco = "Cresta",
			Cresta__Brillo_rayo = "Cresta",
			AlaIzq__Brillo_rayo = "AlaIzq",
			AlaDer__Brillo_rayo = "AlaDer",
			PataIzq__Brillo_cian_brillo = "PataIzq",
			PataDer__Brillo_cian_brillo = "PataDer",
			Cola2__Brillo_cian_brillo = "Cola2",
		},
	},
	coloresBrillo = {
		Cuerpo__Brillo_rayo = Color3.fromRGB(255, 219, 38),
		Cabeza__Brillo_cian_brillo = Color3.fromRGB(76, 242, 255),
		Cresta__Brillo_rayo_blanco = Color3.fromRGB(255, 242, 133),
		Cresta__Brillo_rayo = Color3.fromRGB(255, 219, 38),
		AlaIzq__Brillo_rayo = Color3.fromRGB(255, 219, 38),
		AlaDer__Brillo_rayo = Color3.fromRGB(255, 219, 38),
		PataIzq__Brillo_cian_brillo = Color3.fromRGB(76, 242, 255),
		PataDer__Brillo_cian_brillo = Color3.fromRGB(76, 242, 255),
		Cola2__Brillo_cian_brillo = Color3.fromRGB(76, 242, 255),
	},
	animaciones = {
		ciclos = {
			Idle = {
				Raiz = {
					{ "py", 0.04, 1.2, 0 },
					{ "rx", 1.5, 0.6, 0.3 },
				},
				Cabeza = {
					{ "rx", 4, 0.6, 0 },
					{ "ry", 14, 0.35, 0.1 },
				},
				Cresta = {
					{ "rz", 4, 3.5, 0 },
					{ "rx", 3, 2.1, 0.3 },
				},
				AlaIzq = {
					{ "rz", -4, 1.2, 0 },
				},
				Cola1 = {
					{ "rx", 3, 0.6, 0.2 },
					{ "ry", 3, 0.4, 0 },
				},
				Cola2 = {
					{ "rx", 5, 0.6, 0.4 },
					{ "ry", 4, 0.4, 0.25 },
				},
				AlaDer = {
					{ "rz", 4, 1.2, 0 },
				},
			},
			Caminar = {
				Raiz = {
					{ "py", 0.15, 5.2, 0.25 },
					{ "rz", 3, 2.6, 0 },
				},
				Cabeza = {
					{ "pz", 0.15, 5.2, 0 },
					{ "rx", 5, 5.2, 0.25 },
				},
				Cresta = {
					{ "rx", 6, 5.2, 0.4 },
				},
				AlaIzq = {
					{ "rz", -8, 2.6, 0.25 },
				},
				PataIzq = {
					{ "rx", 32, 2.6, 0 },
				},
				PataDer = {
					{ "rx", 32, 2.6, 0.5 },
				},
				Cola1 = {
					{ "rx", 5, 5.2, 0.1 },
					{ "ry", 4, 2.6, 0 },
				},
				Cola2 = {
					{ "rx", 6, 5.2, 0.3 },
					{ "ry", 5, 2.6, 0.2 },
				},
				AlaDer = {
					{ "rz", 8, 2.6, 0.25 },
				},
			},
		},
		clips = {
			Picotazo = {
				duracion = 0.6,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.11,
						pose = {
							Raiz = {
								rx = 6,
								pz = 0.25,
							},
							Cabeza = {
								rx = 25,
								pz = 0.15,
							},
							Cresta = {
								rx = 15,
							},
							AlaIzq = {
								rz = -15,
							},
							Cola1 = {
								rx = -6,
							},
							AlaDer = {
								rz = 15,
							},
						},
					},
					{
						t = 0.2,
						pose = {
							Raiz = {
								rx = -14,
								pz = -0.35,
							},
							Cabeza = {
								rx = -45,
								pz = -0.3,
							},
							Cresta = {
								rx = -12,
							},
							AlaIzq = {
								rz = -30,
							},
							Cola1 = {
								rx = 8,
							},
							Cola2 = {
								rx = 10,
							},
							AlaDer = {
								rz = 30,
							},
						},
					},
					{
						t = 0.32,
						pose = {
							Raiz = {
								rx = -10,
								pz = -0.25,
							},
							Cabeza = {
								rx = -35,
								pz = -0.2,
							},
							AlaIzq = {
								rz = -20,
							},
							Cola2 = {
								rx = -6,
							},
							AlaDer = {
								rz = 20,
							},
						},
					},
					{
						t = 0.6,
						pose = {},
					},
				},
			},
			RayoEncadenado = {
				duracion = 1.1,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.28,
						pose = {
							Raiz = {
								py = -0.1,
								rx = -6,
							},
							Cabeza = {
								rx = -12,
							},
							Cresta = {
								rx = -12,
							},
							AlaIzq = {
								rz = -40,
							},
							Cola1 = {
								rx = 6,
							},
							AlaDer = {
								rz = 40,
							},
						},
					},
					{
						t = 0.4,
						pose = {
							Raiz = {
								py = 0.35,
								rx = 10,
							},
							Cabeza = {
								rx = 22,
							},
							Cresta = {
								rx = 20,
							},
							AlaIzq = {
								rz = -80,
								ry = -15,
							},
							Cola1 = {
								rx = -15,
							},
							Cola2 = {
								rx = -10,
							},
							AlaDer = {
								rz = 80,
								ry = 15,
							},
						},
					},
					{
						t = 0.65,
						pose = {
							Raiz = {
								py = 0.25,
								rx = 8,
							},
							Cabeza = {
								rx = 16,
							},
							Cresta = {
								rx = 14,
							},
							AlaIzq = {
								rz = -70,
								ry = -12,
							},
							Cola1 = {
								rx = -12,
							},
							Cola2 = {
								rx = 6,
							},
							AlaDer = {
								rz = 70,
								ry = 12,
							},
						},
					},
					{
						t = 1.1,
						pose = {},
					},
				},
			},
			Embestida = {
				duracion = 1.15,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.2,
						pose = {
							Raiz = {
								py = -0.3,
								rx = -12,
								pz = 0.35,
							},
							Cabeza = {
								rx = 15,
							},
							AlaIzq = {
								rz = -30,
							},
							PataIzq = {
								rx = 40,
							},
							PataDer = {
								rx = -16,
							},
							Cola1 = {
								rx = -12,
							},
							AlaDer = {
								rz = 30,
							},
						},
					},
					{
						t = 0.3,
						pose = {
							Raiz = {
								py = -0.15,
								rx = -28,
								pz = -0.6,
							},
							Cabeza = {
								rx = -20,
								pz = -0.2,
							},
							Cresta = {
								rx = 25,
							},
							AlaIzq = {
								rz = -55,
								ry = -30,
							},
							Cola1 = {
								rx = 20,
							},
							Cola2 = {
								rx = 15,
							},
							PataIzq = {
								rx = -10,
							},
							PataDer = {
								rx = -10,
							},
							AlaDer = {
								rz = 55,
								ry = 30,
							},
						},
					},
					{
						t = 0.55,
						pose = {
							Raiz = {
								py = -0.1,
								rx = -25,
								pz = -0.5,
							},
							Cabeza = {
								rx = -18,
								pz = -0.2,
							},
							Cresta = {
								rx = 22,
							},
							AlaIzq = {
								rz = -60,
								ry = -30,
							},
							Cola1 = {
								rx = 18,
							},
							Cola2 = {
								rx = 20,
							},
							PataIzq = {
								rx = -12,
							},
							PataDer = {
								rx = -12,
							},
							AlaDer = {
								rz = 60,
								ry = 30,
							},
						},
					},
					{
						t = 0.8,
						pose = {
							Raiz = {
								py = -0.25,
								rx = -8,
							},
							Cabeza = {
								rx = 10,
							},
							AlaIzq = {
								rz = -35,
							},
							PataIzq = {
								rx = 33,
							},
							PataDer = {
								rx = -17,
							},
							Cola2 = {
								rx = -8,
							},
							AlaDer = {
								rz = 35,
							},
						},
					},
					{
						t = 1.15,
						pose = {},
					},
				},
			},
			Golpeado = {
				duracion = 0.35,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.08,
						pose = {
							Raiz = {
								rx = 10,
								pz = 0.25,
							},
							Cabeza = {
								rx = 20,
							},
							Cresta = {
								rx = 15,
							},
							AlaIzq = {
								rz = -25,
							},
							AlaDer = {
								rz = 25,
							},
						},
					},
					{
						t = 0.35,
						pose = {},
					},
				},
			},
			Derrota = {
				duracion = 1.3,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.25,
						pose = {
							Raiz = {
								rx = 12,
								py = 0.1,
							},
							Cabeza = {
								rx = 30,
							},
							Cresta = {
								rx = 20,
							},
							AlaIzq = {
								rz = -50,
							},
							AlaDer = {
								rz = 50,
							},
						},
					},
					{
						t = 0.55,
						pose = {
							Raiz = {
								rx = 5,
								rz = -10,
							},
							Cabeza = {
								rx = -20,
								ry = 20,
							},
							AlaIzq = {
								rz = -30,
							},
							AlaDer = {
								rz = 30,
							},
						},
					},
					{
						t = 1.3,
						pose = {
							Raiz = {
								rz = -85,
								py = -2.25,
							},
							Cabeza = {
								rx = -25,
								rz = -20,
							},
							Cresta = {
								rx = 15,
							},
							AlaIzq = {
								rz = -35,
							},
							AlaDer = {
								rz = -10,
							},
							PataIzq = {
								rx = 25,
							},
							PataDer = {
								rx = -15,
							},
							Cola1 = {
								rx = 15,
							},
						},
					},
				},
			},
		},
	},
}
