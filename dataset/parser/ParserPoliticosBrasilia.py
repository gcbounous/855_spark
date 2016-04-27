#! /usr/bin/python2.7
# -*- coding:utf-8 -*

from urllib2 import urlopen
import bs4 as BeautifulSoup
import csv
import re

todos_politicos = []

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
					lista_ministros.append(unicode(" ".join(nome).upper(), "utf-8"))
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
		nome = limparLinhaSTF(a.text).upper()
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
		nome = tagB.text.upper()
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
			lista_senadores.append(a.text.upper())
	return lista_senadores

def lavaJato():
	nomes = []
	with open('./fontes/lavaJato.html','r') as f:
		html = f.read()
		soup = BeautifulSoup.BeautifulSoup(html, 'html.parser')
		alvos = soup.find_all('div',class_='alvo')
		for alvo in alvos:
			politico = alvo.strong.string
			if politicoFederal(politico):
				nomes.append(politico)
	return nomes

def panamaPapers():
	nomes = []
	pattern = re.compile(".*person.*name.*")
	csvfile = urlopen('https://raw.githubusercontent.com/amaboura/panama-papers-dataset-2016/master/pt.csv')
	spamreader = csv.DictReader(csvfile)
	for line in spamreader:
		if(pattern.search(line["fieldname"]) is not None):
			politico = unicode(sanitize(line["text"]), "utf-8")
			if politicoFederal(politico):
				nomes.append(politico)
	return nomes

def odebrecht():
	nomes = []
	html = urlopen("http://m.congressoemfoco.uol.com.br/noticias/lista-da-odebrecht-os-politicos-e-seus-respectivos-partidos")
	soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
	nomesTr = soup.find_all("td",height="20")
	for nome in nomesTr[1:]:
		politico = sanitize(nome.string)
		if politicoFederal(politico):
			nomes.append(politico)
	return nomes

def acusadosCondenados():
	nomes =[]
	html = urlopen("http://www.contracorrupcao.org/2013/04/lista-da-corrupcao.html?m=1")
	soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
	nomesTr = soup.find_all("td",itemprop="name")

	for nome in nomesTr:
		if nome.div.span is not None:
			politico = sanitize(nome.div.span.string)
			if politicoFederal(politico):
				nomes.append(politico)
	return nomes

def getPoliticosCorruptos():
	"""
	metodo que recupera o nomes dos politicos envolvidos em corrupçao, fazendo uma triagem para termos apenas os politicos da esfera federal
		-return nomes: um dicionario com listas de nomes relacionadas a cada escandalo
	"""
	global todos_politicos 
	todos_politicos = getPoliticosNivelFederal()

	nomes = dict()
	nomes["lavaJato"] = lavaJato()
	nomes["panamaPapers"] = panamaPapers()
	nomes["odebrecht"] = odebrecht()
	nomes["acusadosCondenados"] = acusadosCondenados()
	return nomes

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
	lista_politicos.append(unicode("Dilma Rousseff", "utf-8").upper())
	lista_politicos.append(unicode("Michel Temer", "utf-8").upper())
	return lista_politicos

def politicoFederal(politico):
	"""
	funcao que verifica se um polico esta na esfera federal ou nao
		-return politico_ok = True se ele estiver na esfera Federal
	"""
	politico = politico.upper().split()
	politico_ok = False
	for nome in todos_politicos:
		nome = nome.split()
		if nome == politico:
			# print nome," | ",politico
			politico_ok = True
			break
	return politico_ok

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

def sanitize(toto):
	return toto.split(",")[0]

if __name__ == "__main__":
	nomes = getPoliticosCorruptos()
	print nomes
