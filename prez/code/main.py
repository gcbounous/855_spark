# -*- coding: utf-8 -*-
import sys
from functions import *
from multiprocessing import Pool
from timeit import default_timer as timer

"""
main program 
map group and reduce
"""
def main():
    if (len(sys.argv) != 2):
        print "Program requires path to file for reading!"
        sys.exit(1)
    start = timer()
    lines = load(sys.argv[1])
    linebis = cutIn10(lines)
    print "Starting "+str(len(lines)/10)+" processes as Mappers"
    pool = Pool(processes=len(lines)/10)
    interPreMap = timer()
    resultats = pool.map(Map, linebis)
    interPostMap = timer()
    toto = list(chunks(Group(resultats),1000))
    print "launching "+str(len(toto))+" Reducers"
    interPreReduce = timer()
    result = pool.map(Reduce, toto)
    interPostReduce = timer()
    listDictWrite(result)
    end = timer()
    print "Total time : "+str(end-start)
    print "Map time : "+str(interPostMap-interPreMap)
    print "Reduce time : "+str(interPostReduce-interPreReduce)

if __name__ == '__main__':
    main()