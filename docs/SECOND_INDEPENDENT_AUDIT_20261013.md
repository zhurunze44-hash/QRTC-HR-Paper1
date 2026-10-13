# Paper1 QRTC-HR — Public / Reviewer Release Second Independent Audit

Date: 2026-10-13

## Inputs and scope

Inspected uploaded `VERIFY_PUBLIC_REVIEWER_REPORTS.zip` (12 files). Programmatically checked TSV row counts, SHA/path uniqueness, byte totals, mapped CODE / RELEASE counts, WEIGHTS_INDEX SHA/byte correspondence, and the text checksum file. The original 427,682,473-byte `.tar.zst` and the 846-file Code tree were **not** supplied; their actual bytes and security cannot be independently verified here. No GitHub repository or Release was accessed or changed.

## Verified ledger

| Item | Result |
|---|---|
| Included scientific files | 1,434 distinct paths / 1,434 distinct SHA256 |
| Dropped scientific files | 133 distinct paths / 133 distinct SHA256 |
| Disjoint included/dropped | Yes, by path and SHA256 |
| Included uncompressed bytes | 1,845,696,825 |
| Dropped bytes | 158,813,468 |
| Reconciled source total | 2,004,510,293 (equal to former 1,567-file inventory total) |
| `.pth` assets | 21 / 1,734,868,337 bytes, SHA+size matches 21 WEIGHTS_INDEX rows |
| Public archive size/hash | 427,682,473 bytes / 17b3e6ef0c101e4de011d3d564952a60fe0feb1626f66077ee131d36cf90b4d5 (reported, NOT archive-bytes verified) |
| `CHECKSUMS.sha256` | 116 bytes / SHA256 `140ad634e69b80224568920e585229ab481f27cbf1094842aa9a12e8e9f16458` verified |
| Proposed Git CODE entries | 846 files / 112,187,423 bytes, all mapped under `25_朱润泽/JIIS/` |
| GitHub remote publication | PENDING per supplied terminal JSON |

The one 0-byte CODE manifest item is `src/biopathnet/__init__.py`, a plausible intentionally empty Python package initializer, not proof of a broken GitHub upload.

## Critical remaining issues

1. **Rights unresolved in both Release and CODE.** The CODE tree manifest directly includes `results/final_server_evidence_index/13_DATA_SPLIT_PROVENANCE/PC_KEGG_0602/train1.txt` (60,999,631 bytes) and `.../lnctardppi/train1.txt` (31,248,591 bytes), as well as entity/split files. The 408 MiB Release also contains graph assets according to the included manifest. Merely saying `reviewer-restricted` in DATA_AVAILABILITY does not establish redistribution permission. Do not push those Code files or upload restricted data to a public Release until the original source license/permission is confirmed; assess whether private GitHub hosting/distribution is allowed too.
2. **Content scan not a security clearance.** `SECRET_CONTENT_SCAN.txt` reports `NO_PATTERN_HITS_IN_SCANNED_TEXT_FILES`, yet `sensitive_paths_still_in_public_pack=21`. Neither the exact 21-path review nor the actual content of 846 CODE files was in the uploaded reports. Inspect all 21 paths, full text/code history, manifests/inventories, config/log files, checkpoint metadata, and generated docs for secrets, local paths and protected information before a push, including to a private repo. Rotate previously exposed credentials as necessary.
3. **Mechanical exclusion of potentially useful dependencies.** The 133 dropped files include 15 provisionally classified PRIMARY_PUBLISHED_EVIDENCE and 11 REPRODUCIBILITY_DEPENDENCY files. E.g. six scripts under `_tools/p1_v5_src/` were dropped. They may be duplicate/irrelevant, but a dependency-by-claim crosswalk is needed before saying the open reviewer package is complete. Keep original master unchanged.
4. **Code tree is broader than a curated reproducible source tree.** CODE includes 846 entries, of which 319 are `results/`, and around 154 file paths contain `.bak`. Keep core code/config/evaluation/documentation discoverable. Avoid mixing large possibly restricted graph files into Git history: deleting them in a later commit does not remove them from Git history.
5. **Repository-mapping not final.** `02_SOURCE_TO_GITHUB_MANIFEST.tsv` currently maps all 846 CODE items to `25_朱润泽/JIIS/` in the lab vault. If publishing to a dedicated repository, regenerate mapping, README links, and affected file SHA256s (do not merely relabel as already uploaded).
6. **Only reported archive hash, no bytes.** The 408 MiB `.tar.zst` and CODE files were absent from the uploaded 158 KiB report pack; original archiving correctness, script functioning, absence of leaks, and external GitHub downloads remain NOT TESTED. Expected remote hash `17b3...4d5` must be validated by actually downloading the asset.
7. **Old broken repo status.** A new dedicated repository avoids new empty placeholders, but does not repair old repository history. Mark old links as superseded/redirect to the new verified entry point after publication, if the old repo can be edited.
8. **Research limitations retained.** Missing 5-seed formal panel, missing `PC_WOBRG_MAY02_QRTC` checkpoint, some weights are negative/historical, live end-to-end replay not run. Do not state `fully reproducible`.

