from complexModel import complexModel
from edata import edata
import numpy as np
import time
import datetime
import random as r
from baseline import baseline


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
    #number of students; number of questions; number of components
    nrs = 100
    nri = 300
    nrkc = 15
    #average number of questions per student:
    qavg=120
    #nr of runs/models to be made
    nrm =[5,10,20,40,80,160]
    results=[]
    for n in nrm:
        print "busy"
        results.append(runtests(nrs,nri,nrkc,qavg,n))
#    results=[[ 0.7452381, 0.82857143  ,0.33525848 ,0.05208333, 0.74420388, 0.30348135],[ 0.6611039   ,0.78383117,  0.25821469, -0.00554006 , 0.72587477,  0.31196007],[ 0.74664966  ,0.88564626 , 0.12142106  ,0.15964661  ,0.79418181 , 0.35329201],[ 0.78304878 , 0.93614547  ,0.27912602 , 0.09050584,  0.86693033  ,0.38202623],[ 0.84163029,  0.93798832  ,0.24373561,  0.06769448,  0.86349338,  0.30427406],[ 0.80154697,  0.95238437,  0.0343433,   0.10796303,  0.78064365,  0.1476567 ]]
    ca=[]
    cb=[]
    cg=[]
    cr=[]
    st=[]
    se=[]
    for result in results:
        ca.append(result[0])
        cb.append(result[1])
        cg.append(result[2])
        cr.append(result[3])
        st.append(result[4])
        se.append(result[5])
        print result
    plt.figure(1)
    p1,=plt.plot(nrm,ca,"b-", label="alpha")
    p2,=plt.plot(nrm,cb,"g-", label="beta")
    p3,=plt.plot(nrm,cg,"r-", label="gamma")
    p4,=plt.plot(nrm,cr,"c-", label="ro")
    p5,=plt.plot(nrm,st,"m-", label="theta0")
    p6,=plt.plot(nrm,se,"k-", label="eta")
    lines=[p1,p2,p3,p4,p5,p6]
    plt.ylabel('Average spearman')
    plt.xlabel("Questions per student")
    plt.legend(lines, ["alpha","beta","gamme","ro","theta0","eta"])
    plt.show()
    
    
    
def runtests(nrs,nri,nrkc,qavg,nrm):
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

    #Now create data for every student, returning questions vs no questions are 
    #seen twice!
    #questions seen per student
    sq=[]
    for s in range(nrs):
        #Number of questions answered by student,
        nrans=r.normalvariate(qavg,5)
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
    tSpearman=np.zeros(6)
    for nr,model in enumerate(modellist):
        for i in range (nr):
            tSpearman+=model.spearman(modellist[i])
    #print "alpha, beta, gamma, ro, t0, eta"
    return tSpearman/(nrm/2*(nrm+1))
            
    
if __name__ == "__main__":
    t0=time.time()
    main()
    t1=time.time()
    print "Time taken by all code", str(datetime.timedelta(seconds=(t1-t0)))
