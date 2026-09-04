# PISI — Predictive Instant Settlement Intelligence
**TRACK 3 • AI REVENUE RECOVERY**
*Razorpay AI Buildathon 2026*

---

## Slide 1: Title
**PISI**
**Predictive Instant Settlement Intelligence**
*TRACK 3 • AI REVENUE RECOVERY*
*Razorpay AI Buildathon 2026*

---

## Slide 2: The Problem (Two Different Failures)

### AUTHORIZATION FAILURE
The payment attempt itself doesn't go through — the customer's bank can't approve the debit.
Razorpay's own error docs call this "beyond our control" and point to multi-terminal routing — **Smart Routing's job.**
*Already handled.*

### SETTLEMENT RISK
The payment already succeeded. What's at risk is the leg that moves funds onward, through a now-degraded bank.
Not a customer-facing failure — a **merchant cash-flow problem.**
**Nothing in Razorpay's stack predicts it ahead of time.**
*This is what PISI builds.*

---

## Slide 3: Razorpay Already Built Both Halves

| **SMART ROUTING** | **INSTANT SETTLEMENT** |
|---|---|
| 94.69% Random Forest precision (best of 5 models) | T+0 payout advance using Razorpay's own corporate capital |
| 4-6% measured lift in production success rate | Published at 0.30% per settlement |
| ~35M transactions trained on | T = the captured payment date |
| Operates on the acquiring/gateway side only | Merchant-triggered today |
| | Only applies to a payment that's already captured |

---

## Slide 4: The Gap — Nothing Connects Prediction to Capital

```
SMART ROUTING                INSTANT SETTLEMENT              PISI
predicts which terminal      advances payout,               predictive,
succeeds                     reactively                     automatic,
                                                           settlement
                                                           protection
```

**"Smart Routing already handles gateway-side degradation. Nothing predicts settlement-path risk ahead of time and pre-approves the advance automatically — today a merchant has to notice the delay themselves."**

---

## Slide 5: How It Works — Two Independent Legs

### LEG A · SETTLEMENT PROTECTION
Pre-approves Instant Settlement for already-captured payments, when the settlement-path bank is predicted to degrade.

**MOVES MONEY**

### LEG B · AUTHORIZATION WARNING
Notifies merchants when a bank is predicted to cause authorization failures. Shortens reaction time.

**INFORMATIONAL ONLY — NEVER CLAIMS TO PREVENT FAILURE**

---

## Slide 6: Architecture — Six Layers, Perceive to Learn

```
┌─────────────────────────────────────────────────────────┐
│ L1  Data Ingestion    Captured-payment + failed-payment  │
│                       webhook streams                    │
├─────────────────────────────────────────────────────────┤
│ L2  Feature          5-dimension bank vitality           │
│     Engineering      composite score                     │
├─────────────────────────────────────────────────────────┤
│ L3  Prediction       Downtime probability + duration     │
│     Engine           estimate                            │
├─────────────────────────────────────────────────────────┤
│ L4  Decision         Leg A / Leg B gates, capital        │
│     Engine           ledger, safety caps                 │
├─────────────────────────────────────────────────────────┤
│ L5  Execution        Instant Settlement call + Bridge    │
│                       Key ID audit trail                 │
├─────────────────────────────────────────────────────────┤
│ L6  Monitoring &     Precision/recall tracking, drift    │
│     Feedback         detection, retrain trigger          │
└─────────────────────────────────────────────────────────┘
```

---

## Slide 7: Live System — Not Slides, a Working Console

**BANK VITALITY — SBI**
```
91 → 67 → 34 /100
        CRITICAL
```

**DECISION ENGINE**
- LEG A: **ACTIVATE**
- LEG B: WARN (informational)

**BRIDGE KEY ID — SAMPLE AUDIT RECORD**
```
BRIDGE-SBI-20260823T133603-mo_000
- Rs 3,641.63
- Rs 3,637.99 settled
SHA-256: 944c25f386d8358b22f4f7734c67b12e55516bd2392ef54642803b93903a398
Books balanced — verified byte-for-byte against Python's hashlib.sha256
```

---

## Slide 8: Measured Results (1,000 Independent Incidents)

| Metric | Value |
|--------|-------|
| True Positives | **119** |
| False Negatives | **49** |
| False Positives | **0** |
| True Negatives | **832** |

**100% PRECISION**
**70.8% RECALL (N=1000, STABLE)**

### READING THE FALSE NEGATIVES HONESTLY
- **43 of 49** — confidence stayed below the 70% activation floor on a genuine risk incident. The engine correctly held back rather than act on an uncertain signal.
- **6 of 49** — happen only after incident #965 of 1000, once cumulative deployment approaches the 30% capital cap. The safety gate is a real constraint, not decorative.

