"""Regenerate every figure used in the README (run by the GitHub Actions workflow).

Usage (from the repo root):  python src/make_figures.py
Writes PNGs into figures/.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")                      # no screen needed (GitHub runner)
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from nsga2 import nsga2, zdt1, zdt2      # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(OUT, exist_ok=True)
GREEN, AMBER, GREY = "#2E7D4F", "#C7841A", "#C9D3CC"


def save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, name), dpi=150)
    plt.close()


# 1. Part A: ten made-up pups (ventilation up = good, energy cost down = good)
pups = {"A": (1.48, 3.2), "B": (1.85, 3.6), "C": (2.00, 4.6), "D": (1.70, 4.0),
        "E": (2.25, 5.9), "F": (1.50, 3.0), "G": (1.90, 4.8), "H": (1.95, 5.0),
        "I": (1.40, 3.3), "J": (2.30, 7.2)}


def dominates(a, b):
    return a[0] >= b[0] and a[1] <= b[1] and (a[0] > b[0] or a[1] < b[1])


front = [n for n, v in pups.items() if not any(dominates(w, v) for w in pups.values() if w != v)]
plt.figure(figsize=(5.5, 4))
for n, (vent, cost) in pups.items():
    plt.scatter(cost, vent, s=70, zorder=3, color=GREEN if n in front else GREY)
    plt.annotate(n, (cost, vent), xytext=(5, 3), textcoords="offset points")
pts = sorted((pups[n][1], pups[n][0]) for n in front)
plt.plot(*zip(*pts), "--", color=GREEN, lw=1)
plt.xlabel("Energy cost (a.u.)  <- better")
plt.ylabel("Ventilation (mL/min/g)  better ->")
plt.title("Part A: the Pareto front (illustrative pups)")
save("partA_rat_front.png")

# 2. Weighted sums on a convex vs a concave front
t = np.linspace(0, 1, 200)
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, (name, F) in zip(axes, {"convex front": np.c_[t, 1 - np.sqrt(t)],
                               "concave front": np.c_[t, 1 - t ** 2]}.items()):
    hits = sorted({int(np.argmin(w * F[:, 0] + (1 - w) * F[:, 1])) for w in np.linspace(0, 1, 101)})
    ax.plot(F[:, 0], F[:, 1], color=GREY, lw=4, label="true front")
    ax.scatter(F[hits, 0], F[hits, 1], color=GREEN, zorder=3, label=f"weighted-sum hits ({len(hits)})")
    ax.set_title(name); ax.set_xlabel("f1 (minimize)"); ax.set_ylabel("f2 (minimize)"); ax.legend()
save("weighted_sum_convex_vs_concave.png")

# 3. NSGA-II on ZDT1
F_on = nsga2(zdt1)
plt.figure(figsize=(5.5, 4))
plt.plot(t, 1 - np.sqrt(t), color=GREY, lw=4, label="true front")
plt.scatter(F_on[:, 0], F_on[:, 1], s=14, color=GREEN, label="NSGA-II, generation 150")
plt.xlabel("f1"); plt.ylabel("f2"); plt.title("ZDT1"); plt.legend()
save("nsga2_zdt1.png")

# 4. Ablations ("break it on purpose")
runs = {"baseline": {}, "no crowding": {"use_crowding": False}, "pop = 10": {"pop": 10},
        "gens = 20": {"gens": 20}, "seed = 3": {"seed": 3}, "ZDT2 (concave)": {"problem": zdt2}}
fig, axes = plt.subplots(2, 3, figsize=(13, 7.5), sharex=True, sharey=True)
for ax, (name, kw) in zip(axes.flat, runs.items()):
    kw = dict(kw); p = kw.pop("problem", zdt1)
    F = nsga2(p, **kw)
    true = 1 - np.sqrt(t) if p is zdt1 else 1 - t ** 2
    ax.plot(t, true, color=GREY, lw=4)
    ax.scatter(F[:, 0], F[:, 1], s=12, color=GREEN if name == "baseline" else AMBER)
    ax.set_title(f"{name}\ncoverage {np.ptp(F[:, 0]):.2f}", fontsize=10)
    ax.set_ylim(-0.05, 2)
save("investigations.png")
print("wrote figures to", os.path.abspath(OUT))
