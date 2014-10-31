import sys
sys.path.append('..\models')
from edata import edata
from collections import defaultdict




def main():
    trainfile="D:\\scriptie\\Thesisdata\\gong3\\PFA_train_with_splitting.csv"
    testsfile="D:\\scriptie\\Thesisdata\\gong3\\PFA_test_with_splitting.csv"
    f = open(trainfile, 'r')
    #kcq counts how many questions are associated with a certain number of kcs (the key)
    kcq=defaultdict(int)
    #First line has the headers
    line=f.readline()
    for n,p in enumerate(line.split(',')):
        print n, p
    #ikc links question # to KC #
    ikc=[]
    #kcsmap maps a written kc to a unique number
    kcsmap={}
    #items maps an item to a number
    imap={}
    #sid maps a student to a int id
    sid={}
    data=[]
    labels=[]
    total = 0

  
    
    previous=-1
    for line in f:
        total+=1
        parts=line.split(',')
        if not previous==int(parts[3]):
            if not int(parts[1]) in sid.keys():
                sid[int(parts[1])]=len(sid.keys())
            if not int(parts[4]) in imap.keys():
                imap[int(parts[4])]=len(imap.keys())
                ikc.append([])
            item=imap[int(parts[4])]
            if not int(parts[0]) in kcsmap.keys():
                kcsmap[int(parts[0])]=len(kcsmap.keys())
            kc=kcsmap[int(parts[0])]
            if not kc in ikc[item]:
                ikc[item].append(kc)
            data.append((sid[int(parts[1])],item))
            labels.append(int(parts[2]))
        if not int(parts[0]) in kcsmap.keys():
            kcsmap[int(parts[0])]=len(kcsmap.keys())
        kc=kcsmap[int(parts[0])]
        if not kc in ikc[item]:
            ikc[item].append(kc)
        previous=int(parts[3])


    f=open(testsfile,'r')
    #First line has the headers
    line=f.readline()
    previous=-1
    for line in f:
        total+=1
        parts=line.split(',')
        if not previous==int(parts[3]):
            if not int(parts[1]) in sid.keys():
                sid[int(parts[1])]=len(sid.keys())
            if not int(parts[4]) in imap.keys():
                imap[int(parts[4])]=len(imap.keys())
                ikc.append([])
            item=imap[int(parts[4])]
            if not int(parts[0]) in kcsmap.keys():
                kcsmap[int(parts[0])]=len(kcsmap.keys())
            kc=kcsmap[int(parts[0])]
            if not kc in ikc[item]:
                ikc[item].append(kc)
            data.append((sid[int(parts[1])],item))
            labels.append(int(parts[2]))
        if not int(parts[0]) in kcsmap.keys():
            kcsmap[int(parts[0])]=len(kcsmap.keys())
        kc=kcsmap[int(parts[0])]
        if not kc in ikc[item]:
            ikc[item].append(kc)
        previous=int(parts[3])
    f.close()
    print "total records/datapoints", total, len(data)
    print "number students", len(sid.keys())
    print "number of items", len(imap.keys())
    print "number of kcs", len(kcsmap)
    kcq=defaultdict(int)
    for l in ikc:
        kcq[len(l)]+=1
    for k,v in kcq.iteritems():
        print "number of items per kc versus occurences", k,v
    f.close()
    
    
    dataset=edata()    
    dataset.initialize(ikc, len(sid),len(kcsmap),data,labels)
    dataset.createTestSet(7)
    dataset.save("gong.edata")
    
#    print "The length of testdata", len(testdata)
'''
    testsfile="D:\\scriptie\\Thesisdata\\gong\\student_pretest_posttest.csv"
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
