# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 17:11:20 2014

@author: Lieuwe
"""
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
    for c in correct:
        for n in incorrect:
            if c>incorrect:
                total+=1
    return total/len(correct)*len(incorrect)
        
