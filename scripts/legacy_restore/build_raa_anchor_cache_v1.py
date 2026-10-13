import argparse
import json
import math
import os
from collections import defaultdict, Counter


def parse_headerless_triples(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) != 3:
                raise ValueError(f"{path}:{lineno} split('\\t') 后不是 3 列: {parts[:5]}")
            h, r, t = [x.strip() for x in parts]
            rows.append((h, r, t))
    return rows


def read_entity_types(path):
    ent2type = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                ent2type[parts[0].strip()] = parts[1].strip()
    return ent2type


def build_relation_cooc(out_adj, in_adj):
    rel_cooc = defaultdict(Counter)
    rel_cooc_max = Counter()
    all_heads = set(out_adj.keys()) | set(in_adj.keys())
    for h in all_heads:
        rels = set()
        for r1, _, _, _ in out_adj.get(h, []):
            rels.add(r1)
        for r1, _, _, _ in in_adj.get(h, []):
            rels.add(r1)
        rels = list(rels)
        for i in range(len(rels)):
            for j in range(len(rels)):
                if i != j:
                    rel_cooc[rels[i]][rels[j]] += 1
    for r, cnt in rel_cooc.items():
        rel_cooc_max[r] = max(cnt.values()) if cnt else 1
    return rel_cooc, rel_cooc_max


def dominant_tail_types(train_rows, ent2type, keep_topk=2):
    rel_to_tail_type = defaultdict(Counter)
    for _, r, t in train_rows:
        tt = ent2type.get(t)
        if tt is not None:
            rel_to_tail_type[r][tt] += 1
    rel_to_top_types = {}
    for r, cnt in rel_to_tail_type.items():
        rel_to_top_types[r] = {k for k, _ in cnt.most_common(keep_topk)}
    return rel_to_top_types


