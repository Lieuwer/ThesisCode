# -*- coding: utf-8 -*-
from edata import edata
import time,datetime
from collections import defaultdict,OrderedDict
import matplotlib.pyplot as plt

def main():
    test= edata()
    #test.save("testing.edata")
    test=edata.load("train.edata")
#    csq=test.countKCQuestions()
#    print len(csq),min(csq.values())
#    qps=defaultdict(int)
#    for q in csq.values():
#        qps[q]+=1
#    print max(qps.keys())
#    csq=OrderedDict(sorted(csq.items(), key=lambda t: t[1]))
#    fig={}
#    for nr,i in enumerate(csq.values()):
#        fig[nr]=i
#    plt.figure(1)
#    plt.plot(fig.keys(),fig.values())
#    plt.show()
    print len(test.data)
    test.removekcsq(3,15)

    print len(test.data)
    datas=test.splitDataS(3)
    
if __name__ == "__main__":
    t0=time.time()
    main()
    t1=time.time()
    print "Time taken by all code", str(datetime.timedelta(seconds=(t1-t0)))