from complexModel import complexModel
from pfasModel import pfasModel
from afmModel import afmModel
from edata import edata
import numpy as np
import time
import datetime
import random as r
from baseline import baseline
import warnings

import matplotlib.pyplot as plt
#Get some commandline stuff?


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

def compareParams(models):
    return()
    #make sure all models are normalized!
    par=models[0].giveParams()
    params=[]
    for nr,p in enumerate(par):
        params.append(np.zeros((len(p),len(models))))
    for i in range(len(models)):
        for nr,p in enumerate(models[i].giveParams()):
            params[nr][:,i]=p
    for i in range(len(par)):
        print ""
        print i
        print ""
        avg=np.mean(params[i],1)
        std=np.std(params[i],1)
        for j in range(len(std)): print avg[j], std[j]
    
    

def main():
    warnings.filterwarnings('error')
    #number of students; number of questions; number of components
    nrs = 100
    nri = 300
    nrkc = 15
    runs=10
    #average number of questions per student:
    #qslist =[5,10,20,40,80]
    qslist=[5,10,20,40,80,160]
    #nr of runs/models to be made
    results=[]

    # Create the data objects and have it generate a kc to item distribution    

    data = edata()
    data.generate(nrs,nrkc,nri)
    genmodel=complexModel(data)
    genmodel.genParams()    
    
    for qs in qslist:
        print "busy"
        results.append(runtests(data,genmodel,qs,runs))
    params=[]
    for i in range(genmodel.nrParams()):
        params.append([])
    for result in results:
        for i in range(genmodel.nrParams()):
            params[i].append(result[i])
    plt.figure(1)
    lines=[0]*genmodel.nrParams()
    colors=["b-","g-","r-","c-","m-","k-"]
    for i in range(genmodel.nrParams()):
        lines[i],=plt.plot(qslist,params[i],colors[i],label=genmodel.paranames[i])
    plt.ylabel('Average spearman')
    plt.xlabel("Questions per student")
    plt.legend(lines, genmodel.paranames)
    plt.show()
    
    
    
def runtests(data,genmodel,qavg,nrm):
    testdata=edata()
    testdata.initializeCopy(data)
    nri=len(data.ikc)
    ergenlist=[]
    ertrainlist=[]
    ertestlist=[]
    modellist=[]

    #Now create data for every student, returning questions vs no questions are 
    #seen twice!
    #questions seen per student
    sq=[]
    for s in range(data.nrs):
        #Number of questions answered by student,
        nrans=r.normalvariate(qavg,5)
        if nrans<1:
            sq.append(1)    
        else:
            sq.append(int(nrans))
    
    #Generate models a number of times
    for i in range(nrm):
        genmodel.clearGenerate()
        genmodel.changeData(data)
        genmodel.clearGenerate()        
        for s in range(data.nrs):
            for j in range(sq[s]):
                genmodel.generate(s,r.randrange(nri))
        print "just did generating"  
#        answered=range(nri)
#        r.shuffle(answered)
#        print answered[0]
#        if nrans<1:
#            answered=answered[0]
#        #python should do this even if nrans>list length
#        else:
#            answered=answered[:int(nrans)]
#        for i in answered:
#            model.generate(s,i)
        ergenlist.append(genmodel.giveGenError())
        #continue with making a testset
        genmodel.changeData(testdata)
        for s in range(data.nrs):
            genmodel.generate(s,r.randrange(nri))
            ertestlist.append(genmodel.giveGenError())
        model=complexModel(data,True)
        err = model.fit()
        print "just did fitting"
        ertrainlist.append(err)
        
        ertestlist.append(model.useTestset(testdata))

        
        for other in modellist:
            #build the similarity matrix here
            j=1
        model.normalizeParameters()
        modellist.append(model)
    compareParams(modellist)
    #genmodel.printParamStats()
    rSpearman=np.zeros(len(genmodel.giveParams()))
    for model in modellist:
        #model.printParamStats()
        adding=model.spearman(genmodel)

        for v in adding:
            if v==np.NaN:
                print "we have a NaN!"
        rSpearman+=adding
    return rSpearman/nrm
    tSpearman=np.zeros(6)
    for nr,model in enumerate(modellist):
        for j in range (nr):
            tSpearman+=model.spearman(modellist[j])
    #print "alpha, beta, gamma, ro, t0, eta"
    return tSpearman/(nrm/2*(nrm+1))
            
    
if __name__ == "__main__":
    t0=time.time()
    main()
    t1=time.time()
    print "Time taken by all code", str(datetime.timedelta(seconds=(t1-t0)))