def qtile(xs, q):
    if not xs:
        return 0
    ys = sorted(xs)
    idx = int(round((len(ys) - 1) * q))
    idx = max(0, min(idx, len(ys) - 1))
    return ys[idx]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train_paths", nargs="+", required=True)
    ap.add_argument("--query_paths", nargs="+", required=True)
    ap.add_argument("--entity_type_path", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--top_m", type=int, default=8)
    ap.add_argument("--min_score", type=float, default=0.0)
    ap.add_argument("--keep_topk_types", type=int, default=2)
    ap.add_argument("--hub_lambda", type=float, default=0.15)
    ap.add_argument("--dir_bonus", type=float, default=0.05)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    train_rows = []
    for path in args.train_paths:
        train_rows.extend(parse_headerless_triples(path))

    query_rows = []
    for path in args.query_paths:
        query_rows.extend(parse_headerless_triples(path))

    ent2type = read_entity_types(args.entity_type_path)

    out_adj = defaultdict(list)
    in_adj = defaultdict(list)
    node_degree = Counter()

    train_heads, train_rels, train_tails = [], [], []
    for h, r, t in train_rows:
        ht = ent2type.get(h)
        tt = ent2type.get(t)
        out_adj[h].append((r, t, tt, "out"))
        in_adj[t].append((r, h, ht, "in"))
        node_degree[h] += 1
        node_degree[t] += 1
        train_heads.append(h)
        train_rels.append(r)
        train_tails.append(t)

    rel_cooc, rel_cooc_max = build_relation_cooc(out_adj, in_adj)
    rel_to_top_types = dominant_tail_types(train_rows, ent2type, keep_topk=args.keep_topk_types)

    query_pairs = set((h, r) for h, r, _ in train_rows)
    for h, r, _ in query_rows:
        query_pairs.add((h, r))

    relation_total = Counter()
    relation_nonempty = Counter()
    nonempty_pair_n = 0
    anchor_count_list = []
    exact_rel_first_used_n = 0
    backoff_used_n = 0
    filtered_by_type_n = 0

    cache_path = os.path.join(args.out_dir, "anchor_cache.jsonl")
    with open(cache_path, "w", encoding="utf-8") as wf:
        for h, query_rel in sorted(query_pairs):
            relation_total[query_rel] += 1

            cands = []
            for r1, nbr, nbr_type, direction in out_adj.get(h, []):
                cands.append((r1, nbr, nbr_type, direction))
            for r1, nbr, nbr_type, direction in in_adj.get(h, []):
                cands.append((r1, nbr, nbr_type, direction))

            allowed_types = rel_to_top_types.get(query_rel, None)
            tier1, tier2 = [], []

            for cand_rel, nbr, nbr_type, direction in cands:
                if allowed_types is not None:
                    if nbr_type is None or nbr_type not in allowed_types:
                        filtered_by_type_n += 1
                        continue

                if cand_rel == query_rel:
                    tier1.append((cand_rel, nbr, nbr_type, direction))
                else:
                    co = rel_cooc[query_rel][cand_rel] if query_rel in rel_cooc else 0
                    if co > 0:
                        tier2.append((cand_rel, nbr, nbr_type, direction))

            def score_bucket(bucket, is_tier1):
                best = {}
                for cand_rel, nbr, nbr_type, direction in bucket:
                    if is_tier1:
                        rel_score = 2.0
                    else:
                        mx = rel_cooc_max.get(query_rel, 1)
                        co = rel_cooc[query_rel][cand_rel] if query_rel in rel_cooc else 0
                        rel_score = math.log1p(co) / math.log1p(mx) if co > 0 and mx > 0 else 0.0
                    dir_bonus = args.dir_bonus if direction == "out" else 0.0
                    hub_penalty = args.hub_lambda * math.log1p(node_degree[nbr])
                    score = rel_score + dir_bonus - hub_penalty
                    if score < args.min_score:
                        continue
                    cur = best.get(nbr)
                    if cur is None or score > cur["score"]:
                        best[nbr] = {
                            "anchor_id": nbr,
                            "score": score,
                            "tier": 1 if is_tier1 else 2,
                        }
                return sorted(best.values(), key=lambda x: x["score"], reverse=True)

            ranked1 = score_bucket(tier1, True)
            ranked2 = score_bucket(tier2, False)

            final_ranked, seen = [], set()
            for x in ranked1:
                if x["anchor_id"] not in seen:
                    final_ranked.append(x)
                    seen.add(x["anchor_id"])
                if len(final_ranked) >= args.top_m:
                    break
            if ranked1:
                exact_rel_first_used_n += 1

            if len(final_ranked) < args.top_m:
                for x in ranked2:
                    if x["anchor_id"] not in seen:
                        final_ranked.append(x)
                        seen.add(x["anchor_id"])
                    if len(final_ranked) >= args.top_m:
                        break
                if ranked2:
                    backoff_used_n += 1

            anchor_ids = [x["anchor_id"] for x in final_ranked[:args.top_m]]
            anchor_scores = [round(float(x["score"]), 6) for x in final_ranked[:args.top_m]]

            if anchor_ids:
                nonempty_pair_n += 1
                relation_nonempty[query_rel] += 1
            anchor_count_list.append(len(anchor_ids))

            rec = {
                "head_id": h,
                "relation_id": query_rel,
                "anchor_ids": anchor_ids,
                "anchor_scores": anchor_scores,
                "anchor_count": len(anchor_ids),
                "allowed_types": sorted(list(allowed_types)) if allowed_types is not None else None,
                "tier1_candidate_n": len(tier1),
                "tier2_candidate_n": len(tier2),
            }
            wf.write(json.dumps(rec, ensure_ascii=False) + "\n")

    train_entity_space = set(train_heads) | set(train_tails)
    train_relation_space = set(train_rels)
    anchor_ids_all = []
    with open(cache_path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            anchor_ids_all.extend([str(x) for x in rec["anchor_ids"]])

    anchor_not_in_train_entity = [x for x in anchor_ids_all if x not in train_entity_space]
    query_pairs_from_queries = set((h, r) for h, r, _ in query_rows)
    cache_keys = set()
    with open(cache_path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            cache_keys.add((str(rec["head_id"]), str(rec["relation_id"])))
    hit_n = sum(1 for x in query_pairs_from_queries if x in cache_keys)

    stats = {
        "asset": "raa_anchor_cache_v1_exactrel_first",
        "pair_n": len(query_pairs),
        "nonempty_pair_n": nonempty_pair_n,
        "nonempty_coverage": round(nonempty_pair_n / max(1, len(query_pairs)), 6),
        "mean_anchor_count": round(sum(anchor_count_list) / max(1, len(anchor_count_list)), 6),
        "p50_anchor_count": qtile(anchor_count_list, 0.50),
        "p90_anchor_count": qtile(anchor_count_list, 0.90),
        "top_m": args.top_m,
        "keep_topk_types": args.keep_topk_types,
        "hub_lambda": args.hub_lambda,
        "dir_bonus": args.dir_bonus,
        "exact_rel_first_used_n": exact_rel_first_used_n,
        "backoff_used_n": backoff_used_n,
        "filtered_by_type_n": filtered_by_type_n,
        "relation_level_nonempty_coverage": {
            r: round(relation_nonempty[r] / max(1, relation_total[r]), 6)
            for r in sorted(relation_total.keys())
        },
    }
    id_selfcheck = {
        "asset": "raa_anchor_cache_string_space_selfcheck_v1",
        "id_space_type": "raw_string_entities_relations",
        "train_entity_n": len(train_entity_space),
        "train_relation_n": len(train_relation_space),
        "anchor_id_n": len(anchor_ids_all),
        "anchor_not_in_train_entity_count": len(anchor_not_in_train_entity),
        "anchor_not_in_train_entity_examples": anchor_not_in_train_entity[:20],
        "query_pair_cache_hit": {
            "query_pair_n": len(query_pairs_from_queries),
            "cache_hit_n": hit_n,
            "cache_hit_rate": round(hit_n / max(1, len(query_pairs_from_queries)), 6),
        },
    }

    with open(os.path.join(args.out_dir, "anchor_stats.json"), "w", encoding="utf-8") as wf:
        json.dump(stats, wf, ensure_ascii=False, indent=2)
    with open(os.path.join(args.out_dir, "id_selfcheck.json"), "w", encoding="utf-8") as wf:
        json.dump(id_selfcheck, wf, ensure_ascii=False, indent=2)

    print(f"[DONE] {cache_path}")
    print(f"[DONE] {os.path.join(args.out_dir, 'anchor_stats.json')}")
    print(f"[DONE] {os.path.join(args.out_dir, 'id_selfcheck.json')}")


if __name__ == "__main__":
    main()
