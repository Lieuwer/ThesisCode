import random as r
import math as m
import numpy as np
import scipy.sparse as sparsesp
from sklearn import linear_model
import cPickle as pickle
import scipy.stats as stat

class complexModel:
    def save(self, filename):
        filehandle= open (filename,"wb")
        pickle.dump(self,filehandle)
        filehandle.close()
        
    @staticmethod
    def load(filename):
        filehandle=open (filename,"rb")
        return pickle.load(filehandle)

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
            g=r.uniform(.075,.15)
            self.cg[i]=g
            self.cr[i]=g*r.uniform(.2,.8)
            self.cb[i]=r.normalvariate(0,.5)
        
    def genParams(self):       
        
        for i in range(self.data.nrs):
            self.st[i]=r.normalvariate(-.03,1)


        #create knowledge component parameter estimates, idem as above
        for i in range(self.data.nrkc):
            g=r.uniform(.015,.06)
            self.cg[i]=g
            self.cr[i]=g*r.uniform(.2,.8)
            self.cb[i]=r.normalvariate(0,1.5)
     
    def changeData(self,newdata):
        #continue on another dataset, but keep all other info
        self.genError=0.0
        self.fitError=[1]
        self.data=newdata
        
    def clearGenerate(self):
        #clear the data and reset the generator to the moment when no data is made yet
        self.data.clearData()
        self.kcc=np.zeros((self.data.nrs,self.data.nrkc))
        self.kcf=np.zeros((self.data.nrs,self.data.nrkc))
        
    def predict(self,s,i):
        k=float(len(self.ikc[i]))
        x=0
        for c in self.ikc[i]:
            x+=self.st[s]/k+(self.kcf[s,c]*self.cr[c]+self.kcc[s,c]*self.cg[c])-self.cb[c]
        return 1/(m.exp(-x)+1)
        
    def generate(self,s,i):
        p = self.predict(s,i)
        self.data.data.append((s,i))
        if r.random()<p:
            self.data.labels.append(1)
            self.genError+=(1-p)
            for kc in self.ikc[i]:
                self.kcc[s,kc]+=1
        else:
            self.data.labels.append(0)
            self.genError+=p
            for kc in self.ikc[i]:
                self.kcf[s,kc]+=1
     
    def giveGenError(self):
        return self.genError/len(self.data.data)
    
    def giveParams(self):
        return (self.cb, self.cg, self.cr,self.st)
        
    def spearman(self, other):
        answerlist=np.zeros(4)
        answerlist[0]=stat.spearmanr(self.cb,other.cb)[0]
        answerlist[1]=stat.spearmanr(self.cg,other.cg)[0]
        answerlist[2]=stat.spearmanr(self.cr,other.cr)[0]
        answerlist[3]=stat.spearmanr(self.st,other.st)[0]
        return answerlist
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
            studentdata=np.zeros((len(self.data.data),nrs*2+nrkc))
        else:
            studentdata=sparsesp.lil_matrix((len(self.data.data),nrs*2+nrkc))
        #keep track of questions answered correctly and questions answered wrongly
        kcc = self.kcc= np.zeros((nrs,nrkc))
        kcf = self.kcf= np.zeros((nrs,nrkc))
        totalerror=0.0
        for nr,d in enumerate(self.data.giveData()):
            
            s=d[0]
            it=d[1]
            x=0
            k=float(len(self.ikc[it]))
            for c in self.ikc[it]:
                x+=self.ca[c]*self.st[s]/k+(kcf[s,c]*self.cr[c]+kcc[s,c]*self.cg[c])*self.se[s]-self.cb[c]
                studentdata[nr,s]+=self.ca[c]/k
                studentdata[nr,s+nrs]+=self.cg[c]*kcc[s,c]+self.cr[c]*kcf[s,c]
                studentdata[nr,nrs*2+c]=-1
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
        model=linear_model.LogisticRegression(fit_intercept=False,penalty='l1',C=10^9)
        model.fit(studentdata,labels)
                  
        self.st=model.coef_[0][:nrs].copy()
        self.se=model.coef_[0][nrs:nrs*2].copy()
        self.cb=model.coef_[0][nrs*2:].copy()
        #Save the found kcc and kcf

        
        return totalerror/len(self.data.data)

    def kcUpdate(self):
        nrs=len(self.st)
        nrkc=len(self.ca)
        labels=self.data.labels
        #Do a single fitting of the kc parameters and update them
        if self.fullmatrix:
            kcdata=np.zeros((len(self.data.data),4*nrkc))
        else:
            kcdata=sparsesp.lil_matrix((len(self.data.data),4*nrkc))
        
        kcc = np.zeros((nrs,nrkc))
        kcf = np.zeros((nrs,nrkc))
        totalerror=0.0    
        for nr,d in enumerate(self.data.giveData()):
            s=d[0]
            it=d[1]
            k=float(len(self.ikc[it]))
            x=0
            for c in self.ikc[it]:
                x+=self.ca[c]*self.st[s]/k+(kcf[s,c]*self.cr[c]+kcc[s,c]*self.cg[c])*self.se[s]-self.cb[c]
                kcdata[nr,c]+=self.st[s]/k
                kcdata[nr,c+nrkc]+=self.se[s]*kcc[s,c]
                kcdata[nr,c+2*nrkc]+=self.se[s]*kcf[s,c]
                kcdata[nr,nrkc*3+c]=-1
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
                    print "WARNING: major error added in kc"
                    totalerror+=1
      
        model=linear_model.LogisticRegression(fit_intercept=False,penalty='l1',C=10^9)
        model.fit(kcdata,labels)
        
        
        self.ca=model.coef_[0][:nrkc].copy()
        self.cg=model.coef_[0][nrkc:nrkc*2].copy()
        self.cr=model.coef_[0][nrkc*2:nrkc*3].copy()
        self.cb=model.coef_[0][nrkc*3:].copy()
        
        return totalerror/len(self.data.data)

    def fit(self,maxiterations=50):
        #keep track how often in succession no improvements were made       
        noimprov=0
        # this method performs iterative alternating logarithmic optamilatization of the logit of p for all datapoints
        for i in range(maxiterations):
            self.fitError.append(self.sUpdate())
            #print self.fitError[-1]
            
            if self.fitError[-3]-self.fitError[-1]<.001:
                noimprov+=1
            else:
                noimprov=0
            if noimprov>1:
                print "Improvement threshold reached at 1 iteration", i
                break
            
            #Now estimate the kc parameters
            
            #normalize st and ca with eachother
#            size=sum(abs(self.st))/nrs
#            self.st/=size
#            self.ca*=size
            #see if we want to get out of the loop
            
            self.fitError.append(self.kcUpdate())
            #print self.fitError[-1]
            if self.fitError[-3]-self.fitError[-1]<.001:
                noimprov+=1
            else:
                noimprov=0
            if noimprov>1:
                print "Improvement threshold reached at 2 iteration", i
                break
        return self.fitError[-1]
        
    def normalizeParameters(self):
        #make the average of alpha equal to 1 and the average of eta equal to .05
        avga=np.mean(self.ca)
        self.ca/=avga
        self.st*=avga
        avge=np.mean(self.se)*20
        self.se/=avge
        self.cr*=avge
        self.cg*=avge
        
    def useTestset(self,testdata):
        error=0
        for d in testdata.giveData():
            p=self.predict(d[0],d[1])
            if d[2]:
                error+=1-p
            else:
                error+=p
        return error/len(testdata)