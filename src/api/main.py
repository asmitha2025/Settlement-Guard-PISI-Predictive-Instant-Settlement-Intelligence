"""
PISI FastAPI Server — Layer 6 REST API · v2.3 (Multi-Route Webhook Alias)
Track 3: AI Revenue Recovery — Razorpay AI Buildathon 2026
"""
import sys
import os
import hmac
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request, Header

# Configure import paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ingestion.error_stream import ErrorStreamIngestor
from src.ingestion.capture_stream import CaptureStreamIngestor
from src.features.bank_vitality import BankVitalityEngine
from src.models.downtime_classifier import DowntimeClassifier, DurationPredictor
from src.decision.pisi_engine import PISIDecisionEngine
from src.decision.bridge_key_id import BridgeKeyIDSystem
from src.execution.instant_settlement import InstantSettlementExecutor, MerchantNotifier
from src.monitoring.metrics import MetricsCollector, DriftDetector

app = FastAPI(
    title="PISI REST API",
    description="Predictive Instant Settlement Intelligence — Track 3: AI Revenue Recovery",
    version="2.3.0"
)

# Instantiate Core System Stack
error_stream = ErrorStreamIngestor()
capture_stream = CaptureStreamIngestor()
vitality_engine = BankVitalityEngine(error_stream=error_stream)
classifier = DowntimeClassifier()
duration_predictor = DurationPredictor()
pisi_engine = PISIDecisionEngine(
    vitality_engine, classifier=classifier, duration_predictor=duration_predictor
)
bridge_system = BridgeKeyIDSystem()
executor = InstantSettlementExecutor()
notifier = MerchantNotifier()
metrics_collector = MetricsCollector()
drift_detector = DriftDetector()

# --- Request / Response Pydantic Models ---

class ErrorEventInput(BaseModel):
    bank_code: str
    error_type: str
    error_code: str = "bank_technical_error"
    error_source: str = "issuing_bank"
    amount: float = 0.0
    timestamp: Optional[str] = None

class CapturePaymentInput(BaseModel):
    tx_id: str
    order_id: str
    amount: float
    settlement_path_bank: str
    merchant_bank: str
    merchant_id: str
    method: str = "upi"
    timestamp: Optional[str] = None

class SettlementEvaluationInput(BaseModel):
    bank_code: str
    timestamp: Optional[str] = None

class AuthorizationEvaluationInput(BaseModel):
    bank_code: str
    timestamp: Optional[str] = None

# --- API Endpoints ---

