import csv
import json
import sys

from jsp import read_instance, solve

ROOT = "JSPLIB-master"
DEFAULT = (
    ["ft06", "ft10"]
    + [f"la{i:02d}" for i in range(1, 11)]
    + ["abz5", "abz6"]
    + [f"orb{i:02d}" for i in range(1, 6)]
    + [f"ta{i:02d}" for i in range(1, 11)]
)

# usage: python bench.py [time_limit_seconds] [instance names...]
time_limit = float(sys.argv[1]) if len(sys.argv) > 1 else 60
names = sys.argv[2:] or DEFAULT

meta = {d["name"]: d for d in json.load(open(f"{ROOT}/instances.json"))}


def best_known(name):
    d = meta.get(name, {})
    if d.get("optimum") is not None:
        return d["optimum"], "optimum"
    ub = (d.get("bounds") or {}).get("upper")
    return ub, "best-known upper bound"


rows = []
for name in names:
    jobs = read_instance(f"{ROOT}/instances/{name}")
    solver, status = solve(jobs, time_limit=time_limit)
    makespan = solver.ObjectiveValue()
    bks, kind = best_known(name)
    gap = round(100 * (makespan - bks) / bks, 2) if bks else None
    row = {
        "instance": name,
        "size": f"{len(jobs)}x{len(jobs[0])}",
        "status": solver.StatusName(status),
        "makespan": int(makespan),
        "lower_bound": int(solver.BestObjectiveBound()),
        "best_known": bks,
        "bk_type": kind,
        "gap_%": gap,
        "time_s": round(solver.WallTime(), 2),
    }
    rows.append(row)
    print(row, flush=True)

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print("\nSaved results.csv")