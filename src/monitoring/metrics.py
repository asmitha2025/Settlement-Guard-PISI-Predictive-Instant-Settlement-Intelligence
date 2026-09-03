"""
Monitoring & Evaluation Metrics — Layer 6 · v2.0
Computes Precision, Recall, F1, ROI per bridge, False-Positive Cost, and Drift Status.
Track 3: AI Revenue Recovery
"""
import sys
import numpy as np

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

class MetricsCollector:
    def __init__(self):
        self.predictions = []  # list of (predicted_downtime: bool, actual_downtime: bool, volume: float)

    def record_incident_result(self, predicted, actual, volume=0.0, fee_earned=0.0, capital_cost=0.0):
        self.predictions.append({
            'predicted': bool(predicted),
            'actual': bool(actual),
            'volume': float(volume),
            'fee_earned': float(fee_earned),
            'capital_cost': float(capital_cost)
        })

    def compute_confusion_matrix(self):
        tp = sum(1 for p in self.predictions if p['predicted'] and p['actual'])
        fp = sum(1 for p in self.predictions if p['predicted'] and not p['actual'])
        fn = sum(1 for p in self.predictions if not p['predicted'] and p['actual'])
        tn = sum(1 for p in self.predictions if not p['predicted'] and not p['actual'])

        precision = tp / max(1, (tp + fp))
        recall = tp / max(1, (tp + fn))
        f1 = (2 * precision * recall) / max(1e-6, (precision + recall))

        # False-positive cost computation (unnecessary capital deployment cost for false alarms)
        fp_cost = sum(p['capital_cost'] for p in self.predictions if p['predicted'] and not p['actual'])
        total_protected = sum(p['volume'] for p in self.predictions if p['predicted'] and p['actual'])
        total_fees = sum(p['fee_earned'] for p in self.predictions if p['predicted'])
        total_capital_cost = sum(p['capital_cost'] for p in self.predictions if p['predicted'])
        net_profit = total_fees - total_capital_cost

        return {
            'total_incidents_evaluated': len(self.predictions),
            'true_positives': tp,
            'false_positives': fp,
            'false_negatives': fn,
            'true_negatives': tn,
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1, 4),
            'false_positive_capital_cost': round(fp_cost, 2),
            'total_protected_volume': round(total_protected, 2),
            'total_fee_revenue': round(total_fees, 2),
            'total_capital_cost': round(total_capital_cost, 2),
            'net_profit': round(net_profit, 2)
        }

class DriftDetector:
    def __init__(self, baseline_f1=0.90):
        self.baseline_f1 = baseline_f1

    def evaluate_drift(self, current_f1):
        drift_delta = self.baseline_f1 - current_f1
        drift_detected = drift_delta > 0.08
        return {
            'baseline_f1': self.baseline_f1,
            'current_f1': round(current_f1, 4),
            'drift_detected': drift_detected,
            'status': 'WARNING_DRIFT_DETECTED' if drift_detected else 'STABLE',
            'recommended_action': 'TRIGGER_MODEL_RETRAINING' if drift_detected else 'NONE'
        }
