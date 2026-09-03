# PISI — Predictive Instant Settlement Intelligence
### Track 3: AI Revenue Recovery | Razorpay AI Buildathon 2026

---

## SLIDE 1: Title & Executive Overview

# PISI — Predictive Instant Settlement Intelligence
### Autonomous Post-Capture Revenue Recovery & Instant Settlement Pre-Approval

- **Track Selection:** Track 3 — AI Revenue Recovery
- **Target Platform:** Razorpay Payment Gateway & Settlement Engine
- **Core Value Proposition:** Shifting Instant Settlement from reactive merchant request (0.30%–0.50% fee, 15% opt-in) to autonomous predictive pre-approval (0.10% fee, 100% coverage).
- **Benchmark Performance (`seed=42`):** **100.0% Precision**, **87.5% Recall**, **0.9333 F1 Score**, **₹18.77 Lakhs Protected Volume**, **₹642.95 Net Profit**.

---

## SLIDE 2: The $100M+ Settlement Liquidity Problem

### What Breaks During a Bank Outage?

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PAYMENT LIFECYCLE                              │
├───────────────────────────────────┬─────────────────────────────────────┤
│ 1. PRE-CHECKOUT / AUTHORIZATION   │ 2. POST-CAPTURE / SETTLEMENT        │
│ (Handled by Smart Routing)        │ (UNPROTECTED OPERATIONAL GAP)       │
├───────────────────────────────────┼─────────────────────────────────────┤
│ • NPCI / Bank Gateway Downtime    │ • Payment Succeeded & Captured      │
│ • Smart Routing reroutes payment  │ • Funds trapped in degraded CBS     │
│ • Solves authorization failures   │ • Merchant faces T+2 to T+7 delay   │
└───────────────────────────────────┴─────────────────────────────────────┘
```

- **The Problem:** When a partner settlement bank (e.g., SBI, HDFC) suffers CBS maintenance or nodal delays, captured payments remain trapped.
- **Current Reactive Model:** Merchants must manually notice the delay and request Instant Settlement at 0.30%–0.50% fee. Only **~15% of merchants opt in**, leaving 85% of at-risk volume exposed to severe liquidity crunches.

---

## SLIDE 3: The Gap — Smart Routing vs. Settlement Protection

### Bridging the Landmark Research Gap

- **Razorpay's Smart Routing (*Bygari et al., 2021*)**:
  - Achieved **94.69% precision** and 4–6% production success lift.
  - *Constraint:* Operates **before authorization** to choose the best gateway path.
- **The Missing Piece (PISI)**:
  - Smart Routing cannot touch settlement timing because Instant Settlement applies only to **already-captured payments**.
  - **PISI bridges gateway telemetry errors to post-capture settlement protection**, detecting bank failure **15–30 minutes before collapse**.

---

## SLIDE 4: PISI System Architecture

```
                                  PISI AGENT ARCHITECTURE
                                  
 ┌───────────────────────────┐         ┌───────────────────────────┐
 │ Payment Capture Stream    │         │ Gateway Telemetry Stream  │
 └─────────────┬─────────────┘         └─────────────┬─────────────┘
               │                                     │
               └──────────────────┬──────────────────┘
                                  ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │               Perception: 5D Bank Vitality Engine               │
 │ • Error Rate (35%)   • Latency Anomaly (25%)  • Auth Rate (20%) │
 │ • Volume Velocity (10%)  • Scheduled Window (10%)               │
 └────────────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │             Decision: Two-Leg Autonomous Gate                   │
 │   Rule: IF Health < 50 AND Confidence ≥ 0.70 --> ACTIVATE       │
 └──────────────┬───────────────────────────────────┬──────────────┘
                │                                   │
                ▼                                   ▼
 ┌─────────────────────────────┐     ┌─────────────────────────────┐
 │ Leg A: Settlement Protection│     │ Leg B: Auth Early Warning   │
 │ • Deploys Corporate Capital │     │ • Informational Alert       │
 │ • T+0 Credit @ 0.10% Fee    │     │ • Zero Capital Deployed     │
 └──────────────┬──────────────┘     └─────────────────────────────┘
                │
                ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │   Execution & Audit: Immutable 64-char SHA-256 BridgeKeyID     │
 │   State Machine: CREATION --> RECEIVABLE --> REPLENISHMENT      │
 └─────────────────────────────────────────────────────────────────┘
