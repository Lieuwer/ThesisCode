# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 14:02:47 2014

@author: Lieuwe
"""

import random as r
import math as m
import numpy as np
import scipy.sparse as sparsesp
from sklearn import linear_model
import scipy.stats as stat
from model import model

class afmModel(model):
    def __init__(self,data,fullmatrix=True):
        #fullmatrix is a lot faster, but takes more memory and can thus simply
        #be infeasable        
        self.fullmatrix=fullmatrix        
        #store the kc's belonging to each item
        self.ikc=data.ikc
        #lists that will hold the parameters of items and students
        self.cg=np.zeros(data.nrkc)
        self.cb=np.zeros(data.nrkc)
        self.st=np.zeros(data.nrs)
        
        self.paranames=["beta","gamma","theta0"]
        self.parameters=[]
        self.parameters.append(self.cb)
        self.parameters.append(self.cg)       
        self.parameters.append(self.st)        
        
        self.basekcc=np.zeros((data.nrs,data.nrkc))
        self.basekcf=np.zeros((data.nrs,data.nrkc))        
        
        self.kcc=np.zeros((data.nrs,data.nrkc))
        self.kcf=np.zeros((data.nrs,data.nrkc))
        
        #linkage of kcs to items is known
        self.data=data
        #This keeps track of the total error in generating data
        self.genError=0.0
        #This keeps track over the errors while fitting
        self.fitError=[1,1]
        #create student parameter estimates, now done in similar fashion as generating data
        for i in range(data.nrs):
            self.st[i]=r.normalvariate(0,.5)

        #create knowledge component parameter estimates, idem as above
        for i in range(data.nrkc):
            self.cg[i]=r.uniform(.075,.15)
            self.cb[i]=r.normalvariate(0,.5)
        
    def genParams(self):       
        
        for i in range(self.data.nrs):
            self.st[i]=r.normalvariate(0,1)


        #create knowledge component parameter estimates, idem as above
        for i in range(self.data.nrkc):
            self.cg[i]=r.uniform(.02,.05)
            self.cb[i]=r.normalvariate(0,1.5)
    
    def probability(self,s,i):
        x=self.st[s]
        for c in self.ikc[i]:
            x+=(self.kcf[s,c]+self.kcc[s,c])*self.cg[c]-self.cb[c]
        try:
            return 1/(m.exp(-x)+1)
        except:
            return 0
            
        
    

        
    #
    # Methods for the fitting procedure
    #
    def sUpdate(self):
        #Do a single fitting of the student parameters and update them
        nrs=len(self.st)
        nrkc=len(self.cb)
        labels=self.data.labels
        #Create an array of dimensions number of datapoints by number of students *2 + number of kcs
        if self.fullmatrix:  
            studentdata=np.zeros((len(self.data.data),nrs+nrkc*2))
        else:
            studentdata=sparsesp.lil_matrix((len(self.data.data),nrs+nrkc*2))
        #keep track of questions answered correctly and questions answered wrongly
        kcc = self.kcc= np.zeros((nrs,nrkc))
        kcf = self.kcf= np.zeros((nrs,nrkc))
        totalerror=0.0
        print "entering data"
        for nr,d in enumerate(self.data.giveData()):
            s=d[0]
            it=d[1]
            x=self.st[s]
            studentdata[nr,s]=1
            for c in self.ikc[it]:
                x+=(kcf[s,c]+kcc[s,c])*self.cg[c]-self.cb[c]
                studentdata[nr,c+nrs]=kcc[s,c]+kcf[s,c]
                studentdata[nr,nrs+c+nrkc]=-1
                if labels[nr]:
                    kcc[s,c]+=1
                else:
                    kcf[s,c]+=1
            try:
                big=m.exp(x)+1
                if labels[nr]:
                    totalerror+=1/big
                else:
                    totalerror+=1-(1/big)
            except:
                if not labels[nr]:
                    print "WARNING: major error added in s"
                    totalerror+=1
        print "about to fit model"
        model=linear_model.LogisticRegression(fit_intercept=False,penalty='l1',C=10^9)
        model.fit(studentdata,labels)
        print "Copying parameters"        
        self.st[:]=model.coef_[0][:nrs]
        self.cg[:]=model.coef_[0][nrs:nrs+nrkc]
        self.cb[:]=model.coef_[0][nrs+nrkc:]
        #Save the found kcc and kcf   
        return totalerror/len(self.data.data)

    def fit(self,maxiterations=50):
        self.fitError.append(self.sUpdate())
        return self.fitError[-1]
        

        