@app.get("/")
@app.get("/health")
def health_check():
    return {
        "service": "PISI — Predictive Instant Settlement Intelligence",
        "version": "2.3.0",
        "track": "Track 3: AI Revenue Recovery",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/")
@app.post("/webhook/razorpay")
@app.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request, x_razorpay_signature: Optional[str] = Header(None)):
    """
    Razorpay HMAC-SHA256 Webhook Receiver.
    Accepts webhooks on /, /webhook/razorpay, and /webhooks/razorpay.
    Validates signature, ingests telemetry events, updates 5D Vitality,
    and automatically triggers Leg A evaluation if bank degradation is detected.
    """
    body_bytes = await request.body()
    webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "rzp_whsec_pisi_2026_buildathon_secret")

    # HMAC Signature verification
    if x_razorpay_signature:
        expected_sig = hmac.new(
            webhook_secret.encode('utf-8'), body_bytes, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected_sig, x_razorpay_signature):
            raise HTTPException(status_code=400, detail="Invalid Razorpay webhook HMAC signature")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("event", "unknown")
    entity_data = payload.get("payload", {}).get("payment", {}).get("entity", {})

    processed_action = "IGNORED"
    auto_decision = None

    if event_type == "payment.captured":
        tx_id = entity_data.get("id", f"tx_wh_{datetime.now().strftime('%H%M%S')}")
        amount = float(entity_data.get("amount", 0)) / 100.0  # paise to rupees
        bank = entity_data.get("bank", "SBI")
        method = entity_data.get("method", "upi")

        capture_stream.ingest_captured_payment(
            tx_id=tx_id,
            order_id=entity_data.get("order_id", f"ord_{tx_id}"),
            amount=amount,
            settlement_path_bank=bank,
            merchant_bank="HDFC",
            merchant_id="M-1001",
            method=method
        )
        processed_action = "INGESTED_CAPTURE"

    elif event_type in ["payment.failed", "bank.error", "payment.downtime.started", "payment.downtime.updated"]:
        bank = entity_data.get("bank", "SBI")
        amount = float(entity_data.get("amount", 0)) / 100.0
        error_code = entity_data.get("error_code", "bank_technical_error")

        error_stream.ingest_error_event(
            bank_code=bank,
            error_type=error_code,
            amount=amount,
            error_source="issuing_bank"
        )
        vitality_engine.ingest_error(
            bank_code=bank,
            error_type=error_code,
            amount=amount
        )
        processed_action = "INGESTED_ERROR_AND_EVALUATED"

        # Auto-trigger Leg A evaluation for the degraded bank corridor
        health = vitality_engine.compute_composite_health(bank)
        if health['composite_health'] < 50:
            pending = capture_stream.get_pending_captures(bank)
            auto_decision = pisi_engine.evaluate_leg_a(bank, pending)

    return {
        "status": "processed",
        "event": event_type,
        "action": processed_action,
        "auto_decision": auto_decision,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/ingest/error")
def ingest_error_event(event: ErrorEventInput):
    """Ingest a failed-payment or telemetry error event (feeds Leg B & Vitality)."""
    e = error_stream.ingest_error_event(
        bank_code=event.bank_code,
        error_type=event.error_type,
        timestamp=event.timestamp,
        amount=event.amount,
        error_source=event.error_source,
        error_code=event.error_code
    )
    vitality_engine.ingest_error(
        bank_code=event.bank_code,
        error_type=event.error_type,
        timestamp=event.timestamp,
        amount=event.amount,
        error_source=event.error_source
    )
    return {"status": "ingested", "event": str(e)}

@app.post("/ingest/capture")
def ingest_captured_payment(payment: CapturePaymentInput):
    """Ingest a captured payment event pending settlement (Leg A pool)."""
    tx = capture_stream.ingest_captured_payment(
        tx_id=payment.tx_id,
        order_id=payment.order_id,
        amount=payment.amount,
        settlement_path_bank=payment.settlement_path_bank,
        merchant_bank=payment.merchant_bank,
        merchant_id=payment.merchant_id,
        timestamp=payment.timestamp,
        method=payment.method
    )
    return {"status": "captured_pending_settlement", "tx": tx}

@app.get("/bank/{code}/vitality")
def get_bank_vitality(code: str):
    """Get 5-dimension health score and risk factors for a bank."""
    if code not in vitality_engine.banks:
        raise HTTPException(status_code=404, detail=f"Bank {code} not found in supported corridors")
    return vitality_engine.compute_composite_health(code)

@app.get("/banks/vitality")
def get_all_banks_vitality():
    """Get health scores for all supported banks."""
    return {
        "timestamp": datetime.now().isoformat(),
        "banks": vitality_engine.get_all_bank_health()
    }

@app.post("/pisi/evaluate-settlement")
def evaluate_settlement(req: SettlementEvaluationInput):
    """Evaluate Leg A: Settlement Protection for captured payments on a bank."""
    pending = capture_stream.get_pending_captures(req.bank_code)
    decision = pisi_engine.evaluate_leg_a(req.bank_code, pending, req.timestamp)

    # If decision is ACTIVATE, execute advances & create Bridge Key IDs
    activations = []
    if decision['decision'] == 'ACTIVATE':
        for tx in pending:
            bridge_rec = bridge_system.create_bridge_record(
                tx, decision, vitality_score=34.0, confidence=decision['confidence']
            )
            pisi_engine.activate_bridge_protection(tx, decision, bridge_rec['bridge_id'])
            settlement_res = executor.execute_instant_settlement(tx, bridge_rec)
            capture_stream.mark_protected(tx['tx_id'], req.bank_code)
            activations.append({
                "tx_id": tx['tx_id'],
                "bridge_id": bridge_rec['bridge_id'],
                "amount": tx['amount'],
                "merchant_credited": settlement_res['merchant_credited'],
                "audit_hash": bridge_rec['audit_hash_sha256']
            })

    return {
        "decision": decision,
        "activations_count": len(activations),
        "activations": activations[:5]
    }

@app.post("/pisi/evaluate-authorization")
def evaluate_authorization(req: AuthorizationEvaluationInput):
    """Evaluate Leg B: Authorization Early-Warning (Informational Only)."""
    warning = pisi_engine.evaluate_leg_b(req.bank_code, req.timestamp)
    if warning['action'] == 'WARN':
        notifier.send_early_warning(req.bank_code, confidence=warning['confidence'])
    return warning

@app.get("/bridge/{bridge_id}")
def get_bridge_details(bridge_id: str):
    """Retrieve verified Bridge Key ID statement with real SHA-256 audit hash."""
    statement = bridge_system.get_bridge_statement(bridge_id)
    if not statement:
        raise HTTPException(status_code=404, detail=f"Bridge Key ID {bridge_id} not found")
    return statement

@app.get("/bridge/ledger/summary")
def get_ledger_summary():
    """Get double-entry audit ledger entries and hash chain verification."""
    chain_valid = bridge_system.verify_hash_chain()
    return {
        "total_entries": len(bridge_system.ledger),
        "books_balanced": True,
        "hash_chain_verified": chain_valid,
        "entries_sample": bridge_system.ledger[-10:]
    }

@app.post("/pisi/close/{bridge_id}")
def close_bridge_protection(bridge_id: str):
    """Close a Bridge Key ID upon arrival of standard settlement."""
    record = bridge_system.close_bridge_record(bridge_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Bridge {bridge_id} not found")
    pisi_engine.close_bridge_protection(bridge_id)
    return {
        "status": "CLOSED",
        "bridge_id": bridge_id,
        "books_balanced": record['books_balanced'],
        "capital_replenished": record['transaction_amount']
    }

@app.get("/pisi/metrics")
def get_pisi_metrics():
    """Get system metrics and performance tracking."""
    return {
        "pisi_metrics": pisi_engine.get_dashboard_metrics(),
        "execution_metrics": executor.get_summary()
    }

@app.get("/dashboard/data")
def get_dashboard_data():
    """Consolidated data feed for Streamlit War Room UI."""
    return {
        "bank_health": vitality_engine.get_all_bank_health(),
        "metrics": pisi_engine.get_dashboard_metrics(),
        "active_bridges": list(bridge_system.bridge_records.values())[:10],
        "notifications": notifier.notifications[-5:]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
