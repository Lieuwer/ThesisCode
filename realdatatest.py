# -*- coding: utf-8 -*-
import modelFitter
import cPickle as pickle

def main():
    #number of students; number of questions; number of components, gotten from
    #dataprepper. Need to adapt to automate
    filehandle=open ("datatest","rb")
    data=pickle.load(filehandle)
    filehandle=open ("ikc","rb")
    ikc=pickle.load(filehandle)
    nrs = 574
    nrq = 210710
    nrkc = 111
    #data = dataGenerator(nrs,nrq,nrkc,kcdist)
    #data.save("test.data")
    #print len(data.data)
    model=modelFitter.modelFitter(nrs,nrkc,ikc,data)
    model.iterate()
    #see how the model does on testset
    testerror=0.0
#    for d in data.testdata:
#        if d[2]:
#            testerror+=1-model.predict(d[0],d[1])
#        else:
#            testerror+=model.predict(d[0],d[1])
#    print "Fitted model error on testset", testerror/len(data.testdata)
if __name__ == "__main__":
    main()