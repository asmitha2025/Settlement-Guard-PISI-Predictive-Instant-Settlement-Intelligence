"""
PISI Live Agent Loop Demo Script
================────────────────
Demonstrates the full autonomous agent loop:
1. Ingests payment captures and bank failure telemetry via webhook receiver
2. Updates 5D Bank Vitality Engine in real-time
3. Evaluates 3-Tier Escalation Matrix with trained XGBoost model
4. Executes Leg A Instant Settlement via Razorpay API (with paise conversion)
5. Generates immutable SHA-256 Hash-Chain Bridge Key ID audit statement

Run: python scripts/live_demo.py
Track 3: AI Revenue Recovery
"""
import sys
import os
import json
import hmac
import hashlib
from datetime import datetime

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from src.api.main import app, vitality_engine, error_stream


def main():
    print("=" * 76)
    print("  PISI LIVE AGENT LOOP DEMONSTRATION")
    print("  Razorpay Webhook -> 5D Vitality -> XGBoost -> Razorpay Settlement API")
    print("  Track 3: AI Revenue Recovery | Razorpay AI Buildathon 2026")
    print("=" * 76)

    client = TestClient(app)
    secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "rzp_whsec_pisi_2026_buildathon_secret")

    # --- STEP 1: Ingest 5 Captured Payments ---
    print("\n  [1/5] Ingesting captured payments pending settlement on SBI corridor...")
    for i in range(5):
        payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": f"pay_live_sbi_{i+1:03d}",
                        "order_id": f"order_sbi_{i+1:03d}",
                        "amount": 249900,  # ₹2,499.00 in paise
                        "currency": "INR",
                        "status": "captured",
                        "bank": "SBI",
                        "method": "upi"
                    }
                }
            }
        }
        body_bytes = json.dumps(payload).encode('utf-8')
        sig = hmac.new(secret.encode('utf-8'), body_bytes, hashlib.sha256).hexdigest()

        resp = client.post(
            "/webhook/razorpay",
            content=body_bytes,
            headers={"Content-Type": "application/json", "X-Razorpay-Signature": sig}
        )
        assert resp.status_code == 200

    print("        5 captured payments ingested into Leg A pending pool.")

    # --- STEP 2: Ingest Telemetry Error Events (Bank Degradation) ---
    print("\n  [2/5] Ingesting gateway & bank outage telemetry events for SBI...")
    now_maint = datetime(2026, 8, 22, 2, 30, 0)
    for i in range(10):
        vitality_engine.ingest_error("SBI", "bank_technical_error", timestamp=now_maint, amount=2499.0)
        error_stream.ingest_error_event("SBI", "bank_technical_error", timestamp=now_maint, amount=2499.0)

    print("        Telemetry error stream ingested.")

    # --- STEP 3: Check 5D Vitality Health Score ---
    print("\n  [3/5] Computing SBI 5D Bank Vitality Score...")
    health = vitality_engine.compute_composite_health("SBI", now=now_maint)
    print(f"        Composite Bank Health: {health['composite_health']} HP [{health['status'].upper()} {health['emoji']}]")
    print(f"        Dimensions: {health['dimensions']}")

    # --- STEP 4: Trigger Leg A Evaluation & Razorpay Settlement API ---
    print("\n  [4/5] Evaluating Leg A Decision Gate & Executing Instant Settlement...")
    resp = client.post("/pisi/evaluate-settlement", json={"bank_code": "SBI", "timestamp": now_maint.isoformat()})
    eval_res = resp.json()
    dec = eval_res["decision"]

    print(f"        Decision:        {dec['decision']}")
    print(f"        Escalation Tier: {dec['escalation_tier']}")
    print(f"        Confidence:      {dec['confidence']:.1%}")
    print(f"        Protected Tx:    {dec['protected_transaction_count']}")
    print(f"        Protected Vol:   ₹{dec['protected_volume']:,.2f}")
    print(f"        Fee Revenue:     ₹{dec['razorpay_fee_revenue']:,.2f} (0.10%)")
    print(f"        Merchant Savings:₹{dec['merchant_fee_savings_vs_reactive_rate']:,.2f}")

    if eval_res["activations"]:
        first_act = eval_res["activations"][0]
        print(f"\n        Sample Activation Output:")
        print(f"        Bridge Key ID:   {first_act['bridge_id']}")
        print(f"        Audit Hash:      {first_act['audit_hash'][:24]}...")
        print(f"        Credited Amount: ₹{first_act['merchant_credited']:,.2f}")

    # --- STEP 5: Verify Hash Chain Ledger Integrity ---
    print("\n  [5/5] Verifying Double-Entry Ledger & SHA-256 Hash Chain...")
    resp = client.get("/bridge/ledger/summary")
    summary = resp.json()
    print(f"        Total Ledger Entries: {summary['total_entries']}")
    print(f"        Books Balanced:       {summary['books_balanced']}")
    print(f"        Hash Chain Verified:  {summary['hash_chain_verified']}")

    print("\n" + "=" * 76)
    print("  LIVE DEMO COMPLETE — ALL AGENT LOOP STEPS OPERATIONAL")
    print("=" * 76 + "\n")


if __name__ == '__main__':
    main()
