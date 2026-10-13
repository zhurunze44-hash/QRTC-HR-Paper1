# A1 Competing Source Search
UTC: 2026-10-02T09:40:20Z

## Searched
- `<REDACTED_SERVER_PATH>
- conda env site-packages for biopathnet / egg-link / editable
- bashrc/profile/pam for PYTHONPATH (none found earlier)
- WORK and A0 worktree (forbidden as A1 roots)

## Found biopathnet packages
- **PAPER1_ROOT_COPY_SAME_SHA_AS_AUTHORITY**: `<REDACTED_SERVER_PATH> model_sha16=2cb1e5765a271ae5
- **WORK_FORBIDDEN**: `<REDACTED_SERVER_PATH> model_sha16=a9ab3e73ba27eeab
- **AUTHORITY**: `<REDACTED_SERVER_PATH> model_sha16=2cb1e5765a271ae5
- **REPLAY_ROOT_COPY_SAME_SHA**: `<REDACTED_SERVER_PATH> model_sha16=2cb1e5765a271ae5

## site-packages biopathnet
Count: 0 → **ABSENT** (no installable biopathnet package in formal env)

## egg-link / editable
Count: 0 → **NONE** relevant to biopathnet

## Shadowing risk assessment
| Candidate | Could beat SOURCE_RESTORE append? | Evidence |
|-----------|-----------------------------------|----------|
| site-packages/biopathnet | No (absent) | filesystem |
| WORK tree | Only if on PYTHONPATH/sys.path earlier | 0 WORK paths in any completed-cell `File "..."` traceback |
| paper1/biopathnet (root copy) | Only if cwd/PYTHONPATH put it first | same model SHA as authority; **NOT PROVEN** on path during Sep trains; train cwd becomes unique `runs/.../timestamp` workdir (no biopathnet package there) |
| A0 worktree | forbidden | 0 hits in File tracebacks |

## Conclusion
No demonstrated competing import hit in logs. Residual: `sys.path.append` means an ambient earlier entry **could** have won; historical PYTHONPATH **NOT_PROVEN**. Therefore competing-source search supports SOURCE_RESTORE but does **not** upgrade quiet lineages to FULLY_BOUND.
