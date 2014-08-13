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

class model(object):
    def save(self, filename):
        filehandle= open (filename,"wb")
        pickle.dump(self,filehandle)
        filehandle.close()
    
    @staticmethod
    def load(filename):
        filehandle=open(filename,"rb")
        return pickle.load(filehandle)
    
    def clearGenerate(self):
        #clear the data and reset the generator to the moment when no data is made yet
        self.data.clearData()
        self.kcc=self.basekcc.copy()
        self.kcf=self.basekcf.copy()
    
    def setBaseKCCF(self,other):
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
        self.data.data.append((s,i))
        if r.random()<p:
            self.data.labels.append(1)
            self.genError-=np.log(1-p)
        else:
            self.data.labels.append(0)
            self.genError-=np.log(p)

    def giveGenError(self):
        return self.genError/len(self.data.data)
    
    def useTestset(self,testdata):
        predictions=[]
        self.ikc=testdata.ikc
        for d in testdata.giveData():
            predictions.append(self.predict(d[0],d[1]))
        return aprime(predictions,testdata.labels)
    
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
    
    def spearman(self, other):
        answerlist=np.zeros(len(self.parameters))
        for i in range(len(answerlist)):
            answerlist[i]=stat.spearmanr(self.parameters[i],other.parameters[i])[0]
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
        params=[]
        for i in range(len(self.parameters)):      
            params.append(np.zeros((runs,len(self.parameters[i]))))
        othermodel=copy.deepcopy(self)
        for i in range(runs):
            
            othermodel.clearGenerate()
            for d in self.data.giveData():
                othermodel.generate(d[0],d[1])
            othermodel.fit()
            for j,p in enumerate(othermodel.giveParams()):
                params[j][i,:]=p
        stds=[]
        for i in range(len(self.parameters)):
            print ""
            print self.paranames[i]
            avg=np.mean(params[i],0)
            std=np.std(params[i],0)
            stds.append(std)
            for j in range(params[i].shape[1]):
                print j,avg[j],std[j]
        stds=np.concatenate(stds)
        return stds
            
    
    