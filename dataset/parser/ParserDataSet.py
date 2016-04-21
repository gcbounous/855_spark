#coding: utf-8

from urllib2 import urlopen
import bs4 as BeautifulSoup
import csv
import unicodedata
import re
from fuzzywuzzy import fuzz

def myfunction(text):
    try:
        text = unicode(text, 'utf-8')
    except TypeError:
        return text
    return text

def criarCSV(listas):
	c = csv.writer(open("corrupcao.csv", "wb"))
	c.writerow(["Nome","lavaJato","panamaPapers","odebrecht","acusadosCondenados"])
	for key,value in listas.iteritems():
		c.writerow([key,value[0],value[1],value[2],value[3]])

def fazerLista(listas):
	nomes =dict()
	found = False
	i = 0
	g = 0
	e= 0
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

	# cs.writerow()
def sanitize(toto):
	return toto.split(",")[0]

def lavaJato():
	nomes = []
	with open('lavaJato.html','r') as f:
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
	criarCSV(fazerLista(nomes))
	print "done"

if __name__ == '__main__':
	main()