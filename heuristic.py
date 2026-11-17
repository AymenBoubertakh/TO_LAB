import random
import sys

from jsp import read_instance


def giffler_thompson(jobs, rule="SPT", rng=None, return_seq=False):
    """Build one active schedule. Returns the makespan
    (and the job order used, if return_seq=True)."""
    n = len(jobs)
    nops = [len(j) for j in jobs]
    nxt = [0] * n                      # next operation of each job
    job_ready = [0] * n                # time each job becomes free
    mach_ready = {}                    # time each machine becomes free
    remaining = [sum(d for _, d in j) for j in jobs]
    total, done = sum(nops), 0
    order = []                         # job id of each scheduled operation

    while done < total:
        cand = []
        for j in range(n):
            if nxt[j] < nops[j]:
                m, d = jobs[j][nxt[j]]
                est = max(job_ready[j], mach_ready.get(m, 0))
                cand.append((est + d, est, j, m, d))
        c_star, _, _, m_star, _ = min(cand)          # earliest completion
        conflict = [c for c in cand if c[3] == m_star and c[1] < c_star]

        def score(c):                                  # smaller = chosen first
            _, est, j, m, d = c
            if rule == "SPT":
                return (d, j)
            if rule == "MWKR":                         # most work remaining
                return (-remaining[j], j)
            if rule == "MOPNR":                        # most operations remaining
                return (-(nops[j] - nxt[j]), j)
            if rule == "FIFO":                         # first arrived at the machine
                return (job_ready[j], j)
            return (rng.random(), j)                   # RANDOM

        _, est, j, m, d = min(conflict, key=score)
        job_ready[j] = est + d
        mach_ready[m] = est + d
        remaining[j] -= d
        nxt[j] += 1
        order.append(j)
        done += 1
    return (max(job_ready), order) if return_seq else max(job_ready)


RULES = ["SPT", "MWKR", "MOPNR", "FIFO"]

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "ft06"
    jobs = read_instance(rf"JSPLIB-master\instances\{name}")
    for r in RULES:
        print(f"{r:6s}", giffler_thompson(jobs, r))
    rng = random.Random(0)
    best = min(giffler_thompson(jobs, "RANDOM", rng) for _ in range(1000))
    print("RANDOM x1000 (best):", best)