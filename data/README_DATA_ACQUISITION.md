# Data acquisition (rights HOLD)

PC_KEGG and LncTarD-derived graph splits are **not** shipped in this sanitized GitHub package
because redistribution rights were not independently cleared (2026-10-13 audits).

## What was omitted

- `PC_KEGG_0602/` entity/split files (including large `train1.txt`)
- `lnctardppi/` entity/split files (including large `train1.txt`)
- Related trees under `*/13_DATA_SPLIT_PROVENANCE/*`

## Reviewer options

1. Obtain upstream datasets under their original licenses, then regenerate the experimental graphs using the frozen configs/scripts in this repo; or
2. Request controlled access via the journal / PI if a private data drop is authorized; or
3. Use the offline internal master archive on the authors' side for PI-supervised verification only (not for public redistribution).

Do not commit restricted graphs into this repository history.
