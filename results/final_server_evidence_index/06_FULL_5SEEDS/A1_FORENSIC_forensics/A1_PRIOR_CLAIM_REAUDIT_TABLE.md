# PRIOR_CLAIM_REAUDIT_TABLE

| # | Prior claim | Verdict | Minimal evidence |
|---|-------------|---------|------------------|
| 1 | “RAW1024 是真实坏 seed” | PARTIALLY_SUPPORTED | Within-run BCE divergence ESTABLISHED + admissible lineage; “坏 seed” as scientific object OK; “坏” ≠ invalid execution |
| 2 | “QRTC 优化动力学本身不稳定” | UNSUPPORTED | One lineage ≠ method-wide law; generalized instability NOT_ESTABLISHED |
| 3 | “历史 0.55 与 fresh 0.195 证明同 seed 不稳定” | FALSE / OVERCLAIM | Different ckpt SHAs; historical is replay of May weights; not same stochastic realization; contract only SCIENTIFICALLY_EQUIVALENT_WITH_OPERATIONAL_DIFFS + May source SHA NOT_PROVEN |
| 4 | “RAW1024 必须进入 primary” | PARTIALLY_SUPPORTED / CONDITIONAL | Numerical+lineage ESTABLISHED; **contract-admissibility still HOLD** until Gate1 fully bound; if later ADMISSIBLE then must enter primary; never drop for ugly MRR |
| 4b | “RAW1024 = ADMISSIBLE__WITH_OPERATIONAL_INCIDENTS…” (prior adversarial pass) | WITHDRAWN_PREMATURE | Conflated fresh lineage with frozen-source contract binding; replaced by HOLD__RUNTIME_SOURCE_IMPORT_PROVENANCE_REQUIRES_FINAL_BINDING |
| 5 | “剩余 9 个可以安全 resume” | UNSUPPORTED | PRE_POST_PATCH compatibility UNRESOLVED; harness bytes at train time NOT_PROVEN |
| 6 | “当前 harness 8/8 MATCH ⇒ 执行链已完全修复” | PARTIALLY_SUPPORTED | MATCH proves *current* tree consistency only; does not wash historical runs |
| 7 | “前 6 + 后 9 可组成统一 frozen panel” | UNRESOLVED | Cannot close all 8 mix conditions without historical script SHA / import provenance receipts |
| 8 | “A1 只剩执行收尾，没有科学设计问题” | FALSE | Design caveats remain (FEEDBACK_STATE unread; GATE not pure gate; seed only PARTIALLY_BOUND); plus panel provenance HOLD |

Additional overclaims corrected:
- “GATE has extra trainable params vs BASE” on this DistMult fused A1 path: **UNSUPPORTED** for saved state (identical 115 tensor keys / 343911 params).
- “sys.path scrub is purely operational”: **FALSE as blanket** — SCIENCE_AFFECTING_IF ambient contamination; cold `run.py` uses `append` not scrub.
