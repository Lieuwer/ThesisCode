from complexModel import complexModel
from edata import edata
import numpy as np
import time
import datetime
import random as r
from baseline import baseline


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
    #number of students; number of questions; number of components
    nrs = 100
    nri = 300
    nrkc = 15
    #nr of runs/models to be made
    nrm =10
    # Create the data objects and have it generate a kc to item distribution    
    data = edata()
    testdata=edata()
    data.generate(nrs,nrkc,nri)
    testdata.initializeCopy(data)
    genmodel=complexModel(data)
    genmodel.genParams()
    ergenlist=[]
    ertrainlist=[]
    ertestlist=[]
    modellist=[]
    distanceMatrix=np.zeros((nrm,nrm))
    #Now create data for every student, returning questions vs no questions are 
    #seen twice!
    #questions seen per student
    sq=[]
    for s in range(nrs):
        #Number of questions answered by student,
        nrans=r.normalvariate(30,5)
        if nrans<1:
            sq.append(1)    
        else:
            sq.append(int(nrans))
    
    #Generate models ten times
    for i in range(nrm):
        genmodel.changeData(data)
        genmodel.clearGenerate()
        for s in range(nrs):
            for j in range(sq[s]):
                genmodel.generate(s,r.randrange(nri))
                
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
        genmodel.clearGenerate()
        for s in range(nrs):
            genmodel.generate(s,r.randrange(nri))
            ertestlist.append(genmodel.giveGenError())
        model=complexModel(data,True)
        err = model.fit()
        ertrainlist.append(err)
        ertestlist.append(0)
        for d in testdata.giveData():
            p=model.predict(d[0],d[1])
            if d[2]:
                ertestlist[i]+=1-p
            else:
                ertestlist[i]+=p
        ertestlist[i]=ertestlist[i]/len(testdata)
        for other in modellist:
            #build the similarity matrix here
            i=1
        model.normalizeParameters()
        modellist.append(model)
    compareParams(modellist)
    
    
if __name__ == "__main__":
    t0=time.time()
    main()
    t1=time.time()
    print "Time taken by all code", str(datetime.timedelta(seconds=(t1-t0)))
