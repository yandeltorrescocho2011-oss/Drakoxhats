-- Generado por herramientas/criaturas/generar.py. No lo edites a mano: cambia el archivo
-- herramientas/criaturas/pollitobomba.py y vuelve a generar.
return {
	nombre = "Pollito Bomba",
	vida = 30,
	velocidad = 24,
	comportamiento = "kamikaze",
	radioDeteccion = 45,
	radioPatrulla = 10,
	radioPersecucion = 90,
	reaparecer = 0,
	colorUI = Color3.fromRGB(255, 200, 40),
	habilidades = {
		{
			nombre = "¡Kabum!",
			tipo = "Explotar",
			anim = "Explotar",
			rango = 5,
			cooldown = 0,
			retraso = 1.1,
			radio = 11,
			danio = 25,
			empuje = 70,
			color = Color3.fromRGB(255, 150, 30),
		},
	},
	tipo = "PollitoBomba",
	rig = {
		marcador = 2.0,
		suelo = -0.9996,
		partes = {
			Cabeza = {
				padre = "Cuerpo",
				union = { 0.2836, -0.0, 0.4 },
			},
			Mecha = {
				padre = "Cabeza",
				union = { 0.3836, -0.0, 1.3 },
			},
			AlaIzq = {
				padre = "Cuerpo",
				union = { 0.0836, -0.62, 0.25 },
			},
			AlaDer = {
				padre = "Cuerpo",
				union = { 0.0836, 0.62, 0.25 },
			},
			PataIzq = {
				padre = "Cuerpo",
				union = { 0.0836, -0.25, -0.4 },
			},
			PataDer = {
				padre = "Cuerpo",
				union = { 0.0836, 0.25, -0.4 },
			},
		},
		adjuntos = {
			Mecha__Brillo_chispa = "Mecha",
			Mecha__Brillo_amarillo = "Mecha",
		},
	},
	coloresBrillo = {
		Mecha__Brillo_chispa = Color3.fromRGB(255, 191, 38),
		Mecha__Brillo_amarillo = Color3.fromRGB(255, 209, 51),
	},
	animaciones = {
		ciclos = {
			Idle = {
				Raiz = {
					{ "py", 0.05, 2.0, 0 },
				},
				Cabeza = {
					{ "rx", 6, 1.0, 0 },
					{ "ry", 8, 0.4, 0.2 },
				},
				Mecha = {
					{ "rz", 12, 3.0, 0 },
					{ "rx", 8, 2.3, 0.3 },
				},
				AlaIzq = {
					{ "rz", -10, 2.0, 0 },
				},
				AlaDer = {
					{ "rz", 10, 2.0, 0 },
				},
			},
			Caminar = {
				Raiz = {
					{ "rz", 9, 3.0, 0 },
					{ "py", 0.08, 6.0, 0 },
				},
				Cabeza = {
					{ "rx", 7, 6.0, 0.25 },
				},
				Mecha = {
					{ "rz", 18, 6.0, 0 },
				},
				AlaIzq = {
					{ "rz", -30, 8.0, 0 },
				},
				PataIzq = {
					{ "rx", 35, 3.0, 0 },
				},
				PataDer = {
					{ "rx", 35, 3.0, 0.5 },
				},
				AlaDer = {
					{ "rz", 30, 8.0, 0 },
				},
			},
		},
		clips = {
			Explotar = {
				duracion = 1.1,
				claves = {
					{
						t = 0.0,
						pose = {},
					},
					{
						t = 0.25,
						pose = {
							Raiz = {
								py = 0.15,
								rx = -12,
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
						t = 0.5,
						pose = {
							Raiz = {
								py = -0.1,
								rx = 6,
							},
							Cabeza = {
								rx = 12,
							},
							AlaIzq = {
								rz = 10,
							},
							AlaDer = {
								rz = -10,
							},
						},
					},
					{
						t = 0.8,
						pose = {
							Raiz = {
								py = 0.35,
								rx = -8,
							},
							AlaIzq = {
								rz = -70,
							},
							Mecha = {
								rz = 30,
							},
							AlaDer = {
								rz = 70,
							},
						},
					},
					{
						t = 1.1,
						pose = {
							Raiz = {
								py = 0.5,
							},
							AlaIzq = {
								rz = -80,
							},
							Cabeza = {
								rx = 20,
							},
							Mecha = {
								rz = -30,
							},
							AlaDer = {
								rz = 80,
							},
						},
					},
				},
			},
			Derrota = {
				duracion = 0.8,
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
								rz = 30,
							},
						},
					},
					{
						t = 0.8,
						pose = {
							Raiz = {
								py = -0.25,
								rz = 90,
							},
							AlaIzq = {
								rz = -40,
							},
							PataIzq = {
								rx = 40,
							},
							AlaDer = {
								rz = 40,
							},
							PataDer = {
								rx = 40,
							},
						},
					},
				},
			},
		},
	},
}
