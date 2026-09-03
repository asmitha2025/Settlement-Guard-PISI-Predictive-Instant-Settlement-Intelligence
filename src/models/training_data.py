"""
PISI ML Training Data Generator
Generates realistic labeled datasets from the 47 engineered features
for training the XGBoost downtime classifier.
Track 3: AI Revenue Recovery
"""
import sys
import os
import math
import random
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def generate_training_dataset(n_samples=2000, seed=42, noise_level=0.10):
    """
    Generate a labeled training dataset with 47 features + 3 noise features.
    
    Labels:
      1 = genuine settlement risk (bank will experience downtime)
      0 = no risk (normal operations)
    
    The generating function uses a non-trivial combination of features
    so that a simple threshold rule cannot match a trained model.
    """
    rng = np.random.RandomState(seed)
    
    banks = ['SBI', 'HDFC', 'ICICI', 'AXIS', 'KOTAK', 'PNB']
    maintenance_windows = {
        'SBI': [(2, 4), (14, 15)],
        'HDFC': [(2, 4)],
        'ICICI': [(1, 3)],
        'AXIS': [(3, 5)],
        'KOTAK': [(1, 2)],
        'PNB': [(9, 11)],
    }
    
    features_list = []
    labels = []
    bank_codes = []
    
    for i in range(n_samples):
        bank = banks[rng.randint(0, len(banks))]
        hour = rng.randint(0, 24)
        dow = rng.randint(0, 7)
        
        windows = maintenance_windows.get(bank, [])
        is_maint = int(any(s <= hour < e for s, e in windows))
        
        # --- Generate features with realistic distributions ---
        # Risk factors that contribute to genuine downtime
        error_rate_1h = rng.poisson(3) if rng.random() < 0.3 else rng.poisson(0.5)
        error_rate_4h = error_rate_1h * rng.uniform(0.8, 1.5) + rng.poisson(1)
        error_rate_24h = error_rate_4h * rng.uniform(0.5, 1.2) + rng.poisson(2)
        error_acceleration = max(0, error_rate_1h - (error_rate_4h / 4.0))
        error_trend_slope = 1.2 if error_acceleration > 1.0 else rng.uniform(-0.3, 0.5)
        
        bank_tech_pct = rng.beta(2, 8) if error_rate_1h > 0 else 0.0
        gateway_tech_pct = rng.beta(2, 6) if error_rate_1h > 0 else 0.0
        timed_out_pct = rng.beta(1.5, 10)
        vpa_failed_pct = rng.beta(1, 15)
        error_amount_1h = error_rate_1h * rng.uniform(1000, 5000)
        
        hour_sin = math.sin(2 * math.pi * hour / 24.0)
        hour_cos = math.cos(2 * math.pi * hour / 24.0)
        is_weekend = int(dow >= 5)
        mins_to_maint = rng.randint(0, 999)
        is_salary_week = int(rng.random() < 0.3)
        days_since_maint = rng.randint(1, 14)
        
        avg_settle_1h = 48.0 + rng.exponential(2.0)
        avg_settle_4h = 48.0 + rng.exponential(1.5)
        settle_trend = rng.uniform(-1.0, 3.0)
        settle_delayed = rng.poisson(0.5)
        settle_success = rng.uniform(0.85, 1.0)
        settle_batch = rng.randint(200, 800)
        
        peer_avg = rng.uniform(70, 95)
        peer_min = rng.uniform(50, peer_avg)
        net_congestion = rng.uniform(0.05, 0.5)
        corr_sbi_hdfc = rng.uniform(0.7, 1.0)
        corr_sbi_icici = rng.uniform(0.7, 1.0)
        corr_sbi_axis = rng.uniform(0.65, 1.0)
        cross_fail_corr = rng.uniform(0.0, 0.4)
        gw_down_count = rng.poisson(0.3)
        
        leading_15m = rng.poisson(1) if error_rate_1h > 2 else 0
        gw_before_bank = int(gateway_tech_pct > 0.1 and bank_tech_pct < 0.05)
        timeout_spike = int(timed_out_pct > 0.15)
        complaint_vel = rng.exponential(0.05)
        pred_maint_prob = 0.90 if is_maint else rng.uniform(0.01, 0.15)
        hist_recurrence = 0.85 if is_maint else rng.uniform(0.05, 0.25)
        seasonal_pattern = rng.uniform(0.05, 0.35)
        
        pending_count = rng.randint(50, 500)
        pending_amount = pending_count * rng.uniform(1500, 3500)
        tx_velocity = rng.uniform(50, 300)
        high_val_ratio = rng.uniform(0.05, 0.30)
        tier3_ratio = rng.uniform(0.10, 0.40)
        merch_diversity = rng.uniform(0.5, 0.95)
        peak_load = int(10 <= hour <= 18)
        
        # 3 NOISE FEATURES (should rank last in importance)
        noise_random_uniform = rng.uniform(0, 1)
        noise_random_normal = rng.normal(50, 15)
        noise_random_id = rng.randint(0, 10000)
        
        # --- Generate ground-truth label ---
        # Non-trivial function: combination of error acceleration, 
        # maintenance window, gateway leading indicators, and settlement lag
        risk_score = (
            0.30 * min(1.0, error_rate_1h / 8.0) +
            0.15 * min(1.0, error_acceleration / 4.0) +
            0.15 * is_maint +
            0.10 * min(1.0, bank_tech_pct * 3.0) +
            0.10 * int(gw_before_bank) +
            0.08 * min(1.0, (avg_settle_1h - 48.0) / 10.0) +
            0.07 * min(1.0, leading_15m / 3.0) +
            0.05 * (1.0 - settle_success)
        )
        
        # Add controlled noise so it's not perfectly separable
        risk_score += rng.normal(0, noise_level)
        label = int(risk_score > 0.30)
        
        feature_vec = [
            error_rate_1h, error_rate_4h, error_rate_24h, error_acceleration,
            error_trend_slope, bank_tech_pct, gateway_tech_pct, timed_out_pct,
            vpa_failed_pct, error_amount_1h,
            hour_sin, hour_cos, dow, is_weekend, is_maint,
            mins_to_maint, is_salary_week, days_since_maint,
            avg_settle_1h, avg_settle_4h, settle_trend, settle_delayed,
            settle_success, settle_batch,
            peer_avg, peer_min, net_congestion, corr_sbi_hdfc,
            corr_sbi_icici, corr_sbi_axis, cross_fail_corr, gw_down_count,
            leading_15m, gw_before_bank, timeout_spike, complaint_vel,
            pred_maint_prob, hist_recurrence, seasonal_pattern,
            pending_count, pending_amount, tx_velocity, high_val_ratio,
            tier3_ratio, merch_diversity, peak_load,
            # 3 noise features
            noise_random_uniform, noise_random_normal, noise_random_id,
        ]
        
        features_list.append(feature_vec)
        labels.append(label)
        bank_codes.append(bank)
    
    feature_names = [
        'error_rate_1h', 'error_rate_4h', 'error_rate_24h', 'error_acceleration',
        'error_trend_slope', 'bank_technical_error_pct', 'gateway_technical_error_pct',
        'payment_timed_out_pct', 'vpa_resolution_failed_pct', 'error_amount_at_risk_1h',
        'hour_sin', 'hour_cos', 'day_of_week', 'is_weekend', 'is_maintenance_window',
        'minutes_to_maintenance', 'is_salary_week', 'days_since_last_maintenance',
        'avg_settlement_time_1h', 'avg_settlement_time_4h', 'settlement_time_trend',
        'settlements_delayed_1h', 'settlement_success_rate_1h', 'settlement_batch_size_avg',
        'peer_bank_avg_health', 'peer_bank_min_health', 'network_congestion_index',
        'corridor_health_sbi_hdfc', 'corridor_health_sbi_icici', 'corridor_health_sbi_axis',
        'cross_bank_failure_correlation', 'gateway_downtime_count',
        'leading_error_count_15m', 'gateway_error_before_bank', 'timeout_spike_detected',
        'customer_complaint_velocity', 'predicted_maintenance_probability',
        'historical_downtime_recurrence', 'seasonal_downtime_pattern',
        'pending_transaction_count', 'pending_transaction_amount', 'transaction_velocity_1h',
        'high_value_transaction_ratio', 'tier3_transaction_ratio', 'merchant_diversity_index',
        'peak_load_indicator',
        # noise
        'noise_random_uniform', 'noise_random_normal', 'noise_random_id',
    ]
    
    X = np.array(features_list, dtype=np.float64)
    y = np.array(labels, dtype=np.int32)
    
    return X, y, feature_names, bank_codes
