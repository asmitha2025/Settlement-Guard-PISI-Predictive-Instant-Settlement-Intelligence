"""
PISI Configuration · v2.0
Track 3: AI Revenue Recovery — Razorpay AI Buildathon 2026
"""

# Corporate Capital Pool (Razorpay Balance Sheet)
CORPORATE_CAPITAL_TOTAL = 50_000_000.00  # ₹5 Crore total corporate pool
MAX_CAPITAL_DEPLOYMENT_RATIO = 0.30      # 30% cap = ₹1.5 Crore max deployable
CORPORATE_CAPITAL_DEPLOYABLE_CAP = CORPORATE_CAPITAL_TOTAL * MAX_CAPITAL_DEPLOYMENT_RATIO  # ₹1.5 Crore

# Safety Gates (Stopping Rules)
MAX_PER_TRANSACTION = 50_000.00          # ₹50K cap per single bridge (modeled on Razorpay entry tier)
MAX_CONCURRENT_PER_BANK = 10             # Concentration limit per bank
MIN_MERCHANT_HEALTH = 20                 # Floor merchant health score
MIN_PREDICTION_CONFIDENCE = 0.70         # Decision threshold for Leg A & B

# Fee Structure & Unit Economics
PREDICTIVE_FEE_RATE = 0.0010             # 0.10% (PISI pre-approved rate)
REACTIVE_FEE_RATE = 0.0030               # 0.30% (Razorpay published On-Demand Settlement baseline)
COST_OF_CAPITAL_ANNUAL = 0.12            # 12% per annum corporate capital cost

# Settlement Timing
STANDARD_SETTLEMENT_HOURS = 48           # T+2 days standard cycle
EXPECTED_INSTANT_SETTLEMENT_SECONDS = 10

# Supported Corridor Banks
SUPPORTED_BANKS = ['SBI', 'HDFC', 'ICICI', 'AXIS', 'KOTAK', 'PNB']
