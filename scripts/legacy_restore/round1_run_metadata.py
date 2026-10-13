from __future__ import annotations
import argparse
import csv
import re
from pathlib import Path

PATTERNS = {
    "config_path": re.compile(r"config[^ \n]*\.ya?ml"),
    "ckpt_path": re.compile(r"model_epoch_[0-9]+\.pth"),
    "router_force_meta": re.compile(r"ROUTER_FORCE_META[=:\s]+([A-Za-z0-9_/-]+)"),
    "probe_topk": re.compile(r"PROBE_TOPK[=:\s]+([0-9]+)"),
    "probe_valid_offset": re.compile(r"PROBE_VALID_OFFSET[=:\s]+([0-9]+)"),
    "probe_query_limit": re.compile(r"PROBE_QUERY_LIMIT[=:\s]+([0-9]+)"),
    "rg_min_enable": re.compile(r"RG_MIN_ENABLE[=:\s]+([0-9]+)"),
    "srp_enable": re.compile(r"SRP_ENABLE[=:\s]+([0-9]+)"),
    "raa_enable": re.compile(r"RAA_ENABLE[=:\s]+([0-9]+)"),
    "skip_valid": re.compile(r"skip_valid[:=\s]+(True|False|true|false)"),
    "eval_only": re.compile(r"eval_only", re.IGNORECASE),
    "meta_hop": re.compile(r"\bhop\b", re.IGNORECASE),
    "meta_type": re.compile(r"\btype\b", re.IGNORECASE),
}

def extract_text(log_path: Path, max_bytes: int = 120_000) -> str:
    if not log_path.is_file():
        return ""
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    return text[:max_bytes]

def extract_fields(text: str):
    out = {}
    for key, pat in PATTERNS.items():
        m = pat.search(text)
        if not m:
            out[key] = ""
        else:
            out[key] = m.group(1) if m.groups() else "1"
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-runs", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    probe_runs = Path(args.probe_runs).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    with probe_runs.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            if row["pair_status"] != "paired":
                continue
            run_dir = Path(row["run_dir"])
            log_path = run_dir / "log.txt"
            text = extract_text(log_path)
            meta = extract_fields(text)
            rows.append({
                "run_dir": str(run_dir),
                "log_path": str(log_path),
                **meta
            })

    out_tsv = outdir / "RUN_METADATA.tsv"
    fields = [
        "run_dir", "log_path",
        "config_path", "ckpt_path",
        "router_force_meta",
        "probe_topk", "probe_valid_offset", "probe_query_limit",
        "rg_min_enable", "srp_enable", "raa_enable",
        "skip_valid", "eval_only", "meta_hop", "meta_type",
    ]
    with out_tsv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for row in rows:
            w.writerow(row)

    out_txt = outdir / "RUN_METADATA.txt"
    lines = [f"RUN_COUNT\t{len(rows)}", "", "[TOP_60]"]
    for row in rows[:60]:
        lines.append(
            "\t".join(str(row[k]) for k in fields)
        )
    out_txt.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] wrote: {out_tsv}")
    print(f"[OK] wrote: {out_txt}")

if __name__ == "__main__":
    main()
