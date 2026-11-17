import sys
from ortools.sat.python import cp_model


def read_instance(path):
    lines = open(path).read().splitlines()
    for i, line in enumerate(lines):
        tok = line.split()
        if len(tok) == 2 and all(t.isdigit() for t in tok):
            n, m = map(int, tok)
            jobs = []
            for l in lines[i + 1 : i + 1 + n]:
                v = list(map(int, l.split()))
                jobs.append([(v[k], v[k + 1]) for k in range(0, len(v), 2)])
            return jobs
    raise ValueError("Instance format not recognized")


def solve(jobs, time_limit=60):
    model = cp_model.CpModel()
    horizon = sum(d for job in jobs for _, d in job)
    n_machines = 1 + max(m for job in jobs for m, _ in job)

    by_machine = {m: [] for m in range(n_machines)}
    ends = {}
    for j, job in enumerate(jobs):
        for k, (m, d) in enumerate(job):
            s = model.NewIntVar(0, horizon, f"s_{j}_{k}")
            e = model.NewIntVar(0, horizon, f"e_{j}_{k}")
            iv = model.NewIntervalVar(s, d, e, f"i_{j}_{k}")
            by_machine[m].append(iv)
            ends[j, k] = e
            if k > 0:  # precedence inside a job
                model.Add(s >= ends[j, k - 1])

    for m in by_machine:  # one operation at a time per machine
        model.AddNoOverlap(by_machine[m])

    makespan = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(makespan, [ends[j, len(job) - 1] for j, job in enumerate(jobs)])
    model.Minimize(makespan)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 8
    status = solver.Solve(model)
    return solver, status


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else r"JSPLIB-master\instances\ft06"
    jobs = read_instance(path)
    print(f"{len(jobs)} jobs x {len(jobs[0])} operations")
    solver, status = solve(jobs)
    print("Status  :", solver.StatusName(status))
    print("Makespan:", solver.ObjectiveValue())
    print("Bound   :", solver.BestObjectiveBound())
    print("Time (s):", round(solver.WallTime(), 2))