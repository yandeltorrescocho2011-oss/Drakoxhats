-- Generado por herramientas/criaturas/generar.py. No lo edites a mano: cambia el archivo
-- herramientas/criaturas/gallocatrin.py y vuelve a generar.
return {
	nombre = "Gallo Catrín",
	vida = 240,
	velocidad = 20,
	comportamiento = "normal",
	radioDeteccion = 38,
	radioPatrulla = 16,
	radioPersecucion = 75,
	reaparecer = 25,
	colorUI = Color3.fromRGB(170, 80, 255),
	habilidades = {
		{
			nombre = "Picotazo de Hueso",
			tipo = "Golpe",
			anim = "PicotazoHueso",
			rango = 6,
			cooldown = 1.8,
			retraso = 0.2,
			danio = 10,
			alcance = 6,
			angulo = 90,
			empuje = 20,
			color = Color3.fromRGB(245, 235, 215),
		},
		{
			nombre = "Huesos Malditos",
			tipo = "Proyectil",
			anim = "HuesosMalditos",
			rango = 35,
			cooldown = 4,
			retraso = 0.35,
			danio = 12,
			cantidad = 3,
			dispersion = 20,
			velocidad = 60,
			forma = "hueso",
			tamano = 1,
			radioExplosion = 0,
			color = Color3.fromRGB(180, 80, 255),
		},
		{
			nombre = "Forma Fantasma",
			tipo = "Fantasma",
			anim = "FormaFantasma",
			rango = 40,
			cooldown = 14,
			retraso = 0.3,
			duracion = 3,
			velocidadExtra = 1.6,
			color = Color3.fromRGB(150, 110, 255),
		},
		{
			nombre = "Grito del Más Allá",
			tipo = "Onda",
			anim = "GritoMasAlla",
			rango = 10,
			cooldown = 10,
			retraso = 0.5,
			danio = 10,
			radio = 14,
			empuje = 30,
			aturdir = 1.5,
			color = Color3.fromRGB(60, 240, 220),
		},
	},
	tipo = "GalloCatrin",
	rig = {
		marcador = 2.0,
		suelo = -3.0974,
		partes = {
			Cabeza = {
				padre = "Cuerpo",
				union = { 0.7872, -0.0, 0.6726 },
			},
			Mandibula = {
				padre = "Cabeza",
				union = { 1.7372, -0.0, 1.4426 },
			},
			Sombrero = {
				padre = "Cabeza",
				union = { 1.2372, -0.0, 2.1926 },
			},
			AlaIzq = {
				padre = "Cuerpo",
				union = { 0.5872, -0.8, 0.3126 },
			},
			AlaDer = {
				padre = "Cuerpo",
				union = { 0.5872, 0.8, 0.3126 },
			},
			PataIzq = {
				padre = "Cuerpo",
				union = { -0.1128, -0.42, -0.9074 },
			},
			PataDer = {
				padre = "Cuerpo",
				union = { -0.1128, 0.42, -0.9074 },
			},
			Cola = {
				padre = "Cuerpo",
				union = { -1.0628, -0.0, 0.3426 },
			},
		},
		adjuntos = {
			Cuerpo__Brillo_alma_morada = "Cuerpo",
			Cabeza__Brillo_alma_morada = "Cabeza",
			Cola__Brillo_alma_turquesa = "Cola",
			Cola__Brillo_alma_morada = "Cola",
			Cola__Vidrio = "Cola",
		},
	},
	coloresBrillo = {
		Cuerpo__Brillo_alma_morada = Color3.fromRGB(204, 97, 255),
		Cabeza__Brillo_alma_morada = Color3.fromRGB(204, 97, 255),
		Cola__Brillo_alma_turquesa = Color3.fromRGB(64, 255, 224),
		Cola__Brillo_alma_morada = Color3.fromRGB(204, 97, 255),
	},
	animaciones = {
		ciclos = {
			Idle = {
				Raiz = {
					{ "py", 0.05, 0.8, 0 },
					{ "rz", 1.5, 0.4, 0.2 },
				},
				Cabeza = {
					{ "rx", 4, 0.8, 0.1 },
					{ "ry", 9, 0.3, 0 },
				},
				Mandibula = {
					{ "rx", 2, 0.8, 0.6 },
				},
				Sombrero = {
					{ "rz", 2, 0.4, 0.5 },
				},
				AlaIzq = {
					{ "rz", -4, 0.8, 0 },
				},
				Cola = {
					{ "rz", 4, 0.5, 0 },
					{ "rx", 3, 0.8, 0.3 },
				},
				AlaDer = {
					{ "rz", 4, 0.8, 0 },
				},
			},
			Caminar = {
				Raiz = {
					{ "py", 0.08, 5.0, 0.25 },
					{ "rz", 3, 2.5, 0 },
					{ "ry", 4, 2.5, 0.25 },
				},
				Cabeza = {
					{ "rx", 7, 5.0, 0.0 },
					{ "pz", 0.08, 5.0, 0.25 },
				},
				Sombrero = {
					{ "rx", 3, 5.0, 0.1 },
				},
				AlaIzq = {
					{ "rz", -6, 2.5, 0 },
				},
				PataIzq = {
					{ "rx", 30, 2.5, 0 },
				},
				PataDer = {
					{ "rx", 30, 2.5, 0.5 },
				},
				Cola = {
					{ "rz", 6, 2.5, 0.2 },
					{ "rx", 4, 5.0, 0.4 },
				},
				AlaDer = {
					{ "rz", 6, 2.5, 0 },
				},
			},
		},
		clips = {
			PicotazoHueso = {
				duracion = 0.6,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.1,
						pose = {
							Raiz = {
								rx = 5,
								pz = 0.15,
							},
							Cabeza = {
								rx = 12,
								pz = 0.1,
							},
							Mandibula = {
								rx = -32,
							},
							Sombrero = {
								rx = -3,
							},
							AlaIzq = {
								rz = -15,
							},
							Cola = {
								rx = 4,
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
								rx = -8,
								pz = -0.4,
								py = -0.05,
							},
							Cabeza = {
								rx = -20,
								pz = -0.3,
								py = -0.08,
							},
							Mandibula = {
								rx = 0,
							},
							Sombrero = {
								rx = 6,
							},
							AlaIzq = {
								rz = -28,
								rx = -10,
							},
							Cola = {
								rx = -8,
							},
							PataIzq = {
								rx = 10,
							},
							PataDer = {
								rx = -10,
							},
							AlaDer = {
								rz = 28,
								rx = -10,
							},
						},
					},
					{
						t = 0.32,
						pose = {
							Raiz = {
								rx = -6,
								pz = -0.35,
								py = -0.04,
							},
							Cabeza = {
								rx = -15,
								pz = -0.25,
								py = -0.06,
							},
							Sombrero = {
								rx = 4,
							},
							AlaIzq = {
								rz = -20,
								rx = -6,
							},
							Cola = {
								rx = -6,
							},
							PataIzq = {
								rx = 8,
							},
							PataDer = {
								rx = -8,
							},
							AlaDer = {
								rz = 20,
								rx = -6,
							},
						},
					},
					{
						t = 0.6,
						pose = {},
					},
				},
			},
			HuesosMalditos = {
				duracion = 0.8,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.2,
						pose = {
							Raiz = {
								rx = 8,
								pz = 0.2,
								py = 0.05,
							},
							Cabeza = {
								rx = 10,
							},
							Mandibula = {
								rx = -12,
							},
							AlaIzq = {
								rz = -100,
								ry = 15,
								rx = 15,
							},
							Cola = {
								rx = -10,
							},
							Sombrero = {
								rx = -4,
							},
							AlaDer = {
								rz = 100,
								ry = -15,
								rx = 15,
							},
						},
					},
					{
						t = 0.35,
						pose = {
							Raiz = {
								rx = -9,
								pz = -0.35,
							},
							Cabeza = {
								rx = -12,
								pz = -0.1,
							},
							Mandibula = {
								rx = -34,
							},
							AlaIzq = {
								rz = -20,
								ry = -85,
								rx = -20,
							},
							Cola = {
								rx = 8,
							},
							Sombrero = {
								rx = 7,
							},
							PataIzq = {
								rx = 8,
							},
							PataDer = {
								rx = -8,
							},
							AlaDer = {
								rz = 20,
								ry = 85,
								rx = -20,
							},
						},
					},
					{
						t = 0.5,
						pose = {
							Raiz = {
								rx = -7,
								pz = -0.3,
							},
							Cabeza = {
								rx = -9,
								pz = -0.08,
							},
							Mandibula = {
								rx = -22,
							},
							AlaIzq = {
								rz = -15,
								ry = -72,
								rx = -14,
							},
							Cola = {
								rx = 5,
							},
							Sombrero = {
								rx = 4,
							},
							PataIzq = {
								rx = 6,
							},
							PataDer = {
								rx = -6,
							},
							AlaDer = {
								rz = 15,
								ry = 72,
								rx = -14,
							},
						},
					},
					{
						t = 0.8,
						pose = {},
					},
				},
			},
			FormaFantasma = {
				duracion = 0.9,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.15,
						pose = {
							Raiz = {
								py = -0.25,
								rx = -6,
							},
							Cabeza = {
								rx = -22,
							},
							Sombrero = {
								rx = -10,
							},
							AlaIzq = {
								ry = 18,
								rz = 8,
							},
							Cola = {
								rx = 12,
							},
							PataIzq = {
								rx = -8,
							},
							PataDer = {
								rx = -8,
							},
							AlaDer = {
								ry = -18,
								rz = -8,
							},
						},
					},
					{
						t = 0.3,
						pose = {
							Raiz = {
								py = 0.45,
								rx = 4,
							},
							Cabeza = {
								rx = 20,
							},
							Mandibula = {
								rx = -30,
							},
							Sombrero = {
								py = 0.15,
								rx = 8,
							},
							AlaIzq = {
								rz = -70,
								ry = -10,
							},
							Cola = {
								rx = -25,
							},
							PataIzq = {
								rx = 20,
							},
							PataDer = {
								rx = 20,
							},
							AlaDer = {
								rz = 70,
								ry = 10,
							},
						},
					},
					{
						t = 0.65,
						pose = {
							Raiz = {
								py = 0.4,
								ry = 360,
							},
							Cabeza = {
								rx = 10,
							},
							Mandibula = {
								rx = -15,
							},
							Sombrero = {
								py = 0.05,
							},
							AlaIzq = {
								rz = -55,
							},
							Cola = {
								rx = -15,
							},
							PataIzq = {
								rx = 15,
							},
							PataDer = {
								rx = 15,
							},
							AlaDer = {
								rz = 55,
							},
						},
					},
					{
						t = 0.65,
						pose = {
							Raiz = {
								py = 0.4,
								ry = 0,
							},
							Cabeza = {
								rx = 10,
							},
							Mandibula = {
								rx = -15,
							},
							Sombrero = {
								py = 0.05,
							},
							AlaIzq = {
								rz = -55,
							},
							Cola = {
								rx = -15,
							},
							PataIzq = {
								rx = 15,
							},
							PataDer = {
								rx = 15,
							},
							AlaDer = {
								rz = 55,
							},
						},
					},
					{
						t = 0.9,
						pose = {},
					},
				},
			},
			GritoMasAlla = {
				duracion = 1.15,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.3,
						pose = {
							Raiz = {
								rx = 12,
								pz = 0.15,
								py = 0.08,
							},
							Cabeza = {
								rx = 28,
							},
							Mandibula = {
								rx = -10,
							},
							AlaIzq = {
								rz = -35,
								rx = 8,
							},
							Cola = {
								rx = -12,
							},
							Sombrero = {
								rx = -6,
							},
							AlaDer = {
								rz = 35,
								rx = 8,
							},
						},
					},
					{
						t = 0.5,
						pose = {
							Raiz = {
								rx = -7,
								pz = -0.25,
								py = -0.12,
							},
							Cabeza = {
								rx = 6,
								pz = -0.2,
							},
							Mandibula = {
								rx = -50,
							},
							AlaIzq = {
								rz = -75,
								ry = -25,
							},
							Cola = {
								rx = -22,
							},
							Sombrero = {
								py = 0.35,
								rx = 18,
							},
							PataIzq = {
								rx = 8,
							},
							PataDer = {
								rx = -8,
							},
							AlaDer = {
								rz = 75,
								ry = 25,
							},
						},
					},
					{
						t = 0.62,
						pose = {
							Raiz = {
								rx = -7,
								pz = -0.25,
								py = -0.12,
							},
							Cabeza = {
								rx = 6,
								ry = 7,
								pz = -0.2,
							},
							Mandibula = {
								rx = -45,
							},
							AlaIzq = {
								rz = -72,
								ry = -25,
							},
							Cola = {
								rx = -22,
							},
							Sombrero = {
								py = 0.45,
								rx = 22,
							},
							PataIzq = {
								rx = 8,
							},
							PataDer = {
								rx = -8,
							},
							AlaDer = {
								rz = 72,
								ry = 25,
							},
						},
					},
					{
						t = 0.74,
						pose = {
							Raiz = {
								rx = -6,
								pz = -0.22,
								py = -0.1,
							},
							Cabeza = {
								rx = 6,
								ry = -7,
								pz = -0.2,
							},
							Mandibula = {
								rx = -45,
							},
							AlaIzq = {
								rz = -70,
								ry = -22,
							},
							Cola = {
								rx = -20,
							},
							Sombrero = {
								py = 0.4,
								rx = 18,
							},
							PataIzq = {
								rx = 8,
							},
							PataDer = {
								rx = -8,
							},
							AlaDer = {
								rz = 70,
								ry = 22,
							},
						},
					},
					{
						t = 0.86,
						pose = {
							Raiz = {
								rx = -4,
								pz = -0.15,
								py = -0.06,
							},
							Cabeza = {
								rx = 4,
								ry = 5,
								pz = -0.12,
							},
							Mandibula = {
								rx = -35,
							},
							AlaIzq = {
								rz = -50,
								ry = -15,
							},
							Cola = {
								rx = -12,
							},
							Sombrero = {
								py = 0.15,
								rx = 8,
							},
							PataIzq = {
								rx = 5,
							},
							PataDer = {
								rx = -5,
							},
							AlaDer = {
								rz = 50,
								ry = 15,
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
								rx = 16,
								rz = 8,
							},
							Mandibula = {
								rx = -20,
							},
							Sombrero = {
								py = 0.15,
								rz = -10,
							},
							AlaIzq = {
								rz = -18,
							},
							AlaDer = {
								rz = 18,
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
				duracion = 1.5,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.3,
						pose = {
							Raiz = {
								py = 0.15,
								rx = 6,
							},
							Cabeza = {
								rx = 15,
								ry = 10,
							},
							Mandibula = {
								rx = -35,
							},
							Sombrero = {
								py = 0.5,
								rx = -10,
								rz = 12,
							},
							AlaIzq = {
								rz = -45,
							},
							Cola = {
								rx = -10,
							},
							PataIzq = {
								rx = -5,
							},
							PataDer = {
								rx = -5,
							},
							AlaDer = {
								rz = 45,
							},
						},
					},
					{
						t = 0.8,
						pose = {
							Raiz = {
								py = -1.0,
								rx = -6,
								rz = 5,
							},
							Cabeza = {
								rx = -20,
								rz = 10,
							},
							Mandibula = {
								rx = -25,
							},
							AlaIzq = {
								rz = 15,
							},
							PataIzq = {
								rz = -45,
								rx = -15,
							},
							PataDer = {
								rz = 45,
								rx = -15,
							},
							Cola = {
								rx = 10,
							},
							Sombrero = {
								rx = -63.2,
								ry = 18.9,
								rz = 83.0,
								px = 2.24,
								py = 0.07,
								pz = 0.66,
							},
							AlaDer = {
								rz = -15,
							},
						},
					},
					{
						t = 1.5,
						pose = {
							Raiz = {
								py = -1.95,
								rx = -10,
								rz = 8,
							},
							Cabeza = {
								rx = -10,
								ry = 32,
								rz = 10,
								py = -1.92,
								pz = -0.6,
							},
							Mandibula = {
								rx = -30,
							},
							AlaIzq = {
								rz = 30,
								ry = 10,
							},
							PataIzq = {
								rz = -84,
								rx = -10,
							},
							PataDer = {
								rz = 84,
								rx = -10,
							},
							Cola = {
								rx = 20,
								rz = 12,
							},
							Sombrero = {
								rx = 0.4,
								ry = 2.1,
								rz = -12.2,
								px = 1.87,
								py = -1.5,
								pz = 1.06,
							},
							AlaDer = {
								rz = -30,
								ry = -10,
							},
						},
					},
				},
			},
		},
	},
}
