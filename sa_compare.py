import random
import statistics
import sys

import pandas as pd

from heuristic import RULES, giffler_thompson
from jsp import read_instance
from sa import simulated_annealing

# usage: python sa_compare.py [seconds_per_run] [number_of_seeds]
SA_TIME = float(sys.argv[1]) if len(sys.argv) > 1 else 60
SEEDS = list(range(int(sys.argv[2]) if len(sys.argv) > 2 else 3))
N_RANDOM = 100

cp = pd.read_csv("results_cpsat_3instances.csv")
rows = []

for _, r in cp.iterrows():
    name = r["instance"]
    jobs = read_instance(rf"JSPLIB-master\instances\{name}")
    ref = r["best_known"] if pd.notna(r["best_known"]) else r["lower_bound"]

    # best dispatching schedule = starting point of the "heuristic start" version
    disp, best_seq = None, None
    for rule in RULES:
        v, s = giffler_thompson(jobs, rule, return_seq=True)
        if disp is None or v < disp:
            disp, best_seq = v, s
    rng = random.Random(0)
    for _ in range(N_RANDOM):
        v, s = giffler_thompson(jobs, "RANDOM", rng, return_seq=True)
        if v < disp:
            disp, best_seq = v, s

    random_runs, warm_runs = [], []
    for seed in SEEDS:
        random_runs.append(simulated_annealing(jobs, SA_TIME, seed=seed)[0])
        warm_runs.append(simulated_annealing(jobs, SA_TIME, seed=seed, init_seq=best_seq)[0])
        print(name, "seed", seed, "random:", random_runs[-1], "warm:", warm_runs[-1], flush=True)

    gap = lambda v: round(100 * (v - ref) / ref, 2)
    rows.append({
        "instance": name, "reference": int(ref), "dispatch": disp,
        "random_best": min(random_runs), "random_mean": round(statistics.mean(random_runs), 1),
        "random_gap_%": gap(min(random_runs)),
        "warm_best": min(warm_runs), "warm_mean": round(statistics.mean(warm_runs), 1),
        "warm_gap_%": gap(min(warm_runs)),
    })

out = pd.DataFrame(rows)
out.to_csv("results_sa_comparison.csv", index=False)
print()
print(out.to_string())