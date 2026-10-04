-- Generado por herramientas/criaturas/generar.py. No lo edites a mano: cambia el archivo
-- herramientas/criaturas/huevomimico.py y vuelve a generar.
return {
	nombre = "Huevo Mímico",
	vida = 280,
	velocidad = 14,
	comportamiento = "emboscada",
	radioDeteccion = 14,
	radioPatrulla = 6,
	radioPersecucion = 45,
	reaparecer = 40,
	colorUI = Color3.fromRGB(255, 190, 40),
	habilidades = {
		{
			nombre = "Mordisco",
			tipo = "Golpe",
			anim = "Mordisco",
			rango = 7,
			alcance = 7,
			angulo = 90,
			danio = 20,
			empuje = 30,
			cooldown = 2,
			retraso = 0.25,
			color = Color3.fromRGB(255, 60, 50),
		},
		{
			nombre = "Nidada Explosiva",
			tipo = "Invocar",
			anim = "NidadaExplosiva",
			rango = 40,
			criatura = "PollitoBomba",
			cantidad = 3,
			maximo = 6,
			cooldown = 12,
			retraso = 0.6,
			color = Color3.fromRGB(255, 200, 40),
		},
		{
			nombre = "Aplastón",
			tipo = "Onda",
			anim = "Aplaston",
			rango = 9,
			radio = 10,
			danio = 18,
			empuje = 50,
			cooldown = 7,
			retraso = 0.6,
			color = Color3.fromRGB(255, 215, 90),
		},
	},
	tipo = "HuevoMimico",
	rig = {
		marcador = 2.0,
		suelo = -1.6414,
		partes = {
			Cabeza = {
				padre = "Cuerpo",
				union = { -1.485, 0.0, 0.6536 },
			},
			Ojo = {
				padre = "Cabeza",
				union = { 0.165, 0.0, 1.6736 },
			},
			Lengua = {
				padre = "Cuerpo",
				union = { -0.635, 0.0, 0.0936 },
			},
			PuntaLengua = {
				padre = "Lengua",
				union = { 0.285, 0.0, 0.1336 },
			},
			PataIzq = {
				padre = "Cuerpo",
				union = { 0.035, -0.62, -0.8064 },
			},
			PataDer = {
				padre = "Cuerpo",
				union = { 0.035, 0.62, -0.8064 },
			},
		},
		adjuntos = {
			Cuerpo__Brillo_grieta = "Cuerpo",
			Cabeza__Brillo_grieta = "Cabeza",
			Ojo__Brillo_ojo_rojo = "Ojo",
			Ojo__Brillo_grieta = "Ojo",
		},
	},
	coloresBrillo = {
		Cuerpo__Brillo_grieta = Color3.fromRGB(255, 224, 102),
		Cabeza__Brillo_grieta = Color3.fromRGB(255, 224, 102),
		Ojo__Brillo_ojo_rojo = Color3.fromRGB(255, 26, 15),
		Ojo__Brillo_grieta = Color3.fromRGB(255, 224, 102),
	},
	animaciones = {
		ciclos = {
			Idle = {
				Raiz = {
					{ "py", 0.04, 1.0, 0 },
					{ "rz", 2, 0.5, 0 },
				},
				Cabeza = {
					{ "rx", 8, 0, 0.25 },
					{ "rx", 5, 1.0, 0 },
				},
				Ojo = {
					{ "ry", 9, 0.45, 0 },
					{ "rz", -16, 0.45, 0 },
					{ "rx", 8, 0.7, 0.3 },
				},
				Lengua = {
					{ "rx", 5, 1.0, 0.1 },
					{ "ry", 7, 0.6, 0 },
				},
				PuntaLengua = {
					{ "rx", 12, 1.0, 0.35 },
					{ "ry", 12, 0.6, 0.25 },
				},
				PataIzq = {
					{ "rx", 3, 1.0, 0 },
				},
				PataDer = {
					{ "rx", 3, 1.0, 0.5 },
				},
			},
			Disfrazado = {
				Raiz = {
					{ "py", -0.45, 0, 0.25 },
					{ "rz", 1.0, 0.3, 0 },
				},
				Cabeza = {
					{ "rx", 0.7, 0, 0.25 },
					{ "rx", 0.7, 0.2, 0 },
				},
				PataIzq = {
					{ "py", 0.45, 0, 0.25 },
				},
				PataDer = {
					{ "py", 0.45, 0, 0.25 },
				},
			},
			Caminar = {
				Raiz = {
					{ "py", 0.14, 0, 0.25 },
					{ "py", 0.14, 5.2, 0.25 },
					{ "rz", 6, 2.6, 0 },
					{ "rx", -4, 5.2, 0 },
				},
				Cabeza = {
					{ "rx", 10, 0, 0.25 },
					{ "rx", 7, 5.2, 0 },
				},
				Ojo = {
					{ "ry", 6, 1.3, 0 },
				},
				Lengua = {
					{ "rx", 6, 5.2, 0.2 },
				},
				PuntaLengua = {
					{ "rx", 14, 5.2, 0.45 },
					{ "ry", 10, 2.6, 0 },
				},
				PataIzq = {
					{ "rx", 34, 2.6, 0 },
				},
				PataDer = {
					{ "rx", 34, 2.6, 0.5 },
				},
			},
		},
		clips = {
			Mordisco = {
				duracion = 0.7,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.13,
						pose = {
							Raiz = {
								rx = 8,
								pz = 0.25,
							},
							Cabeza = {
								rx = 58,
							},
							Lengua = {
								rx = 10,
							},
							PuntaLengua = {
								rx = 20,
							},
							PataIzq = {
								rx = -10,
							},
							PataDer = {
								rx = -10,
							},
						},
					},
					{
						t = 0.25,
						pose = {
							Raiz = {
								rx = -12,
								pz = -0.8,
								py = 0.2,
							},
							Cabeza = {
								rx = -6,
							},
							Lengua = {
								rx = -4,
							},
							PataIzq = {
								rx = 22,
							},
							PataDer = {
								rx = 22,
							},
						},
					},
					{
						t = 0.42,
						pose = {
							Raiz = {
								rx = -6,
								pz = -0.45,
								py = 0.05,
							},
							Cabeza = {
								rx = -3,
							},
							PataIzq = {
								rx = 10,
							},
							PataDer = {
								rx = 10,
							},
						},
					},
					{
						t = 0.7,
						pose = {},
					},
				},
			},
			NidadaExplosiva = {
				duracion = 1.25,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.25,
						pose = {
							Raiz = {
								rx = 10,
								py = -0.2,
							},
							Cabeza = {
								rx = 15,
							},
							PataIzq = {
								py = 0.2,
							},
							PataDer = {
								py = 0.2,
							},
						},
					},
					{
						t = 0.45,
						pose = {
							Raiz = {
								rx = 16,
								py = -0.1,
							},
							Cabeza = {
								rx = 30,
							},
							Lengua = {
								rx = -6,
							},
							PataIzq = {
								py = 0.1,
							},
							PataDer = {
								py = 0.1,
							},
						},
					},
					{
						t = 0.6,
						pose = {
							Raiz = {
								rx = -12,
								py = 0.35,
								pz = -0.2,
							},
							Cabeza = {
								rx = 78,
							},
							Lengua = {
								rx = 22,
								pz = -0.3,
							},
							PuntaLengua = {
								rx = -25,
							},
							Ojo = {
								rx = -10,
							},
							PataIzq = {
								rx = 15,
							},
							PataDer = {
								rx = 15,
							},
						},
					},
					{
						t = 0.85,
						pose = {
							Raiz = {
								rx = -6,
								py = 0.1,
							},
							Cabeza = {
								rx = 70,
							},
							Lengua = {
								rx = 16,
								pz = -0.25,
							},
							PuntaLengua = {
								rx = -35,
							},
						},
					},
					{
						t = 1.25,
						pose = {},
					},
				},
			},
			Aplaston = {
				duracion = 1.1,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.2,
						pose = {
							Raiz = {
								py = -0.35,
								rx = 4,
							},
							PataIzq = {
								py = 0.35,
							},
							PataDer = {
								py = 0.35,
							},
							Cabeza = {
								rx = -4,
							},
						},
					},
					{
						t = 0.42,
						pose = {
							Raiz = {
								py = 1.7,
								rx = -6,
							},
							PataIzq = {
								rx = 28,
							},
							PataDer = {
								rx = 28,
							},
							Cabeza = {
								rx = 32,
							},
							Lengua = {
								rx = 15,
							},
							PuntaLengua = {
								rx = -15,
							},
						},
					},
					{
						t = 0.53,
						pose = {
							Raiz = {
								py = 0.6,
								rx = 0,
							},
							PataIzq = {
								rx = 10,
							},
							PataDer = {
								rx = 10,
							},
							Cabeza = {
								rx = 22,
							},
						},
					},
					{
						t = 0.6,
						pose = {
							Raiz = {
								py = -0.3,
							},
							PataIzq = {
								py = 0.3,
							},
							PataDer = {
								py = 0.3,
							},
							Cabeza = {
								rx = -6,
							},
							Lengua = {
								rx = -6,
							},
						},
					},
					{
						t = 0.75,
						pose = {
							Raiz = {
								py = 0.12,
							},
							Cabeza = {
								rx = 14,
							},
						},
					},
					{
						t = 1.1,
						pose = {},
					},
				},
			},
			Despertar = {
				duracion = 1.4,
				claves = {
					{
						t = 0.0,
						pose = {
							Raiz = {
								py = -0.45,
							},
							PataIzq = {
								py = 0.45,
							},
							PataDer = {
								py = 0.45,
							},
							Cabeza = {
								rx = -7,
							},
						},
					},
					{
						t = 0.12,
						pose = {
							Raiz = {
								py = -0.45,
								rz = 4,
							},
							PataIzq = {
								py = 0.45,
							},
							PataDer = {
								py = 0.45,
							},
							Cabeza = {
								rx = -5,
							},
						},
					},
					{
						t = 0.24,
						pose = {
							Raiz = {
								py = -0.45,
								rz = -4,
							},
							PataIzq = {
								py = 0.45,
							},
							PataDer = {
								py = 0.45,
							},
							Cabeza = {
								rx = -3,
							},
						},
					},
					{
						t = 0.34,
						pose = {
							Raiz = {
								py = -0.5,
								rz = 3,
							},
							PataIzq = {
								py = 0.5,
							},
							PataDer = {
								py = 0.5,
							},
							Cabeza = {
								rx = -7,
							},
						},
					},
					{
						t = 0.55,
						pose = {
							Raiz = {
								py = 1.3,
								rx = 6,
							},
							PataIzq = {
								rx = 30,
							},
							PataDer = {
								rx = 30,
							},
							Cabeza = {
								rx = 72,
							},
							Lengua = {
								rx = 24,
								pz = -0.35,
							},
							PuntaLengua = {
								rx = -40,
							},
							Ojo = {
								rx = -8,
							},
						},
					},
					{
						t = 0.8,
						pose = {
							Raiz = {
								py = -0.15,
								rx = 4,
							},
							PataIzq = {
								py = 0.15,
							},
							PataDer = {
								py = 0.15,
							},
							Cabeza = {
								rx = 55,
							},
							Lengua = {
								rx = 16,
								pz = -0.3,
							},
							PuntaLengua = {
								rx = -35,
							},
						},
					},
					{
						t = 1.0,
						pose = {
							Raiz = {
								rx = 12,
								py = 0.1,
							},
							Cabeza = {
								rx = 70,
							},
							Lengua = {
								rx = 22,
								pz = -0.35,
							},
							PuntaLengua = {
								rx = -45,
								ry = 15,
							},
							Ojo = {
								ry = 15,
							},
						},
					},
					{
						t = 1.4,
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
								rz = 7,
								rx = 6,
							},
							Cabeza = {
								rx = 18,
							},
							Ojo = {
								rx = 15,
							},
						},
					},
					{
						t = 0.22,
						pose = {
							Raiz = {
								rz = -5,
							},
							Cabeza = {
								rx = -4,
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
				duracion = 1.3,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.3,
						pose = {
							Raiz = {
								py = 0.3,
								rz = -14,
							},
							Cabeza = {
								rx = 30,
							},
							Ojo = {
								ry = 20,
							},
						},
					},
					{
						t = 0.55,
						pose = {
							Raiz = {
								py = 0.2,
								rz = 18,
							},
							Cabeza = {
								rx = 10,
							},
						},
					},
					{
						t = 1.0,
						pose = {
							Raiz = {
								py = -0.15,
								rz = 88,
							},
							Cabeza = {
								rx = 52,
							},
							Lengua = {
								rx = 18,
								pz = -0.4,
							},
							PuntaLengua = {
								rx = -50,
							},
							PataIzq = {
								rx = -30,
							},
							PataDer = {
								rx = 25,
							},
							Ojo = {
								rx = 25,
							},
						},
					},
					{
						t = 1.3,
						pose = {
							Raiz = {
								py = -0.12,
								rz = 84,
							},
							Cabeza = {
								rx = 46,
							},
							Lengua = {
								rx = 14,
								pz = -0.45,
							},
							PuntaLengua = {
								rx = -60,
							},
							PataIzq = {
								rx = -36,
							},
							PataDer = {
								rx = 30,
							},
							Ojo = {
								rx = 30,
							},
						},
					},
				},
			},
		},
	},
}
