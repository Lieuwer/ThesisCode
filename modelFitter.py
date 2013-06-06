import random as r
import math as m
import matplotlib.pyplot as plt
import numpy as np
from sklearn import linear_model

class modelFitter:


    def __init__(self,nrs,nrkc,ikc,data):
        #store the kc's belonging to each item
        self.ikc=[]
        #lists that will hold the parameters of items and students
        self.ca=np.zeros(nrkc)
        self.cg=np.zeros(nrkc)
        self.cr=np.zeros(nrkc)
        self.cb=np.zeros(nrkc)
        self.st=np.zeros(nrs)
        self.se=np.zeros(nrs)
        
        self.kcc=np.zeros((nrs,nrkc))
        self.kcf=np.zeros((nrs,nrkc))
        #linkage of kcs to items is known
        self.ikc=ikc
        self.data=data
        #create student parameter estimates, now done in same fashion as generating data
        for i in range(nrs):
            self.st[i]=r.normalvariate(0,.5)
            self.se[i]=r.uniform(.06,.15)

        #create knowledge component parameter estimates, idem as above
        for i in range(nrkc):
            self.ca[i]=r.uniform(.75,1.5)
            g=r.uniform(.75,1.5)
            self.cg[i]=g
            self.cr[i]=g*r.uniform(.2,.8)
            self.cb[i]=r.normalvariate(0,.5)

    def iterate(self,maxiterations=250):
        #keep track of the error rate over the different itterations
        erlist=[]
        # this method performs iterative alternating logarithmic optamilatization of the logit of p for all datapoints
        labels=np.zeros(len(self.data))
        kcc=self.kcc
        kcf=self.kcf
        for i in range(15):
            nrs=len(self.st)
            nrkc=len(self.ca)
            #first fit the user parameters
            #Create an array of dimensions number of datapoints by number of students *2 + number of kcs
            studentdata=np.zeros((len(self.data),nrs*2+nrkc))
            #keep track of questions answered correctly and questions answered wrongly
            kcc = np.zeros((nrs,nrkc))
            kcf = np.zeros((nrs,nrkc))
            totalerror=0.0
            for nr,d in enumerate(self.data):
                s=d[0]
                it=d[1]
                x=0
                k=float(len(self.ikc[it]))
                labels[nr]=d[2]
                for c in self.ikc[it]:
                    x+=self.ca[c]*self.st[s]/k+(kcf[s,c]*self.cr[c]+kcc[s,c]*self.cg[c])*self.se[s]-self.cb[c]
                    studentdata[nr,s]+=self.ca[c]/k
                    studentdata[nr,s+nrs]+=self.cg[c]*kcc[s,c]+self.cr[c]*kcf[s,c]
                    studentdata[nr,nrs*2+c]=-1
                    if d[2]:
                        kcc[s,c]+=1
                    else:
                        kcf[s,c]+=1
                try:
                    big=m.exp(x)+1
                    if d[2]:
                        totalerror+=1/big
                    else:
                        totalerror+=1-(1/big)
                except:
                    if not d[2]:
                        totalerror+=1
            
            model=linear_model.LogisticRegression(fit_intercept=False,penalty='l1', C=10^9)
            model.fit(studentdata,labels)
                      
            self.st=model.coef_[0][:nrs].copy()
            self.se=model.coef_[0][nrs:nrs*2].copy()
            self.cb=model.coef_[0][nrs*2:].copy()

                
            #print result.summary() 
            print sum(abs(self.st))/nrs, sum(abs(self.se))/nrs, sum(abs(self.cb))/nrkc
            erlist.append(totalerror/len(self.data))
            print(totalerror/len(self.data))
            
            #Now estimate the kc parameters
            kcdata=np.zeros((len(self.data),4*nrkc))
            kcc = np.zeros((nrs,nrkc))
            kcf = np.zeros((nrs,nrkc))
            totalerror=0.0    
            for nr,d in enumerate(self.data):
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
                    if d[2]:
                        kcc[s,c]+=1
                    else:
                        kcf[s,c]+=1
                try:
                    big=m.exp(x)+1
                    if d[2]:
                        totalerror+=1/big
                    else:
                        totalerror+=1-(1/big)
                except:
                    if not d[2]:
                        totalerror+=1
            erlist.append(totalerror/len(self.data))
            print (totalerror/len(self.data))
            
            model=linear_model.LogisticRegression(fit_intercept=False,penalty='l1', C=10^9)
            model.fit(kcdata,labels)
            
            self.ca=model.coef_[0][:nrkc].copy()
            self.cg=model.coef_[0][nrkc:nrkc*2].copy()
            self.cr=model.coef_[0][nrkc*2:nrkc*3].copy()
            self.cb=model.coef_[0][nrkc*3:].copy()
            print sum(abs(self.ca))/nrkc, sum(abs(self.cg))/nrkc, sum(abs(self.cr))/nrkc, sum(abs(self.cb))/nrkc
            #normalize st and ca with eachother
#            size=sum(abs(self.st))/nrs
#            self.st/=size
#            self.ca*=size

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



    def predict(self,s,i):
        k=float(len(self.ikc[i]))
        x=0
        for c in self.ikc[i]:
            x+=self.ca[c]*self.st[s]/k+(self.kcf[s,c]*self.cr[c]+self.kcc[s,c]*self.cg[c])*self.se[s]-self.cb[c]
        return 1/(m.exp(-x)+1)

    def normalizegre(self):
        i=1
#old mistaken stuff
#dst[s]+=self.ca[c]/(-self.cb[c]*len(self.ikc[it])
                        #                               +(kcf[c]*self.cr[c]+kcc[c]*self.cg[c])*self.se[s]*len(self.ikc[it])
                        #                               + self.st[s]*self.ca[c])
                        #dse[s]+=(kcf[c]*self.cr[c]+kcc[c]*self.cg[c])*len(self.ikc[it])/(-self.cb[c]*len(self.ikc[it])
                        #                               +(kcf[c]*self.cr[c]+kcc[c]*self.cg[c])*self.se[s]*len(self.ikc[it])
                        #                              + self.st[s]*self.ca[c])