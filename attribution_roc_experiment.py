import numpy as np
from drift_framework import *
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
d=5; P_RO=0.01; P_PH=0.001
c0=build_circuit(d,p_readout=P_RO,p_phys=P_PH); lay=Layout(c0)
ref=features(sample_window(c0,200000,seed=1)[0],lay,np.ones(lay.n_anc))["per_anc"]
def fr(c,seed=5): return sample_window(c,100000,seed=seed)[0].mean()
def match_phys(target):
    lo,hi=P_PH,0.05
    for _ in range(18):
        mid=(lo+hi)/2
        if fr(build_circuit(d,p_readout=P_RO,p_phys=mid))<target: lo=mid
        else: hi=mid
    return (lo+hi)/2
# hot-ancilla scale (some ancillas drift harder than others): 1/4 of ancillas get x3 extra readout error
qc=c0.get_final_qubit_coordinates(); inv={tuple(v):k for k,v in qc.items()}
xy=sorted({(float(a),float(b)) for a,b in [tuple(c0.get_detector_coordinates()[i][:2]) for i in range(c0.num_detectors)]})
rng=np.random.default_rng(0); hot=[xy[i] for i in rng.choice(len(xy),len(xy)//4,replace=False)]
hot_scale={inv[h]:3.0 for h in hot if h in inv}
def run(mode,W,nwin,seed0):
    X=[];y=[]
    for m in (1.5,2.0,3.0):
        if mode=="uniform": cr=build_circuit(d,p_readout=m*P_RO,p_phys=P_PH)
        else: cr=build_circuit(d,p_readout=m*P_RO,p_phys=P_PH,readout_scale=hot_scale)
        pp=match_phys(fr(cr)); cp=build_circuit(d,p_readout=P_RO,p_phys=pp)
        for lab,c in ((1,cr),(0,cp)):
            for k in range(nwin):
                det,_=sample_window(c,W,seed=seed0+k+1000*lab+100000*int(m*10))
                f=features(det,lay,ref); X.append([f['fire_rate'],f['tcorr'],f['asym']]); y.append(lab)
    return np.array(X),np.array(y)
for mode in ("uniform","hot-ancilla"):
  for W in (200,1000):
    Xa,ya=run(mode,W,150,0); Xb,yb=run(mode,W,150,10_000_000)   # disjoint seeds train/test
    out=[]
    for name,cols in (("fire only",[0]),("tcorr",[1]),("asym",[2]),("tcorr+asym",[1,2]),("all3",[0,1,2])):
        sc=StandardScaler().fit(Xa[:,cols]); lr=LogisticRegression().fit(sc.transform(Xa[:,cols]),ya)
        out.append("%s %.3f"%(name,roc_auc_score(yb,lr.predict_proba(sc.transform(Xb[:,cols]))[:,1])))
    print(f"{mode:12s} W={W:5d} AUC:", " | ".join(out))
