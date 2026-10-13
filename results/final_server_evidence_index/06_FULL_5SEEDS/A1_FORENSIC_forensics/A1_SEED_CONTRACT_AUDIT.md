# A1 Seed Contract Audit
UTC: 2026-10-02T09:40:20Z

## Observed in SOURCE_RESTORE `script/run.py`
Order:
1. `create_working_directory(cfg)` (datetime path; not RNG)
2. `random.seed(args.seed)`
3. `np.random.seed(args.seed)`
4. `torch.manual_seed(seed_rank)` with `seed_rank = seed + rank`
5. then dataset → solver

## Missing / unbound
- `torch.cuda.manual_seed_all` — absent
- `cudnn.deterministic` / `benchmark` — not forced
- `PYTHONHASHSEED` — not bound
- `worker_init_fn` — `num_worker: 0` in engine dumps mitigates
- Hardcoded `manual_seed(0)` / `np.random.seed(0)` in `dataset.py` / `task.py` paths

## Verdict
**SEED_CONTRACT = PARTIALLY_BOUND**

Same numeric seed gives **partial** paired interpretation across BASE/GATE/RAW, not a fully deterministic shared stochastic realization.
