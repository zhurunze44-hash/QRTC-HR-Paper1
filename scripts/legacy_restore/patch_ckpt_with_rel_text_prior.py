import argparse
import hashlib
import json
import random
from pathlib import Path
import torch


def load_ckpt(path):
    obj = torch.load(path, map_location="cpu")
    if isinstance(obj, dict) and "model" in obj and isinstance(obj["model"], dict):
        return obj, obj["model"], "model"
    if isinstance(obj, dict) and "state_dict" in obj and isinstance(obj["state_dict"], dict):
        return obj, obj["state_dict"], "state_dict"
    if isinstance(obj, dict) and all(torch.is_tensor(v) for v in obj.values()):
        return obj, obj, None
    raise RuntimeError("unsupported checkpoint format")


def save_ckpt(obj, key, sd, out_path):
    if key is None:
        torch.save(sd, out_path)
    else:
        obj[key] = sd
        torch.save(obj, out_path)


def read_rel_names(data_dir):
    files = [
        "relation2id.txt",
        "relation2id.tsv",
        "relations.dict",
        "relations.txt",
        "relation_vocab.txt",
    ]
    for name in files:
        p = Path(data_dir) / name
        if not p.exists():
            continue
        lines = [x.strip() for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
        names = []
        for i, line in enumerate(lines):
            if i == 0 and line.isdigit():
                continue
            parts = line.replace("\t", " ").split()
            if len(parts) == 1:
                if not parts[0].isdigit():
                    names.append(parts[0])
            elif len(parts) >= 2:
                a, b = parts[0], parts[1]
                if a.isdigit() and not b.isdigit():
                    names.append(b)
                elif b.isdigit() and not a.isdigit():
                    names.append(a)
                elif not a.isdigit():
                    names.append(a)
        if names:
            return names, str(p)
    return None, None


def choose_rel_weight(sd, nrel_hint):
    best_key = None
    best_score = None
    best_shape = None
    for k, v in sd.items():
        if not torch.is_tensor(v):
            continue
        if v.ndim != 2:
            continue
        r, c = v.shape
        if r < 2 or r > 512:
            continue
        score = 0
        kl = k.lower()
        if "relation" in kl:
            score += 100
        if "embed" in kl or "embedding" in kl:
            score += 30
        if "weight" in kl:
            score += 5
        if nrel_hint is not None:
            score -= abs(r - nrel_hint)
        if best_score is None or score > best_score:
            best_score = score
            best_key = k
            best_shape = (r, c)
    if best_key is None:
        raise RuntimeError("cannot find relation embedding weight")
    return best_key, best_shape


def text_vec(text, dim):
    vals = []
    idx = 0
    while len(vals) < dim:
        h = hashlib.sha256(f"{text}|{idx}".encode("utf-8")).digest()
        for b in h:
            vals.append((b / 255.0) * 2.0 - 1.0)
            if len(vals) >= dim:
                break
        idx += 1
    x = torch.tensor(vals[:dim], dtype=torch.float32)
    x = x - x.mean()
    x = x / (x.norm() + 1e-12)
    return x


ap = argparse.ArgumentParser()
ap.add_argument("--ckpt", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--data_dir", required=True)
ap.add_argument("--mode", choices=["aligned", "shuffled"], required=True)
ap.add_argument("--lam", type=float, default=0.05)
args = ap.parse_args()

obj, sd, sd_key = load_ckpt(args.ckpt)

rel_names, rel_src = read_rel_names(args.data_dir)
nrel_hint = len(rel_names) if rel_names is not None else None

rel_key, shape = choose_rel_weight(sd, nrel_hint)
rows, dim = shape

if rel_names is None:
    rel_names = [f"rel_{i}" for i in range(rows)]
    rel_src = "fallback"
elif len(rel_names) < rows:
    rel_names = rel_names + [f"rel_{i}" for i in range(len(rel_names), rows)]
else:
    rel_names = rel_names[:rows]

texts = list(rel_names)
if args.mode == "shuffled":
    rnd = random.Random(20260330)
    rnd.shuffle(texts)

prior = torch.stack([text_vec(t, dim) for t in texts], dim=0).to(sd[rel_key].dtype)
sd[rel_key] = sd[rel_key].clone() + args.lam * prior

save_ckpt(obj, sd_key, sd, args.out)

meta = {
    "ckpt_in": args.ckpt,
    "ckpt_out": args.out,
    "mode": args.mode,
    "lam": args.lam,
    "relation_source": rel_src,
    "relation_weight_key": rel_key,
    "relation_weight_shape": [rows, dim],
    "relations": rel_names,
    "texts": texts,
}
Path(args.out + ".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

print("DONE")
print("relation_source =", rel_src)
print("relation_weight_key =", rel_key)
print("relation_weight_shape =", (rows, dim))
print("out =", args.out)
