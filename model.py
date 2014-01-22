# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 13:39:26 2014

@author: Lieuwe
"""
import cPickle as pickle
import random as r

def aprime(predict,labels):
    #Does not yet take into account the issue that there is dependancy between some of the data
    correct=[0]*sum(labels)
    incorrect=[0]*(len(labels)-len(correct))
    c=n=0
    for i in range(len(labels)):
        if labels[i]:
            correct[c]=predict[i]
            c+=1
        else:
            incorrect[n]=predict[i]
            n+=1
    total=0.0
    for yes in correct:
        for no in incorrect:
            if yes>no:
                total+=1
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
            self.genError+=(1-p)
        else:
            self.data.labels.append(0)
            self.genError+=p

    def giveGenError(self):
        return self.genError/len(self.data.data)
    
    def useTestset(self,testdata):
        predictions=[]
        self.ikc=testdata.ikc
        for d in testdata.giveData():
            predictions.append(self.predict(d[0],d[1]))
        return aprime(predictions,testdata.labels)