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
            
        
    def covarianceMatrix(self):
        #Returns the covariance matrix according to Fisher information based on the current estimates of the parameters
        nrs=len(self.st)
        nrkc=len(self.cb)  
        labels=self.data.labels
        print "length according to afmModel",  nrs+nrkc*2
        if self.fullmatrix:  
            data=np.zeros((len(self.data.data),nrs+nrkc*2))
            R=np.zeros((len(self.data.data),len(self.data.data)))
        else:
            data=sparsesp.lil_matrix((len(self.data.data),nrs+nrkc*2))
            R=sparsesp.lil_matrix((len(self.data.data),len(self.data.data)))
        kcc = self.kcc= np.zeros((nrs,nrkc))
        kcf = self.kcf= np.zeros((nrs,nrkc))
        for nr,d in enumerate(self.data.giveData()):
            s=d[0]
            it=d[1]
            x=self.st[s]
            data[nr,s]=1
            for c in self.ikc[it]:
                x+=(kcf[s,c]+kcc[s,c])*self.cg[c]-self.cb[c]
                data[nr,c+nrs]=kcc[s,c]+kcf[s,c]
                data[nr,nrs+c+nrkc]=-1
                if labels[nr]:
                    kcc[s,c]+=1
                else:
                    kcf[s,c]+=1
            try:
                big=m.exp(-x)+1
                R[nr,nr]=1/big*(1-1/big)
            except:
                0
        if not self.fullmatrix:
            data=data.tocsr()
        moment=(data.transpose()*R*data)
        print "moment shape:", moment.shape
        #inversing can be a problem as the matrix can be singular, thus removing those rows and collumns where diagonal is zero
#        removing=[]
#        nrparams = moment.shape[0]
#        mask=np.ones(nrparams,dtype=bool)
#        for i in range(nrparams):
#            if moment[i,i]==0:
#                removing.append(i)
#        mask[removing]=False
#        w=np.flatnonzero(mask)
#        temp = moment[w,:]
#        print "removed: ", removing
#        return np.linalg.inv(temp[:,w].todense())
        return np.linalg.inv(moment.todense())
        
    #
    # Methods for the fitting procedure
    #
    def sUpdate(self):
        #Only a single update function necessary, because the model is linear within the logistic function
        nrs=len(self.st)
        nrkc=len(self.cb)
        labels=self.data.labels
        #Create an array of dimensions number of datapoints by number of students *2 + number of kcs
        if self.fullmatrix:  
            studentdata=np.zeros((len(self.data.data),nrs+nrkc*2))
        else:
            studentdata=sparsesp.lil_matrix((len(self.data.data),nrs+nrkc*2))
        #keep track of questions answered correctly and questions answered wrongly
        self.resetKCCF()        
        kcc = self.kcc
        kcf = self.kcf
        totalerror=0.0
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
                    totalerror+=np.log(1/big)
                else:
                    totalerror+=np.log(1-(1/big))
            except:
                if not labels[nr]:
                    print "WARNING: major error added in s"
                    totalerror+=np.log(.95)
        model=linear_model.LogisticRegression(fit_intercept=False,penalty='l1',C=10**9)
        if sum(labels)==0 or sum(labels)==len(labels):
            print "about to die!"
            print "corrects / Total data", sum(labels), len(labels)
            
        
        model.fit(studentdata,labels)       
        self.st[:]=model.coef_[0][:nrs]
        self.cg[:]=model.coef_[0][nrs:nrs+nrkc]
        self.cb[:]=model.coef_[0][nrs+nrkc:]  
        return totalerror/len(self.data)

    def fit(self,maxiterations=50):
        """
        Testing to see if this works
        """
        self.fitError.append(self.sUpdate())
        return self.fitError[-1]
        

        