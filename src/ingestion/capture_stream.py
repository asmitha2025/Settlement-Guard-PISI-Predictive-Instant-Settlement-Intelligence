"""
Capture Stream Ingestor — Layer 1
Consumes webhooks for captured, successful payments pending standard settlement (Leg A eligibility pool).
Track 3: AI Revenue Recovery
"""
import sys
from datetime import datetime, timedelta
from collections import defaultdict

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

class CaptureStreamIngestor:
    def __init__(self):
        # settlement_bank -> list of captured transactions pending settlement
        self.pending_captures = defaultdict(list)
        self.settled_captures = defaultdict(list)

    def ingest_captured_payment(self, tx_id, order_id, amount, settlement_path_bank, merchant_bank, merchant_id, timestamp=None, method="upi"):
        """
        Ingests order.paid / payment.captured event.
        These are transactions that ALREADY SUCCEEDED and are pending settlement.
        """
        if timestamp is None:
            ts = datetime.now()
        elif isinstance(timestamp, str):
            ts = datetime.fromisoformat(timestamp)
        else:
            ts = timestamp

        tx = {
            'tx_id': tx_id,
            'order_id': order_id,
            'amount': float(amount),
            'settlement_path_bank': settlement_path_bank,
            'merchant_bank': merchant_bank,
            'merchant_id': merchant_id,
            'method': method,
            'status': 'captured_pending_settlement',
            'captured_at': ts,
            'expected_settlement_hours': 48,
            'pisi_protected': False
        }

        self.pending_captures[settlement_path_bank].append(tx)
        return tx

    def get_pending_captures(self, settlement_path_bank):
        """Retrieve all currently pending captured payments for a settlement path bank."""
        return [
            tx for tx in self.pending_captures[settlement_path_bank]
            if tx['status'] == 'captured_pending_settlement' and not tx['pisi_protected']
        ]

    def mark_protected(self, tx_id, settlement_path_bank):
        """Mark transaction as advanced via Instant Settlement."""
        for tx in self.pending_captures[settlement_path_bank]:
            if tx['tx_id'] == tx_id:
                tx['pisi_protected'] = True
                tx['status'] = 'instant_settlement_advanced'
                return tx
        return None

    def mark_standard_settled(self, tx_id, settlement_path_bank):
        """Mark transaction as settled via standard T+1/T+2 cycle."""
        for i, tx in enumerate(self.pending_captures[settlement_path_bank]):
            if tx['tx_id'] == tx_id:
                tx['status'] = 'settled_standard'
                self.settled_captures[settlement_path_bank].append(tx)
                del self.pending_captures[settlement_path_bank][i]
                return tx
        return None

    def clear(self):
        self.pending_captures.clear()
        self.settled_captures.clear()
