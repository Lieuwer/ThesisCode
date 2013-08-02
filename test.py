from dataGenerator import dataGenerator
import modelFitter
import numpy as np
import time

#TODO:1. Andere classe structuur? Meer klasses?

#Get some commandline stuff soon...
def normalize(obj):
    #fix the standard deviation of theta 0 to be 1, change alpha accordingly
    stdt=np.std(obj.st)
    obj.st=np.divide(obj.st,stdt)
    obj.ca=np.multiply(obj.ca,stdt)
    #fix the largest value of gamma to be one
    maxg=max(obj.cg)
    obj.cg=np.divide(obj.cg,maxg)
    obj.cr=np.divide(obj.cr,maxg)
    obj.se=np.multiply(obj.se,maxg)


def compareparameters(pars1, pars2):
    normalize(pars1)
    normalize(pars2)
    difa=np.absolute(np.subtract(pars1.ca,pars2.ca))
    difb=np.absolute(np.subtract(pars1.cb,pars2.cb))
    difg=np.absolute(np.subtract(pars1.cg,pars2.cg))
    difr=np.absolute(np.subtract(pars1.cr,pars2.cr))
    dift=np.absolute(np.subtract(pars1.st,pars2.st))
    dife=np.absolute(np.subtract(pars1.se,pars2.se))
    print np.average(difa), np.average(difb), np.average(difg), np.average(difr), np.average(dift), np.average(dife)

def main():
    #number of students; number of questions; number of components
    nrs = 100
    nrq = 300
    nrkc = 15
    #distribution of components, cumilative starting at 1 components, up to length + 1
    kcdist = [.4,.65,.85,.99]
    data = dataGenerator(nrs,nrq,nrkc,kcdist)
    #data.save("test2.data")
    #data=dataGenerator.loadFile("test2.data")
    print "Using full matrix"
    model=modelFitter.modelFitter(nrs,nrkc,data.ikc,data.data,True)
    model.iterate()
    
    #see how the model does on testset
    testerror=0.0
    for d in data.testdata:
        if d[2]:
            testerror+=1-model.predict(d[0],d[1])
        else:
            testerror+=model.predict(d[0],d[1])
    print "Fitted model error on testset", testerror/len(data.testdata)
    
    print "Using sparse matrix"
    model=modelFitter.modelFitter(nrs,nrkc,data.ikc,data.data,False)
    model.iterate()
    testerror=0.0
    for d in data.testdata:
        if d[2]:
            testerror+=1-model.predict(d[0],d[1])
        else:
            testerror+=model.predict(d[0],d[1])
    print "Fitted model error on testset", testerror/len(data.testdata)    
    
if __name__ == "__main__":
    t0=time.clock()
    main()
    t1=time.clock()
    #print "Time taken by all code", t1-t0
