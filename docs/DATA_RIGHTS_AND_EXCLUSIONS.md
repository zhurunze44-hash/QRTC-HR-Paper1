# Data Rights and Exclusions (Paper1 / QRTC-HR)

## Credential exclusions (MUST NOT PUBLISH)
The following local helper scripts contain hardcoded SSH host/password material used for server restore and were excluded from the publication freeze package:
- `_local_archives/paper1_backup_20260510/restore_paper1_to_nxu.py`
- `_local_archives/paper1_backup_20260510/restore_paper1_to_nxu_resume.py`
- `_local_archives/paper1_backup_20260510/sync_all_paper1_assets.py`
- `_tools/upload_helpers/*`

**Action required offline:** rotate the exposed server password if it is still in use.

## Dataset redistribution
PC_KEGG and LncTarD-derived graphs under `data/` are research derivatives used by the frozen experiments.
Public redistribution status was not independently cleared with upstream dataset licenses in this session.
Until cleared, treat Release assets containing `data/` as **restricted to reviewers with authorized access** if the GitHub repository remains private; do not describe them as unrestricted public redistributable dumps.

## Other exclusions
- Nested zip/tar duplicates of `PAPER1_FINAL_SERVER_EVIDENCE_20261005`
- Large Chrome profiler traces under runtime forensic profiler
- Publication workspace itself
