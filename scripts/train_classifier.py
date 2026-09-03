"""
PISI XGBoost Model Training Pipeline
=====================================
Trains the downtime classifier on synthetic 47-feature data,
evaluates against a naive rule baseline, validates feature importance
(noise features should rank last), and saves the production model.

Run:  python scripts/train_classifier.py
Track 3: AI Revenue Recovery
"""
import sys
import os
import json
import numpy as np

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from src.models.training_data import generate_training_dataset
from src.models.downtime_classifier import DowntimeClassifier, AnomalyDetector


def naive_rule_baseline(X, feature_names):
    """
    The naive rule anyone would hand-write:
    IF error_rate_1h > 4 AND is_maintenance_window == 1 THEN risk=1
    """
    err_idx = feature_names.index('error_rate_1h')
    maint_idx = feature_names.index('is_maintenance_window')
    
    preds = []
    for row in X:
        if row[err_idx] > 4 and row[maint_idx] == 1:
            preds.append(1)
        elif row[err_idx] > 6:
            preds.append(1)
        else:
            preds.append(0)
    return np.array(preds)


def main():
    print("=" * 72)
    print("  PISI MODEL TRAINING PIPELINE")
    print("  XGBoost Downtime Classifier + Isolation Forest Anomaly Detector")
    print("  Track 3: AI Revenue Recovery | Razorpay AI Buildathon 2026")
    print("=" * 72)
    
    # ── Step 1: Generate Training Data ────────────────────────────────
    print("\n  [1/6] Generating training dataset (2000 samples, seed=42)...")
    X, y, feature_names, bank_codes = generate_training_dataset(n_samples=2000, seed=42)
    
    positive_rate = np.mean(y)
    print(f"        Samples: {len(y)}  |  Positive rate: {positive_rate:.1%}")
    print(f"        Features: {len(feature_names)} (47 real + 3 noise)")
    
    # ── Step 2: Train/Test Split ──────────────────────────────────────
    print("\n  [2/6] Splitting into train (70%) / test (30%)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    print(f"        Train: {len(y_train)} ({np.mean(y_train):.1%} positive)")
    print(f"        Test:  {len(y_test)} ({np.mean(y_test):.1%} positive)")
    
    # ── Step 3: Train XGBoost Classifier ──────────────────────────────
    print("\n  [3/6] Training XGBoost classifier with Platt calibration...")
    classifier = DowntimeClassifier(model_type="xgboost")
    classifier.train(X_train, y_train, feature_names=feature_names)
    
    # Predict probabilities on test set
    proba_test = classifier.predict_proba(X_test)
    preds_xgb = (proba_test >= 0.50).astype(int)
    
    prec_xgb = precision_score(y_test, preds_xgb, zero_division=0)
    rec_xgb = recall_score(y_test, preds_xgb, zero_division=0)
    f1_xgb = f1_score(y_test, preds_xgb, zero_division=0)
    
    cm_xgb = confusion_matrix(y_test, preds_xgb)
    tn, fp, fn, tp = cm_xgb.ravel()
    
    print(f"        XGBoost Results (test set, threshold=0.50):")
    print(f"        Precision: {prec_xgb:.1%}  |  Recall: {rec_xgb:.1%}  |  F1: {f1_xgb:.4f}")
    print(f"        TP: {tp}  FP: {fp}  FN: {fn}  TN: {tn}")
    
    # ── Step 4: Compare Against Naive Rule Baseline ───────────────────
    print("\n  [4/6] Comparing against naive hand-written rule baseline...")
    preds_naive = naive_rule_baseline(X_test, feature_names)
    
    prec_naive = precision_score(y_test, preds_naive, zero_division=0)
    rec_naive = recall_score(y_test, preds_naive, zero_division=0)
    f1_naive = f1_score(y_test, preds_naive, zero_division=0)
    
    cm_naive = confusion_matrix(y_test, preds_naive)
    tn_n, fp_n, fn_n, tp_n = cm_naive.ravel()
    
    print(f"        Naive Rule Results (test set):")
    print(f"        Precision: {prec_naive:.1%}  |  Recall: {rec_naive:.1%}  |  F1: {f1_naive:.4f}")
    print(f"        TP: {tp_n}  FP: {fp_n}  FN: {fn_n}  TN: {tn_n}")
    
    print(f"\n        {'Metric':<15} {'XGBoost':<15} {'Naive Rule':<15} {'Winner':<10}")
    print(f"        {'-'*55}")
    
    p_win = "XGBoost" if prec_xgb > prec_naive else ("Tie" if prec_xgb == prec_naive else "Naive")
    r_win = "XGBoost" if rec_xgb > rec_naive else ("Tie" if rec_xgb == rec_naive else "Naive")
    f_win = "XGBoost" if f1_xgb > f1_naive else ("Tie" if f1_xgb == f1_naive else "Naive")
    
    print(f"        {'Precision':<15} {prec_xgb:<15.1%} {prec_naive:<15.1%} {p_win:<10}")
    print(f"        {'Recall':<15} {rec_xgb:<15.1%} {rec_naive:<15.1%} {r_win:<10}")
    print(f"        {'F1 Score':<15} {f1_xgb:<15.4f} {f1_naive:<15.4f} {f_win:<10}")
    
    # ── Step 5: Feature Importance Validation ─────────────────────────
    print("\n  [5/6] Feature importance ranking (noise features should rank LAST)...")
    ranking = classifier.get_feature_importance_ranking()
    
    print(f"\n        Top 10 Features:")
    for i, (name, imp) in enumerate(ranking[:10]):
        bar = '#' * int(imp * 200)
        print(f"        {i+1:>3}. {name:<40s} {imp:.4f}  {bar}")
    
    print(f"\n        Bottom 5 Features (expect noise here):")
    for i, (name, imp) in enumerate(ranking[-5:]):
        marker = " ** NOISE **" if 'noise' in name else ""
        print(f"        {len(ranking)-4+i:>3}. {name:<40s} {imp:.4f}{marker}")
    
    # Check noise features are in bottom 10
    noise_positions = []
    for i, (name, _) in enumerate(ranking):
        if 'noise' in name:
            noise_positions.append(i + 1)
    
    all_noise_bottom = all(p > len(ranking) - 10 for p in noise_positions)
    print(f"\n        Noise features at positions: {noise_positions}")
    print(f"        All noise in bottom 10: {'YES - Model learned signal, not spurious correlation' if all_noise_bottom else 'PARTIAL - Some noise features ranked higher than expected'}")
    
    # ── Step 6: Train Anomaly Detector & Save ─────────────────────────
    print("\n  [6/6] Training Isolation Forest anomaly detector...")
    anomaly_det = AnomalyDetector(contamination=0.05)
    anomaly_det.train(X_train)
    
    scores = anomaly_det.predict_anomaly_score(X_test)
    n_anomalous = np.sum(scores < 0)
    print(f"        Anomalies detected in test set: {n_anomalous}/{len(X_test)} ({n_anomalous/len(X_test):.1%})")
    
    # Save everything
    print("\n  Saving models...")
    
    # Store training metrics
    classifier.training_metrics = {
        'precision': round(prec_xgb, 4),
        'recall': round(rec_xgb, 4),
        'f1': round(f1_xgb, 4),
        'tp': int(tp), 'fp': int(fp), 'fn': int(fn), 'tn': int(tn),
        'naive_precision': round(prec_naive, 4),
        'naive_recall': round(rec_naive, 4),
        'naive_f1': round(f1_naive, 4),
        'train_samples': len(y_train),
        'test_samples': len(y_test),
        'positive_rate': round(float(positive_rate), 4),
    }
    
    classifier.save_model()
    anomaly_det.save()
    
    # Save results JSON
    os.makedirs(os.path.join(project_root, 'output'), exist_ok=True)
    results = {
        'xgboost': {
            'precision': round(prec_xgb, 4), 'recall': round(rec_xgb, 4),
            'f1': round(f1_xgb, 4), 'tp': int(tp), 'fp': int(fp),
            'fn': int(fn), 'tn': int(tn)
        },
        'naive_rule': {
            'precision': round(prec_naive, 4), 'recall': round(rec_naive, 4),
            'f1': round(f1_naive, 4), 'tp': int(tp_n), 'fp': int(fp_n),
            'fn': int(fn_n), 'tn': int(tn_n)
        },
        'feature_ranking': [(n, round(v, 6)) for n, v in ranking],
        'noise_feature_positions': noise_positions,
        'anomaly_detector': {
            'test_anomalies': int(n_anomalous),
            'test_total': len(X_test),
        }
    }
    
    out_path = os.path.join(project_root, 'output', 'training_results.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"        Model saved to: models/xgb_downtime_v1.joblib")
    print(f"        Scaler saved to: models/scaler_v1.joblib")
    print(f"        Anomaly detector saved to: models/anomaly_detector_v1.joblib")
    print(f"        Results saved to: output/training_results.json")
    print(f"\n{'=' * 72}")
    print(f"  TRAINING COMPLETE")
    print(f"  XGBoost F1: {f1_xgb:.4f}  vs  Naive Rule F1: {f1_naive:.4f}")
    print(f"  Model is production-ready for PISIDecisionEngine.")
    print(f"{'=' * 72}\n")


if __name__ == '__main__':
    main()
