"""
Execution Layer — Layer 5 · v2.0 (Real Razorpay API Ready)
InstantSettlementExecutor (Leg A: Payouts) + MerchantNotifier (Leg B: Alerts).
Track 3: AI Revenue Recovery — Razorpay AI Buildathon 2026
"""
import sys
import os
import json
from datetime import datetime
import requests

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Try importing razorpay SDK
try:
    import razorpay
    HAS_RAZORPAY_SDK = True
except ImportError:
    HAS_RAZORPAY_SDK = False


def _load_env_credentials():
    """Load credentials from .env if present."""
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    
    if not key_id or not key_secret:
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        if k.strip() == "RAZORPAY_KEY_ID":
                            key_id = v.strip()
                        elif k.strip() == "RAZORPAY_KEY_SECRET":
                            key_secret = v.strip()
    
    return key_id, key_secret


class InstantSettlementExecutor:
    """
    Executes Leg A instant settlement advance for captured payments.
    Supports both real Razorpay On-Demand Settlement API and offline test simulation mode.
    """
    def __init__(self, razorpay_client=None, force_simulation=False):
        self.key_id, self.key_secret = _load_env_credentials()
        self.simulation_mode = force_simulation or (not self.key_id or not self.key_secret)
        self.execution_log = []
        
        if HAS_RAZORPAY_SDK and self.key_id and self.key_secret and not force_simulation:
            try:
                self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
            except Exception:
                self.client = None
        else:
            self.client = None

    def execute_instant_settlement(self, tx, bridge_record, use_live_api=False):
        """
        Executes Leg A instant settlement advance for a captured payment.
        Converts amount to paise for Razorpay API.
        """
        amount = float(tx['amount'])
        bridge_fee = float(bridge_record['bridge_fee'])
        merchant_credit = round(amount - bridge_fee, 2)
        amount_in_paise = int(round(amount * 100))

        api_response = None
        razorpay_settlement_id = None
        is_live_executed = False

        if use_live_api and self.key_id and self.key_secret:
            try:
                url = "https://api.razorpay.com/v1/settlements/ondemand"
                payload = {
                    "amount": amount_in_paise,
                    "settle_full_balance": False,
                    "description": f"PISI protection bridge for {tx.get('settlement_path_bank', 'SBI')}",
                    "notes": {
                        "bridge_id": bridge_record['bridge_id'],
                        "tx_id": tx['tx_id'],
                        "merchant_id": tx.get('merchant_id', 'M-1000')
                    }
                }
                resp = requests.post(
                    url, json=payload, auth=(self.key_id, self.key_secret), timeout=5
                )
                if resp.status_code in [200, 201]:
                    api_response = resp.json()
                    razorpay_settlement_id = api_response.get("id")
                    is_live_executed = True
                else:
                    api_response = {"error": resp.text, "status_code": resp.status_code}
            except Exception as e:
                api_response = {"error": str(e)}

        result = {
            'status': 'success',
            'bridge_id': bridge_record['bridge_id'],
            'tx_id': tx['tx_id'],
            'merchant_id': tx.get('merchant_id', 'M-1000'),
            'amount_processed': amount,
            'amount_in_paise': amount_in_paise,
            'predictive_fee_deducted': bridge_fee,
            'merchant_credited': merchant_credit,
            'settlement_time_seconds': 10,
            'utr_reference': f"UTR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{tx['tx_id'][-5:]}",
            'razorpay_settlement_id': razorpay_settlement_id or f"setl_pisi_{datetime.now().strftime('%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'simulated': not is_live_executed,
            'api_response': api_response
        }

        self.execution_log.append(result)
        return result

    def get_summary(self):
        total_p = sum(r['amount_processed'] for r in self.execution_log)
        total_f = sum(r['predictive_fee_deducted'] for r in self.execution_log)
        total_c = sum(r['merchant_credited'] for r in self.execution_log)
        return {
            'total_settlements_executed': len(self.execution_log),
            'total_amount_processed': total_p,
            'total_fees_earned': round(total_f, 2),
            'total_merchant_credited': round(total_c, 2),
            'avg_settlement_time_seconds': 10
        }


class MerchantNotifier:
    def __init__(self):
        self.notifications = []

    def send_early_warning(self, bank_code, confidence=0.91, lead_min=60):
        """
        Executes Leg B early-warning notification for issuing bank risk.
        Informational only — does not move capital.
        """
        notification = {
            "notification_id": f"WARN-{bank_code}-{datetime.now().strftime('%Y%m%d%H%M%S')}-x1y2z3",
            "bank_code": bank_code,
            "leg": "authorization_early_warning",
            "confidence": round(confidence, 2),
            "message": f"Elevated authorization-failure risk expected for {bank_code}-linked payments in the next ~{lead_min} minutes.",
            "recommended_action": "Prompt customers toward alternate payment methods where possible.",
            "timestamp": datetime.now().isoformat(),
            "moves_money": False
        }

        self.notifications.append(notification)
        return notification

    def send_leg_a_protection_notice(self, merchant_id, bank_code, tx_count, protected_volume, fee_saved):
        """
        Sends merchant notification for proactive Leg A protection.
        """
        notice = {
            "merchant_id": merchant_id,
            "leg": "settlement_protection",
            "title": "Your Payments Are Protected",
            "message": (
                f"We detected potential settlement delays on {bank_code}. "
                f"Instant Settlement has been proactively activated for {tx_count} captured payments (₹{protected_volume:,.2f}). "
                f"Funds will reach your account within 10 seconds. You saved ₹{fee_saved:,.2f} vs standard on-demand rate."
            ),
            "timestamp": datetime.now().isoformat(),
            "action_required": "NONE"
        }
        self.notifications.append(notice)
        return notice
