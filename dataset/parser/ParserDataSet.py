#! /usr/bin/python2.7
# -*- coding:utf-8 -*

from urllib2 import urlopen
import bs4 as BeautifulSoup
import csv
import unicodedata
import re
from fuzzywuzzy import fuzz
import OAuth
import json

# melhorar funcao para ter certeza de pegar o politico buscado
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

def myfunction(text): # WTF?!?! Ça serait cool de comprendre ce que tu ecris. ;)
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
			temp2 = unicodedata.normalize('NFD', myfunction(nome.upper())).encode('ascii', 'ignore')
			for tempNome,liste in nomes.iteritems():
				temp1 = unicodedata.normalize('NFD', myfunction(tempNome)).encode('ascii', 'ignore')
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

def adicionarIdEAmigos(lista):
	"""
	Reorganiza a lista adicionando o id (values[0]) e a lista de amigos(values[5]) em values
		- param lista : Um dicionario de listas com key: nome do politico; value: lista de booleans ["lavaJato","panamaPapers","odebrecht","acusadosCondenados"]
		- return lista : lista reorganizada
	"""
	print("length: {0}".format(len(lista)))

	# para nao passar do rate limit
	# fazer controle de tempo para o rate limit a cada 15min
	#	- /friends/ids (max 15)		|
	# 	- /users/search (max180)	| => alors on doit se limiter a 15 requests/15min 
	max_rate_limit = 0

	for key, values in lista.iteritems():

		if max_rate_limit == 1:
			break
		else:
			max_rate_limit+=1

		user = getTwitterUser(key)
		if user == -1:
			user_id = -1
			lista_amigos = []
		else:
			user_id = user["id"]
			lista_amigos = getTwitterUsersFriends(user_id)			

		temp1 = values[0]
		values[0] = user_id
		for i in xrange(1,4):
			temp2 = values[i]
			values[i] = temp1
			temp1 = temp2
		values.append(temp1)

		values.append(lista_amigos)		

	return lista

	# cs.writerow()
def sanitize(toto):
	return toto.split(",")[0]

def lavaJato():
	nomes = []
	with open('./fontes/lavaJato.html','r') as f:
		html = f.read()
		soup = BeautifulSoup.BeautifulSoup(html, 'html.parser')
		alvos = soup.find_all('div',class_='alvo')
		for alvo in alvos:
			nomes.append(sanitize(alvo.strong.string))
		return nomes

def panamaPapers():
	nomes = []
	pattern = re.compile(".*person.*name.*")
	csvfile = urlopen('https://raw.githubusercontent.com/amaboura/panama-papers-dataset-2016/master/pt.csv')
	spamreader = csv.DictReader(csvfile)
	for line in spamreader:
		if(pattern.search(line["fieldname"]) is not None):
			nomes.append(sanitize(line["text"]))
	return nomes

def odebrecht():
	nomes = []
	html = urlopen("http://m.congressoemfoco.uol.com.br/noticias/lista-da-odebrecht-os-politicos-e-seus-respectivos-partidos")
	soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
	nomesTr = soup.find_all("td",height="20")
	for nome in nomesTr[1:]:
		nomes.append(sanitize(nome.string))
	return nomes

def acusadosCondenados():
	nomes =[]
	html = urlopen("http://www.contracorrupcao.org/2013/04/lista-da-corrupcao.html?m=1")
	soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
	nomesTr = soup.find_all("td",itemprop="name")
	for nome in nomesTr:
		if nome.div.span is not None:
			nomes.append(sanitize(nome.div.span.string))
	return nomes
	
def main():
	nomes = dict()
	nomes["lavaJato"] = lavaJato()
	nomes["panamaPapers"] = panamaPapers()
	nomes["odebrecht"] = odebrecht()
	nomes["acusadosCondenados"] = acusadosCondenados()

	lista = fazerLista(nomes)	
	lista = adicionarIdEAmigos(lista)
	criarCSV(lista)

	print "done"

if __name__ == '__main__':
	main()
