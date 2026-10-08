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
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)
for ax, mode in zip(axes, ("uniform", "hot-ancilla")):
    W = 200
    Xa, ya = run(mode, W, 150, 0); Xb, yb = run(mode, W, 150, 10_000_000)  # disjoint seeds: train / test
    out = []
    for name, cols in (("fire rate only", [0]), ("correlation only", [1]), ("asymmetry only", [2]), ("all three", [0, 1, 2])):
        sc = StandardScaler().fit(Xa[:, cols]); lr = LogisticRegression().fit(sc.transform(Xa[:, cols]), ya)
        score = lr.predict_proba(sc.transform(Xb[:, cols]))[:, 1]
        auc = roc_auc_score(yb, score); fpr, tpr, _ = roc_curve(yb, score)
        ax.plot(fpr, tpr, label=f"{name} (AUC {auc:.3f})"); out.append(f"{name} {auc:.3f}")
    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.set_title(f"{mode} readout drift, {W}-shot windows"); ax.set_xlabel("false positive rate")
    ax.legend(fontsize=8, loc="lower right")
    print(f"{mode:12s} W={W}: " + " | ".join(out))
axes[0].set_ylabel("true positive rate (positive = readout drift)")
fig.tight_layout(); fig.savefig("attribution_roc.png", dpi=150)
print("wrote attribution_roc.png")
