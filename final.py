import random
import time

import pandas as pd

from heuristic import RULES, giffler_thompson
from jsp import read_instance
from sa import simulated_annealing

SA_TIME = 60        # seconds per instance for simulated annealing
N_RANDOM = 100      # random dispatching tries per instance

cp = pd.read_csv("results_cpsat_3instances.csv")
rows = []

for _, r in cp.iterrows():
    name = r["instance"]
    jobs = read_instance(rf"JSPLIB-master\instances\{name}")

    # reference: best-known value if the repo has one, otherwise the CP-SAT lower bound
    if pd.notna(r["best_known"]):
        ref, ref_type = r["best_known"], "best-known"
    else:
        ref, ref_type = r["lower_bound"], "lower bound"

    # heuristic 1: dispatching rules (+ random tries), keep the best schedule's job order
    t = time.time()
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
    t_disp = time.time() - t

    # heuristic 2: simulated annealing, warm-started from the best dispatching schedule
    t = time.time()
    sa, _ = simulated_annealing(jobs, SA_TIME, seed=0, init_seq=best_seq)
    t_sa = time.time() - t

    gap = lambda v: round(100 * (v - ref) / ref, 2)
    rows.append({
        "instance": name, "size": r["size"], "reference": int(ref), "ref_type": ref_type,
        "cpsat": int(r["makespan"]), "cpsat_status": r["status"],
        "cpsat_gap_%": gap(r["makespan"]), "cpsat_time_s": round(r["time_s"], 1),
        "dispatch": disp, "dispatch_gap_%": gap(disp), "dispatch_time_s": round(t_disp, 1),
        "sa": sa, "sa_gap_%": gap(sa), "sa_time_s": round(t_sa, 1),
    })
    print(rows[-1], flush=True)

out = pd.DataFrame(rows)
out.to_csv("results_final.csv", index=False)
print()
print(out.to_string())