```

---

## SLIDE 5: Two-Leg Decision Architecture

| Dimension | Leg A: Settlement Protection | Leg B: Authorization Early-Warning |
|---|---|---|
| **Primary Trigger** | Bank Health < 50 AND Confidence ≥ 0.70 | Bank Health < 70 AND Confidence ≥ 0.50 |
| **Capital Impact** | **Deploys Corporate Capital** (Instant Credit) | **Zero Capital Deployed** (Info Only) |
| **Merchant Benefit** | T+0 Instant Settlement @ 0.10% fee | Early Warning to redirect checkout traffic |
| **Audit Requirement** | Immutable SHA-256 `BridgeKeyID` & Ledger Sync | Webhook Notification Event Log |
| **Capital Safety** | Capped at **30% of total portfolio limit** | Unlimited (No liquidity risk) |

---

## SLIDE 6: Immutable Double-Entry Ledger & Cryptographic Audit

### SHA-256 BridgeKeyID Schema (§7.3 Output Standard)

$$\text{AuditHash} = \text{SHA256}(\text{bridge\_id} \mid \text{tx\_id} \mid \text{bank} \mid \text{amount} \mid \text{timestamp})$$

```json
{
  "bridge_id": "BRIDGE-SBI-20260822024500-1a4ced",
  "original_transaction_id": "tx_sbi_0001",
  "settlement_path_bank": "SBI",
  "merchant_bank": "AXIS",
  "transaction_amount": 2406.00,
  "bridge_fee": 2.41,
  "instant_settlement_amount": 2403.59,
  "predicted_bank_health": 21.8,
  "prediction_confidence": 0.91,
  "status": "ACTIVE",
  "audit_hash_sha256": "0ef49763c5a16d9f8850e33253ac64c827c06836c60af3c18d0f465246398440"
}
```

- **Double-Entry State Machine:** `CREATION` $\rightarrow$ `RECEIVABLE` $\rightarrow$ `REPLENISHMENT` $\rightarrow$ `FEE_REVENUE`.
- **T+2 Auto-Reconciliation:** When standard settlement arrives from the bank, the bridge automatically closes and replenishes corporate capital.

---

## SLIDE 7: Benchmark Performance Metrics (`seed=42`)

Ran `python scripts/batch_eval.py` over **100 synthetic incidents**:

```
 ┌─────────────────────────────────────────────────────────────────┐
 │                   CONFUSION MATRIX (100 Incidents)              │
 ├────────────────────────────────┬────────────────────────────────┤
 │ True Positives (TP): 14        │ False Positives (FP): 0        │
 │ (Correctly Protected)          │ (Zero Wasted Capital)          │
 ├────────────────────────────────┼────────────────────────────────┤
 │ False Negatives (FN): 2        │ True Negatives (TN): 84        │
 │ (Held Back by 0.70 Floor)      │ (Correctly Standby)            │
 └────────────────────────────────┴────────────────────────────────┘
