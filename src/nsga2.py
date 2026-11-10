"""NSGA-II from scratch (numpy only), as used in the DCS 340 class activity.

How to read this file, top to bottom:
  1. zdt1 / zdt2      - test problems: turn a population into objective scores
  2. nondominated_sort - "Step 1: Rank"   (peel the population into fronts)
  3. crowding_distance - "Step 2: Spread" (prefer points in empty regions)
  4. vary              - ordinary GA variation (crossover + mutation)
  5. nsga2             - "Step 3: Keep the elite" (the main generational loop)

Shapes used everywhere:
  X : (n_individuals, n_variables)  genomes, each value in [0, 1]
  F : (n_individuals, 2)            objective scores, BOTH minimized

References:
  Deb, Pratap, Agarwal & Meyarivan (2002), IEEE TEC 6(2):182-197  (NSGA-II)
  Zitzler, Deb & Thiele (2000), Evolutionary Computation 8(2)      (ZDT problems)
"""
import numpy as np

rng = np.random.default_rng(0)


# ----------------------------------------------------------------------------
# 1. Test problems
# ----------------------------------------------------------------------------
def zdt1(X):
    """ZDT1: true Pareto front is f2 = 1 - sqrt(f1) (bulges toward the origin).

    f1 is just the first gene. g measures how far the OTHER 29 genes are from 0;
    the front is reached only when they are all 0 (g = 1).
    """
    f1 = X[:, 0]
    g = 1 + 9 * X[:, 1:].mean(axis=1)
    f2 = g * (1 - np.sqrt(f1 / g))
    return np.c_[f1, f2]          # stack into an (n, 2) array


def zdt2(X):
    """ZDT2: same as ZDT1 but the front sags (concave): f2 = 1 - f1**2."""
    f1 = X[:, 0]
    g = 1 + 9 * X[:, 1:].mean(axis=1)
    f2 = g * (1 - (f1 / g) ** 2)
    return np.c_[f1, f2]


# ----------------------------------------------------------------------------
# 2. Non-dominated sorting  (Deb's "fast" bookkeeping version)
# ----------------------------------------------------------------------------
def nondominated_sort(F):
    """Return a list of fronts; each front is a list of row indices into F.

    fronts[0] = nobody dominates them (the Pareto front of this population)
    fronts[1] = the front once fronts[0] is removed, and so on.
    """
    n = len(F)
    dominated_by = [[] for _ in range(n)]   # dominated_by[i] = everyone i beats
    counts = np.zeros(n, int)                # counts[i] = how many beat i

    for i in range(n):
        # i dominates j  <=>  i is <= j on every objective AND < on at least one
        i_beats = np.all(F[i] <= F, axis=1) & np.any(F[i] < F, axis=1)
        dominated_by[i] = list(np.where(i_beats)[0])
        # same test the other way round: how many rows dominate i?
        counts[i] = np.sum(np.all(F <= F[i], axis=1) & np.any(F < F[i], axis=1))

    fronts = []
    current = list(np.where(counts == 0)[0])     # nobody beats them -> front 1
    while current:
        fronts.append(current)
        nxt = []
        for i in current:                        # "remove" this front...
            for j in dominated_by[i]:
                counts[j] -= 1                   # ...j has one fewer conqueror
                if counts[j] == 0:               # nobody left above j
                    nxt.append(j)
        current = nxt
    return fronts


# ----------------------------------------------------------------------------
# 3. Crowding distance
# ----------------------------------------------------------------------------
def crowding_distance(F):
    """Bigger value = lonelier point. Used only to break ties inside one front.

    For each objective: sort the front, then give each point the gap between
    its two neighbours, divided by that objective's range. Sum over objectives
    (this is half the perimeter of the box drawn on slide 9).
    """
    n, m = F.shape
    d = np.zeros(n)
    for k in range(m):
        order = np.argsort(F[:, k])                       # sort by objective k
        d[order[0]] = d[order[-1]] = np.inf               # always keep the two ends
        span = F[order[-1], k] - F[order[0], k] or 1.0    # avoid dividing by 0
        # neighbour after minus neighbour before, for every interior point
        d[order[1:-1]] += (F[order[2:], k] - F[order[:-2], k]) / span
    return d


# ----------------------------------------------------------------------------
# 4. Variation (nothing multi-objective here - same as our earlier GAs)
# ----------------------------------------------------------------------------
def vary(P, pm=None):
    """Make len(P) children: uniform crossover, then Gaussian mutation."""
    n, d = P.shape
    pm = pm or 1 / d                                   # ~1 gene mutated per child
    idx = rng.integers(0, n, (n, 2))                   # pick two random parents
    a, b = P[idx[:, 0]], P[idx[:, 1]]
    take_a = rng.random((n, d)) < 0.5                  # coin flip per gene
    C = np.where(take_a, a, b)                         # uniform crossover
    mutate = rng.random((n, d)) < pm
    C = C + rng.normal(0, 0.1, (n, d)) * mutate        # small Gaussian nudge
    return np.clip(C, 0, 1)                            # stay inside [0, 1]


# ----------------------------------------------------------------------------
# 5. The NSGA-II loop
# ----------------------------------------------------------------------------
def nsga2(problem, n_var=30, pop=100, gens=150, use_crowding=True, seed=0):
    """Run NSGA-II and return the final population's objective scores F.

    use_crowding=False replaces step 2 with a random pick (the ablation used
    in the activity and in my_investigations.ipynb).
    """
    global rng
    rng = np.random.default_rng(seed)
    P = rng.random((pop, n_var))                       # random starting genomes

    for _ in range(gens):
        R = np.vstack([P, vary(P)])                    # parents + children: 2N
        F = problem(R)                                 # score all 2N
        survivors = []
        for front in nondominated_sort(F):             # best front first
            if len(survivors) + len(front) <= pop:
                survivors += front                     # whole front fits: keep it
            else:
                need = pop - len(survivors)            # only room for some
                if use_crowding:
                    cd = crowding_distance(F[front])
                    pick = np.argsort(-cd)[:need]      # loneliest first
                else:
                    pick = rng.choice(len(front), need, replace=False)
                survivors += list(np.array(front)[pick])
                break                                  # population is full
        P = R[survivors]                               # next generation (elitism)
    return problem(P)


if __name__ == "__main__":
    F = nsga2(zdt1, gens=50)
    print("final population:", F.shape, " f1 range covered:", round(float(np.ptp(F[:, 0])), 2))
