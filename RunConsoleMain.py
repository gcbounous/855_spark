#! /usr/bin/python2.7
# -*- coding:utf-8 -*

from fuzzywuzzy import fuzz

def imprimirPolitico(id, politico):
	perfil_pol = "{0} ({1}): coef. corrupçao = {2} | id = {3} | ".format(politico["nome"],politico["ranking"], politico["coefficientCorruption"], id)
	
	perfil_pol +="denuncias: "
	if(politico["lavaJato"]):
		perfil_pol += " Lava Jato,"
	if(politico["panamaPapers"]):
		perfil_pol += " Panama Papers,"
	if(politico["odebrecht"]):
		perfil_pol += " Odebrecht,"
	if(politico["acusadosCondenados"]):
		perfil_pol += " Acusado e condenado,"

	perfil_pol += " | Amigos corruptos: {0} | Total de amigos: {1} | Coef. amigos sujos {2}".format(politico["numeroAmigosSujos"], politico["numeroAmigos"], politico["coefficientAmigosSujos"])
	print perfil_pol

# Melhorar comparaçao (usar fuzzy)
def buscaPorNome(dic_politicos):
	nome = input()
	nome_achado =  False
	if nome.isalpha():
		for id, dic in dic_politicos.items():
			if fuzz.ratio(nome.upper(),dic.nome.upper()) > 80:
				imprimirPolitico(id, dic)
				nome_achado = True
				break
	else:
		return False

	if nome_achado:
		return False
	else:
		return nome

def rankingCompleto(dic_politicos):

	for id in enumerate(dic_politicos["rankingCompleto"], start = 1):
		imprimirPolitico(id, dic_politicos[id])

	return False

def buscaPorDenuncia(dic_politicos):
	# TODO
	return False

def sair():
	return "chewbacca"


# TESTAR!!
def calcularRanking(dic_politicos):
	lista_id_coef = []
	# copia os ids e coeficientes em uma lista
	for id, dic in dic_politicos.items():
		t = (id, dic["coefficientCorruption"])
		lista_id_coef.append(t)
	# ordena lista pelos coeficiente
	lista_id_coef = sorted(lista_id_coef, reverse = True, key = lambda tupla : tupla[1])
	# insere ranking no dicionario
	for i, tupla in enumerate(lista_id_coef, start = 1):
		dic_politicos[tupla[0]]["ranking"] = i
	# adicionamos o ranking geral no dicionario dos politicos
	dic_politicos["rankingGeral"] = lista_id_coef

	return dic_politicos

def imprimeMenuPrincipal():
	menu = "Escolha um modo para ver a corrupçao em Brasilia: "
	menu += "1) Buscar por nome \n2) Ver ranking completo \n3) Por denuncia \n4) Sair"
	print(menu)

def imprimeMenuListas():
	menu = "Escolha denuncia: "
	menu += "1) Lava Jato \n2) Odrebrech \n3) Panama Papers \n4) Acusados que foram condenados"

def consoleMain(dic_politicos, id = 0):
	"""
		Fonction qui traite les options du menu principale
		-param dic_politicos: dicionario com todos os politicos
		-param id: id do politico a ser impresso/ se -1 politico nao achado/ se 0 menu inicial
		-return sortir si vrai le jeu s'arrete
	"""
	dic_politicos = calcularRanking(dic_politicos)
	sortir = False

	if id == -1:
		print "Politico nao encontrado!"
	elif id == 0:
		pass
	else:
		imprimirPolitico(id, dic_politicos[id])


	while True:
		dic_menu = {
			1: buscaPorNome,
			2: rankingCompleto,
			3: buscaPorDenuncia,
			4: sair
		}

		menu_ok = False
		while not menu_ok:
			imprimerMenu()
			menu = input()
			try:
				menu = int(menu)
				assert (menu > 0 and menu <= 4)
			except ValueError:
				print("Voce nao digitou um numero. Tente novamente.")
			except AssertionError:
				print("*** Escolha um numero dentre as opçoes ***")
			else:
				menu_ok = True

		function = dic_menu[menu]
		sortir = function(dic_politicos)

		if sortir != False:
			return sortir	

if __name__ == "__main__":
	consoleMain()