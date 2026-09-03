"""
Error Stream Ingestor — Layer 1
Consumes webhooks for failed payments and telemetry error codes (feeds Leg B and vitality scoring).
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

class ErrorStreamIngestor:
    def __init__(self):
        # bank_code -> list of error event dicts
        self.error_buffer = defaultdict(list)

    def ingest_error_event(self, bank_code, error_type, timestamp=None, amount=0.0, error_source="issuing_bank", error_code="bank_technical_error"):
        """
        Ingests payment.failed or telemetry error event.
        Args:
            bank_code: str (e.g., 'SBI')
            error_type: str ('gateway_technical_error', 'bank_technical_error', 'payment_timed_out', etc.)
            timestamp: datetime or ISO string
            amount: float
            error_source: 'issuing_bank' (affects authorization), 'acquiring_gateway', etc.
            error_code: standard error code
        """
        if timestamp is None:
            ts = datetime.now()
        elif isinstance(timestamp, str):
            ts = datetime.fromisoformat(timestamp)
        else:
            ts = timestamp

        event = {
            'bank_code': bank_code,
            'error_type': error_type,
            'error_code': error_code,
            'error_source': error_source,
            'amount': float(amount),
            'timestamp': ts
        }

        self.error_buffer[bank_code].append(event)
        self._trim_buffer(bank_code)
        return event

    def _trim_buffer(self, bank_code):
        """Keep rolling 24-hour buffer relative to newest event."""
        if not self.error_buffer[bank_code]:
            return
        latest = max(e['timestamp'] for e in self.error_buffer[bank_code])
        cutoff = latest - timedelta(hours=24)
        self.error_buffer[bank_code] = [
            e for e in self.error_buffer[bank_code] if e['timestamp'] > cutoff
        ]

    def get_errors_in_window(self, bank_code, start_time, end_time):
        """Fetch errors for a bank within a specific time window."""
        return [
            e for e in self.error_buffer[bank_code]
            if start_time <= e['timestamp'] <= end_time
        ]

    def get_recent_errors(self, bank_code, duration_minutes=60, now=None):
        """Get errors in the last N minutes."""
        if now is None:
            now = datetime.now()
        start = now - timedelta(minutes=duration_minutes)
        return self.get_errors_in_window(bank_code, start, now)

    def clear(self):
        self.error_buffer.clear()
