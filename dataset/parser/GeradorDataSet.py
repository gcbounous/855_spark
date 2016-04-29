#! /usr/bin/python2.7
# -*- coding:utf-8 -*

import ParserPoliticosBrasilia
import OAuth
import csv
import unicodedata
from fuzzywuzzy import fuzz
import json
import time
import tweepy

# melhorar funcao para ter certeza de pegar o politico buscado (buscar palavras como dep deputado senador ministro)
def getTwitterUser(query):
	"""
	Faz a busca de usuarios por uma query e pega o primeiro (o mais relevante)
		- param query: query com o nome do politico
		- return user._json : "json" (dicionario) com as informacoes do politico se nao achar nada retorna -1
	"""
	users = OAuth.api.search_users(query)
	if len(users) > 0:
		# printTwitterUserJson(users[0]._json)
		return users[0]._json
	else:
		return -1

def getTwitterUsersFriends(user_id):
	"""
	Recupera a lista de ids dos usuarios que o usuario segue
		-param user_id: id do usurario
		-return lista_amigos: lista de ids dos amigos do usuario
	"""
	lista_amigos = OAuth.api.friends_ids(user_id)
	return lista_amigos

def printTwitterUserJson(user):
	print(json.dumps(user, sort_keys=True, indent=2, separators=(',', ': ')))
	print(user["id"])

def adicionarIdEAmigos(lista):
	"""
	Reorganiza a lista adicionando o id (values[0]) e a lista de amigos(values[5]) em values
		- param lista : Um dicionario de listas com key: nome do politico; value: lista de booleans ["lavaJato","panamaPapers","odebrecht","acusadosCondenados"]
		- return lista : lista reorganizada
	"""
	count = 0;
	for key, values in lista.iteritems():
		user = getTwitterUser(key)
		lista_amigos = []

		# user = -1
		if user == -1:
			user_id = -1
		else:
			user_id = user["id"]

			try:
				lista_amigos = getTwitterUsersFriends(user_id)
			except tweepy.error.TweepError as e:
				# Rate limit error
				if e.message == [{u'message': u'Rate limit exceeded', u'code': 88}]:
					print("Rate Limit Reached: devemos esperar 15min para continuar.")
					espera = 0
					# Esperamos 15min para relançar
					for i in xrange(0,15):
						espera += 1
						time.sleep(60)
						if espera%5 == 0:
							print("Faltam {}min".format(15-espera))
					lista_amigos = getTwitterUsersFriends(user_id)	
				# No permission to access friends 
				else:
					print("Failed to run the command on that user, no permission.")

		temp1 = values[0]
		values[0] = user_id
		for i in xrange(1,4):
			temp2 = values[i]
			values[i] = temp1
			temp1 = temp2
		values.append(temp1)

		values.append(lista_amigos)

		count+=1
		print("\n{}: {} done!".format(count,key))
		# time.sleep(60)	
	return lista

def convertToUnicode(text): 
    try:
        text = unicode(text, 'utf-8')
    except TypeError:
        return text
    return text

def criarCSV(listas):
	c = csv.writer(open("corrupcao.csv", "wb"))
	c.writerow(["Nome","id","lavaJato","panamaPapers","odebrecht","acusadosCondenados","lista de amigos"])
	for key,value in listas.iteritems():
		c.writerow([key,value[0],value[1],value[2],value[3],value[4],value[5]])

def fazerLista(listas):
	nomes = dict()
	found = False
	i = 0
	g = 0
	e = 0
	for nomeListe in ["lavaJato","panamaPapers","odebrecht","acusadosCondenados"]:
		for nome in listas[nomeListe]:
			temp2 = unicodedata.normalize('NFD', convertToUnicode(nome.upper())).encode('ascii', 'ignore')
			for tempNome,liste in nomes.iteritems():
				temp1 = unicodedata.normalize('NFD', convertToUnicode(tempNome)).encode('ascii', 'ignore')
				if(fuzz.ratio(temp1,temp2)>80):
					found = True
					liste[i] = 1
			if(found is False):
				newListe = [0] * 4
				newListe[i] = 1
				nomes[temp2] = newListe
				g += 1
			found = False
		i += 1
	return nomes
	
def main():
	nomes = ParserPoliticosBrasilia.getPoliticosCorruptos()
	
	lista = adicionarIdEAmigos(fazerLista(nomes))
	criarCSV(lista)

	print "done"

if __name__ == '__main__':
	# main()


	user = getTwitterUser("michel temer")
	lista = getTwitterUsersFriends(user["id"])
	# jason = OAuth.api.rate_limit_status()
	print "id: ",user["id"]
	print lista
	# print jason["resources"][u"friends"][u"/friends/ids"]
		