---

## Slide 9: A Real Trained Classifier, on Harder Data

The batch above uses a rule-based scorer on cleanly-separable data — that's why precision was 100%. This trains a real model on a harder dataset where risk is genuinely noisy, and compares it to the naive rule anyone would hand-write.

| | Precision | Recall | F1 |
|---|---|---|---|
| **Naive Rule** | 27.9% | 50.2% | 0.359 |
| **XGBoost** | **38.4%** | **54.5%** | **0.450** |

- Beats the naive rule on **both metrics at once**, on a held-out test set it never trained on.
- 3 planted noise features correctly rank last in feature importance (avg rank 8.0 of 10) — evidence it learned signal, not spurious correlation.
- **Finding along the way:** at the old 0.70 threshold, every trained model's recall collapsed near zero. Fixed by choosing each model's own threshold on validation data (0.225), not reusing one calibrated for a different, easier dataset.

---

## Slide 10: Found, Measured, and Fixed — Not Just Identified

### CAPITAL ALLOCATION
6 of 49 misses happened only because the 30% cap ran out near the end of a busy batch — not a confidence problem, an **ordering problem**.
**Fix:** smallest-transaction-first, plus a per-incident reserve cap.
**100% of capital-exhaustion misses rescued across 5 seeds · 0 new false positives**

### LEARNING LOOP
Load the deployed model → simulate drift after deployment → retrain on accumulated data → verify on a third, untouched batch.
The only fair test: does retraining actually help, or just memorize the drift sample?

**0.413 → 0.454 F1**
*improved in 5 of 5 seed pairs tested*

---

## Slide 11: Small, Honest, Reproducible

| ₹1.50 Cr | ₹14,999.90 | ₹5,136.95 | ₹29,999.80 |
|----------|------------|-----------|------------|
| PROTECTED | FEE REVENUE | NET FEE | MERCHANT SAVINGS |
| VOLUME | @ 0.10% | PROFIT | VS 0.30% REACTIVE |

*Every figure above is the literal stdout of `python scripts/batch_eval.py` — seed=42, n=1000. Rerun it and get the identical numbers.*

**This isn't a new prediction model — Razorpay's is better than anything built in two weeks. It's a product gap: turning a settlement product from reactive to predictive.**

---

## Slide 12: Production-Ready & Deployed

### LIVE FULL-STACK SYSTEM
- **Interactive Console (Vercel):** https://pisi-eosin.vercel.app
- **Decision Engine (Render):** https://settlement-guard-pisi-predictive-instant.onrender.com
- **Live Agent Loop:** One-click "Simulate Downtime" button triggers real-time perception → XGBoost inference → capital escalation → instant settlement.
- **Webhook Ingestion:** 6 Razorpay event types supported with synchronous HMAC-SHA256 verification (<5ms).

### SECURITY & CAPITAL SAFEGUARDS
- Tamper-evident SHA-256 hash audit trail (byte-for-byte verified with Web Crypto & Python hashlib)
- Double-entry protection ledger (debits = credits)
- 3-tier escalation matrix (HIGH / MEDIUM / LOW)
- Hard stopping rules: 30% portfolio cap, 10 concurrent bridges, ₹50K per-tx limit

---

## Slide 13: What We've Built Beyond the Original Scope

| Feature | Impact |
|---------|--------|
| **Real Razorpay API Integration** | Executes on-demand settlements with paise conversion |
| **Live Webhook Receiver** | Ingests real payment events, verifies HMAC signatures |
| **Trained XGBoost Model** | F1 = 0.6965 on core benchmark (and 0.450 on adversarial stress-test, Slide 9) |
| **Isolation Forest** | Catches novel out-of-distribution bank failures |
| **Learning Loop** | Auto-retrains on drift, validated across 5 seeds |
| **Resilient Fallback** | Rule-based scorer catches failures gracefully |
| **FastAPI Production Server** | Deployed on Render, response < 5ms |

---

## Slide 14: Closing

```
Smart Routing optimizes the path.
PISI optimizes the safety net.
```

**PISI — Predictive Instant Settlement Intelligence**

*One question: What if the merchant never had to ask?*

---

## Slide 15: Links & Resources

- **Interactive Live Dashboard:** https://pisi-eosin.vercel.app
- **Production REST API / Health:** https://settlement-guard-pisi-predictive-instant.onrender.com/health
- **GitHub Repository:** https://github.com/asmitha2025/Settlement-Guard-PISI-Predictive-Instant-Settlement-Intelligence

*Built for Razorpay AI Buildathon 2026 — Track 3: AI Revenue Recovery*
