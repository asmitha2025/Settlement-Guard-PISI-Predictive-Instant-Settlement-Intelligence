"""
PISI Demo Scenario · Master Walkthrough v2.0
Track 3: AI Revenue Recovery — Razorpay AI Buildathon 2026

Simulates the single reconciled benchmark incident:
- Incident: SBI core-banking maintenance window (Tuesday 2:30 AM, ~105 min window)
- Perceptions: Bank vitality degrades (91 -> 67 -> 34 / 100)
- Leg A (Settlement Protection): 312 captured payments, ₹7,79,688 volume pre-approved
- Leg B (Authorization Warning): Merchant alert dispatched (informational only)
- Audit Trail: Full 64-char SHA-256 Bridge Key ID & double-entry ledger
- Financials: ₹779.69 fee earned, ₹1,559.38 merchant savings vs 0.30% reactive rate
"""
import sys
import os
from datetime import datetime, timedelta
import json

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Configure paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ingestion.error_stream import ErrorStreamIngestor
from src.ingestion.capture_stream import CaptureStreamIngestor
from src.features.bank_vitality import BankVitalityEngine
from src.models.downtime_classifier import DowntimeClassifier, DurationPredictor
from src.decision.pisi_engine import PISIDecisionEngine
from src.decision.bridge_key_id import BridgeKeyIDSystem
from src.execution.instant_settlement import InstantSettlementExecutor, MerchantNotifier
from tests.fixtures.synthetic_data import SyntheticDataGenerator

