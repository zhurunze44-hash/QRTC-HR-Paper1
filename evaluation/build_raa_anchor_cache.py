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

            # lnctardppi 这里是真实的无表头三列文本，字段之间是 tab
            parts = line.split("\t")

            # 有些文件可能混入多空格展示，但从你贴的输出看是 tab 对齐
            if len(parts) != 3:
                raise ValueError(
                    f"{path}:{lineno} 不是 3 列 tab 分隔格式；"
                    f"split('\\t') 后得到 {len(parts)} 列: {parts[:5]}"
                )

            h, r, t = [x.strip() for x in parts]
            if not h or not r or not t:
                raise ValueError(f"{path}:{lineno} 存在空字段: {parts}")

            rows.append((h, r, t))
    return rows


def maybe_read_entity_types(path):
    if path is None:
        return {}

    ent2type = {}
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            ent = parts[0].strip()
            typ = parts[1].strip()
            if ent:
                ent2type[ent] = typ
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
                if i == j:
                    continue
                rel_cooc[rels[i]][rels[j]] += 1

    for r, cnt in rel_cooc.items():
        rel_cooc_max[r] = max(cnt.values()) if cnt else 1
    return rel_cooc, rel_cooc_max


def dominant_tail_types(train_rows, ent2type, keep_topk=3):
    rel_to_tail_type = defaultdict(Counter)
    for _, r, t in train_rows:
        tt = ent2type.get(t)
        if tt is not None:
            rel_to_tail_type[r][tt] += 1

    rel_to_top_types = {}
    for r, cnt in rel_to_tail_type.items():
        rel_to_top_types[r] = {k for k, _ in cnt.most_common(keep_topk)}
    return rel_to_top_types


