# -*- coding: utf-8 -*-
from edata import edata
import time,datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from complexModel import complexModel
import numpy as np

def main():
    test= edata()
    #test.save("testing.edata")
    test=edata.load("train.edata")
    test.checkdata()
    models=[]
#    csq=test.countKCQuestions()
#    print len(csq),min(csq.values())
#    qps=defaultdict(int)
#    for q in csq.values():
#        qps[q]+=1
#    print max(qps.keys())
#    csq=OrderedDict(sorted(csq.items(), key=lambda t: t[1]))
#    fig={}
#    for nr,i in enumerate(csq.values()):
#        fig[nr]=i
#    plt.figure(1)
#    plt.plot(fig.keys(),fig.values())
#    plt.show()
    print len(test.data)
    test.removekcsq(3,15)
    test.checkdata()

    trainerror=[]
    testerror=[]
    print len(test.data)
    datas=test.splitDataS(3)
    for i in range(len(datas)):
        models.append(complexModel(datas[i],False))
        if i>0:
            models[i].setBaseKCCF(models[i-1])
        trainerror.append(models[i].fit())
        if i<len(datas)-1:
            testerror.append(models[i].useTestset(datas[i+1]))
            print "test done"
        else:
            #set kcc
            models[i].basekcc=models[i-2].basekcc.copy()
            models[i].basekcf=models[i-2].basekcf.copy()
            testerror.append(models[i].useTestset(datas[i-1]))
    tSpearman=np.zeros(6)
    for nr,model in enumerate(models):
        for i in range (nr):
            tSpearman+=model.spearman(models[i])
    print "alpha, beta, gamma, ro, t0, eta"
    nrm=len(models)
    print tSpearman/(nrm/2*(nrm+1))
    print trainerror
    print sum(trainerror)/float(len(trainerror))
    print testerror
    
if __name__ == "__main__":
    t0=time.time()
    main()
    t1=time.time()
    print "Time taken by all code", str(datetime.timedelta(seconds=(t1-t0)))