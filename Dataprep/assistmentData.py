import sys
sys.path.append('..\models')
from edata import edata
from collections import defaultdict




def main():
    trainfile="D:\\scriptie\\Thesisdata\\assistments_2009_2010.csv"
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
    parts=line.split(',')
    line=f.readline()
    parts2=line.split(',')
    for n,part in enumerate (parts):
        print n,part, parts2[n]
    #ikc links question # to KC #
    ikc=[]
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
    kcitems=0
    additional=0
    total = 0
    
    data=[]
    labels=[]
    smap={}
    kcmap={}
    imap ={}   
    
    for line in f:
        total+=1
        parts=line.split(',')
        if not smap.has_key(int(parts[2])):
            smap[int(parts[2])]=len(sid)
        if not imap.has_key(int(parts[4])):
            imap[int(parts[4])]=len(imap.keys())
            ikc.append([])
            if len(parts[16])>0:
                for p in parts[16].split(';'):
                    if not kcmap.has_key(int(p)):
                        kcmap[int(p)]=len(kcmap)
                    ikc[imap[int(parts[4])]].append(kcmap[int(p)])
            elif len(parts[17])>2:
                print "\nEven though there are no skill Id's we still have skills!!!!\n"
        if len(ikc[imap[int(parts[4])]])>0:

            data.append((smap[int(parts[2])],imap[int(parts[4])]))
            label=float(parts[6])
            if label<1.0:
                label=0
            else:
                label=1
            labels.append(label)
#        sid[int(parts[2])]+=1
#        item=int(parts[4])
#        items[item]+=1
#        if len(parts[16])>0:
#            if items[item]==1: kcitems+=1
#            existing=True
#            for p in parts[16].split(';'):
#                skill=int(p)
#                kcs[skill]+=1
#                if not ikc.has_key(item):
#                    ikc[item]=[skill]
#                    existing=False
#                elif not skill in ikc[item]:
#                    ikc[item].append(skill)
#                    if existing:
#                        additional+=1
    empty=0
    for l in ikc:
        if len(l)==0:
            empty+=1
    print "total records", total
    print "number students", len(smap)
    print "number of items / items with kcs", len(ikc), empty
    #without rechecking
    print "number of kcs", len(kcmap)
#    print "Added skills", additional
    kcq=defaultdict(int)
    for l in ikc:
        kcq[len(l)]+=1
    for k,v in kcq.iteritems():
        print "number of items per kc versus occurences", k,v
    f.close()
    
    dataset=edata()    
    dataset.initialize(ikc, len(smap),len(kcmap),data,labels)
    dataset.save("assistment.edata")
    
    print "correct versus total data:", sum(labels),len(data)
'''
    f=open(testsfile,'r')
    #First line has the headers
    line=f.readline()
    ins=0
    out=0
    for line in f:
        parts=line.split(',')
        if int(parts[0]) in smap.keys:
            ins+=1
        else:
            out+=1
            print parts[0]
    print "Students in file vs not", ins, out
'''
if __name__ == '__main__':
    main()
