#! /usr/bin/python2.7
# -*- coding:utf-8 -*

# import dataset/ProcessData as rocess

def imprimirPolitico(politico):

def buscaPorNome(dic_politicos):
	return False

def rankingCompleto(dic_politicos):
	return False

def buscaPorDenuncia(dic_politicos):
	return False

def sair():
	return True

def imprimeMenuPrincipal():
	menu = "Escolha um modo para ver a corrupçao em Brasilia: "
	menu += "1) Buscar por nome \n2) Ver ranking completo \n3) Por denuncia \n4) Sair"
	print(menu)

def imprimeMenuListas():
	menu = "Escolha denuncia: "
	menu += "1) Lava Jato \n2) Odrebrech \n3) Panama Papers \n4) Acusados que foram condenados"

def consoleMain(dic_politicos):
	"""
		Fonction qui traite les options du menu principale
		-return sortir si vrai le jeu s'arrete
	"""
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
	# return sortir	

if __name__ == "__main__":
	main()