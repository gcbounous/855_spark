# -*- coding: utf-8 -*-
from sets import Set
import multiprocessing
from itertools import islice
"""
param : path<string>
loads a file and returns it as list of his lines 
"""
def load(path):
    word_list = []
    f = open(path, "r")
    ret = f.readlines()
    f.close()
    return ret
"""
param : list<list>
takes a list and returns a generator. One element in the generator is 10 in the list
"""
def cutIn10(list):
    for i in xrange(0, len(list), 10):
        yield list[i:i+10]
"""
param : data<dictionnary> Size<int>
takes a dictionnary and a size and return a generator of dictionnary with a size = SIZE
"""
def chunks(data, SIZE=10000):
    it = iter(data)
    for i in xrange(0, len(data), SIZE):
        yield {k:data[k] for k in islice(it, SIZE)}
"""
param : list<list> 
takes a list and write in a file the contents
"""
def listDictWrite(list):
    with open("tempResult",'w') as f:
        for dicto in list:
            for key,value in dicto.items():
                f.write(key[0]+" e "+str(key[1])+" share friendship with "+', '.join(value)+"\n")

"""
aimed to Sanitize a data set of friends fb
entry pattern : facebook_combined
"""
def Sanitize(path):
	with open(path, "r") as fichier:
		last = -1
		couple = dict()
		for line in fichier:
			if line:
				foo = line.split()
				if foo[0] in couple:
					couple[foo[0]].append(foo[1])
				else:
					couple[foo[0]]=[foo[1]]
				if foo[1] not in couple:
					couple[foo[1]]=[foo[0]]
				else:
					couple[foo[1]].append(foo[0])
		with open(path+"_sanitize","w") as destination:
			for keys, values in couple.items():
				destination.write(keys+" => ")
				for el in values:
					destination.write(el+" ")
				destination.write("\n")
"""
param : allFriend<list>, him<int>
returns a set from a list without the int him
"""
def setWithoutHim(allFriends,him):
	newSet = Set()
	for current in allFriends:
		if current!=him:
			newSet.add(current)
	return newSet
"""
param : n lines of the form 'element => el1 el2 el3...'
resturns a dictionnary of the form
key1 = (element,el1) => value1 = set(el2, el3...)
key2 = (element,el2) =>value2 = set(el1,el3,...)
...
"""
def Map(lignes):
	current = multiprocessing.current_process()
	ret = dict()
	for ligne in lignes:
		part = ligne.split("=>")
		base = part[0].strip()
		friendList = part[1].split()
		for friend in friendList:
			ret[(min(base,friend),max(base,friend))] = setWithoutHim(friendList,friend)
	print 'ending mapper n°:', current.name, current._identity
	return ret
"""
param : resultats<list>
group a list of dictionnary in one dictionnary, appending the value which has the same key
"""
def Group(resultats):
    dicto = dict()
    for ligne in resultats:
        for key, value in ligne.items():
            if not key in dicto:
                dicto[key]=[value]
            else:
                dicto[key]+= [value]
    return dicto
"""
param : dictionnaire<dictionnary>
return a dictionnary where the values are intersection of the value from the entry dictionnary
"""
def Reduce(dictionnaire):
	current = multiprocessing.current_process()
	#print dictionnaire.items()"
	for key,value in dictionnaire.items():
		if len(value)>1:
			dictionnaire[key]=value[0]&value[1]
		elif len(value) == 1:
			dictionnaire[key]=value[0]
		else:
			dictionnaire[key]={}
	print 'ending mapper n°:', current.name, current._identity
	return dictionnaire
