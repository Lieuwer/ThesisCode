import sys
sys.path.append('..\models')
from edata import edata
from collections import defaultdict




def main():
    trainfile="D:\\scriptie\\Thesisdata\\gong3\\PFA_train_with_splitting.csv"
    testsfile="D:\\scriptie\\Thesisdata\\gong\\student_pretest_posttest.csv"
    f = open(trainfile, 'r')
    #Steps will count for each item, how often it occurs
    steps={}
    #kcs counts for every kc how often it occurs
    kcs=defaultdict(int)
    #kcq counts how many questions are associated with a certain number of kcs (the key)
    kcq=defaultdict(int)
    #First line has the headers
    line=f.readline()
    for n,p in enumerate(line.split(',')):
        print n, p
    #ikc links question # to KC #
    ikc={}
    icounter=0
    #kcsmap maps a written kc to a unique number
    kcsmap={}
    #items maps a problem name plus step name to a unique item number
    items=defaultdict(int)
    #sid maps a student to a int id
    sid=defaultdict(int)
    kcs=defaultdict(int)
    data=[]
    labels=[]
    additional=0
    total = 0

    check=defaultdict(int)    
    
    for line in f:
        total+=1
        parts=line.split(',')
        sid[int(parts[1])]+=1
        item=int(parts[4])
        items[item]+=1
        skill=int(parts[0])
        kcs[skill]+=1
        if not ikc.has_key(item):
            ikc[item]=[skill]
        elif not skill in ikc[item]:
            ikc[item].append(skill)
            additional+=1

    print "total records", total
    print "number students", len(sid.keys())
    print "number of items", len(items.keys())
    print "number of kcs", len(kcs.keys())
    print "Added skills", additional
    kcq=defaultdict(int)
    for l in ikc.values():
        kcq[len(l)]+=1
    for k,v in kcq.iteritems():
        print "number of items per kc versus occurences", k,v
    f.close()
'''
    f=open(testsfile,'r')
    #First line has the headers
    line=f.readline()
    ins=0
    out=0
    for line in f:
        parts=line.split(',')
        if int(parts[0]) in sid:
            ins+=1
        else:
            out+=1
            print parts[0]
    print "Students in file vs not", ins, out
'''
if __name__ == '__main__':
    main()
