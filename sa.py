import math
import random
import sys
import time

from jsp import read_instance


def decode(seq, jobs, n_mach):
    """Turn a job sequence (job id repeated once per operation) into a schedule. Returns the makespan."""
    nxt = [0] * len(jobs)
    job_ready = [0] * len(jobs)
    mach_ready = [0] * n_mach
    for j in seq:
        m, d = jobs[j][nxt[j]]
        start = job_ready[j] if job_ready[j] > mach_ready[m] else mach_ready[m]
        job_ready[j] = mach_ready[m] = start + d
        nxt[j] += 1
    return max(job_ready)


def simulated_annealing(jobs, time_limit=30, seed=0, init_seq=None):
    rng = random.Random(seed)
    n_mach = 1 + max(m for job in jobs for m, _ in job)
    if init_seq is None:                 # random start
        seq = [j for j in range(len(jobs)) for _ in jobs[j]]
        rng.shuffle(seq)
    else:                                # warm start from a given sequence
        seq = list(init_seq)
    L = len(seq)

    cur = decode(seq, jobs, n_mach)
    best = cur
    avg = sum(d for job in jobs for _, d in job) / L
    T0, T1 = (avg if init_seq is None else 0.3 * avg), 0.05 * avg  # start and end temperature
    T, it, t0 = T0, 0, time.time()

    while True:
        if it % 200 == 0:               # cooling is driven by elapsed time
            frac = (time.time() - t0) / time_limit
            if frac >= 1:
                break
            T = T0 * (T1 / T0) ** frac
        it += 1
        i = rng.randrange(L - 1)
        j = min(L - 1, i + rng.randint(1, 20))   # swap two nearby positions
        if seq[i] == seq[j]:
            continue
        seq[i], seq[j] = seq[j], seq[i]
        new = decode(seq, jobs, n_mach)
        delta = new - cur
        if delta <= 0 or rng.random() < math.exp(-delta / T):
            cur = new
            best = min(best, cur)
        else:
            seq[i], seq[j] = seq[j], seq[i]      # undo the move
    return best, it


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "ft10"
    limit = float(sys.argv[2]) if len(sys.argv) > 2 else 30
    jobs = read_instance(rf"JSPLIB-master\instances\{name}")
    best, iters = simulated_annealing(jobs, limit)
    print(f"{name}: best makespan {best} after {iters} iterations")