## Repository decision

**Choose a dedicated Paper1 repository, Private while preparing. Do not publish under the mixed laboratory vault path.** Keep authors/PI aligned on repository ownership and permissions. For a journal reviewer link, use a public **sanitized** code/data release when legally permitted, because private repositories require access authorization, and private personal-account collaborators receive write access. A private GitHub vault is not an automatically accessible, anonymous reviewer download link.

## Authentication

**Never send a GitHub token in chat or to the Cursor prompt.** Authenticate locally via GitHub CLI on the Windows machine holding `F:\jiis`:

```powershell
gh auth login --hostname github.com --git-protocol https --web
gh auth status
```

Use GitHub's browser/device authorization flow; do not log or print credentials. If a PAT is unavoidable, create a short-lived fine-grained token confined to the one repository with only required Contents permissions and enter it into a protected local credential prompt, not a chat or script. Avoid authenticating on a multi-user research host unnecessarily.

## Ordered publish gates for Cursor

1. Preserve the 1,567-file internal master and 1,434-file current draft unchanged as an audit source.
2. Identify the 21 sensitive paths and manually inspect each; scan **both** actual CODE and actual Release payload, including manifests, text logs, configuration, and binary metadata, and document findings.
3. Establish licenses/redistribution authority for PC_KEGG/LncTarD derived graphs. If uncertain, remove graph data from **both** CODE and any public Release and substitute legal official acquisition/regeneration instructions. Do not rewrite old Git history with tainted files.
4. Crosswalk all excluded primary/repro artifacts against still-included evidence and actual evaluation imports/entrypoints. Restore only essential and safe/authorized files from the unchanged master as needed.
5. Rebuild a **sanitized** public CODE tree; remove nonessential large graph/train files and backups, or clearly segregate permitted historical artifacts; regenerate SOURCE_TO_GITHUB_MANIFEST with new dedicated-repo layout and exact local hashes.
6. Test `download_assets`, `verify_assets`, path restoration and frozen evaluation entrypoint on the actual staged files. Distinguish delivery integrity from scientific replay capability.
7. Independently verify local new archive's SHA256, restored file count, bytes, and per-file checksums; record the new hash (old hash cannot be carried over when contents change).
8. Create dedicated **private** repository and push verified safe Code using normal commits; do not force-push. No unpublished forbidden data even in its history.
9. Stage a Draft Release with **only cleared** assets, download every asset again from GitHub and compare actual SHA256. Public publication requires licensing and access tests to pass.
10. For actual JIIS submission references, only state what independent download and scientific reproduction checks truly proved. Do not claim complete reproduction.

**Terminal verdict:** `PASS__LOCAL_MANIFEST_ACCOUNTING` and `HOLD__GITHUB_PUBLICATION__DATA_RIGHTS_AND_SECURITY_UNRESOLVED`. This is not a failure of the scientific Paper1 result; it is a release engineering gate.
