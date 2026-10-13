# A1 authorization — independent adjudication accepted 2026-09-25

```
PASS__A1_PREFLIGHT_INDEPENDENTLY_ADJUDICATED
PASS__A1_EXECUTION_GUARDS_BOUND

A1_PREFLIGHT_PROTOCOL_DESIGN = PASS__INDEPENDENTLY_ADJUDICATED
A1_PREFLIGHT_FILE_LEVEL_INDEPENDENT_AUDIT = PASS__INDEPENDENTLY_ADJUDICATED
A1_EXECUTION_GUARDS = PASS__BOUND

FORMAL_ENVIRONMENT_BINDING = CLOSED__PASS__INDEPENDENTLY_ADJUDICATED

A1_EXECUTION_ENVIRONMENT_READY = true
A1_EXECUTION_READY = true
A1_AUTHORIZED = true

A1_STATUS = GO__ONE_SHOT_15_RUN_QRTC_METHOD_PANEL

A2_AUTHORIZED = false
A3_AUTHORIZED = false

NEW_FORMAL_TRAINING_RUNS = 0   # at authorization instant; increments once formal train cells start
```

## Guard patch return (unmodified)

- Zip: `FOR_GPT_A1_EXECUTION_GUARD_PATCH_RETURN.zip`
- SHA256: `76babe51db04c38d37fdbff3d1e1520c3243f7d19c3128f9642a38a99243e4df`

## Panel contract (frozen)

- Methods: BASE, GATE_ONLY, RAW_QRTC
- Seeds: 1024, 1025, 1026, 1027, 1028
- = 15 fresh formal runs
- Historical seed1024 ckpt = reproduction reference only (not a panel cell)
- Primary: paired MRR(RAW_QRTC − BASE)
- Mechanism: MRR(GATE_ONLY − BASE), MRR(RAW_QRTC − GATE_ONLY)
- Stats: 5 paired deltas, mean, sample SD (ddof=1), t95(df=4)=2.776445105
- Claim: **QRTC METHOD PANEL** (not feedback-state validity)

## Launchers (bound)

| Method | SHA256 |
|--------|--------|
| BASE | `500a220b937564e691c16a1699d07edb2dbff6179fd702863b566a4cd8563965` |
| GATE_ONLY | `b45d10cd53dedc4b830088c38f8d8ee7e59f7a8003d1c97896f69c331a2474f0` |
| RAW_QRTC | `d9857317207278b8daccaddf11729562ca20e0eec9ca69622d418fd59d0fcf1d` |

## Discipline

Do not change seeds/methods/launcher/hparams/primary/contrasts/t95/thresholds/proceed-stop after first formal optimizer step.
Return all 15 receipts raw after completion — no cherry-picking.
