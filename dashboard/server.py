"""
PISI Dashboard Backend Server
Serves the HTML dashboard and provides live API endpoints
connected to the real PISI decision engine.

Run: python dashboard/server.py
Opens: http://localhost:8080
"""
import sys
import os
import json
import hashlib
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import webbrowser
import threading

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ingestion.error_stream import ErrorStreamIngestor
from src.ingestion.capture_stream import CaptureStreamIngestor
from src.features.bank_vitality import BankVitalityEngine
from src.models.downtime_classifier import DowntimeClassifier, DurationPredictor
from src.decision.pisi_engine import PISIDecisionEngine
from src.decision.bridge_key_id import BridgeKeyIDSystem
from src.execution.instant_settlement import InstantSettlementExecutor
from tests.fixtures.synthetic_data import SyntheticDataGenerator
from scripts.batch_eval import run_batch_evaluation

# ── Initialize PISI Engine Stack ──────────────────────────────────────
error_stream = ErrorStreamIngestor()
capture_stream = CaptureStreamIngestor()
vitality = BankVitalityEngine(error_stream=error_stream)
classifier = DowntimeClassifier()
duration_predictor = DurationPredictor()
pisi = PISIDecisionEngine(vitality, classifier, duration_predictor, corporate_capital=50_000_000.00)
bridge_system = BridgeKeyIDSystem()
executor = InstantSettlementExecutor()
gen = SyntheticDataGenerator(seed=42)

sbi_scenario_run = False


def get_all_bank_health():
    """Get health for all monitored banks."""
    health_data = vitality.get_all_bank_health()
    result = {}
    for bank, data in health_data.items():
        result[bank] = {
            'composite_health': data['composite_health'],
            'status': data['status'],
            'emoji': data['emoji'],
            'dimensions': data['dimensions'],
            'risk_factors': data.get('risk_factors', [])
        }
    return result


def run_sbi_scenario():
    """Run the full SBI benchmark scenario and return results."""
    global sbi_scenario_run
    sim_time = datetime(2026, 8, 22, 2, 30, 0)
    scenario_gen = SyntheticDataGenerator(seed=42)

    # Ingest captures
    captured_txs = scenario_gen.generate_reconciled_sbi_scenario(
        count=312, avg_amount=2499.0, start_time=sim_time
    )
    for tx in captured_txs:
        capture_stream.ingest_captured_payment(
            tx_id=tx['tx_id'], order_id=tx['order_id'], amount=tx['amount'],
            settlement_path_bank=tx['settlement_path_bank'],
            merchant_bank=tx['merchant_bank'],
            merchant_id=tx['merchant_id'], timestamp=tx['captured_at'],
            method=tx['method']
        )

    # Ingest errors
    error_events = scenario_gen.generate_sbi_outage_error_stream(start_time=sim_time)
    for e in error_events:
        error_stream.ingest_error_event(
            bank_code=e['bank_code'], error_type=e['error_type'],
            timestamp=e['timestamp'], amount=e['amount'],
            error_source=e['error_source']
        )
        vitality.ingest_error(
            bank_code=e['bank_code'], error_type=e['error_type'],
            timestamp=e['timestamp'], amount=e['amount'],
            error_source=e.get('error_source', 'gateway')
        )
    vitality.ingest_settlement('SBI', 48, 72, sim_time - timedelta(hours=2))

    # Evaluate
    pending = capture_stream.get_pending_captures('SBI')
    sbi_health = vitality.compute_composite_health('SBI', sim_time)
    leg_a = pisi.evaluate_leg_a('SBI', pending, sim_time)
    leg_b = pisi.evaluate_leg_b('SBI', sim_time)

    # Execute bridges
    created_bridges = []
    for tx in pending[:5]:  # Sample 5 bridges for display
        b_rec = bridge_system.create_bridge_record(
            tx, leg_a,
            vitality_score=sbi_health['composite_health'],
            confidence=leg_a['confidence']
        )
        pisi.activate_bridge_protection(tx, leg_a, b_rec['bridge_id'])
        executor.execute_instant_settlement(tx, b_rec)
        capture_stream.mark_protected(tx['tx_id'], 'SBI')
        created_bridges.append(b_rec)

    total_volume = sum(t['amount'] for t in captured_txs)
    sbi_scenario_run = True

    return {
        'bank': 'SBI',
        'health_trajectory': [91, 67, round(sbi_health['composite_health'], 1)],
        'health': sbi_health,
        'leg_a': leg_a,
        'leg_b': leg_b,
        'total_volume': round(total_volume, 2),
        'tx_count': len(captured_txs),
        'fee_revenue': round(total_volume * 0.001, 2),
        'merchant_savings': round(total_volume * 0.002, 2),
        'sample_bridge': created_bridges[0] if created_bridges else None,
        'sample_transactions': [
            {
                'tx_id': tx['tx_id'],
                'amount': tx['amount'],
                'method': tx['method'],
                'settlement_path_bank': tx['settlement_path_bank'],
                'merchant_bank': tx['merchant_bank'],
                'captured_at': tx['captured_at'],
                'fee': round(tx['amount'] * 0.001, 2)
            }
            for tx in captured_txs[:10]
        ]
    }


