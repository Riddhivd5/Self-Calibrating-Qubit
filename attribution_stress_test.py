import numpy as np
from drift_framework import *
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
d=5; P_RO=0.01; P_PH=0.001
c0=build_circuit(d,p_readout=P_RO,p_phys=P_PH); lay=Layout(c0)
ref=features(sample_window(c0,200000,seed=1)[0],lay,np.ones(lay.n_anc))["per_anc"]
fr=lambda c: sample_window(c,100000,seed=5)[0].mean()
def match(target,mode):
    lo,hi=P_PH,0.08
    for _ in range(18):
        mid=(lo+hi)/2
        if fr(build_circuit(d,p_readout=P_RO,p_phys=mid,phys_mode=mode))<target: lo=mid
        else: hi=mid
    return (lo+hi)/2
def run(mode,W,nwin,seed0):
    X=[];y=[]
    for m in (1.5,2.0,3.0):
        cr=build_circuit(d,p_readout=m*P_RO,p_phys=P_PH)
        pp=match(fr(cr),mode); cp=build_circuit(d,p_readout=P_RO,p_phys=pp,phys_mode=mode)
        for lab,c in ((1,cr),(0,cp)):
            for k in range(nwin):
                det,_=sample_window(c,W,seed=seed0+k+1000*lab+100000*int(m*10))
                f=features(det,lay,ref); X.append([f['fire_rate'],f['tcorr'],f['asym']]); y.append(lab)
    return np.array(X),np.array(y)
for mode in ("data","gate"):
    for W in (200,1000):
        Xa,ya=run(mode,W,120,0); Xb,yb=run(mode,W,120,10_000_000); out=[]
        for name,cols in (("fire",[0]),("corr",[1]),("asym",[2]),("all3",[0,1,2])):
            sc=StandardScaler().fit(Xa[:,cols]); lr=LogisticRegression().fit(sc.transform(Xa[:,cols]),ya)
            out.append("%s %.3f"%(name,roc_auc_score(yb,lr.predict_proba(sc.transform(Xb[:,cols]))[:,1])))
        print(f"physical drift = {mode:4s}-noise only, W={W:5d} | "+" | ".join(out))
