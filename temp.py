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

def main():
    data=edata.load("train.edata")
    model=afmModel(data,False)
    model.fit()
    
    z=model.determineVariance(10)
    x=model.covarianceMatrix()
    #print z[682],z[683],x.shape,len(z)
    #682 & 683 removed to obtain covariance matrix
    #z=np.delete(z,[682,683])
    for i in range(x.shape[1]):
        print i,z[i],z[i]-x[i,i]**.5
    check=0     

        
    

""" 
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
        if nrans<1:
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

if __name__ == "__main__":
    t0=time.time()
    main()
    t1=time.time()
    print "Time taken by all code", str(datetime.timedelta(seconds=(t1-t0)))