def evaluate_bank(bank_code):
    """Evaluate a specific bank's current state."""
    now = datetime.now()
    health = vitality.compute_composite_health(bank_code, now)
    confidence = classifier.predict_downtime_probability(
        bank_code, health['composite_health'], now
    )
    return {
        'bank': bank_code,
        'health': health,
        'confidence': round(confidence, 4),
        'decision': 'ACTIVATE' if health['composite_health'] < 50 and confidence >= 0.70
                    else 'MONITOR' if health['composite_health'] < 70 and confidence >= 0.50
                    else 'STANDBY'
    }


def get_dashboard_metrics():
    """Get current engine dashboard metrics."""
    return pisi.get_dashboard_metrics()


# ── HTTP Request Handler ──────────────────────────────────────────────
class PISIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.dashboard_dir = os.path.join(project_root, 'dashboard')
        super().__init__(*args, directory=self.dashboard_dir, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # API Routes
        if path == '/api/health/all':
            self._json_response(get_all_bank_health())

        elif path == '/api/health/bank':
            bank = params.get('bank', ['SBI'])[0]
            self._json_response(evaluate_bank(bank))

        elif path == '/api/scenario/sbi':
            result = run_sbi_scenario()
            self._json_response(result)

        elif path == '/api/batch_eval':
            result = run_batch_evaluation(num_incidents=100, seed=42)
            self._json_response(result)

        elif path == '/api/metrics':
            self._json_response(get_dashboard_metrics())

        elif path == '/api/bridge/create':
            bank = params.get('bank', ['SBI'])[0]
            amount = float(params.get('amount', ['2499.00'])[0])
            health_score = float(params.get('health', ['34.0'])[0])
            confidence = float(params.get('confidence', ['0.91'])[0])

            tx = {
                'tx_id': f"tx_live_{datetime.now().strftime('%H%M%S')}_{os.urandom(3).hex()}",
                'order_id': f"ord_live_{os.urandom(3).hex()}",
                'amount': amount,
                'method': 'upi',
                'settlement_path_bank': bank,
                'merchant_bank': 'HDFC',
                'merchant_id': 'M-1001',
                'captured_at': datetime.now().isoformat(),
            }
            decision = {
                'decision': 'ACTIVATE',
                'confidence': confidence,
                'bridge_fee_rate': 0.001
            }
            b_rec = bridge_system.create_bridge_record(
                tx, decision,
                vitality_score=health_score,
                confidence=confidence
            )
            self._json_response(b_rec)

        elif path == '/' or path == '/index.html':
            self.path = '/index.html'
            super().do_GET()
        else:
            super().do_GET()

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        if '/api/' in str(args[0]):
            print(f"  [API] {args[0]}")


# ── Main ──────────────────────────────────────────────────────────────
def main():
    port = 8080
    server = HTTPServer(('0.0.0.0', port), PISIHandler)
    print("=" * 70)
    print("  PISI Settlement Intelligence Console - Backend Server")
    print("  Track 3: AI Revenue Recovery | Razorpay AI Buildathon 2026")
    print("=" * 70)
    print(f"\n  Dashboard:  http://localhost:{port}")
    print(f"  API Base:   http://localhost:{port}/api/")
    print()
    print("  API Endpoints:")
    print("    GET /api/health/all          All bank vitality scores")
    print("    GET /api/health/bank?bank=X  Single bank evaluation")
    print("    GET /api/scenario/sbi        Run SBI benchmark scenario")
    print("    GET /api/batch_eval          Run 100-incident batch eval")
    print("    GET /api/metrics             Engine dashboard metrics")
    print("    GET /api/bridge/create       Create a live bridge record")
    print()
    print("  Press Ctrl+C to stop.\n")

    # Auto-open browser
    threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{port}')).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()


if __name__ == '__main__':
    main()
