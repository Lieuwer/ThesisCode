# -*- coding: utf-8 -*-
# Currently the baseline takes the product average of the fraction of how 
#often the user has seen the corresponding KC's
from model import model

class baseline(model):
    def __init__(self,data):
        # Keep track of how many questions containing that kc each student has
        # answered correctly
        # and incorrectly respectively
        self.data=data
        self.sc=[0]*data.nrs
        self.sf=[0]*data.nrs
        for i in range(data.nrs):
           self.sc[i]=[0]*data.nrkc
           self.sf[i]=[0]*data.nrkc
        #Same for items
        self.ikc=data.ikc
        self.itc=[0]*len(data.ikc)
        self.itf=[0]*len(data.ikc)
        
       
        
    def fit(self):
        for d in self.data.giveData():
            s=d[0]
            i=d[1]
            if d[2]:
                self.itc[i]+=1
                for kc in self.ikc[i]:
                    self.sc[s][kc]+=1
            else:
                self.itf[i]+=1
                for kc in self.ikc[i]:
                    self.sf[s][kc]+=1
    
    def predict(self,s,it):
        result=1
        for kc in self.ikc[it]:
            try:
                if (self.sc[s][kc]+self.sf[s][kc])>0:
                    result*=float(self.sc[s][kc])/(self.sc[s][kc]+self.sf[s][kc])
                else:
                    #take care of the problem that sometimes a student hasn't seen a kc yet
                    result*=.1
            except:
                print it,kc
        if len(self.ikc[it])==0:
            result= .5
        else:
            result=result**(1.0/len(self.ikc[it]))
        return result
    

              
                    
            
