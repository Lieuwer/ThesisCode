# -*- coding: utf-8 -*-
import cPickle as pickle
import random as r

#Go from a cumulative distribution list to determine what kc's are
#linked to what item

def distribution(plist):
    n=r.random()
    for i in range(len(plist)):
        if n<plist[i]:
            return i+1
    return len(plist)+1

class edata:
    def save(self, filename):
        filehandle= open (filename,"wb")
        pickle.dump(self,filehandle)
        filehandle.close()
        
    @staticmethod
    def load(filename):
        filehandle=open (filename,"rb")
        return pickle.load(filehandle)
    
    def __len__(self):
        return len(self.data)


    def __init__(self):
        self.data=None
        self.labels=None
        self.ikc=None
        self.nrs=None
        self.nrkc=None

    def giveData(self):
        i=0
        while i<len(self.data):
            yield (self.data[i][0],self.data[i][1],self.labels[i])
            i+=1

    def generate(self,nrs,nrkc,nri):
        self.data=[]
        self.labels=[]
        self.nrs=nrs
        self.nrkc=nrkc
        self.ikc=[]
        kcdist = [.4,.65,.85,.99]

        
        for i in range(nri):
            kcs=[]
            for i in range(distribution(kcdist)):
                kc = r.randrange(nrkc)
                #make sure no KC is double
                while kc in kcs:
                    kc = r.randrange(nrkc)
                kcs.append(kc)
            self.ikc.append(kcs)
        
        
    def initialize(self,ikc,nrs,nrkc,data=[],labels=[]):
        self.data=data
        self.labels=labels
        self.ikc=ikc
        self.nrs=nrs
        self.nrkc=nrkc

    def initializeCopy(self,other,data=[],labels=[]):
        self.data=data
        self.labels=labels
        self.ikc=other.ikc
        self.nrs=other.nrs
        self.nrkc=other.nrkc
        
        
    def clearData(self):
        self.data=[]
        self.labels=[]        
        

        

    
    