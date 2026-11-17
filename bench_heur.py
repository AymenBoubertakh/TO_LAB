import random
import time

import pandas as pd

from heuristic import RULES, giffler_thompson
from jsp import read_instance

N_RANDOM = 1000
cp = pd.read_csv("results_cpsat_60s.csv")
rows = []

for _, r in cp.iterrows():
    name, bks = r["instance"], r["best_known"]
    jobs = read_instance(rf"JSPLIB-master\instances\{name}")
    res, times = {}, {}

    for rule in RULES:
        t = time.time()
        res[rule] = giffler_thompson(jobs, rule)
        times[rule] = time.time() - t

    t = time.time()
    rng = random.Random(0)
    res["RANDOM"] = min(giffler_thompson(jobs, "RANDOM", rng) for _ in range(N_RANDOM))
    times["RANDOM"] = time.time() - t

    best_rule = min(res, key=res.get)
    rows.append({
        "instance": name,
        "best_known": bks,
        "cpsat": r["makespan"],
        "cpsat_gap_%": r["gap_%"],
        **{f"{k}": v for k, v in res.items()},
        "best_rule": best_rule,
        "heur_best": res[best_rule],
        "heur_gap_%": round(100 * (res[best_rule] - bks) / bks, 2),
        "heur_time_s": round(sum(times.values()), 3),
    })

out = pd.DataFrame(rows)
out.to_csv("results_heuristic.csv", index=False)
print(out[["instance", "best_known", "cpsat", "heur_best", "best_rule",
           "cpsat_gap_%", "heur_gap_%", "heur_time_s"]].to_string())
print("\nMean gap  CP-SAT: ", round(out["cpsat_gap_%"].mean(), 2),
      "%   Heuristic:", round(out["heur_gap_%"].mean(), 2), "%")