"""
Bank Vitality Engine — 5-Dimension Health Scoring
Uses Razorpay error codes to compute real-time bank health.
Track 3: AI Revenue Recovery
"""
import json
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

class BankVitalityEngine:
    def __init__(self):
        self.banks = ['HDFC', 'ICICI', 'SBI', 'AXIS', 'KOTAK', 'PNB']
        self.error_buffer = defaultdict(list)  # bank -> list of error events
        self.settlement_buffer = defaultdict(list)  # bank -> list of settlement times
        self.health_history = defaultdict(list)  # bank -> list of health scores

        # Maintenance windows (from RBI/bank schedules)
        self.maintenance_windows = {
            'SBI': [(2, 4), (14, 15)],      # 2-4 AM, 2-3 PM
            'HDFC': [(2, 4)],
            'ICICI': [(1, 3)],
            'AXIS': [(3, 5)],
            'KOTAK': [(1, 2)],
            'PNB': [(9, 11)],
        }

    def ingest_error(self, bank_code, error_type, timestamp, amount=0):
        """Ingest a single error event."""
        self.error_buffer[bank_code].append({
            'error_type': error_type,
            'timestamp': timestamp if isinstance(timestamp, datetime) else datetime.fromisoformat(timestamp),
            'amount': amount
        })

        # Keep only last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        self.error_buffer[bank_code] = [
            e for e in self.error_buffer[bank_code] 
            if e['timestamp'] > cutoff
        ]

    def ingest_settlement(self, bank_code, expected_hours, actual_hours, timestamp):
        """Ingest settlement timing data."""
        self.settlement_buffer[bank_code].append({
            'expected_hours': expected_hours,
            'actual_hours': actual_hours,
            'delay_hours': max(0, actual_hours - expected_hours),
            'timestamp': timestamp if isinstance(timestamp, datetime) else datetime.fromisoformat(timestamp)
        })

        cutoff = datetime.now() - timedelta(hours=24)
        self.settlement_buffer[bank_code] = [
            s for s in self.settlement_buffer[bank_code]
            if s['timestamp'] > cutoff
        ]

    def compute_error_vitality(self, bank_code, now):
        """Dimension 1: Error rate acceleration (30% weight)"""
        errors = self.error_buffer[bank_code]
        if not errors:
            return 100.0

        # Error rate in last 1 hour vs last 6 hours
        last_1h = [e for e in errors if e['timestamp'] > now - timedelta(hours=1)]
        last_6h = [e for e in errors if e['timestamp'] > now - timedelta(hours=6)]

        rate_1h = len(last_1h) / 1.0
        rate_6h = len(last_6h) / 6.0

        if rate_6h == 0:
            acceleration = 0
        else:
            acceleration = (rate_1h - rate_6h) / max(rate_6h, 0.1)

        # Score: higher acceleration = lower vitality
        score = max(0, 100 - (acceleration * 50) - (len(last_1h) * 5))
        return round(score, 2)

    def compute_temporal_health(self, bank_code, now):
        """Dimension 2: Time-of-day / maintenance window match (20% weight)"""
        hour = now.hour
        dow = now.weekday()

        # Check if in maintenance window
        windows = self.maintenance_windows.get(bank_code, [])
        in_maintenance = any(start <= hour <= end for start, end in windows)

        if in_maintenance:
            return 35.0  # Hard penalty during maintenance

        # Historical pattern: certain banks degrade at certain times
        time_risk = 0
        if bank_code == 'SBI' and 2 <= hour <= 4:
            time_risk = 40
        elif bank_code == 'PNB' and 9 <= hour <= 11:
            time_risk = 35
        elif bank_code == 'ICICI' and 14 <= hour <= 15:
            time_risk = 20
        elif dow in [1, 2]:  # Tue-Wed higher risk
            time_risk += 10

        score = max(0, 100 - time_risk)
        return round(score, 2)

    def compute_settlement_velocity(self, bank_code, now):
        """Dimension 3: Settlement speed degradation (20% weight)"""
        settlements = self.settlement_buffer[bank_code]
        if not settlements:
            return 95.0

        # Average delay in last 6 hours
        recent = [s for s in settlements if s['timestamp'] > now - timedelta(hours=6)]
        if not recent:
            return 95.0

        avg_delay = np.mean([s['delay_hours'] for s in recent])

        # Score: 0 delay = 100, 12+ hours delay = 0
        score = max(0, 100 - (avg_delay * 8))
        return round(score, 2)

    def compute_network_resilience(self, bank_code, now):
        """Dimension 4: Peer bank correlation (15% weight)"""
        # If multiple banks failing simultaneously = network issue, not bank-specific
        all_errors = []
        for bank in self.banks:
            recent = [e for e in self.error_buffer[bank] 
                     if e['timestamp'] > now - timedelta(hours=1)]
            all_errors.extend([(bank, e) for e in recent])

        if len(all_errors) < 3:
            return 90.0

        # Count how many unique banks have errors in last hour
        failing_banks = len(set(bank for bank, _ in all_errors))

        if failing_banks >= 3:
            # Network-wide issue — individual bank resilience doesn't matter
            return 50.0
        elif failing_banks == 2:
            return 70.0
        else:
            return 90.0

    def compute_predictive_marker(self, bank_code, now):
        """Dimension 5: Leading indicators (15% weight)"""
        # Look for gateway errors preceding bank errors
        errors = self.error_buffer[bank_code]

        gateway_errors = [e for e in errors if 'gateway' in e['error_type']]
        bank_errors = [e for e in errors if 'bank_technical' in e['error_type']]

        # If gateway errors spiking in last 30 min but no bank errors yet = prediction
        last_30min = now - timedelta(minutes=30)
        recent_gateway = [e for e in gateway_errors if e['timestamp'] > last_30min]
        recent_bank = [e for e in bank_errors if e['timestamp'] > last_30min]

        if len(recent_gateway) >= 2 and len(recent_bank) == 0:
            # Leading indicator: gateway degrading before bank fails
            return 45.0
        elif len(recent_bank) >= 1:
            # Bank already failing
            return 25.0
        else:
            return 85.0

    def compute_composite_health(self, bank_code, now=None):
        """Compute 5-dimension composite health score (0-100)."""
        if now is None:
            now = datetime.now()

        e = self.compute_error_vitality(bank_code, now)
        t = self.compute_temporal_health(bank_code, now)
        s = self.compute_settlement_velocity(bank_code, now)
        n = self.compute_network_resilience(bank_code, now)
        p = self.compute_predictive_marker(bank_code, now)

        # Weighted composite
        composite = (
            e * 0.30 +
            t * 0.20 +
            s * 0.20 +
            n * 0.15 +
            p * 0.15
        )

        # Determine status
        if composite >= 80:
            status = 'healthy'
            emoji = '💚'
        elif composite >= 60:
            status = 'degraded'
            emoji = '🟡'
        elif composite >= 40:
            status = 'at_risk'
            emoji = '🟠'
        else:
            status = 'critical'
            emoji = '🔴'

        result = {
            'bank_code': bank_code,
            'timestamp': now.isoformat(),
            'composite_health': round(composite, 2),
            'status': status,
            'emoji': emoji,
            'dimensions': {
                'error_vitality': e,
                'temporal_health': t,
                'settlement_velocity': s,
                'network_resilience': n,
                'predictive_marker': p
            }
        }

        self.health_history[bank_code].append(result)
        return result

    def get_all_bank_health(self, now=None):
        """Get health scores for all banks."""
        if now is None:
            now = datetime.now()
        return {bank: self.compute_composite_health(bank, now) for bank in self.banks}

    def forecast_health(self, bank_code, future_time):
        """Simple linear forecast based on recent trend."""
        history = self.health_history[bank_code]
        if len(history) < 3:
            return 70.0

        # Use last 3 data points
        recent = history[-3:]
        scores = [h['composite_health'] for h in recent]
        times = [datetime.fromisoformat(h['timestamp']) for h in recent]

        # Simple trend: if declining, project forward
        if scores[-1] < scores[0]:
            decline_rate = (scores[0] - scores[-1]) / max(1, (times[-1] - times[0]).total_seconds() / 3600)
            hours_ahead = (future_time - times[-1]).total_seconds() / 3600
            forecast = scores[-1] - (decline_rate * hours_ahead)
            return max(0, min(100, forecast))
        else:
            return scores[-1]

if __name__ == "__main__":
    engine = BankVitalityEngine()

    # Simulate some errors
    now = datetime(2026, 8, 22, 10, 0, 0)
    engine.ingest_error('SBI', 'gateway_technical_error', now - timedelta(minutes=45))
    engine.ingest_error('SBI', 'gateway_technical_error', now - timedelta(minutes=30))
    engine.ingest_error('SBI', 'bank_technical_error', now - timedelta(minutes=15))
    engine.ingest_settlement('SBI', 48, 72, now - timedelta(hours=2))

    health = engine.compute_composite_health('SBI', now)
    print(f"SBI Health: {health['composite_health']}/100 {health['emoji']}")
    print(f"Status: {health['status']}")
    print(f"Dimensions: {health['dimensions']}")
