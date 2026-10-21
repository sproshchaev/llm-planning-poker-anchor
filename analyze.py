"""Compare LLM story point estimates with the team's ones and with each other."""
import csv
import statistics
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
RUN_DIR = ROOT / "runs"
MODELS = sorted({f.name.split("_")[0] for f in RUN_DIR.glob("*_[AB][123].txt")}, reverse=True)
PROMPTS = ["A", "B"]
RUNS = [1, 2, 3]
ANCHOR = 32
SCALE = {1, 2, 3, 5, 8, 13, 21}

if len(MODELS) != 2:
    sys.exit(f"expected runs of exactly two models in {RUN_DIR}, found: {MODELS}")


def load_run(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    est = {}
    for line in lines:
        n, sp = line.split(":")
        est[int(n)] = int(sp)
    if len(lines) != 12 or sorted(est) != list(range(1, 13)) or not set(est.values()) <= SCALE:
        sys.exit(f"{path}: expected 12 lines 'number: estimate' on the scale {sorted(SCALE)}")
    return [est[i] for i in range(1, 13)]


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ma, mb = statistics.mean(ra), statistics.mean(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    var = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return cov / var


issues = list(csv.DictReader(open(ROOT / "data" / "issues.csv", encoding="utf-8")))
team = [int(r["storypoint"]) for r in issues]
runs = {(m, p, k): load_run(RUN_DIR / f"{m}_{p}{k}.txt")
        for m in MODELS for p in PROMPTS for k in RUNS}

print(f"Team sum: {sum(team)} SP, anchor in prompt B: {ANCHOR} SP")
print()
print("1. Sums per run")
for m in MODELS:
    for p in PROMPTS:
        sums = [sum(runs[(m, p, k)]) for k in RUNS]
        print(f"   {m:6} {p}: {sums}  mean {statistics.mean(sums):.1f}")

print()
print("2. Anchor shift (mean sum B vs A)")
for m in MODELS:
    a = statistics.mean(sum(runs[(m, "A", k)]) for k in RUNS)
    b = statistics.mean(sum(runs[(m, "B", k)]) for k in RUNS)
    print(f"   {m:6}: {a:.1f} -> {b:.1f} SP ({(b - a) / a * 100:+.0f}%)")

print()
print("3. Run-to-run stability (same model, same prompt)")
for m in MODELS:
    for p in PROMPTS:
        changed = [i + 1 for i in range(12)
                   if len({runs[(m, p, k)][i] for k in RUNS}) > 1]
        print(f"   {m:6} {p}: tasks with different estimates {len(changed)} of 12 {changed}")

print()
print("4. Agreement with the team (median of 3 runs)")
for m in MODELS:
    for p in PROMPTS:
        med = [statistics.median(runs[(m, p, k)][i] for k in RUNS) for i in range(12)]
        mae = statistics.mean(abs(x - y) for x, y in zip(med, team))
        exact = sum(1 for x, y in zip(med, team) if x == y)
        print(f"   {m:6} {p}: MAE {mae:.2f} SP, exact {exact} of 12, "
              f"Spearman {spearman(med, team):.2f}")
m1, m2 = MODELS
med1 = [statistics.median(runs[(m1, "A", k)][i] for k in RUNS) for i in range(12)]
med2 = [statistics.median(runs[(m2, "A", k)][i] for k in RUNS) for i in range(12)]
print(f"   {m1} vs {m2} (A): Spearman {spearman(med1, med2):.2f}")

print()
print("5. Per task: team | " + " | ".join(f"{m} {p} runs" for m in MODELS for p in PROMPTS))
for i, r in enumerate(issues):
    cells = [str(team[i])] + [",".join(str(runs[(m, p, k)][i]) for k in RUNS)
                              for m in MODELS for p in PROMPTS]
    print(f"   {i + 1:2} {r['issuekey']:8} " + " | ".join(cells) + f"  {r['title'][:45]}")