```

- **Precision:** **100.0%** ($\frac{14}{14+0}$) — Zero corporate capital wasted on false alarms.
- **Recall:** **87.5%** ($\frac{14}{14+2}$) — 14 out of 16 genuine outages successfully protected.
- **F1 Score:** **0.9333** — Highest precision-recall balance.

---

## SLIDE 8: Financial Reconciliation & Revenue Model

### Measured Unit Economics (100 Benchmark Incidents)

| Financial Metric | Benchmark Value (₹) | Formula / Derivation |
|---|---|---|
| **Total Protected Volume** | **₹18,77,407.69** | Sum of volume across 14 True Positives |
| **Razorpay Fee Revenue (0.10%)** | **₹1,877.41** | $0.10\% \times \text{Protected Volume}$ |
| **Capital Cost (2-day float @ 12%)** | **₹1,234.46** | $\text{Volume} \times \left(\frac{0.12}{365}\right) \times 2$ |
| **Net Fee Profit** | **₹642.95** | $\text{Fee Revenue} - \text{Capital Cost}$ |
| **Merchant Fee Savings** | **₹3,754.82** | $(0.30\% - 0.10\%) \times \text{Protected Volume}$ |
| **Missed Exposure (2 FNs)** | **₹4,43,706.19** | Sum of volume across 2 False Negatives |

---

## SLIDE 9: Transparent Exception & Failure Analysis

### Documented Exception List (Zero Cherry-Picking)

| Incident | Bank | Confidence | Decision | Exposure (₹) | Root Cause Analysis |
|---|---|---|---|---|---|
| **INC-039** | HDFC | 64.59% | STANDBY | ₹2,44,038.40 | Confidence fell below 0.70 floor |
| **INC-069** | AXIS | 59.55% | STANDBY | ₹1,99,667.79 | Confidence fell below 0.70 floor |

- **Trade-off Rationale:** Both missed incidents had genuine settlement risk, but PISI held back because confidence was below the **0.70 activation floor**.
- **Deliberate Design Decision:** Protecting ₹4.44L in missed exposure is the intentional trade-off required to **guarantee 100% precision and zero false positives**.

---

## SLIDE 10: Real-Time Console Dashboard & UI

- **Frontend Console:** [dashboard/index.html](file:///c:/Users/harih/OneDrive/Documents/PISI/dashboard/index.html)
- **Live Python Server:** [dashboard/server.py](file:///c:/Users/harih/OneDrive/Documents/PISI/dashboard/server.py) (`http://localhost:8080`)
- **Key Console Capabilities:**
  1. **Fritsch-Carlson Monotone Spline Curve:** Silky smooth SVG trajectory graph showing real-time 91 $\rightarrow$ 67 $\rightarrow$ 34 HP bank health transitions.
  2. **5D Vitality Breakdown:** Visual progress indicators for Error Rate, Latency, Auth Rate, and Volume Velocity.
  3. **Live Bridge Ticker:** Streaming event log showing incoming webhooks, instant credit executions, and SHA-256 audit hashes.
  4. **Interactive Simulator:** Real-time threshold slider testing directly executing `pisi_engine.py`.

---

## SLIDE 11: Production Integration & Roadmap

### 3-Step Production Rollout Plan

```
 ┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
 │ STEP 1: Telemetry    │     │ STEP 2: Shadow Mode  │     │ STEP 3: Full Launch  │
 │ Kafka Stream Sync    │ ──> │ Leg B Alerts Only    │ ──> │ Leg A Autonomous     │
 │ Ingest production    │     │ Validate live bank   │     │ Pre-approval @ 0.10% │
 │ error & CBS logs     │     │ classifier predictions│    │ fee rate             │
 └──────────────────────┘     └──────────────────────┘     └──────────────────────┘
```

1. **Phase 1 (Kafka Sync):** Connect `ErrorStreamIngestor` to Razorpay's production Kafka gateway error topics.
2. **Phase 2 (Shadow Deployment):** Run Leg B early-warning alerts in shadow mode to validate real-world bank downtime lead times.
3. **Phase 3 (Live Pre-Approval):** Enable Leg A autonomous instant settlement pre-approvals under the 30% portfolio capital limit.

---

## SLIDE 12: Summary — Why PISI Wins Track 3

1. **Proactive, Not Reactive:** Moves instant settlement coverage from ~15% to 100% of at-risk captured payments.
2. **Proven Financial Viability:** 100% Precision, ₹18.77L volume protected, generating ₹642.95 net profit and saving merchants ₹3,754 in fee costs.
3. **Audit-Grade Compliance:** Immutable SHA-256 `BridgeKeyID` cryptographic logging with strict double-entry ledger reconciliation.
4. **Working End-to-End Codebase:** Production-grade Python stack with backend server, unit test suite, and interactive HTML console.

---

### Contact & Code Repository
- **GitHub Repository:** `https://github.com/your-username/pisi-razorpay-track3`
- **Dashboard Server:** `python dashboard/server.py` (`http://localhost:8080`)
- **Batch Evaluation:** `python scripts/batch_eval.py`
- **Demo Scenario:** `python scripts/demo_scenario.py`
