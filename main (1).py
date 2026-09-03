"""
PISI FastAPI — REST endpoints for the Predictive Instant Settlement Intelligence system.
Track 3: AI Revenue Recovery
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from features.bank_vitality import BankVitalityEngine
from decision.pisi_engine import PISIDecisionEngine
from decision.bridge_key_id import BridgeKeyIDSystem
from execution.instant_settlement import InstantSettlementExecutor

app = FastAPI(
    title="PISI API",
    description="Predictive Instant Settlement Intelligence — Track 3: AI Revenue Recovery",
    version="1.0.0"
)

# Initialize engines
vitality_engine = BankVitalityEngine()
pisi_engine = PISIDecisionEngine(vitality_engine)
bridge_system = BridgeKeyIDSystem()
executor = InstantSettlementExecutor()

# --- Request/Response Models ---

class TransactionInput(BaseModel):
    tx_id: str
    order_id: str
    amount: float
    method: str
    customer_bank: str
    merchant_bank: str
    merchant_id: str
    timestamp: str
    status: str = "captured"
    captured_at: Optional[str] = None

class BankHealthResponse(BaseModel):
    bank_code: str
    composite_health: float
    status: str
    emoji: str
    dimensions: dict

class PISIDecisionResponse(BaseModel):
    tx_id: str
    decision: str
    bank_code: str
    bank_health: float
    bank_status: str
    confidence: float
    amount: float
    reason: str
    predictive_fee: Optional[float] = None
    estimated_capital_cost: Optional[float] = None
    net_protection_value: Optional[float] = None

class BridgeStatementResponse(BaseModel):
    bridge_key_id: str
    original_tx_id: str
    acquiring_bank: str
    amount: float
    predictive_fee: float
    merchant_credited: float
    prediction_confidence: float
    status: str
    creation_hash: str

# --- Endpoints ---

@app.get("/")
def root():
    return {
        "service": "PISI — Predictive Instant Settlement Intelligence",
        "track": "Track 3: AI Revenue Recovery",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health/banks")
def get_all_bank_health():
    """Get real-time health scores for all banks."""
    health = vitality_engine.get_all_bank_health()
    return {
        "timestamp": datetime.now().isoformat(),
        "banks": health
    }

@app.get("/health/bank/{bank_code}")
def get_bank_health(bank_code: str):
    """Get health score for a specific bank."""
    if bank_code not in vitality_engine.banks:
        raise HTTPException(status_code=404, detail=f"Bank {bank_code} not found")
    return vitality_engine.compute_composite_health(bank_code)

@app.post("/evaluate", response_model=PISIDecisionResponse)
def evaluate_transaction(tx: TransactionInput):
    """Evaluate a transaction for settlement risk and return PISI decision."""
    tx_dict = tx.dict()
    result = pisi_engine.evaluate_transaction(tx_dict)
    return result

@app.post("/activate")
def activate_protection(tx: TransactionInput):
    """Activate PISI protection for a transaction."""
    tx_dict = tx.dict()

    # First evaluate
    decision = pisi_engine.evaluate_transaction(tx_dict)
    if decision['decision'] != 'ACTIVATE':
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot activate: decision was {decision['decision']} — {decision['reason']}"
        )

    # Activate
    protection = pisi_engine.activate_protection(tx_dict, decision)

    # Create Bridge Key ID
    bridge_record = bridge_system.create_bridge_record(protection, tx_dict, decision)

    # Execute Instant Settlement (simulated)
    settlement_result = executor.execute_instant_settlement(tx_dict, protection, bridge_record)

    # Notify merchant
    notification = executor.notify_merchant(
        tx_dict['merchant_id'], 
        protection, 
        decision['bank_status']
    )

    return {
        "status": "activated",
        "tx_id": tx_dict['tx_id'],
        "bridge_key_id": protection['bridge_key_id'],
        "predictive_fee": protection['predictive_fee'],
        "merchant_credited": settlement_result['merchant_credited'],
        "settlement_time_seconds": settlement_result['settlement_time_seconds'],
        "decision": decision
    }

@app.post("/close/{tx_id}")
def close_protection(tx_id: str, standard_settlement_arrived: bool = True):
    """Close PISI protection when standard settlement arrives."""
    protection = pisi_engine.close_protection(tx_id, standard_settlement_arrived)
    if not protection:
        raise HTTPException(status_code=404, detail=f"No active protection found for {tx_id}")

    # Close bridge record
    bridge_record = bridge_system.close_bridge_record(
        protection['bridge_key_id'],
        standard_settlement_arrived
    )

    return {
        "status": "closed",
        "tx_id": tx_id,
        "bridge_key_id": protection['bridge_key_id'],
        "capital_replenished": protection['capital_deployed']
    }

@app.get("/bridge/{bridge_key_id}", response_model=BridgeStatementResponse)
def get_bridge_statement(bridge_key_id: str):
    """Get full audit statement for a Bridge Key ID."""
    statement = bridge_system.get_bridge_statement(bridge_key_id)
    if not statement:
        raise HTTPException(status_code=404, detail=f"Bridge Key ID {bridge_key_id} not found")
    return statement

@app.get("/dashboard/metrics")
def get_dashboard_metrics():
    """Get PISI system metrics for dashboard."""
    pisi_metrics = pisi_engine.get_dashboard_metrics()
    exec_summary = executor.get_execution_summary()

    return {
        "pisi_metrics": pisi_metrics,
        "execution_summary": exec_summary,
        "active_bridge_count": len(bridge_system.bridge_records),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/bridges")
def list_all_bridges():
    """List all Bridge Key IDs."""
    statements = bridge_system.get_all_statements()
    return {
        "count": len(statements),
        "bridges": statements
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