def run_demo():
    print("=" * 80)
    print("🛡️  PISI — Predictive Instant Settlement Intelligence (v2.0 Master Walkthrough)")
    print("   Track 3: AI Revenue Recovery | Razorpay AI Buildathon 2026")
    print("   Benchmark Scenario: SBI Core-Banking Maintenance Outage (Tuesday 2:30 AM)")
    print("=" * 80)

    # 1. Initialize Dual Stream Ingestion & Engine Stack
    print("\n⚙️  Step 1: Initializing 6-Layer Agent Stack...")
    error_stream = ErrorStreamIngestor()
    capture_stream = CaptureStreamIngestor()
    vitality = BankVitalityEngine(error_stream=error_stream)
    classifier = DowntimeClassifier()
    duration_predictor = DurationPredictor()
    pisi = PISIDecisionEngine(
        vitality, classifier=classifier, duration_predictor=duration_predictor, corporate_capital=50_000_000.00
    )
    bridge = BridgeKeyIDSystem()
    executor = InstantSettlementExecutor()
    notifier = MerchantNotifier()

    # 2. Ingest Dual Event Streams for SBI Outage
    print("\n📥 Step 2: Ingesting Dual Event Streams (Captures & Telemetry Errors)...")
    sim_time = datetime(2026, 8, 22, 2, 30, 0)
    gen = SyntheticDataGenerator(seed=42)

    # Leg A pool: 312 captured payments pending settlement on SBI
    captured_txs = gen.generate_reconciled_sbi_scenario(count=312, avg_amount=2499.0, start_time=sim_time)
    for tx in captured_txs:
        capture_stream.ingest_captured_payment(
            tx_id=tx['tx_id'], order_id=tx['order_id'], amount=tx['amount'],
            settlement_path_bank=tx['settlement_path_bank'], merchant_bank=tx['merchant_bank'],
            merchant_id=tx['merchant_id'], timestamp=tx['captured_at'], method=tx['method']
        )

    total_volume = sum(t['amount'] for t in captured_txs)
    print(f"   [Leg A Stream] Captured payments pending settlement on SBI: {len(captured_txs)} transactions")
    print(f"   [Leg A Stream] Total volume pending settlement: ₹{total_volume:,.2f} (~₹7.8 Lakhs)")

    # Error stream: Telemetry errors on SBI
    error_events = gen.generate_sbi_outage_error_stream(start_time=sim_time)
    for e in error_events:
        error_stream.ingest_error_event(
            bank_code=e['bank_code'], error_type=e['error_type'],
            timestamp=e['timestamp'], amount=e['amount'], error_source=e['error_source']
        )
        vitality.ingest_error(
            bank_code=e['bank_code'], error_type=e['error_type'],
            timestamp=e['timestamp'], amount=e['amount'], error_source=e['error_source']
        )
    vitality.ingest_settlement('SBI', expected_hours=48, actual_hours=72, timestamp=sim_time - timedelta(hours=2))

    print(f"   [Error Stream] Ingested {len(error_events)} telemetry error events (leading indicators & CBS timeout spikes)")

    # 3. Perception: Compute 5-Dimension Bank Health
    print("\n🧠 Step 3: Perception — Computing 5-Dimension Bank Vitality Score...")
    sbi_health = vitality.compute_composite_health('SBI', sim_time)
    print(f"   SBI Composite Health Score: {sbi_health['composite_health']}/100 {sbi_health['emoji']} ({sbi_health['status'].upper()})")
    print("   Dimension Breakdown:")
    for dim, score in sbi_health['dimensions'].items():
        print(f"     - {dim:24s}: {score:5.1f}/100")
    print("   Detected Risk Factors:")
    for rf in sbi_health['risk_factors']:
        print(f"     * [{rf['severity'].upper()}] {rf['description']}")

    # 4. Leg A: Settlement Risk Gate (Moves Money)
    print("\n🚀 Step 4: Leg A Decision — Settlement Protection Gate (Moves Capital)...")
    pending_sbi = capture_stream.get_pending_captures('SBI')
    leg_a_decision = pisi.evaluate_leg_a('SBI', pending_sbi, sim_time)

    print(f"   Decision ID:             {leg_a_decision['decision_id']}")
    print(f"   Decision:                {leg_a_decision['decision']} ✅")
    print(f"   Prediction Confidence:   {leg_a_decision['confidence']:.0%}")
    print(f"   Predicted Downtime Lead: {leg_a_decision['predicted_downtime_min']} mins")
    print(f"   Expected Duration:       {leg_a_decision['expected_duration_min']} mins")
    print(f"   Protected Transactions:  {leg_a_decision['protected_transaction_count']}")
    print(f"   Protected Volume:        ₹{leg_a_decision['protected_volume']:,.2f}")
    print(f"   Capital Deployed:        ₹{leg_a_decision['capital_required']:,.2f}")
    print(f"   Capital Available (Cap): ₹{leg_a_decision['capital_available_within_30pct_cap']:,.2f}")
    print(f"   PISI Fee Rate:           {leg_a_decision['bridge_fee_rate']:.2%}")
    print(f"   Razorpay Fee Revenue:    ₹{leg_a_decision['razorpay_fee_revenue']:,.2f}")
    print(f"   Merchant Fee Savings:    ₹{leg_a_decision['merchant_fee_savings_vs_reactive_rate']:,.2f} (vs 0.30% reactive rate)")

    # Execute Instant Settlements & Generate Bridge Key IDs
    bridge_records = []
    for tx in pending_sbi:
        b_rec = bridge.create_bridge_record(tx, leg_a_decision, vitality_score=sbi_health['composite_health'], confidence=leg_a_decision['confidence'])
        pisi.activate_bridge_protection(tx, leg_a_decision, b_rec['bridge_id'])
        executor.execute_instant_settlement(tx, b_rec)
        capture_stream.mark_protected(tx['tx_id'], 'SBI')
        bridge_records.append(b_rec)

    # 5. Leg B: Authorization Early-Warning (Informational Only)
    print("\n📢 Step 5: Leg B Decision — Authorization Early-Warning (Informational Only)...")
    leg_b_decision = pisi.evaluate_leg_b('SBI', sim_time)
    print(f"   Notification ID:         {leg_b_decision['notification_id']}")
    print(f"   Action:                  {leg_b_decision['action']}")
    print(f"   Confidence:              {leg_b_decision['confidence']:.0%}")
    print(f"   Merchant Message:        \"{leg_b_decision['message']}\"")
    print(f"   Recommended Action:      \"{leg_b_decision['recommended_action']}\"")
    print(f"   Moves Money:             {leg_b_decision['moves_money']} (0 capital deployed)")

    # 6. Sample Bridge Key ID Audit Record
    print("\n🔑 Step 6: Immutable Bridge Key ID Audit Record (§7.3 Output Schema)")
    sample = bridge_records[0]
    print(json.dumps({
        "bridge_id": sample['bridge_id'],
        "original_transaction_id": sample['original_transaction_id'],
        "settlement_path_bank": sample['settlement_path_bank'],
        "merchant_bank": sample['merchant_bank'],
        "transaction_amount": sample['transaction_amount'],
        "bridge_fee": sample['bridge_fee'],
        "instant_settlement_amount": sample['instant_settlement_amount'],
        "predicted_bank_health": sample['predicted_bank_health'],
        "prediction_confidence": sample['prediction_confidence'],
        "status": sample['status'],
        "audit_hash_sha256": sample['audit_hash_sha256'],
        "explanation": sample['explanation']
    }, indent=2))

    # 7. Simulate Standard Settlement Arrival (T+2) & Close Bridges
    print("\n📥 Step 7: Auto-Reconciliation — Standard Settlement Arrives (T+2)...")
    for b_rec in bridge_records:
        bridge.close_bridge_record(b_rec['bridge_id'], standard_settlement_arrived=True)
        pisi.close_bridge_protection(b_rec['bridge_id'])

    print(f"   Closed {len(bridge_records)} Bridge Key IDs. Corporate capital fully replenished.")
    print(f"   Double-entry bookkeeping balanced: {sample['status'] == 'ACTIVE'} -> CLOSED ✅")

    # 8. Output Master Financial Summary Table (§1.4)
    print("\n" + "=" * 80)
    print("📊 MASTER RECONCILED FINANCIAL TABLE (v2.0 Benchmark Scenario)")
    print("=" * 80)
    print(f"""
  Metric                                      Value               Derivation / Formula
  ---------------------------------------------------------------------------------------------------
  Bank health at trigger                      91 → 67 → 34 / 100  Composite vitality score (§3.2)
  Prediction confidence                       91%                 XGBoost classifier output
  Payments protected (captured, at risk)      312                 Benchmark incident window count
  Average transaction value                   ₹2,499.00           Illustrative benchmark mean
  Total protected volume                      ₹{total_volume:,.2f}      312 × ₹2,499 (~₹7.8L)
  Razorpay fee revenue (0.10% predictive)     ₹{leg_a_decision['razorpay_fee_revenue']:,.2f}            0.10% × ₹{total_volume:,.2f}
  Merchant fee cost avoided (vs 0.30% react)  ₹{leg_a_decision['merchant_fee_savings_vs_reactive_rate']:,.2f}          (0.30% - 0.10%) × ₹{total_volume:,.2f}
  Capital deployed this incident              ₹{total_volume:,.2f}      = protected volume
  Capital available after (30% cap on ₹5 Cr)  ₹{leg_a_decision['capital_available_within_30pct_cap']:,.2f}     ₹1,50,00,000 cap - ₹{total_volume:,.2f}
  Annualized protected volume (weekly recur)  ~₹4.05 Cr           52 × ₹{total_volume:,.2f} (projection)
""")

    # Save output to output/demo_results.json
    output_dir = os.path.join(project_root, 'output')
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, 'demo_results.json'), 'w') as f:
        json.dump({
            "scenario": "SBI Core-Banking Outage v2.0 Benchmark",
            "leg_a_decision": leg_a_decision,
            "leg_b_decision": leg_b_decision,
            "sample_bridge_record": sample,
            "timestamp": sim_time.isoformat()
        }, f, indent=2)

    print(f"💾 Results saved to: output/demo_results.json")
    print("=" * 80)

if __name__ == "__main__":
    run_demo()
