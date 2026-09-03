"""
PISI Synthetic Data Generator — Track 3: AI Revenue Recovery
Generates 200+ realistic transactions with settlement degradation patterns.
For measured money recovered across a batch.
"""
import random
import json
from datetime import datetime, timedelta
import numpy as np

class SyntheticDataGenerator:
    def __init__(self, seed=42):
        random.seed(seed)
        np.random.seed(seed)
        self.banks = {
            'HDFC': {'base_health': 92, 'maintenance_windows': [(2, 4)], 'failure_spike_prob': 0.05},
            'ICICI': {'base_health': 88, 'maintenance_windows': [(1, 3)], 'failure_spike_prob': 0.06},
            'SBI': {'base_health': 78, 'maintenance_windows': [(2, 4), (14, 15)], 'failure_spike_prob': 0.12},
            'AXIS': {'base_health': 82, 'maintenance_windows': [(3, 5)], 'failure_spike_prob': 0.08},
            'KOTAK': {'base_health': 85, 'maintenance_windows': [(1, 2)], 'failure_spike_prob': 0.07},
            'PNB': {'base_health': 70, 'maintenance_windows': [(9, 11)], 'failure_spike_prob': 0.15},
        }
        self.merchants = [f"M-{1000+i}" for i in range(50)]
        self.methods = ['upi', 'card', 'netbanking', 'wallet']

    def generate_transaction(self, tx_id, timestamp):
        bank = random.choice(list(self.banks.keys()))
        merchant = random.choice(self.merchants)
        method = random.choice(self.methods)
        amount = int(np.random.lognormal(7.8, 0.6))
        amount = max(100, min(amount, 50000))

        hour = timestamp.hour
        dow = timestamp.weekday()
        bank_config = self.banks[bank]

        in_maintenance = any(start <= hour <= end for start, end in bank_config['maintenance_windows'])
        settlement_risk_prob = bank_config['failure_spike_prob']
        if in_maintenance:
            settlement_risk_prob *= 4
        if dow in [1, 2]:
            settlement_risk_prob *= 1.3

        has_settlement_risk = random.random() < settlement_risk_prob

        if has_settlement_risk:
            status = 'captured'
            captured_at = timestamp + timedelta(minutes=random.randint(1, 5))
            settlement_delay_hours = random.randint(24, 72)
            settlement_initiated_at = captured_at + timedelta(hours=settlement_delay_hours)
            settlement_completed_at = settlement_initiated_at + timedelta(minutes=random.randint(30, 120))
            expected_settlement_hours = 48
            actual_settlement_hours = (settlement_completed_at - captured_at).total_seconds() / 3600
        else:
            status = 'captured'
            captured_at = timestamp + timedelta(minutes=random.randint(1, 5))
            settlement_initiated_at = captured_at + timedelta(hours=random.randint(36, 52))
            settlement_completed_at = settlement_initiated_at + timedelta(minutes=random.randint(10, 60))
            expected_settlement_hours = 48
            actual_settlement_hours = (settlement_completed_at - captured_at).total_seconds() / 3600

        return {
            'tx_id': f"RZP-tx-{tx_id:05d}",
            'order_id': f"RZP-ord-{tx_id:05d}",
            'amount': amount,
            'method': method,
            'customer_bank': bank,
            'merchant_bank': random.choice([b for b in self.banks.keys() if b != bank]),
            'merchant_id': merchant,
            'timestamp': timestamp.isoformat(),
            'status': status,
            'captured_at': captured_at.isoformat() if captured_at else None,
            'settlement_initiated_at': settlement_initiated_at.isoformat() if settlement_initiated_at else None,
            'settlement_completed_at': settlement_completed_at.isoformat() if settlement_completed_at else None,
            'expected_settlement_hours': expected_settlement_hours,
            'actual_settlement_hours': round(actual_settlement_hours, 2),
            'has_settlement_risk': has_settlement_risk,
            'settlement_delay_hours': max(0, actual_settlement_hours - expected_settlement_hours) if has_settlement_risk else 0,
        }

    def generate_batch(self, count=200, start_time=None):
        if start_time is None:
            start_time = datetime(2026, 8, 22, 0, 0, 0)
        transactions = []
        for i in range(count):
            hour_bias = random.choices(range(24), weights=[1,1,1,1,1,2,3,5,7,8,9,9,8,7,6,5,5,6,7,8,8,6,4,2])[0]
            minute = random.randint(0, 59)
            tx_time = start_time + timedelta(hours=hour_bias, minute=minute)
            tx = self.generate_transaction(i+1, tx_time)
            transactions.append(tx)
        return transactions

    def save_batch(self, transactions, filepath):
        with open(filepath, 'w') as f:
            json.dump(transactions, f, indent=2)
        return filepath

if __name__ == "__main__":
    gen = SyntheticDataGenerator()
    batch = gen.generate_batch(200)
    gen.save_batch(batch, "synthetic_transactions.json")
    risky = [t for t in batch if t['has_settlement_risk']]
    print(f"Generated {len(batch)} transactions")
    print(f"Settlement-risk transactions: {len(risky)} ({len(risky)/len(batch)*100:.1f}%)")
    print(f"Total amount at risk: ₹{sum(t['amount'] for t in risky):,}")
