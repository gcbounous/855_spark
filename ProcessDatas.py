#coding: utf-8
import csv
# import matplotlib.pyplot as plt
import sys
import runConsoleMain 
from StringIO import StringIO
from datetime import datetime
from collections import namedtuple
from operator import add, itemgetter
from pyspark import SparkConf, SparkContext

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
        coefficient = float(-1)
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

def process():
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

def main():
    confSpark()
    dictionary = process()
    while True:
        chewie = runConsoleMain.consoleMain(dictionary)
        if chewie != "chewbacca":
            break
        newId = getAndAdd(chewie)
        if newId != -1:
            dictionary = process()


if __name__ == "__main__":
    main()