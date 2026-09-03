"""
PISI Real-Time Dashboard
Track 3: AI Revenue Recovery
"""
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from features.bank_vitality import BankVitalityEngine
from decision.pisi_engine import PISIDecisionEngine
from decision.bridge_key_id import BridgeKeyIDSystem
from execution.instant_settlement import InstantSettlementExecutor
from datetime import datetime, timedelta
import json
import pandas as pd

st.set_page_config(
    page_title="PISI Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 32px; font-weight: 800; color: #1f2937; }
    .sub-header { font-size: 14px; color: #6b7280; margin-top: -10px; }
    .metric-card { background: #f3f4f6; border-radius: 12px; padding: 16px; text-align: center; }
    .metric-value { font-size: 28px; font-weight: 700; color: #111827; }
    .metric-label { font-size: 12px; color: #6b7280; text-transform: uppercase; }
    .status-healthy { color: #10b981; font-weight: 700; }
    .status-degraded { color: #f59e0b; font-weight: 700; }
    .status-critical { color: #ef4444; font-weight: 700; }
    .bridge-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# Initialize
@st.cache_resource
def init_engines():
    vitality = BankVitalityEngine()
    pisi = PISIDecisionEngine(vitality)
    bridge = BridgeKeyIDSystem()
    executor = InstantSettlementExecutor()
    return vitality, pisi, bridge, executor

vitality, pisi, bridge, executor = init_engines()

# Header
st.markdown('<div class="main-header">🛡️ PISI Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Predictive Instant Settlement Intelligence — Track 3: AI Revenue Recovery</div>', unsafe_allow_html=True)
st.divider()

# Sidebar
st.sidebar.header("⚙️ Controls")
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

simulation_mode = st.sidebar.checkbox("Run Simulation Mode", value=True)

# Main Layout
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader("🏦 Bank Health Map")
    health_data = vitality.get_all_bank_health()

    for bank, data in health_data.items():
        status_class = f"status-{data['status']}"
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; 
                    background: #f9fafb; padding: 10px 14px; border-radius: 8px; margin-bottom: 6px;">
            <span style="font-weight: 600;">{bank}</span>
            <span style="font-size: 18px;">{data['emoji']}</span>
            <span class="{status_class}">{data['composite_health']}/100</span>
            <span style="font-size: 11px; color: #6b7280; text-transform: uppercase;">{data['status']}</span>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.subheader("📊 System Metrics")
    metrics = pisi.get_dashboard_metrics()

    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{metrics['total_corporate_capital']:,.0f}</div>
            <div class="metric-label">Total Capital</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{metrics['deployed_capital']:,.0f}</div>
            <div class="metric-label">Deployed</div>
        </div>
        """, unsafe_allow_html=True)

    m3, m4 = st.columns(2)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['active_protections']}</div>
            <div class="metric-label">Active</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['closed_protections']}</div>
            <div class="metric-label">Closed</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-card" style="margin-top: 10px; border: 2px solid #10b981;">
        <div class="metric-value" style="color: #10b981;">₹{metrics['net_profit']:,.2f}</div>
        <div class="metric-label">Net Profit (All Time)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.subheader("💰 Financial Impact")
    st.markdown(f"""
    <div style="background: #f0fdf4; border-radius: 12px; padding: 16px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #374151;">Amount Protected</span>
            <span style="font-weight: 700;">₹{metrics['total_amount_protected']:,.0f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #374151;">Predictive Fees (0.10%)</span>
            <span style="font-weight: 700; color: #10b981;">₹{metrics['total_predictive_fees']:,.2f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #374151;">Capital Cost</span>
            <span style="font-weight: 700; color: #ef4444;">₹{metrics['total_capital_cost']:,.2f}</span>
        </div>
        <hr style="border: 0; border-top: 1px solid #d1d5db; margin: 12px 0;">
        <div style="display: flex; justify-content: space-between;">
            <span style="color: #111827; font-weight: 600;">Net Profit</span>
            <span style="font-weight: 800; color: #059669; font-size: 18px;">₹{metrics['net_profit']:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Bridge Key IDs Section
st.subheader("🔑 Active Bridge Key IDs")

if bridge.bridge_records:
    for bridge_id, record in list(bridge.bridge_records.items())[:5]:
        status_color = "#10b981" if record['status'] == 'CLOSED' else "#f59e0b"
        st.markdown(f"""
        <div class="bridge-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-family: monospace; font-size: 12px; color: #6b7280;">{bridge_id}</div>
                    <div style="font-size: 14px; font-weight: 600; margin-top: 4px;">
                        TX: {record['original_tx_id']} | ₹{record['amount']:,} | {record['acquiring_bank']}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="color: {status_color}; font-weight: 700; text-transform: uppercase;">{record['status']}</div>
                    <div style="font-size: 11px; color: #6b7280;">Fee: ₹{record['predictive_fee']:.2f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No active Bridge Key IDs. Run the demo scenario to generate data.")

# Simulation Section
if simulation_mode:
    st.divider()
    st.subheader("🎬 Run Demo Scenario")

    if st.button("▶️ Execute SBI Downtime Simulation"):
        with st.spinner("Running simulation..."):
            now = datetime(2026, 8, 22, 10, 0, 0)

            # Inject risk signals
            vitality.ingest_error('AXIS', 'gateway_technical_error', now - timedelta(minutes=40))
            vitality.ingest_error('AXIS', 'gateway_technical_error', now - timedelta(minutes=25))
            vitality.ingest_settlement('AXIS', 48, 68, now - timedelta(hours=3))

            # Evaluate a test transaction
            tx = {
                'tx_id': 'RZP-tx-00999',
                'order_id': 'RZP-ord-00999',
                'amount': 2500,
                'method': 'upi',
                'customer_bank': 'HDFC',
                'merchant_bank': 'AXIS',
                'merchant_id': 'M-4421',
                'timestamp': now.isoformat(),
                'status': 'captured'
            }

            decision = pisi.evaluate_transaction(tx, now)

            if decision['decision'] == 'ACTIVATE':
                protection = pisi.activate_protection(tx, decision)
                bridge_record = bridge.create_bridge_record(protection, tx, decision)
                settlement = executor.execute_instant_settlement(tx, protection, bridge_record)

                st.success(f"✅ PISI ACTIVATED — Bridge Key ID: {protection['bridge_key_id']}")
                st.json({
                    "tx_id": tx['tx_id'],
                    "amount": tx['amount'],
                    "decision": decision['decision'],
                    "bank_health": decision['bank_health'],
                    "confidence": decision['confidence'],
                    "predictive_fee": decision['predictive_fee'],
                    "merchant_credited": settlement['merchant_credited'],
                    "settlement_time": f"{settlement['settlement_time_seconds']}s"
                })
            else:
                st.warning(f"Decision: {decision['decision']} — {decision['reason']}")

        st.rerun()

# Footer
st.divider()
st.caption("PISI v1.0 — Predictive Instant Settlement Intelligence | Track 3: AI Revenue Recovery | Razorpay AI Builder 2026")
