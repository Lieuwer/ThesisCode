# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 14:22:54 2014

@author: Lieuwe
"""

import random as r
import math as m
#import matplotlib.pyplot as plt
import numpy as np
import scipy.sparse as sparsesp
from sklearn import linear_model
from model import model

class eirtModel(model):
    def __init__(self,data,fullmatrix=True):
        #debug option
        self.debug=True
        #fullmatrix is a lot faster, but takes more memory and can thus simply
        #be infeasable
        self.fullmatrix=fullmatrix        
        #store the kc's belonging to each item
        self.ikc=data.ikc
        #lists that will hold the parameters of items and students
        self.ca=np.zeros(data.nrkc)
        self.cb=np.zeros(data.nrkc)
        self.st=np.zeros(data.nrs)
        self.se=np.zeros(data.nrs)
        
        self.paranames=["beta","alpha","theta0","eta"]
        self.parameters=[]
        self.parameters.append(self.cb)        
        self.parameters.append(self.ca)        
        self.parameters.append(self.st)
        self.parameters.append(self.se)
        
        self.basekcc=np.zeros((data.nrs,data.nrkc))
        self.basekcf=np.zeros((data.nrs,data.nrkc))        
        
        self.kcc=np.zeros((data.nrs,data.nrkc))
        self.kcf=np.zeros((data.nrs,data.nrkc))
        
        #linkage of kcs to items is known
        self.data=data
        #This keeps track of the total error in generating data
        self.genError=0.0
        #This keeps track over the errors while fitting
        self.fitError=[]
        #create student parameter estimates, now done in same fashion as generating data
        #create student parameter estimates, now done in same fashion as generating data
        for i in range(data.nrs):
            self.st[i]=r.normalvariate(-.75,1)
            self.se[i]=r.uniform(.01,.05)

        #create knowledge component parameter estimates, idem as above
        for i in range(data.nrkc):
            self.ca[i]=r.uniform(.7,1.5)
            self.cb[i]=r.normalvariate(0,1)
        
    def genParams(self):       
        
        for i in range(self.data.nrs):
            self.st[i]=r.normalvariate(-.75,1)
            self.se[i]=r.uniform(.01,.05)

        #create knowledge component parameter estimates, idem as above
        for i in range(self.data.nrkc):
            self.ca[i]=r.uniform(.5,2)
            self.cb[i]=r.normalvariate(0,1.5)
                 
    def probability(self,s,i):
        k=float(len(self.ikc[i]))
        x=0
        for c in self.ikc[i]:
            x+=self.ca[c]*self.st[s]/k+self.ca[c]*(self.kcf[s,c]+self.kcc[s,c])*self.se[s]-self.cb[c]
        try:
            return 1/(m.exp(-x)+1)
        except:
            return 0
    
    
    #
    # Methods for the fitting procedure
    #
    def sUpdate(self):
        if self.debug:
            print "Starting student update"
        #Do a single fitting of the student parameters and update them
        nrs=len(self.st)
        nrkc=len(self.ca)
        labels=self.data.labels
        #Create an array of dimensions number of datapoints by number of students *2 + number of kcs
        if self.fullmatrix:  
            studentdata=np.zeros((len(self.data.data),nrs*2+nrkc))
        else:
            studentdata=sparsesp.lil_matrix((len(self.data.data),nrs*2+nrkc))
        #keep track of questions answered correctly and questions answered wrongly
        
        kcc = self.kcc= self.basekcc.copy()
        kcf = self.kcf= self.basekcf.copy()
        likely=0.0
        for nr,d in enumerate(self.data.giveData()):
            
            s=d[0]
            it=d[1]
            x=0
            k=float(len(self.ikc[it]))
            for c in self.ikc[it]:
                x+=self.ca[c]*self.st[s]/k+self.ca[c]*(kcf[s,c]+kcc[s,c])*self.se[s]-self.cb[c]
                studentdata[nr,s]+=self.ca[c]/k
                studentdata[nr,s+nrs]+=(kcc[s,c]+kcf[s,c])*self.ca[c]
                studentdata[nr,nrs*2+c]=-1
                if labels[nr]:
                    kcc[s,c]+=1
                else:
                    kcf[s,c]+=1
            try:
                big=m.exp(x)+1
                if labels[nr]:
                    likely+=np.log(1-(1/big))
                else:
                    likely+=np.log(1/big)
            except:
                if not labels[nr]:
                    print "WARNING: major error added in s"
                    likely+=np.log(10**-99)
        model=linear_model.LogisticRegression(fit_intercept=False,penalty='l1',C=10^9)
        model.fit(studentdata,labels)
                  
        self.st[:]=model.coef_[0][:nrs]
        self.se[:]=model.coef_[0][nrs:nrs*2]
        self.cb[:]=model.coef_[0][nrs*2:]
        #Save the found kcc and kcf

        
        return likely/len(self.data.data)

    def kcUpdate(self):
        if self.debug:
            print "Starting kc update"
        nrs=len(self.st)
        nrkc=len(self.ca)
        labels=self.data.labels
        #Do a single fitting of the kc parameters and update them
        if self.fullmatrix:
            kcdata=np.zeros((len(self.data.data),2*nrkc))
        else:
            kcdata=sparsesp.lil_matrix((len(self.data.data),4*nrkc))
        
        kcc = np.zeros((nrs,nrkc))
        kcf = np.zeros((nrs,nrkc))
        likely=0.0    
        for nr,d in enumerate(self.data.giveData()):
            s=d[0]
            it=d[1]
            k=float(len(self.ikc[it]))
            x=0
            for c in self.ikc[it]:
                x+=self.ca[c]*self.st[s]/k+(kcf[s,c]+kcc[s,c])*self.se[s]*self.ca[c]-self.cb[c]
                kcdata[nr,c]+=self.st[s]/k+(kcf[s,c]+kcc[s,c])*self.se[s]
                kcdata[nr,nrkc+c]=-1
                if labels[nr]:
                    kcc[s,c]+=1
                else:
                    kcf[s,c]+=1
            try:
                big=m.exp(x)+1
                if labels[nr]:
                    likely+=np.log(1-(1/big))
                else:
                    likely+=np.log(1/big)
            except:
                if not labels[nr]:
                    print "WARNING: major error added in kc"
                    likely+=np.log(10**-99)
      
        model=linear_model.LogisticRegression(fit_intercept=False,penalty='l1',C=10^9)
        model.fit(kcdata,labels)
        
        
        self.ca[:]=model.coef_[0][:nrkc]
        self.cb[:]=model.coef_[0][nrkc:nrkc*2]
        
        return likely/len(self.data.data)

    def fit(self,maxiterations=50):
        #keep track how often in succession no improvements were made       
        noimprov=0
        # this method performs iterative alternating logarithmic optamilatization of the logit of p for all datapoints
        for i in range(maxiterations):
            self.fitError.append(self.sUpdate())
            #print self.fitError[-1]
            
            if len(self.fitError)>2 and self.fitError[-1]-self.fitError[-3]<.001:
                noimprov+=1
            else:
                noimprov=0
            if noimprov>1:
                #print "Improvement threshold reached at 1 iteration", i
                break
            
            #Now estimate the kc parameters
            
            #normalize st and ca with eachother
#            size=sum(abs(self.st))/nrs
#            self.st/=size
#            self.ca*=size
            #see if we want to get out of the loop
            
            self.fitError.append(self.kcUpdate())
            #print self.fitError[-1]
            if len(self.fitError)>2 and self.fitError[-1]-self.fitError[-3]<.001:
                noimprov+=1
            else:
                noimprov=0
            if noimprov>1:
                #print "Improvement threshold reached at 2 iteration", i
                break
            self.normalizeParameters()
        print "Fiterrors", self.fitError
        return self.fitError[-1]
        
    def normalizeParameters(self):
        #make the average of alpha equal to 1 and the average of eta equal to .05
        avga=np.mean(self.ca)
        if avga!=0:
            self.ca/=avga
            self.st*=avga
            self.se*=avga
    

#        plt.figure(1)
#        plt.plot(erlist)
#        plt.ylabel('error')
#        plt.show()

##        plt.figure(2)
##        plt.subplot(231)
##        plt.plot(dalist)
##        plt.ylabel('da')
##        plt.subplot(232)
##        plt.plot(dglist)
##        plt.ylabel('dg')
##        plt.subplot(233)
##        plt.plot(drlist)
##        plt.ylabel('dr')
##        plt.subplot(234)
##        plt.plot(dalist)
##        plt.ylabel('db')
##        plt.subplot(235)
##        plt.plot(erlist)
##        plt.ylabel('error')
##        plt.show()
##        print "a,b,g,r,e and t stats", np.average(self.ca), np.std(self.ca), np.average(self.cb), np.std(self.cb), np.average(self.cg), np.std(self.cg), np.average(self.cr), np.std(self.cr), np.average(self.se), np.std(self.se), np.average(self.st), np.std(self.st)
##        print "max values", max(self.ca), max(self.cb), max(self.cg), max(self.cr), max(self.se),max(self.st)
##        plt.plot(erlist)
        #plt.show()





#    def gre(self):
#        i=1
#old mistaken stuff
#dst[s]+=self.ca[c]/(-self.cb[c]*len(self.ikc[it])
                        #                               +(kcf[c]*self.cr[c]+kcc[c]*self.cg[c])*self.se[s]*len(self.ikc[it])
                        #                               + self.st[s]*self.ca[c])
                        #dse[s]+=(kcf[c]*self.cr[c]+kcc[c]*self.cg[c])*len(self.ikc[it])/(-self.cb[c]*len(self.ikc[it])
                        #                               +(kcf[c]*self.cr[c]+kcc[c]*self.cg[c])*self.se[s]*len(self.ikc[it])
                        #                              + self.st[s]*self.ca[c])