def score_candidate(
    query_rel,
    cand_rel,
    cand_type,
    direction,
    rel_cooc,
    rel_cooc_max,
    rel_to_top_types,
    same_rel_bonus=1.0,
    type_bonus=0.35,
    out_bonus=0.05,
):
    s_rel = 0.0
    if cand_rel == query_rel:
        s_rel += same_rel_bonus

    co = rel_cooc[query_rel][cand_rel] if query_rel in rel_cooc else 0
    mx = rel_cooc_max.get(query_rel, 1)
    if co > 0 and mx > 0:
        s_rel += math.log1p(co) / math.log1p(mx)

    s_type = 0.0
    top_types = rel_to_top_types.get(query_rel, None)
    if top_types and cand_type is not None and cand_type in top_types:
        s_type += type_bonus

    s_dir = out_bonus if direction == "out" else 0.0

    score = s_rel + s_type + s_dir
    meta = {
        "same_rel": int(cand_rel == query_rel),
        "type_compat": int(top_types is not None and cand_type is not None and cand_type in top_types),
        "out_dir": int(direction == "out"),
    }
    return score, meta


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
    ap.add_argument("--out_dir", required=True)

    ap.add_argument("--top_m", type=int, default=8)
    ap.add_argument("--min_score", type=float, default=0.0)

    # 可选：实体类型表，第一轮允许不给
    ap.add_argument("--entity_type_path", default=None)

    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    # 读取多 train 文件
    train_rows = []
    train_source_sizes = {}
    for path in args.train_paths:
        rows = parse_headerless_triples(path)
        train_rows.extend(rows)
        train_source_sizes[os.path.basename(path)] = len(rows)

    query_rows = []
    query_source_sizes = {}
    for path in args.query_paths:
        rows = parse_headerless_triples(path)
        query_rows.extend(rows)
        query_source_sizes[os.path.basename(path)] = len(rows)

    ent2type = maybe_read_entity_types(args.entity_type_path)

    out_adj = defaultdict(list)
    in_adj = defaultdict(list)

    train_heads = []
    train_rels = []
    train_tails = []

    for h, r, t in train_rows:
        ht = ent2type.get(h)
        tt = ent2type.get(t)
        out_adj[h].append((r, t, tt, "out"))
        in_adj[t].append((r, h, ht, "in"))
        train_heads.append(h)
        train_rels.append(r)
        train_tails.append(t)

    rel_cooc, rel_cooc_max = build_relation_cooc(out_adj, in_adj)
    rel_to_top_types = dominant_tail_types(train_rows, ent2type)

    query_pairs = set((h, r) for h, r, _ in train_rows)
    for h, r, _ in query_rows:
        query_pairs.add((h, r))

    cache_path = os.path.join(args.out_dir, "anchor_cache.jsonl")
    relation_total = Counter()
    relation_nonempty = Counter()

    nonempty_pair_n = 0
    anchor_count_list = []

    with open(cache_path, "w", encoding="utf-8") as wf:
        for h, r in sorted(query_pairs):
            relation_total[r] += 1

            cands = []
            for r1, nbr, nbr_type, direction in out_adj.get(h, []):
                cands.append((r1, nbr, nbr_type, direction))
            for r1, nbr, nbr_type, direction in in_adj.get(h, []):
                cands.append((r1, nbr, nbr_type, direction))

            best = {}
            same_rel_count = 0
            type_compat_count = 0

            for r1, nbr, nbr_type, direction in cands:
                score, meta = score_candidate(
                    query_rel=r,
                    cand_rel=r1,
                    cand_type=nbr_type,
                    direction=direction,
                    rel_cooc=rel_cooc,
                    rel_cooc_max=rel_cooc_max,
                    rel_to_top_types=rel_to_top_types,
                )
                if score < args.min_score:
                    continue

                if meta["same_rel"]:
                    same_rel_count += 1
                if meta["type_compat"]:
                    type_compat_count += 1

                cur = best.get(nbr)
                if cur is None or score > cur["score"]:
                    best[nbr] = {
                        "anchor_id": nbr,
                        "score": score,
                        "cand_rel": r1,
                        "cand_type": nbr_type,
                        "direction": direction,
                    }

            ranked = sorted(best.values(), key=lambda x: x["score"], reverse=True)[: args.top_m]
            anchor_ids = [x["anchor_id"] for x in ranked]
            anchor_scores = [round(float(x["score"]), 6) for x in ranked]

            if anchor_ids:
                nonempty_pair_n += 1
                relation_nonempty[r] += 1
            anchor_count_list.append(len(anchor_ids))

            rec = {
                "head_id": h,
                "relation_id": r,
                "anchor_ids": anchor_ids,
                "anchor_scores": anchor_scores,
                "anchor_count": len(anchor_ids),
                "same_rel_count": same_rel_count,
                "type_compat_count": type_compat_count,
            }
            wf.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 基于真实字符串空间做自检
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

    id_selfcheck = {
        "asset": "raa_anchor_cache_string_space_selfcheck_v0",
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

    stats = {
        "asset": "raa_anchor_cache_v0_lnctardppi",
        "train_paths": args.train_paths,
        "query_paths": args.query_paths,
        "train_source_sizes": train_source_sizes,
        "query_source_sizes": query_source_sizes,
        "pair_n": len(query_pairs),
        "nonempty_pair_n": nonempty_pair_n,
        "nonempty_coverage": round(nonempty_pair_n / max(1, len(query_pairs)), 6),
        "mean_anchor_count": round(sum(anchor_count_list) / max(1, len(anchor_count_list)), 6),
        "p50_anchor_count": qtile(anchor_count_list, 0.50),
        "p90_anchor_count": qtile(anchor_count_list, 0.90),
        "top_m": args.top_m,
        "use_entity_types": args.entity_type_path is not None,
        "relation_level_nonempty_coverage": {
            r: round(relation_nonempty[r] / max(1, relation_total[r]), 6)
            for r in sorted(relation_total.keys())
        },
        "top_empty_relations": sorted(
            [
                {
                    "relation_id": r,
                    "nonempty_coverage": round(relation_nonempty[r] / max(1, relation_total[r]), 6),
                    "pair_n": relation_total[r],
                }
                for r in relation_total.keys()
            ],
            key=lambda x: (x["nonempty_coverage"], -x["pair_n"], x["relation_id"])
        )[:20],
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
