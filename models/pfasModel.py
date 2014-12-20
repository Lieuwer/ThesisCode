import random as r
import math as m
import numpy as np
import scipy.sparse as sparsesp
from sklearn import linear_model
import scipy.stats as stat
from model import model

class pfasModel(model):
    def __init__(self,data,fullmatrix=True):
        #fullmatrix is a lot faster, but takes more memory and can thus simply
        #be infeasable        
        self.fullmatrix=fullmatrix        
        #store the kc's belonging to each item
        self.ikc=data.ikc
        #lists that will hold the parameters of items and students
        self.cg=np.zeros(data.nrkc)
        self.cr=np.zeros(data.nrkc)
        self.cb=np.zeros(data.nrkc)
        self.st=np.zeros(data.nrs)
        
        self.paranames=["beta","gamma","ro","theta0"]
        self.parameters=[]
        self.parameters.append(self.cb)
        self.parameters.append(self.cg)
        self.parameters.append(self.cr)        
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
        #create student parameter estimates, now done in same fashion as generating data
        #create student parameter estimates, now done in same fashion as generating data
        for i in range(data.nrs):
            self.st[i]=r.normalvariate(0,.5)

        #create knowledge component parameter estimates, idem as above
        for i in range(data.nrkc):
            g=r.uniform(.05,.02)
            self.cg[i]=g
            self.cr[i]=g*r.uniform(.2,.8)
            self.cb[i]=r.normalvariate(0,.5)
        
    def genParams(self):       
        
        for i in range(self.data.nrs):
            self.st[i]=r.normalvariate(-.5,1)


        #create knowledge component parameter estimates, idem as above
        for i in range(self.data.nrkc):
            g=r.uniform(.005,.02)
            self.cg[i]=g
            self.cr[i]=g*r.uniform(.2,.8)
            self.cb[i]=r.normalvariate(0,1.5)
        
    def probability(self,s,i):
        x=self.st[s]
        for c in self.ikc[i]:
            x+=self.kcf[s,c]*self.cr[c]+self.kcc[s,c]*self.cg[c]-self.cb[c]
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
            studentdata=np.zeros((len(self.data.data),nrs+nrkc*3))
        else:
            studentdata=sparsesp.lil_matrix((len(self.data.data),nrs+nrkc*3))
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
                x+=kcf[s,c]*self.cr[c]+kcc[s,c]*self.cg[c]-self.cb[c]
                studentdata[nr,c+nrs]=kcc[s,c]
                studentdata[nr,c+nrs+nrkc]=kcf[s,c]
                studentdata[nr,nrs+c+2*nrkc]=-1
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
        model.fit(studentdata,labels)
                  
        self.st[:]=model.coef_[0][:nrs]
        self.cg[:]=model.coef_[0][nrs:nrs+nrkc]
        self.cr[:]=model.coef_[0][nrs+nrkc:nrs+nrkc*2]
        self.cb[:]=model.coef_[0][nrs+nrkc*2:]
        #Save the found kcc and kcf

        
        return totalerror/len(self.data)

    def fit(self,maxiterations=50):
        self.fitError.append(self.sUpdate())
        return self.fitError[-1]
        

        