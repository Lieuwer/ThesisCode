# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 12:43:11 2014

@author: Lieuwe
"""
import sys
sys.path.append('.\models')
from edata import edata
from complexModel import complexModel
from pfasModel import pfasModel
from afmModel import afmModel
import time,datetime
from baseline import baseline
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stat
import random as r
from experiment import experiment
from experimentProcessing import experimentProcessing

def main():

#    data=edata.load("bridge0607.edata")
#    data.info()

    np.seterr(all="raise")
    models=["afm","pfa"]
    splits=[6,8,12,16,32]
    for split in splits:
        for model in models:
            print "\nStarting experiment:", model,split
#            exp=experiment.load(model+str(split)+"exp.exp")
            exp=experiment(model,model+str(split))
            exp.runExperiment(split,10,"algebra0506.edata")
            exp.determineStds()

#    exp=experiment.load("pfa6exp.exp")
###    print exp.mainmodel.data.nrs
#    exp.rankOrder()
#    exp.determineStds()         


#    exp=experiment("afm","afm"+str(6))
#    exp.runExperiment(6,10,"bridge.edata")
#    exp.determineStds()

    #29-8-14 Fisher info experiment. Get some outliers atm
#    data=edata.load("train2.edata")
#    data.beforeSplitCleaning()
#    data.splitCleaning()
##    model=afmModel(data,False)
##    model.fit()
##    model.save("testing.afm")
#    model=afmModel.load("testing.afm")
#    model.testSecond()
    #x=model.covarianceMatrix()
    #z=model.determineVariance(5)
    #difference=[]
#    
#    for i in range(len(z)):
#        print "\n next parameter",i,"\n"
#        diff=[]
#        for j in range(len(z[i])):
#            if i==0:
#                offset=data.nrs+data.nrkc
#            if i==1:
#                offset=data.nrs
#            if i==2:
#                offset=0
#            diff.append(z[i][j]-x[offset+j,offset+j])
#            if i==0:
#                print x[offset+j,offset+j]
#        print "mean and std"
#        print np.mean(z[i]),np.std(z[i])
#        print np.mean(diff),np.std(diff)
   

""" 
    data=edata.load("train2.edata")
    model=afmModel(data,False)
    model.fit()
    model.aPrime()
    bl = baseline(data)
    bl.fit()
    bl.aPrime()
    model.determineVariance(5)
        
    

#----------------------11-8-14------------------#

#    data=edata.load("train.edata")
#    model1=afmModel(data,False)
#    model2=afmModel(data,False)
#    model1.fit()
#    model2.fit()
#    print model1.spearman(model2)
#    model1.save("testa1.aModel")
#    model2.save("testa2.aModel")
#    testdata=edata.load("test.edata")


#    data.removekcsq(10,15)
#    
#    model=afmModel(data, False)
#    print model.fit()
#    model.save("trying.aModel")
#    model1.useTestset(testdata)
#    model2.useTestset(testdata)
#    bl = baseline(data)
#    bl.fit()
#    print "baseline:", bl.useTestset(testdata)
#    
##------------------------------------------------------------------------------
#    
#    model=afmModel.load("trying.aModel")
#
#    
#    print "model:", model.useTestset(testdata)
#    print np.average(model.cg), np.std(model.cg)
#    print np.average(model.cb), np.std(model.cb)
#    print np.average(model.st), np.std(model.st)  

#    model1=afmModel.load("testa1.aModel")
#    model2=afmModel.load("testa2.aModel")
#    model1.printParams()
#    model2.printParams()
#    for i in range(len(model1.parameters)):
#        temp=model1.parameters[i]-model2.parameters[i]
#        print sum(temp>=0)/float(len(temp))


    nrs = 100
    nri = 300
    nrkc = 15
    qs=40
    # Create the data objects and have it generate a kc to item distribution    

    data = edata()
    data.generate(nrs,nrkc,nri)
    genmodel=complexModel(data)
    genmodel.genParams()
    nri=len(data.ikc)
    sq=[]
    for s in range(nrs):
        #Number of questions answered by student,
        nrans=r.normalvariate(qs,5)
        if nrans<1:['crimson', 'burlywood','chartreuse']
            sq.append(1)    
        else:
            sq.append(int(nrans))
    for s in range(data.nrs):
            for j in range(sq[s]):
                genmodel.generate(s,r.randrange(nri))
    
    model1=complexModel(data,True)
    model1.fit()
    model2=complexModel(data,True)
    model2.fit()

    genmodel.save("testb0.cModel")
    model1.save("testb1.cModel")
    model2.save("testb2.cModel")
    print model1.spearman(model2)
    print genmodel.spearman(model1)
    print genmodel.spearman(model2)

#    genmodel=complexModel.load("testb0.cModel")
#    model1=complexModel.load("testb1.cModel")
# #   model2=complexModel.load("testb2.cModel")
#    print genmodel.spearman(genmodel)
#    print model1.spearman(genmodel)
#    for i in range(len(genmodel.parameters)):
#        genmodel.parameters[i]+=i-2
#    print genmodel.spearman(genmodel)
#    print genmodel.spearman(model1)
"""

def aprime(predict,labels):
    #Does not yet take into account the issue that there is dependancy between some of the data
    correct=[0]*sum(labels)
    incorrect=[0]*(len(labels)-len(correct))
    c=n=0
    error=0.0
    cor=0.0
    for i in range(len(labels)):
        if labels[i]:
            if predict[i]>=.5:cor+=1
            correct[c]=predict[i]
            c+=1
            error-=np.log(1-predict[i])
        else:
            if predict[i]<.5:cor+=1
            incorrect[n]=predict[i]
            n+=1
            error-=np.log(predict[i])
    total=0.0
## should make an n log n implementation of this, including a heuristic to have the larger value in the log
#    for yes in correct:
#        for no in incorrect:
#            if yes>no:
#                total+=1

    print "error=", error/len(labels)
    print "accuracy=", cor/len(labels)
    print "a-prime=", total/(len(correct)*len(incorrect))
    print "corrects",len(correct)/float(len(correct)+len(incorrect)), sum(correct)/len(correct)
    print "incorrects", len(incorrect), sum(incorrect)/len(incorrect)
    return total/(len(correct)*len(incorrect))

if __name__ == "__main__":
    t0=time.time()
    main()
    t1=time.time()
    print "Time taken by all code", str(datetime.timedelta(seconds=(t1-t0)))
