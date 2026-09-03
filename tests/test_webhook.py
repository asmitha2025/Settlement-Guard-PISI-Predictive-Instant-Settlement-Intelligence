"""
Unit Tests for Razorpay Webhook Endpoint & Signature Verification
Track 3: AI Revenue Recovery
"""
import sys
import os
import unittest
import json
import hmac
import hashlib

# Configure import path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from src.api.main import app

class TestWebhookSecurity(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.secret = "rzp_whsec_pisi_2026_buildathon_secret"
        os.environ["RAZORPAY_WEBHOOK_SECRET"] = self.secret

    def test_webhook_valid_signature_payment_captured(self):
        payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_test_cap_101",
                        "amount": 249900,
                        "currency": "INR",
                        "status": "captured",
                        "order_id": "order_test_101",
                        "bank": "SBI",
                        "method": "upi"
                    }
                }
            }
        }
        body_bytes = json.dumps(payload).encode('utf-8')
        sig = hmac.new(self.secret.encode('utf-8'), body_bytes, hashlib.sha256).hexdigest()

        response = self.client.post(
            "/webhook/razorpay",
            content=body_bytes,
            headers={"Content-Type": "application/json", "X-Razorpay-Signature": sig}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "processed")
        self.assertEqual(data["action"], "INGESTED_CAPTURE")

    def test_webhook_invalid_signature_rejected(self):
        payload = {"event": "payment.captured", "payload": {}}
        body_bytes = json.dumps(payload).encode('utf-8')
        invalid_sig = "a" * 64

        response = self.client.post(
            "/webhook/razorpay",
            content=body_bytes,
            headers={"Content-Type": "application/json", "X-Razorpay-Signature": invalid_sig}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid Razorpay webhook HMAC signature", response.json()["detail"])

if __name__ == '__main__':
    unittest.main()
