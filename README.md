# Settlement Guard (PISI) — Predictive Instant Settlement Intelligence

> **If Smart Routing predicts _where_ to send a payment, Settlement Guard predicts _when_ to protect its settlement.**

PISI (Predictive Instant Settlement Intelligence) is an autonomous agent designed to protect merchants from bank-downtime-induced settlement delays. It predicts when an already-captured payment's settlement path is at risk of disruption and proactively triggers **Razorpay Instant Settlement** before the merchant experiences a cash-flow interruption.

---

## 🔗 Live Links

| What | Where |
|------|-------|
| **Interactive Dashboard** | [Vercel](https://pisi-eosin.vercel.app) |
| **Production API / Health** | [Render Health](https://settlement-guard-pisi-predictive-instant.onrender.com/health) |
| **Webhook Endpoint** | `https://settlement-guard-pisi-predictive-instant.onrender.com/webhook/razorpay` |
| **GitHub Repository** | [Settlement Guard on GitHub](https://github.com/asmitha2025/Settlement-Guard-PISI-Predictive-Instant-Settlement-Intelligence) |

---

## 💡 The Problem

Two different failures can happen when a bank experiences downtime:

| Type | What Happens | Who Solves It? |
|------|--------------|----------------|
| **Authorization-time failure** | The payment itself fails | Smart Routing |
| **Settlement-time risk** | Payment succeeds, but the settlement leg stalls and merchant cash flow freezes | **Settlement Guard** |

Smart Routing optimizes which terminal handles a transaction. However, when the underlying banking infrastructure is unavailable, authorization can fail across terminals. Instant Settlement exists as a solution, but it is traditionally **reactive** — the merchant has to notice the settlement delay and request an intervention.

### Settlement Guard closes this gap.
Instead of waiting for a merchant to discover a settlement problem, PISI continuously evaluates settlement risk and determines whether intervention is required.

---

## 🎯 What Settlement Guard Does

Settlement Guard continuously monitors bank-health signals such as:
- Transaction error rates
- Settlement velocity
- Maintenance windows
- Network resilience
- Bank-specific failure signals

When an imminent settlement-path disruption is predicted, the system:
1. **Auto-activates** Instant Settlement when confidence is high.
2. **Escalates** to the merchant for confirmation when confidence is medium.
3. **Monitors only** when risk is low.

The system is designed to deploy **corporate capital rather than merchant funds**, following the conceptual structure of Instant Settlement. Every intervention is recorded in a **tamper-evident SHA-256 hash-chain audit trail**.

---

# 🧠 Key Features

## 🔮 ML-Powered Prediction
Settlement Guard combines machine learning with rule-based risk controls.

### XGBoost Classifier
- 47 engineered features
- Predicts bank-downtime probability
- Core dataset F1: **0.6965**
- Significantly outperforms the naive rule baseline
- Calibrated probabilities using **Platt scaling**

### Isolation Forest
Used as an additional anomaly-detection layer to identify novel or unusual failure patterns that may not be represented in the training data.

---

## ⚙️ 3-Tier Escalation Matrix

| Tier | Confidence | Health Score | Action |
|------|-------------|--------------|--------|
| **HIGH** | ≥ 0.85 | < 50 | **AUTO-ACTIVATE** |
| **MEDIUM** | 0.60–0.85 | < 70 | **ESCALATE** for merchant confirmation |
| **LOW** | < 0.60 | — | **MONITOR** only |

### Decision Philosophy
The system follows a conservative approach:
> **High confidence → Act automatically**  
> **Medium confidence → Ask for confirmation**  
> **Low confidence → Don't deploy capital**

---

## 🛡️ Hard Stopping Rules

Capital deployment is protected by multiple independent controls:
- Maximum **30% of corporate capital** can be deployed at once.
- Maximum **₹1.5 Cr** deployment cap.
- Maximum **10 concurrent bridges per bank corridor**.
- Maximum **₹50,000 per individual transaction bridge**.
- Merchant **opt-out flags are respected**.
- Every bridge receives a unique `BridgeKeyID`.

These controls prevent the ML model from becoming an unrestricted capital-deployment mechanism.

---

# 🔐 Tamper-Evident Audit Trail

Every bridge transaction generates an auditable record containing:

### SHA-256 Hash Chain
Each record is cryptographically linked to the previous record.

```text
Bridge N-1
    │
    ▼
 SHA-256
    │
    ▼
 Bridge N
    │
    ▼
 SHA-256
    │
    ▼
Bridge N+1
```

Tampering with an earlier record breaks the subsequent hash chain.

### Double-Entry Ledger
The accounting lifecycle follows:
```text
CREATION → RECEIVABLE → REPLENISHMENT → FEE_REVENUE
```
The ledger is designed so that transactions can be reconciled and books remain balanced.

---

## 🔄 Autonomous Agent Loop

```text
PERCEIVE → REASON → DECIDE → ACT → LEARN
   │         │        │       │       │
   ▼         ▼        ▼       ▼       ▼
Webhooks  XGBoost  3-Tier  Razorpay Auto +
+ Metrics  Model    Rules    API    Retrain
```

### 1. Perceive
The system receives Razorpay events and operational signals.  
Supported event categories include:
- `payment.captured`
- `payment.failed`
- `payment.downtime.*`
- `settlement.processed`

Webhook requests use HMAC-SHA256 verification.

### 2. Reason
The Feature Service calculates:
- Bank Vitality Score
- Transaction-health features
- Settlement velocity
- Error-rate signals
- ML probability

### 3. Decide
The Decision Engine applies:
- ML confidence
- Bank health
- Escalation thresholds
- Capital limits
- Corridor limits
- Merchant preferences

### 4. Act
When intervention is required, the Execution Layer communicates with the configured Razorpay settlement integration.

### 5. Learn
The system evaluates prediction performance and supports retraining when model drift is detected.  
Learning experiments were validated across multiple random seeds.

---

## 📊 Measured Results

### Stable Batch Evaluation
Run:
```bash
python scripts/batch_eval.py --n 1000 --seed 42
```
Quick dashboard evaluation:
```bash
python scripts/batch_eval.py --n 100 --seed 42
```

#### `n = 1000` Results

| Metric | Result |
|--------|--------|
| Genuine settlement-risk incidents | 168 / 1000 |
| True Positives | 119 |
| False Negatives | 49 |
| False Positives | 0 |
| True Negatives | 832 |
| Precision | 100% |
| Recall | 70.8% |
| F1 Score | 0.9333 |
| Protected volume | ₹1.50 Cr |
| Fee revenue @ 0.10% | ₹14,999.90 |
| Net fee profit | ₹5,136.95 |
| Merchant savings vs 0.30% reactive model | ₹29,999.80 |

> **Important:** Batch evaluation metrics are generated from the project's reproducible evaluation scripts and synthetic incident data. They should not be interpreted as production performance.

---

## 🧪 ML Model — Adversarial Dataset

The model was also evaluated against a harder adversarial dataset.

| Model | Precision | Recall | F1 |
|-------|-----------|--------|----|
| Naive Rule | 27.9% | 50.2% | 0.359 |
| Trained XGBoost | 38.4% | 54.5% | 0.450 |

### Learning Loop
Across the tested seed pairs:
- **5 / 5 seed pairs** → F1 improvement
- F1 improved from approximately **0.413 → 0.454**

This demonstrates that the learning pipeline is not simply a static rule-based system.

---

## 🏗️ System Architecture

```text
┌──────────────────────────┐
│       Razorpay API       │
│  Webhooks / Settlement   │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      FastAPI Server      │
│    /webhook/razorpay     │
│         /health          │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     Feature Service      │
│    BankVitalityEngine    │
│  47 engineered features  │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      ML Prediction       │
│  XGBoost + Isolation     │
│          Forest          │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     Decision Engine      │
│    3-Tier Escalation     │
│      Stopping Rules      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     Execution Layer      │
│  Settlement Integration  │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      Audit & Ledger      │
│   SHA-256 Hash Chain     │
│   Double-Entry Ledger    │
└──────────────────────────┘
```

---

## 🚀 Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/asmitha2025/Settlement-Guard-PISI-Predictive-Instant-Settlement-Intelligence.git
cd Settlement-Guard-PISI-Predictive-Instant-Settlement-Intelligence
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
```
Add the required Razorpay credentials and webhook secret to `.env`.  
Example:
```env
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
```
*Never commit real API keys or secrets to GitHub.*

### 4. Start the Backend API
```bash
uvicorn src.api.main:app --reload --port 8000
```
The API will be available at: `http://localhost:8000`  
Health endpoint: `http://localhost:8000/health`

### 5. Start the Dashboard
For the local demo:
```bash
python dashboard/server.py
```

### 6. Run the Live Agent Demo
```bash
python scripts/live_demo.py
```
This demonstrates the complete:
```text
Webhook ↓ Feature Engineering ↓ ML Prediction ↓ Risk Decision ↓ Capital Protection ↓ Audit Trail
```

### 7. Run Tests
```bash
python -m unittest discover tests
```
Run the Razorpay integration test:
```bash
python scripts/test_razorpay_integration.py
```

### 8. Run Batch Evaluation
```bash
python scripts/batch_eval.py --n 1000 --seed 42
```

---

## 🌐 Production Deployment

The project includes a deployed backend architecture:

```text
  Internet
     │
     ▼
┌────────────────┐
│    Razorpay    │
│    Webhooks    │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│     Render     │
│    FastAPI     │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│  Feature + ML  │
│ Decision Engine│
└───────┬────────┘
        │
        ▼
┌────────────────┐
│   Settlement   │
│  Integration   │
└────────────────┘
        ▲
        │
┌────────────────┐
│     Vercel     │
│   Dashboard    │
└────────────────┘
```

### Production API
- **Health check:** `https://settlement-guard-pisi-predictive-instant.onrender.com/health`
- **Webhook:** `https://settlement-guard-pisi-predictive-instant.onrender.com/webhook/razorpay`
- **Dashboard:** `https://pisi-eosin.vercel.app`

---

## 🎓 Honest Limitations

### ✅ Solved
- **Webhook Deployment:** The webhook receiver is deployed on Render and is accessible without requiring ngrok.
- **HMAC Verification:** Incoming webhook requests are protected using HMAC-SHA256 signature verification.
- **ML Prediction:** The system uses a trained XGBoost model rather than relying entirely on manually defined rules.
- **Razorpay Integration:** The system includes authenticated settlement API integration and paise-to-rupee conversion handling.
- **Live Webhook Receiver:** The backend supports the configured payment and settlement event flows.

### ⚠️ Remaining Limitations
1. **Synthetic Evaluation Data:** The `batch_eval.py` evaluation uses synthetic incidents for reproducibility. Therefore, the reported metrics do not represent production Razorpay performance. Real-world performance may differ significantly.
2. **Synthetic ML Training Data:** The XGBoost model is trained on synthetic features. Before a production deployment, the model would require retraining and validation using appropriate real-world production data.
3. **Limited Geographic Granularity:** Razorpay downtime signals may not provide sufficient geographic granularity for directly generating a complete regional risk map. The Area Risk Heatmap therefore represents an inference layer based on available merchant-location and bank-specific signals.
4. **Instant Settlement Test Constraints:** The integration is authenticated and implemented against the available API environment, but actual production money movement is subject to Razorpay's account permissions, API availability, and test/production environment constraints.

---

## 🔮 Production Roadmap

### Phase 1 — Data
- Collect production-grade settlement telemetry.
- Build a larger historical failure dataset.
- Improve feature engineering.
- Detect seasonal and corridor-specific patterns.

### Phase 2 — ML
- Retrain XGBoost on real-world data.
- Improve probability calibration.
- Evaluate precision/recall trade-offs.
- Introduce continuous model monitoring.
- Detect model drift automatically.

### Phase 3 — Financial Controls
- Integrate production capital limits.
- Add configurable merchant risk policies.
- Implement stronger reconciliation.
- Add real-time exposure monitoring.

### Phase 4 — Merchant Experience
- Merchant consent flow.
- Merchant-specific risk preferences.
- Real-time alerts.
- Manual override controls.
- Settlement-risk explanations.

### Phase 5 — Production
- Obtain appropriate production Instant Settlement access.
- Conduct security review.
- Perform financial reconciliation testing.
- Implement compliance controls.
- Conduct controlled rollout.

---

## 🔒 Security Considerations

Settlement Guard is designed around a defense-in-depth model.

Security controls include:
- HMAC-SHA256 webhook verification
- Environment-based secret management
- SHA-256 audit-chain integrity
- Capital deployment limits
- Transaction-level limits
- Corridor-level concurrency limits
- Merchant opt-out controls
- Double-entry accounting
- Reconciliation checks

### Secrets
Never commit: `.env`, API keys, Webhook secrets, Private credentials, Production tokens.  
Use `.env.example` as the configuration template.

---

## 📁 Project Structure

```text
Settlement-Guard-PISI/
│
├── src/
│   ├── api/
│   │   └── main.py
│   ├── features/
│   │   └── bank_vitality.py
│   ├── models/
│   │   ├── xgboost_model.py
│   │   └── anomaly_detector.py
│   ├── decision/
│   │   └── escalation_engine.py
│   ├── execution/
│   │   └── settlement.py
│   └── audit/
│       └── ledger.py
│
├── dashboard/
│   └── server.py
│
├── scripts/
│   ├── live_demo.py
│   ├── batch_eval.py
│   └── test_razorpay_integration.py
│
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

---

## 👩‍💻 Contributor

**Asmitha M**  
Core Architecture · ML Model Training · Feature Engineering · Decision Engine · Settlement Integration · Audit & Ledger  
GitHub: [@asmitha2025](https://github.com/asmitha2025)

---

## 📄 License

MIT © 2026 Asmitha M  
Built for the Razorpay AI Buildathon.

---

## 🚀 Final Takeaway

Settlement Guard doesn't wait for settlement failure to happen. It predicts settlement risk and decides whether intervention is justified before merchant cash flow is affected.

```text
       SETTLEMENT GUARD
              │
       ┌──────┴──────┐
       │             │
    PREDICT       PROTECT
       │             │
       ▼             ▼
 Bank Downtime  Merchant Cash Flow
       │             │
       └──────┬──────┘
              ▼
      AUTONOMOUS ACTION
```

**Settlement Guard (PISI) — Don't let bank downtime freeze your settlements.**
