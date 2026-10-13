import json
import sys
from collections import defaultdict
from statistics import mean

path = sys.argv[1]

by_head = defaultdict(list)
pair_n = 0
score_std_list = []
all_anchor_count = []
all_unique_score_count = []

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        rec = json.loads(line)
        h = rec["head_id"]
        r = rec["relation_id"]
        anchors = tuple(rec["anchor_ids"])
        scores = [float(x) for x in rec["anchor_scores"]]

        pair_n += 1
        all_anchor_count.append(len(anchors))
        all_unique_score_count.append(len(set(scores)))

        if len(scores) <= 1:
            score_std = 0.0
        else:
            mu = sum(scores) / len(scores)
            score_std = (sum((x - mu) ** 2 for x in scores) / len(scores)) ** 0.5
        score_std_list.append(score_std)

        by_head[h].append({
            "relation": r,
            "anchors": set(anchors),
            "anchor_tuple": anchors,
            "scores": scores,
        })

multi_rel_head_n = 0
exact_same_anchor_tuple_pair_n = 0
pair_compare_n = 0
jaccards = []
high_overlap_n = 0

for h, rows in by_head.items():
    rels = {x["relation"] for x in rows}
    if len(rels) < 2:
        continue
    multi_rel_head_n += 1
    n = len(rows)
    for i in range(n):
        for j in range(i + 1, n):
            a = rows[i]["anchors"]
            b = rows[j]["anchors"]
            inter = len(a & b)
            union = len(a | b)
            jac = inter / union if union else 0.0
            jaccards.append(jac)
            pair_compare_n += 1
            if rows[i]["anchor_tuple"] == rows[j]["anchor_tuple"]:
                exact_same_anchor_tuple_pair_n += 1
            if jac >= 0.8:
                high_overlap_n += 1

print("pair_n =", pair_n)
print("multi_rel_head_n =", multi_rel_head_n)
print("pair_compare_n =", pair_compare_n)
print("mean_anchor_count =", round(mean(all_anchor_count), 6))
print("mean_unique_score_count =", round(mean(all_unique_score_count), 6))
print("mean_score_std =", round(mean(score_std_list), 6))
if jaccards:
    print("mean_cross_relation_jaccard =", round(mean(jaccards), 6))
    print("high_overlap_rate_jaccard_ge_0.8 =", round(high_overlap_n / len(jaccards), 6))
    print("exact_same_anchor_tuple_rate =", round(exact_same_anchor_tuple_pair_n / len(jaccards), 6))
else:
    print("mean_cross_relation_jaccard = NA")
    print("high_overlap_rate_jaccard_ge_0.8 = NA")
    print("exact_same_anchor_tuple_rate = NA")

problem = []
for h, rows in by_head.items():
    rels = {x["relation"] for x in rows}
    if len(rels) < 2:
        continue
    tuples = [x["anchor_tuple"] for x in rows]
    same_ratio = 1.0 - len(set(tuples)) / len(tuples)
    problem.append((same_ratio, len(rows), h))

problem.sort(reverse=True)
print("\n===== top suspicious heads =====")
for same_ratio, nrows, h in problem[:20]:
    print({"head_id": h, "relation_count": nrows, "same_tuple_ratio_proxy": round(same_ratio, 6)})
