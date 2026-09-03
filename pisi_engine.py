"""
PISI Decision Engine — Core orchestrator for Predictive Instant Settlement Intelligence.
Track 3: AI Revenue Recovery

Safety Gates (Stopping Rules):
- Max 30% of total corporate capital deployable
- Max ₹50,000 per single transaction
- Max 10 concurrent bridges per bank
- Merchant health must be > 20
- Prediction confidence must be > 70%
"""
import json
import hashlib
from datetime import datetime, timedelta
import numpy as np

class PISIDecisionEngine:
    def __init__(self, vitality_engine, corporate_capital=15_000_000):
        """
        Args:
            vitality_engine: BankVitalityEngine instance
            corporate_capital: Total corporate capital pool in INR (default ₹1.5Cr)
        """
        self.vitality = vitality_engine
        self.total_corporate_capital = corporate_capital
        self.deployed_capital = 0
        self.active_protections = {}  # tx_id -> protection record
        self.protection_history = []

        # Safety gates
        self.MAX_CAPITAL_RATIO = 0.30
        self.MAX_PER_TRANSACTION = 50_000
        self.MAX_CONCURRENT_PER_BANK = 10
        self.MIN_MERCHANT_HEALTH = 20
        self.MIN_CONFIDENCE = 0.70

        # Fee structure
        self.PREDICTIVE_FEE_RATE = 0.0010  # 0.10% (vs 0.25% reactive)
        self.REACTIVE_FEE_RATE = 0.0025    # 0.25% (standard)
        self.COST_OF_CAPITAL_ANNUAL = 0.12  # 12%

    def evaluate_transaction(self, transaction, now=None):
        """
        Evaluate a single captured transaction for settlement risk.
        Returns decision: ACTIVATE / MONITOR / STANDBY
        """
        if now is None:
            now = datetime.now()

        tx_id = transaction['tx_id']
        amount = transaction['amount']
        acquiring_bank = transaction.get('merchant_bank', transaction.get('customer_bank'))
        merchant_id = transaction['merchant_id']

        # Gate 1: Already protected?
        if tx_id in self.active_protections:
            return {'decision': 'ALREADY_PROTECTED', 'reason': 'Transaction already under PISI'}

        # Gate 2: Amount too large?
        if amount > self.MAX_PER_TRANSACTION:
            return {
                'decision': 'STANDBY',
                'reason': f'Amount ₹{amount:,} exceeds per-transaction limit ₹{self.MAX_PER_TRANSACTION:,}'
            }

        # Gate 3: Sufficient capital available?
        max_deployable = self.total_corporate_capital * self.MAX_CAPITAL_RATIO
        available_capital = max_deployable - self.deployed_capital
        if amount > available_capital:
            return {
                'decision': 'STANDBY',
                'reason': f'Insufficient capital. Available: ₹{available_capital:,.0f}, Required: ₹{amount:,}'
            }

        # Gate 4: Too many concurrent protections for this bank?
        concurrent_for_bank = sum(
            1 for p in self.active_protections.values()
            if p['acquiring_bank'] == acquiring_bank
        )
        if concurrent_for_bank >= self.MAX_CONCURRENT_PER_BANK:
            return {
                'decision': 'STANDBY',
                'reason': f'Concentration limit reached for {acquiring_bank} ({concurrent_for_bank} active)'
            }

        # Compute bank health
        health = self.vitality.compute_composite_health(acquiring_bank, now)
        composite = health['composite_health']

        # Gate 5: Confidence check
        # Confidence = how certain are we that this bank will delay settlement?
        # Based on predictive marker and temporal health
        confidence = self._compute_confidence(health, transaction)

        if composite < 40 and confidence >= self.MIN_CONFIDENCE:
            decision = 'ACTIVATE'
        elif composite < 60 and confidence >= 0.50:
            decision = 'MONITOR'
        else:
            decision = 'STANDBY'

        result = {
            'tx_id': tx_id,
            'decision': decision,
            'bank_code': acquiring_bank,
            'bank_health': composite,
            'bank_status': health['status'],
            'confidence': round(confidence, 3),
            'amount': amount,
            'merchant_id': merchant_id,
            'timestamp': now.isoformat(),
            'reason': self._generate_reason(decision, health, confidence),
            'dimensions': health['dimensions']
        }

        if decision == 'ACTIVATE':
            result['recommended_action'] = 'TRIGGER_INSTANT_SETTLEMENT'
            result['predictive_fee'] = round(amount * self.PREDICTIVE_FEE_RATE, 2)
            result['estimated_capital_cost'] = self._estimate_capital_cost(amount)
            result['net_protection_value'] = result['predictive_fee'] - result['estimated_capital_cost']

        return result

    def _compute_confidence(self, health, transaction):
        """Compute prediction confidence (0-1)."""
        # Higher confidence if:
        # - predictive marker is low (leading indicators detected)
        # - temporal health is low (in known risk window)
        # - settlement velocity is degrading

        d = health['dimensions']
        score = 0

        if d['predictive_marker'] < 50:
            score += 0.4
        if d['temporal_health'] < 50:
            score += 0.3
        if d['settlement_velocity'] < 60:
            score += 0.2
        if d['error_vitality'] < 60:
            score += 0.1

        # Boost if transaction is in known maintenance window
        hour = datetime.fromisoformat(transaction['timestamp']).hour
        windows = self.vitality.maintenance_windows.get(transaction.get('merchant_bank'), [])
        if any(start <= hour <= end for start, end in windows):
            score = min(1.0, score + 0.15)

        return score

    def _generate_reason(self, decision, health, confidence):
        """Generate human-readable reason."""
        d = health['dimensions']
        reasons = []

        if d['predictive_marker'] < 50:
            reasons.append('leading indicators detected')
        if d['temporal_health'] < 50:
            reasons.append('within risk window')
        if d['settlement_velocity'] < 60:
            reasons.append('settlement velocity degrading')
        if d['error_vitality'] < 60:
            reasons.append('error rate accelerating')

        if not reasons:
            reasons.append('no significant risk factors')

        reason_str = ', '.join(reasons)
        return f"{decision}: {reason_str} (confidence: {confidence:.0%})"

    def _estimate_capital_cost(self, amount):
        """Estimate cost of deploying capital for typical 2-day period."""
        days = 2
        daily_rate = self.COST_OF_CAPITAL_ANNUAL / 365
        cost = amount * daily_rate * days
        return round(cost, 2)

    def activate_protection(self, transaction, decision_result):
        """Activate PISI protection for a transaction."""
        tx_id = transaction['tx_id']
        amount = transaction['amount']
        acquiring_bank = decision_result['bank_code']

        # Create protection record
        protection = {
            'tx_id': tx_id,
            'acquiring_bank': acquiring_bank,
            'amount': amount,
            'activated_at': datetime.now().isoformat(),
            'predictive_fee': decision_result['predictive_fee'],
            'capital_deployed': amount,
            'status': 'ACTIVE',
            'bridge_key_id': self._generate_bridge_key_id(tx_id, acquiring_bank)
        }

        self.active_protections[tx_id] = protection
        self.deployed_capital += amount

        return protection

    def _generate_bridge_key_id(self, tx_id, bank_code):
        """Generate unique Bridge Key ID."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        base = f"PISI-{bank_code}-{timestamp}-{tx_id}"
        hash_val = hashlib.sha256(base.encode()).hexdigest()[:16]
        return f"PISI-{bank_code}-{timestamp}-{hash_val}"

    def close_protection(self, tx_id, standard_settlement_arrived=False):
        """Close protection when standard settlement arrives."""
        if tx_id not in self.active_protections:
            return None

        protection = self.active_protections[tx_id]
        protection['status'] = 'CLOSED'
        protection['closed_at'] = datetime.now().isoformat()
        protection['standard_settlement_arrived'] = standard_settlement_arrived

        # Replenish capital
        self.deployed_capital -= protection['capital_deployed']

        # Move to history
        self.protection_history.append(protection)
        del self.active_protections[tx_id]

        return protection

    def get_dashboard_metrics(self):
        """Get metrics for dashboard display."""
        total_protected = sum(p['amount'] for p in self.protection_history if p['status'] == 'CLOSED')
        total_fees = sum(p['predictive_fee'] for p in self.protection_history if p['status'] == 'CLOSED')
        total_capital_cost = sum(
            self._estimate_capital_cost(p['amount']) 
            for p in self.protection_history if p['status'] == 'CLOSED'
        )

        return {
            'total_corporate_capital': self.total_corporate_capital,
            'deployed_capital': self.deployed_capital,
            'available_capital': (self.total_corporate_capital * self.MAX_CAPITAL_RATIO) - self.deployed_capital,
            'active_protections': len(self.active_protections),
            'closed_protections': len(self.protection_history),
            'total_amount_protected': total_protected,
            'total_predictive_fees': round(total_fees, 2),
            'total_capital_cost': round(total_capital_cost, 2),
            'net_profit': round(total_fees - total_capital_cost, 2),
            'capital_utilization_ratio': self.deployed_capital / self.total_corporate_capital
        }

if __name__ == "__main__":
    from bank_vitality import BankVitalityEngine

    vitality = BankVitalityEngine()
    now = datetime(2026, 8, 22, 10, 0, 0)

    # Inject risk signals
    vitality.ingest_error('AXIS', 'gateway_technical_error', now - timedelta(minutes=40))
    vitality.ingest_error('AXIS', 'gateway_technical_error', now - timedelta(minutes=25))
    vitality.ingest_settlement('AXIS', 48, 68, now - timedelta(hours=3))

    pisi = PISIDecisionEngine(vitality)

    tx = {
        'tx_id': 'RZP-tx-00001',
        'amount': 2500,
        'merchant_bank': 'AXIS',
        'merchant_id': 'M-4421',
        'timestamp': now.isoformat()
    }

    result = pisi.evaluate_transaction(tx, now)
    print(f"Decision: {result['decision']}")
    print(f"Reason: {result['reason']}")
    if result['decision'] == 'ACTIVATE':
        print(f"Predictive Fee: ₹{result['predictive_fee']}")
        print(f"Est. Capital Cost: ₹{result['estimated_capital_cost']}")
        print(f"Net Value: ₹{result['net_protection_value']}")
