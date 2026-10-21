"""Select 12 Spring XD issues: two per story point level, fixed seed."""
import csv
import random
import sys

csv.field_size_limit(10**9)
SEED = 149
LEVELS = [1, 2, 3, 5, 8, 13]
PER_LEVEL = 2

src, dst = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(src, encoding="utf-8", errors="replace")))
rng = random.Random(SEED)
picked = []
for sp in LEVELS:
    pool = [r for r in rows
            if r["storypoint"] == str(sp)
            and r["description"] not in ("", "NULL")
            and 80 <= len(r["description"]) <= 700]
    pool.sort(key=lambda r: r["issuekey"])
    picked += rng.sample(pool, PER_LEVEL)

rng.shuffle(picked)
with open(dst, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["n", "issuekey", "title", "description", "storypoint"])
    for i, r in enumerate(picked, 1):
        desc = " ".join(r["description"].split())
        w.writerow([i, r["issuekey"], r["title"].strip(), desc, r["storypoint"]])
print("written", len(picked))
