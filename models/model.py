# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 13:39:26 2014

@author: Lieuwe
"""
import cPickle as pickle
import random as r
import scipy.stats as stat
import numpy as np
import copy
import time
import datetime


class model(object):
    def save(self, filename):
        filehandle= open (filename,"wb")
        pickle.dump(self,filehandle)
        filehandle.close()
    
    @staticmethod
    def load(filename):
        filehandle=open(filename,"rb")
        return pickle.load(filehandle)
        
    def parameterVariance(self,parname):
        try:
            if parname=="theta0":
                return np.var(self.st)
            if parname=="beta":
                return np.var(self.cb)
            if parname=="gamma":
                return np.var(self.cg)
            if parname=="ro":
                return np.var(self.cr)
        except:
            print "Error, this parameter doesn't exist in the model, thus variance cannot be given"
    
    def clearGenerate(self):
        #clear the data and reset the generator to the moment when no data is made yet
        self.data.clearData()
        self.kcc=self.basekcc.copy()
        self.kcf=self.basekcf.copy()
    
    def setBaseKCCF(self,other):
        #basekccf's need to be implemented into fit procedure of each model as well in order to work!
        self.basekcc=self.kcc.copy()
        self.basekcf=self.kcf.copy()
    
    def copyBaseKCCF(self,other):
        self.basekcc=other.kcc.copy()
        self.basekcf=other.kcf.copy()
        self.kcc=self.basekcc.copy()
        self.kcf=self.basekcf.copy()
        
    def changeData(self,newdata):
        #continue on another dataset, but keep all other info
        self.genError=0.0
        self.fitError=[1]
        self.data=newdata
    
    def generate(self,s,i):
        p = self.predict(s,i)
        if r.random()<p:
            self.data.addPoint(s,i,1)
            self.genError-=np.log(1-p)
        else:
            self.data.addPoint(s,i,0)
            self.genError-=np.log(p)
            
    def generateTest(self,s,i):
        p = self.predict(s,i)
        if r.random()<p:
            self.data.testdata.append((s,i,1))
        else:
            self.data.testdata.append((s,i,0))

    def giveGenError(self):
        return self.genError/len(self.data.data)
    
#    def useTestset(self,testdata):
#        predictions=[]
#        self.ikc=testdata.ikc
#        for d in testdata.giveData():
#            predictions.append(self.predict(d[0],d[1]))
#        return aprime(predictions,testdata.labels)
    
    def giveParams(self):
        return self.parameters
    
    def printParams(self):
        for i in range(len(self.paranames)):
            print self.paranames[i],len(self.parameters[i]), self.parameters[i]

    def printParamStats(self):
        for i in range(len(self.paranames)):
            print self.paranames[i],len(self.parameters[i]), np.average(self.parameters[i]), np.std(self.parameters[i])
    
    def predict(self,s,i):
        p=self.probability(s,i)
        if p<.5:
            for c in self.ikc[i]:
                self.kcf[s,c]+=1
        else:
            for c in self.ikc[i]:
                self.kcc[s,c]+=1        
        return p
    
    def addParam(self, par):
        self.parameters.append(par)
           
    def rankOrder(self, other,rank="kendall"):
        #A bit of a hack momentarily which works for AFM and PFA. Only looks at KC parameters
        answerlist=np.zeros(len(self.parameters)-1)
        for i in range(len(answerlist)):
            pars1=[]
            pars2=[]
            skip1=skip2=0
            for j in range(len(self.parameters[0])+len(self.data.kcmis)):
                if j in self.data.kcmis:
                    skip1+=1
                if j in other.data.kcmis:
                    skip2+=1
                if not (j in self.data.kcmis or j in other.data.kcmis):
                    pars1.append(self.parameters[i][j-skip1])
                    pars2.append(other.parameters[i][j-skip2])
            if rank=="spearman":
                answerlist[i]=stat.spearmanr(pars1,pars2)[0]
            else:
                answerlist[i]=stat.kendalltau(pars1,pars2)[0]
        return answerlist
    
    def nrParams(self):
        return len(self.parameters)
        
    def normalizeParameters(self):
        return
        
    def determineVariance(self,runs):
        #This method determines the variance of parameter values caused by
        #the stochastic nature of the data. Data is generated 'runs' times,
        #redetermining only the labels, and the model is fitted each time.
        #the variance for each parameter over all runs is determined
        parvar=[]
        params=[]
        ranks2=[]
        for i in range(len(self.parameters)):      
            params.append(np.zeros((runs,len(self.parameters[i]))))
            parvar.append([])
        
        
        for i in range(runs):
            othermodel=copy.deepcopy(self)
            othermodel.basekcc=np.zeros((self.data.nrs,self.data.nrkc))
            othermodel.basekcf=np.zeros((self.data.nrs,self.data.nrkc))
            for d in self.data.giveData():
                othermodel.generate(d[0],d[1])
            #Testpart is not yet correct?, as it the basekcc needs to be set at this point and the kcc reset once the testdata has been made.            
#            for d in self.data.giveTestData():
#                othermodel.generateTest(d[0],d[1])
            
            othermodel.fit()
            
            ranks2.append(self.rankOrder(othermodel))
#            othermodel.aPrime()
            for j,p in enumerate(othermodel.giveParams()):
                params[j][i,:]=p
                parvar[j].append(othermodel.parameterVariance(othermodel.paranames[j]))
        ranks=np.zeros((len(self.parameters),runs,runs))
        
        variances=[]
        for i in range(len(self.parameters)):
            parvar[i]=np.mean(parvar[i])
            for j in range(runs):
                for k in range(j+1,runs):
                    
                    ranks[i,j,k]=stat.kendalltau(params[i][j,:],params[i][k,:])[0]
            avg=np.mean(params[i],0)
            var=np.var(params[i],0,ddof=1)
            variances.append(var)
#            print ""
#            print self.paranames[i]
#            for j in range(params[i].shape[1]):
#                print j,avg[j],var[j]
        #variances=np.concatenate(variances)
        ranks=np.sum(ranks,(1,2))/((runs**2-runs)/2)
        ranks2=[[],[],[],[]]
        for j,p in enumerate(self.giveParams()):
            for i in range(runs):
                ranks2[j].append(stat.kendalltau(params[j][i,:],p)[0])
#        print "\nValues for the inherent ranks vs ranks against sourcemodel\n",ranks,np.mean(np.array(ranks2),1),"\n"

        return (variances,ranks,parvar)
            
    def aPrime(self):
        #Doesn't take into account that elements in the test set might be dependant
        t=time.time()
        error=[]
        correct=[]
        incorrect=[]
        for d in self.data.giveTestData():
            p=self.predict(d[0],d[1])
            if d[2]:
                correct.append(p)
                error.append(1-p)
            else:
                incorrect.append(p)
                error.append(p)
        correct.sort()
        incorrect.sort()
        aTotal=0
        i=0
        j=0
        while(i<len(correct)):
            while(j<len(incorrect) and correct[i]>incorrect[j]):
                j+=1
            aTotal+=j
            i+=1
        print "Unadjusted aprime=", float(aTotal)/(len(incorrect)*len(correct))
        print "Average error=", np.mean(error)
        print "Error percentage=", np.mean(np.round(error))
        print "Time taken for accuracies", str(datetime.timedelta(seconds=(time.time()-t)))
        return float(aTotal)/(len(incorrect)*len(correct))
    