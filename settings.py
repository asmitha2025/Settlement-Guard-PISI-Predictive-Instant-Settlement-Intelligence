"""
PISI Configuration
Track 3: AI Revenue Recovery
"""

# Corporate Capital Pool
CORPORATE_CAPITAL_TOTAL = 15_000_000  # ₹1.5 Crore

# Safety Gates
MAX_CAPITAL_DEPLOYMENT_RATIO = 0.30  # 30% max
MAX_PER_TRANSACTION = 50_000  # ₹50K
MAX_CONCURRENT_PER_BANK = 10
MIN_MERCHANT_HEALTH = 20
MIN_PREDICTION_CONFIDENCE = 0.70

# Fee Structure
PREDICTIVE_FEE_RATE = 0.0010  # 0.10%
REACTIVE_FEE_RATE = 0.0025    # 0.25%
COST_OF_CAPITAL_ANNUAL = 0.12  # 12%

# Settlement Timing
STANDARD_SETTLEMENT_HOURS = 48  # T+2
EXPECTED_INSTANT_SETTLEMENT_SECONDS = 10

# Banks
SUPPORTED_BANKS = ['HDFC', 'ICICI', 'SBI', 'AXIS', 'KOTAK', 'PNB']

# Maintenance Windows (hour start, hour end)
MAINTENANCE_WINDOWS = {
    'SBI': [(2, 4), (14, 15)],
    'HDFC': [(2, 4)],
    'ICICI': [(1, 3)],
    'AXIS': [(3, 5)],
    'KOTAK': [(1, 2)],
    'PNB': [(9, 11)],
}
