#! /usr/bin/python2.7
# -*- coding:utf-8 -*

from urllib2 import urlopen
import bs4 as BeautifulSoup
import csv
import unicodedata
import re
from fuzzywuzzy import fuzz
import os

def getMinistros():
	"""
	recupera lista dos ministros atuantes do site do planalto (http://www2.planalto.gov.br)
		- return: lista dos ministros (unicode - utf-8)
	"""	
	# (tive que fazer a recuperaçao na mao pois o site é feito de qualquer jeito)
	lista_ministros = []
	with open("./fontes/ministros.txt", "r") as documento:
		documento = documento.read().split("\n")
		for linha in documento:
			linha = linha.split(" ")
			nome = []
			for palavra in linha:
				if palavra == "-":
					lista_ministros.append(unicode(" ".join(nome), "utf-8"))
					break;
				else:
					nome.append(palavra)
	return lista_ministros

def getSTF():
	"""
	recupera lista dos ministros do STF atuantes do site do stf (http://www.stf.jus.br)
		- return: lista dos ministros do stf (unicode - utf-8)
	"""
	lista_stf = []
	html = urlopen("http://www.stf.jus.br/portal/cms/verTexto.asp?servico=sobreStfComposicaoComposicaoPlenariaApresentacao")
	soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
	tagDiv = soup.find("div", id="divImpressao")
	tagA = tagDiv.find_all("a")
	for a in tagA:
		nome = limparLinhaSTF(a.text)
		lista_stf.append(nome)
	return lista_stf

def getDeputadosFederais():
	"""
	recupera lista dos deputados federais atuantes do site da camera de deputados (www.camara.leg.br)
		- return: lista dos deputados federais (unicode - utf-8)
	"""
	lista_deputados = []
	html = urlopen("http://www.camara.leg.br/internet/deputado/Dep_Lista.asp?Legislatura=55&Partido=QQ&SX=QQ&Todos=None&UF=QQ&condic=QQ&forma=lista&nome=&ordem=nome&origem=None")
	soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
	tagsA = soup.find_all("a", title="Detalhes do Deputado")
	for a in tagsA:
		tagB = a.find("b")
		nome = tagB.text
		lista_deputados.append(nome)
	return lista_deputados

def getSenadores():
	"""
	recupera lista dos senadores atuantes do site do senado (https://www25.senado.leg.br)
		- return: lista dos senadores (unicode - utf-8)
	"""
	lista_senadores = []
	html = urlopen("https://www25.senado.leg.br/web/senadores/em-exercicio")
	soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
	tagTd = soup.find_all("td",{"class":"nowrap"})
	for tag in tagTd:
		tagA = tag.find_all("a")
		for a in tagA:
			lista_senadores.append(a.text)
	return lista_senadores

def getPoliticosNivelFederal():
	"""
	recupera lista dos politicos atuantes a nivel federal nos tres poderes
		- return: lista dos politicos (unicode - utf-8)
	"""
	lista_politicos = []
	lista_politicos  = lista_politicos + getMinistros()
	lista_politicos  = lista_politicos + getSTF()
	lista_politicos  = lista_politicos + getDeputadosFederais()
	lista_politicos  = lista_politicos + getSenadores()
	lista_politicos.append(unicode("Dilma Rousseff", "utf-8"))
	lista_politicos.append(unicode("Michel Temer", "utf-8"))
	return lista_politicos

def limparLinhaSTF(linha):
	"""
	recupera a linha com o nome dos ministros do stf e os "limpa"
		- return: nome , o nome e sobrenome do ministro em questao
	"""
	linha = linha.replace(u'\xa0', u' ').split(" ")
	if len(linha) <= 5:
		nome = "".join([linha[1], " ", linha[2]])
	else:
		nome = "".join([linha[1], " ", linha[2], " ", linha[3]])
	return nome

if __name__ == "__main__":
	getPoliticosNivelFederal()