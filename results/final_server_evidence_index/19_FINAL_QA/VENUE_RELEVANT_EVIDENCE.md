# VENUE_RELEVANT_EVIDENCE

Fact inventory for independent DKE/JIIS judgment. No venue recommendation.

## Architecture novelty evidence
SOURCE_RESTORE layer/model/qrtc_common; METHOD_IDENTITY_AUDIT; IMPLEMENTATION_IDENTITY.json. Gate-before-aggregate + Top-K relation memory. Optional unused heads exist in the same files.

## Mechanism evidence
Query-level PC wBRG rank pairs; LAST_CHANCE G1/G2 frozen-weight interventions (G2 NOT_SELECTED, scale-matched g*A negative). Relation-usage dumps for manuscript introspection: historically NOT_AVAILABLE.

## 5-seed robustness evidence
**Absent as formal complete panel.** A1 forensic 2 seeds only, provenance rejected.

## Cross-dataset evidence
PC KEGG + LncTarD only. Regimes ≠ new datasets.

## Negative/mixed evidence
LncTarD wBRG MRR/Hits@1; PC wBRG test MR and AP/AUROC; query-level minority win; A1 RAW1024 collapse (ineligible); LAST_CHANCE no investment signal.

## Reproducibility evidence
Checkpoint SHAs; split hashes; historical eval log; SOURCE freeze; live replay gap on current host.

## Complexity evidence
State_dict counting: identical total params Base vs QRTC; ~3.5% QRTC-named tensors vs backbone; microbench ~1.47× forward.

## Biological interpretability evidence
Thin: rank-pair / relation-stratified leftovers in CMPB; no clinical validation.

## SOTA comparison evidence
RotatE baselines on wBRG exist (below path models). DistMult/RGCN historical configs exist; CMPB omitted unresolved Top-K/multiseed. Not a broad SOTA sweep.
