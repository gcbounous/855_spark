#coding: utf-8
import csv
# import matplotlib.pyplot as plt

import RunConsoleMain 
import sys
from StringIO import StringIO
from datetime import datetime
from collections import namedtuple
from operator import add, itemgetter
from pyspark import SparkConf, SparkContext
from fuzzywuzzy import fuzz

sys.path.insert(0, 'dataset/parser')
import GeradorDataSet

## Module Constants
APP_NAME = "Social Corruption"
DATE_FMT = "%Y-%m-%d"
TIME_FMT = "%H%M"
fields = ('Nome','id','numberList','lavaJato','panamaPapers','odebrecht','acusadosCondenados','listaDeAmigos')
Person   = namedtuple('Person', fields)
fields2   = ('id','tupleNomNumber')
Couple   = namedtuple('Couple', fields2)

def parse2(row):
    temp = row[0]
    row[0] = int(row[1])
    row[1] = int(row[2])+int(row[3])+int(row[4])+int(row[5])
    return Couple(*row[:2])
    
def makeTuple(corrupt, listCorrupt):
    if corrupt is not None:
        return corrupt.id, coefficient(corrupt,listCorrupt)

def parseAll(row):
    newR = [0]*8
    try:
        newR[0] = row[0]
        newR[1] = int(row[1])
        newR[2] = int(row[2])+int(row[3])+int(row[4])+int(row[5])
        lavaJoto = bool(int(row[2]))
        panamaPapers = bool(int(row[3]))
        odebrecht = bool(int(row[4]))
        acusadosCondenados = bool(int(row[5]))
        toto = row[6].strip("[ ]").split(",")
        if toto != ['']:
            array = map(int,row[6].strip("[ ]").split(","))
        else:
            array=[]
        newR[3] = lavaJoto
        newR[4] = panamaPapers
        newR[5] = odebrecht
        newR[6] = acusadosCondenados
        newR[7] = array
        return Person(*newR[:8])
    except ValueError:
        print "DAFUCK"

def coefficient(corrupt, listCorrupt):
    coefficient1 = 300
    coefficient2 = 20
    coefficient3 = 50
    numero =0
    corruption = corrupt.numberList * coefficient1
    value = corrupt.numberList * 300
    for amigo in corrupt.listaDeAmigos:
        if amigo in listCorrupt:
            corruption+= listCorrupt[amigo]*coefficient2
            numero += 1
    if len(corrupt.listaDeAmigos) > 0:
        coefficient = float(numero)/float(len(corrupt.listaDeAmigos))*100
    else:
        coefficient = 0
    corruption += coefficient*coefficient3
    return {"nome":corrupt.Nome,"lavaJato":corrupt.lavaJato,"panamaPapers":corrupt.panamaPapers,"odebrecht":corrupt.odebrecht,"acusadosCondenados":corrupt.acusadosCondenados,"numberList":corrupt.numberList,"numeroAmigos":len(corrupt.listaDeAmigos),"numeroAmigosSujos":numero,"coefficientAmigosSujos":coefficient,"coefficientCorruption":corruption}

def split(line):
    """
    Operator function for splitting a line with csv module
    """
    reader = csv.reader(StringIO(line))
    return reader.next()

## Main functionality
def run(sc):

    # Load the airlines lookup dictionary
    corrupted = sc.textFile("dataset/parser/corrupcao.csv").map(split).map(parseAll)
    listCorrupt = dict(sc.textFile("dataset/parser/corrupcao.csv").map(split).map(parse2).collect())
    coef  = corrupted.map(lambda f : makeTuple(f,listCorrupt)).collect()
    # coef = sorted(coef, key=itemgetter(1))
    result = dict()
    for el,val in coef:
        result[el] = val
    return result
    # for el,vl in result.iteritems():
    #     print el,vl

def confSpark():
    conf = SparkConf().setMaster("local[*]")
    conf = conf.setAppName(APP_NAME)
    sc   = SparkContext(conf=conf)
    return sc

def process(sc):
    # Configure Spark

    # Execute Main functionality
    return run(sc)

def getAndAdd(name):
    user = GeradorDataSet.getTwitterUser(name)
    if user == -1:
        user_id = -1
    else:
        user_id = user["id"]
        try:
            lista_amigos = GeradorDataSet.getTwitterUsersFriends(user_id)
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
            else:
                print("Failed to run the command on that user, no permission.")
            c = csv.writer(open("dataset/parser/corrupcao.csv", "wb"))
            c.writerow(name,user_id,"0","0","0","0",lista_amigos)
    return user_id

def add(name):
        newId = getAndAdd(name)
        if newId != -1:
            dictionary = process(sc)
def main():
    name = "DILMA ROUSSEF"
    sc = confSpark()
    dictionary = process(sc)
    printAll(dictionary)
    print "\n\n\n"
    ret = buscaPorNome(dictionary,name)
    if not ret:
        getAndAdd(name)
        buscaPorNome(dictionary,name)

def buscaPorNome(dic_politicos,nome):
    dic_politicos = calcularRanking(dic_politicos)[0]
    nome_achado =  False
    for key, value in dic_politicos.iteritems():
        if fuzz.ratio(nome.upper(),value["nome"].upper()) > 80:
            printOne(value)
            nome_achado = True
            break
    return nome_achado

def printAll(dico):
    dico,lista_id_coef= calcularRanking(dico)
    for key,val in lista_id_coef:
        printOne(dico[key])
def numeroLista(dico):
    value = 0
    if(dico["lavaJato"]):
        value += 1
    if(dico["odebrecht"]):
        value+=1
    if(dico["panamaPapers"]):
        value+=1
    if(dico["acusadosCondenados"]):
        value += 1
    return value
def printOne(dicoOne):
    liste = numeroLista(dicoOne)
    print dicoOne["nome"].ljust(22,' ')+" ("+str(dicoOne["ranking"])+") - Amigos "+str(dicoOne["numeroAmigos"]).ljust(6,' ')+" \t- A Sujos "+str(dicoOne["numeroAmigosSujos"]).ljust(5,' ')+" \t- Coef A S "+str(dicoOne["coefficientAmigosSujos"]).ljust(15,' ')+" \t - numero de Lista "+str(liste).ljust(3,' ')+"- Coef corrupcao "+str(dicoOne["coefficientCorruption"])

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
    return dic_politicos,lista_id_coef

if __name__ == "__main__":
    main()

    
