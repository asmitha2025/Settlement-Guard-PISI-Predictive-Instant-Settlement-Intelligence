"""
Bridge Key ID System — Immutable Audit Trail for PISI Protections.
Every protected transaction gets a verifiable, SHA-256 hashed audit record.
Track 3: AI Revenue Recovery
"""
import json
import hashlib
from datetime import datetime

class BridgeKeyIDSystem:
    def __init__(self):
        self.ledger = []
        self.bridge_records = {}

    def create_bridge_record(self, protection_data, transaction_data, decision_data):
        """
        Create an immutable Bridge Key ID record.

        Args:
            protection_data: From PISIDecisionEngine.activate_protection()
            transaction_data: Original transaction
            decision_data: Decision result from evaluate_transaction()
        """
        bridge_id = protection_data['bridge_key_id']

        record = {
            'bridge_key_id': bridge_id,
            'original_tx_id': protection_data['tx_id'],
            'order_id': transaction_data.get('order_id', 'N/A'),
            'acquiring_bank': protection_data['acquiring_bank'],
            'merchant_id': protection_data['merchant_id'],
            'amount': protection_data['amount'],
            'predictive_fee': protection_data['predictive_fee'],
            'merchant_credited': round(protection_data['amount'] - protection_data['predictive_fee'], 2),
            'prediction_confidence': decision_data['confidence'],
            'bank_health_at_activation': decision_data['bank_health'],
            'bank_status_at_activation': decision_data['bank_status'],
            'dimensions_at_activation': decision_data['dimensions'],
            'activated_at': protection_data['activated_at'],
            'corporate_capital_deployed': protection_data['capital_deployed'],
            'status': 'ACTIVE',
            'audit_entries': []
        }

        # Generate creation audit entry
        creation_entry = self._create_audit_entry(
            bridge_id=bridge_id,
            entry_type='CREATION',
            description=f"PISI protection activated for {protection_data['tx_id']}. "
                       f"Bank {protection_data['acquiring_bank']} health: {decision_data['bank_health']}/100. "
                       f"Confidence: {decision_data['confidence']:.0%}. "
                       f"Predictive fee: ₹{protection_data['predictive_fee']:.2f}",
            amount_debit=protection_data['capital_deployed'],
            amount_credit=0,
            account='CORPORATE_CAPITAL_POOL'
        )
        record['audit_entries'].append(creation_entry)

        # Generate receivable entry
        receivable_entry = self._create_audit_entry(
            bridge_id=bridge_id,
            entry_type='RECEIVABLE',
            description=f"Bridge receivable created. Expecting standard settlement from {protection_data['acquiring_bank']}.",
            amount_debit=0,
            amount_credit=protection_data['amount'],
            account=f"RECEIVABLE_{protection_data['acquiring_bank']}"
        )
        record['audit_entries'].append(receivable_entry)

        # Compute overall audit hash
        record['creation_hash'] = self._compute_record_hash(record)

        self.bridge_records[bridge_id] = record
        return record

    def close_bridge_record(self, bridge_id, standard_settlement_arrived=True, 
                           settlement_timestamp=None, actual_delay_hours=None):
        """Close bridge when standard settlement arrives."""
        if bridge_id not in self.bridge_records:
            return None

        record = self.bridge_records[bridge_id]
        record['status'] = 'CLOSED'
        record['closed_at'] = settlement_timestamp or datetime.now().isoformat()
        record['standard_settlement_arrived'] = standard_settlement_arrived
        record['actual_delay_hours'] = actual_delay_hours

        # Capital replenishment entry
        replenish_entry = self._create_audit_entry(
            bridge_id=bridge_id,
            entry_type='REPLENISHMENT',
            description=f"Corporate capital replenished from {record['acquiring_bank']} standard settlement. "
                       f"Bridge closed. Fee earned: ₹{record['predictive_fee']:.2f}",
            amount_debit=0,
            amount_credit=record['corporate_capital_deployed'],
            account='CORPORATE_CAPITAL_POOL'
        )
        record['audit_entries'].append(replenish_entry)

        # Fee revenue entry
        fee_entry = self._create_audit_entry(
            bridge_id=bridge_id,
            entry_type='FEE_REVENUE',
            description=f"Predictive Instant Settlement fee recognized as revenue.",
            amount_debit=0,
            amount_credit=record['predictive_fee'],
            account='PISI_FEE_REVENUE'
        )
        record['audit_entries'].append(fee_entry)

        # Compute closure hash
        record['closure_hash'] = self._compute_record_hash(record)
        record['books_balanced'] = self._verify_double_entry(record)

        return record

    def _create_audit_entry(self, bridge_id, entry_type, description, 
                           amount_debit, amount_credit, account):
        """Create a single audit ledger entry."""
        entry = {
            'entry_id': f"{bridge_id}-{entry_type}-{datetime.now().strftime('%H%M%S')}",
            'bridge_id': bridge_id,
            'type': entry_type,
            'description': description,
            'account': account,
            'debit': amount_debit,
            'credit': amount_credit,
            'timestamp': datetime.now().isoformat(),
            'entry_hash': hashlib.sha256(
                f"{bridge_id}{entry_type}{amount_debit}{amount_credit}{datetime.now().isoformat()}".encode()
            ).hexdigest()
        }
        self.ledger.append(entry)
        return entry

    def _compute_record_hash(self, record):
        """Compute SHA-256 hash of record for immutability verification."""
        # Exclude mutable fields from hash
        hash_data = {
            'bridge_key_id': record['bridge_key_id'],
            'original_tx_id': record['original_tx_id'],
            'amount': record['amount'],
            'predictive_fee': record['predictive_fee'],
            'activated_at': record['activated_at'],
            'audit_entries': record['audit_entries']
        }
        return hashlib.sha256(json.dumps(hash_data, sort_keys=True).encode()).hexdigest()

    def _verify_double_entry(self, record):
        """Verify that debits equal credits for this bridge."""
        total_debit = sum(e['debit'] for e in record['audit_entries'])
        total_credit = sum(e['credit'] for e in record['audit_entries'])
        return abs(total_debit - total_credit) < 0.01

    def get_bridge_statement(self, bridge_id):
        """Generate full statement for a Bridge Key ID."""
        if bridge_id not in self.bridge_records:
            return None

        record = self.bridge_records[bridge_id]

        return {
            'bridge_key_id': bridge_id,
            'original_tx_id': record['original_tx_id'],
            'order_id': record['order_id'],
            'acquiring_bank': record['acquiring_bank'],
            'merchant_id': record['merchant_id'],
            'principal': record['amount'],
            'predictive_fee': record['predictive_fee'],
            'merchant_credited': record['merchant_credited'],
            'prediction_confidence': record['prediction_confidence'],
            'bank_health_at_activation': record['bank_health_at_activation'],
            'activated_at': record['activated_at'],
            'closed_at': record.get('closed_at'),
            'status': record['status'],
            'corporate_capital_deployed': record['corporate_capital_deployed'],
            'audit_entries': record['audit_entries'],
            'creation_hash': record['creation_hash'],
            'closure_hash': record.get('closure_hash'),
            'books_balanced': record.get('books_balanced', False)
        }

    def get_all_statements(self):
        """Get all bridge statements."""
        return [self.get_bridge_statement(bid) for bid in self.bridge_records.keys()]

if __name__ == "__main__":
    bridge_system = BridgeKeyIDSystem()

    # Example
    protection = {
        'tx_id': 'RZP-tx-00001',
        'acquiring_bank': 'AXIS',
        'merchant_id': 'M-4421',
        'amount': 2500,
        'predictive_fee': 2.50,
        'activated_at': datetime.now().isoformat(),
        'capital_deployed': 2500,
        'bridge_key_id': 'PISI-AXIS-20260822103000-a1b2c3d4e5f67890'
    }

    tx = {'order_id': 'RZP-ord-00001', 'merchant_id': 'M-4421'}
    decision = {'confidence': 0.91, 'bank_health': 34, 'bank_status': 'critical', 'dimensions': {}}

    record = bridge_system.create_bridge_record(protection, tx, decision)
    print(f"Bridge Key ID: {record['bridge_key_id']}")
    print(f"Creation Hash: {record['creation_hash'][:32]}... (SHA-256, 64 chars)")
    print(f"Books Balanced: {record['books_balanced']}")
