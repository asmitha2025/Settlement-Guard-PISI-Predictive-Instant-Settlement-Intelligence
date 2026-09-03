# Known Limitations

Written deliberately, because Track 3's own evaluation bar asks for the exception list, not just the wins. This is what's real in this prototype and what isn't yet.

## What's real

- The decision logic in `pisi_engine.py` actually runs, actually enforces its stated safety gates (per-transaction cap, merchant-health floor, 30% portfolio capital cap), and actually excludes transactions that fail them — you can see this in `demo_scenario.py`'s "Excluded by safety gates" line.
- The SHA-256 audit hash is a genuine `hashlib.sha256()` digest, 64 hex characters, computed at runtime — not hand-written or truncated.
- The double-entry ledger in `bridge_key_id.py` actually balances (`books_balanced()` returns `True` after reconciliation) because the debit/credit entries were worked through by hand before being coded, not assumed.
- The numbers in the README's results table are the literal stdout of `batch_eval.py` — nothing was rounded up, cherry-picked, or backfilled.

## What isn't real yet

- **`bank_vitality.py` is a rule-based weighted average, not a trained model.** The architecture document describes an XGBoost classifier trained on 47 engineered features from historical Razorpay data. That training hasn't happened — there's no historical data available to train on in this environment. What's here demonstrates the *scoring logic and decision boundary*, not a validated predictor.
- **The synthetic data is illustrative, not calibrated to real Razorpay traffic.** `synthetic_data.py`'s `base_rate=0.17` (17% of incidents are genuine risk) and its Beta/Normal distribution parameters are chosen to produce a believable-looking batch, not derived from real error-code frequencies, seasonal patterns (Diwali, salary week), or bank-specific maintenance schedules.
- **The 100% precision / 0 false positives in the seed=42 run is a property of the synthetic generator's class separation, not a real result.** The Beta(2,6) confidence distribution for non-risk incidents rarely exceeds the 0.70 activation threshold by construction. With real data — where genuine ambiguity exists — false positives should be expected and budgeted for. Don't present this run's precision as a validated model metric; present it as "the engine behaves correctly against synthetic ground truth," which is a narrower and more honest claim.
- **`MAX_CONCURRENT_PER_BANK` (settings.py) is defined but not enforced.** It's meant to cap concurrent *incident windows* per bank, which requires tracking incident open/close state over time. This prototype evaluates each incident independently and doesn't model that overlap. `MAX_PER_TRANSACTION`, `MIN_MERCHANT_HEALTH`, and the 30% portfolio capital cap are enforced; this one gate is not.
- **No FastAPI or Streamlit layer.** The architecture doc describes both; neither is built here. The decision engine and audit trail are directly callable Python — wrapping them in an API and a dashboard is mechanical, not risky, and is the natural next step if there's time before the deadline.
- **`ANNUAL_COST_OF_CAPITAL = 0.12` is an illustrative placeholder**, not sourced from Razorpay's actual cost of capital. The 0.30% reactive fee rate, by contrast, is Razorpay's published On-Demand Settlement rate and can be cited with more confidence.
- **Leg B has no outcome tracking.** Because it only sends a notification and never moves money, there's no way in this prototype to measure whether a warning actually helped a merchant — unlike Leg A, whose outcomes are auditable through the Bridge Key ID ledger.
