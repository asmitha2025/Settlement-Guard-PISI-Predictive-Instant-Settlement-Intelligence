# Settlement Guard (PISI) — Predictive Instant Settlement Intelligence

**If Smart Routing predicts *where* to send a payment, Settlement Guard predicts *when* to protect its settlement.**

PISI (Predictive Instant Settlement Intelligence) is an autonomous agent that protects merchants from bank‑downtime‑induced settlement delays. It predicts when an already‑captured payment's settlement path is about to fail, and pre‑emptively deploys **Razorpay's corporate capital** via Instant Settlement — before the merchant even notices.

---

## 💡 The Problem

Two different failures can happen when a bank goes down:

| Type | What happens | Who solves it? |
|------|--------------|----------------|
| **Authorization‑time failure** | The payment itself fails | Smart Routing (Bygari et al., 2021) |
| **Settlement‑time risk** | Payment succeeds, but the settlement leg stalls — merchant cash‑flow freezes | **Nobody — until now** |

Smart Routing optimizes *which terminal* handles a transaction, but when the issuing bank itself is down, every terminal fails. Instant Settlement exists but is **reactive** — the merchant has to notice the delay and manually request it.

**Settlement Guard closes that gap.**

---

## 🎯 What Settlement Guard Does

It continuously monitors bank health signals (error rates, settlement velocity, maintenance windows, network resilience). When it predicts an imminent settlement‑path disruption, it:

1. **Auto‑activates Instant Settlement** for already‑captured transactions (if confidence is high).
2. **Escalates** to the merchant for confirmation (if confidence is medium).
3. **Monitors** and does nothing (if risk is low).

It deploys **Razorpay's corporate capital**, never merchant funds — same structure as Razorpay's existing Instant Settlement product. Every action is recorded in a tamper‑evident SHA‑256 hash‑chain audit trail.

---

## 🧠 Key Features

### 🔮 ML‑Powered Prediction
- **Trained XGBoost classifier** (47 features) predicting bank‑downtime probability with **F1 = 0.6965** — beats the naive rule baseline (F1 = 0.1379).
- **Isolation Forest anomaly detector** to catch novel failure modes.
- **Calibrated probabilities** via Platt scaling for trustworthy confidence scores.

### ⚙️ 3‑Tier Escalation Matrix
| Tier | Confidence | Health | Action |
|------|------------|--------|--------|
| **HIGH** | ≥ 0.85 | < 50 | **Auto‑ACTIVATE** – deploy capital autonomously |
| **MEDIUM** | 0.60–0.85 | < 70 | **ESCALATE** – require merchant confirmation (60s window) |
| **LOW** | < 0.60 | – | **MONITOR** – alert only, zero capital deployed |

### 🛡️ Hard Stopping Rules
- Max **30%** of corporate capital (₹1.5 Cr cap) can be deployed at any time.
- Max **10** concurrent bridges per bank corridor.
- Max **₹50,000** per single transaction bridge.
- Merchant **opt‑out flags** respected.

### 🔐 Tamper‑Evident Audit Trail
Every bridge is a `BridgeKeyID` with:
- Immutable SHA‑256 hash chained to the previous bridge’s hash.
- Double‑entry ledger (`CREATION → RECEIVABLE → REPLENISHMENT → FEE_REVENUE`).
- Full reconciliation – books always balance.

---

## 🔄 Agent Loop

```
PERCEIVE → REASON → DECIDE → ACT → LEARN
   ↓         ↓        ↓       ↓       ↓
Webhooks  XGBoost  3‑Tier   Razorpay  Auto‑
+ Metrics  Model   Escalation API      retrain
```

- **Perceive:** Ingests real Razorpay webhooks (`payment.captured`, `payment.failed`, etc.).
- **Reason:** Computes 5‑D bank vitality score + runs ML prediction.
- **Decide:** Applies escalation matrix and stopping rules.
- **Act:** Calls Razorpay On‑Demand Settlement API (live).
- **Learn:** Monitors prediction accuracy, triggers retraining on drift (validated across 5 seeds).

---

## 📊 Measured Results

| Metric | Value |
|--------|-------|
| Precision (synthetic batch) | **100%** |
| Recall (synthetic batch) | **87.5%** |
| F1 (ML model on harder test set) | **0.6965** |
| F1 improvement over naive rule | **+0.5586** |
| Learning loop seeds improved | **5/5** |

> *These numbers are from the actual scripts – run them yourself.*

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Razorpay API   │  ← Webhooks, settlements
└────────┬────────┘
         │
┌────────▼────────┐
│  FastAPI Server │  ← /webhook/razorpay, /health
└────────┬────────┘
         │
┌────────▼────────┐
│ Feature Service │  ← BankVitalityEngine, 47 features
└────────┬────────┘
         │
┌────────▼────────┐
│ ML Prediction   │  ← XGBoost, Isolation Forest
└────────┬────────┘
         │
┌────────▼────────┐
│ Decision Engine │  ← 3‑Tier escalation, stopping rules
└────────┬────────┘
         │
┌────────▼────────┐
│ Execution Layer │  ← Razorpay Instant Settlement API
└────────┬────────┘
         │
┌────────▼────────┐
│ Audit & Ledger  │  ← Hash chain, double‑entry
└─────────────────┘
```

---

## 🚀 Run It

```bash
# 1. Clone and install
git clone https://github.com/asmitha2025/Settlement-Guard-PISI-Predictive-Instant-Settlement-Intelligence.git
cd Settlement-Guard-PISI-Predictive-Instant-Settlement-Intelligence
pip install -r requirements.txt

# 2. Configure your .env
cp .env.example .env   # add your Razorpay keys and webhook secret

# 3. Start the backend dashboard & API server
python dashboard/server.py

# 4. Run the live demo (shows the full agent loop)
python scripts/live_demo.py

# 5. Run tests & integration suite
python -m unittest discover tests
python scripts/test_razorpay_integration.py
```

---

## 🎓 Honest Limitations

- Synthetic data is used for batch metrics; real‑world performance may vary.
- The XGBoost model is trained on feature‑level synthetic data – retrain on production data before full deployment.
- The webhook must be exposed via a persistent HTTPS URL (Cloudflare Tunnel / Render) – `ngrok.io` is blacklisted by Razorpay.

---

## 👩‍💻 Contributors

- **Asmitha M** ([@asmitha2025](https://github.com/asmitha2025)) — Core Architecture, ML Model Training, Decision Engine & Instant Settlement Integration

---

## 📄 License

MIT © 2026 Asmitha M — Built for the Razorpay AI Buildathon.

---

**Settlement Guard (PISI) — Don't let bank downtime freeze your settlements.**
