import argparse
import re
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--base_cfg", required=True)
ap.add_argument("--ckpt", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

text = Path(args.base_cfg).read_text(encoding="utf-8")

patterns = [
    r'^(\s*checkpoint\s*:\s*).*$',
    r'^(\s*ckpt\s*:\s*).*$',
    r'^(\s*ckpt_path\s*:\s*).*$',
    r'^(\s*model_checkpoint\s*:\s*).*$',
    r'^(\s*init_checkpoint\s*:\s*).*$',
    r'^(\s*load_model_path\s*:\s*).*$',
]

count = 0
for pat in patterns:
    text, n = re.subn(pat, r'\1"' + args.ckpt + r'"', text, flags=re.M)
    count += n

if count == 0:
    raise SystemExit("No checkpoint-like key found")

Path(args.out).write_text(text, encoding="utf-8")
print("DONE", args.out, "replaced_keys =", count)
