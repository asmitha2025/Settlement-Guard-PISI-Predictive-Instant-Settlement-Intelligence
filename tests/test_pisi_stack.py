"""
Unit Test Suite for PISI (Predictive Instant Settlement Intelligence)
"""
import unittest
import sys
import os
from datetime import datetime, timedelta

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


class TestBankVitalityEngine(unittest.TestCase):
    def setUp(self):
        self.error_stream = ErrorStreamIngestor()
        self.vitality = BankVitalityEngine(error_stream=self.error_stream)
        self.sim_time = datetime(2026, 8, 22, 2, 30, 0)

    def test_healthy_bank_score(self):
        score = self.vitality.compute_composite_health('SBI', self.sim_time)
        self.assertGreaterEqual(score['composite_health'], 80.0)
        self.assertEqual(score['status'], 'healthy')

    def test_degraded_bank_score(self):
        for _ in range(15):
            self.vitality.ingest_error('HDFC', 'CBS_TIMEOUT', self.sim_time, 2499.0, 'gateway')
        score = self.vitality.compute_composite_health('HDFC', self.sim_time)
        self.assertLess(score['composite_health'], 90.0)


class TestPISIDecisionEngine(unittest.TestCase):
    def setUp(self):
        self.error_stream = ErrorStreamIngestor()
        self.vitality = BankVitalityEngine(error_stream=self.error_stream)
        self.classifier = DowntimeClassifier()
        self.duration_predictor = DurationPredictor()
        self.pisi = PISIDecisionEngine(
            self.vitality, self.classifier, self.duration_predictor, corporate_capital=50_000_000.00
        )
        self.sim_time = datetime(2026, 8, 22, 2, 30, 0)

    def test_standby_decision(self):
        captures = [
            {'tx_id': 'tx_1', 'order_id': 'ord_1', 'amount': 1000.0,
             'settlement_path_bank': 'ICICI', 'merchant_bank': 'HDFC', 'captured_at': self.sim_time.isoformat()}
        ]
        decision = self.pisi.evaluate_leg_a('ICICI', captures, self.sim_time)
        self.assertEqual(decision['decision'], 'STANDBY')

    def test_activate_decision(self):
        gen = SyntheticDataGenerator(seed=42)
        error_events = gen.generate_sbi_outage_error_stream(start_time=self.sim_time)
        for e in error_events:
            self.vitality.ingest_error(e['bank_code'], e['error_type'], e['timestamp'], e['amount'], e['error_source'])
        
        captures = gen.generate_reconciled_sbi_scenario(count=10, avg_amount=2000.0, start_time=self.sim_time)
        decision = self.pisi.evaluate_leg_a('SBI', captures, self.sim_time)
        self.assertIn(decision['decision'], ['ACTIVATE', 'MONITOR'])


class TestBridgeKeyIDSystem(unittest.TestCase):
    def setUp(self):
        self.bridge_system = BridgeKeyIDSystem()

    def test_bridge_record_creation_and_closing(self):
        tx = {
            'tx_id': 'tx_test_001',
            'order_id': 'ord_test_001',
            'amount': 5000.0,
            'settlement_path_bank': 'SBI',
            'merchant_bank': 'HDFC'
        }
        decision = {
            'decision_id': 'dec_test_001',
            'decision': 'ACTIVATE',
            'confidence': 0.95,
            'bridge_fee_rate': 0.001
        }
        record = self.bridge_system.create_bridge_record(tx, decision, vitality_score=30.0, confidence=0.95)
        self.assertIn('BRIDGE-SBI-', record['bridge_id'])
        self.assertEqual(len(record['audit_hash_sha256']), 64)
        self.assertEqual(record['status'], 'ACTIVE')

        closed_record = self.bridge_system.close_bridge_record(record['bridge_id'], standard_settlement_arrived=True)
        self.assertEqual(closed_record['status'], 'CLOSED')


if __name__ == '__main__':
    unittest.main()
