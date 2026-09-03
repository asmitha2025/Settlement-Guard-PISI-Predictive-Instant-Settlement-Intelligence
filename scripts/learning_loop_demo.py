"""
PISI Learning Loop Demo
========================
Demonstrates the model's ability to retrain on new accumulated data,
improving performance over time. Validates across multiple seed
combinations to prove the improvement is robust, not a lucky run.

Run:  python scripts/learning_loop_demo.py
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
from sklearn.metrics import precision_score, recall_score, f1_score
from src.models.training_data import generate_training_dataset
from src.models.downtime_classifier import DowntimeClassifier


def train_and_evaluate(X_train, y_train, X_test, y_test, feature_names):
    """Train a fresh classifier and return metrics."""
    clf = DowntimeClassifier(model_type="xgboost")
    clf.train(X_train, y_train, feature_names=feature_names)
    
    proba = clf.predict_proba(X_test)
    preds = (proba >= 0.50).astype(int)
    
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)
    
    return prec, rec, f1, clf


def main():
    print("=" * 72)
    print("  PISI LEARNING LOOP DEMONSTRATION")
    print("  Retraining on Accumulated Data with Multi-Seed Validation")
    print("  Track 3: AI Revenue Recovery | Razorpay AI Buildathon 2026")
    print("=" * 72)
    
    seeds = [42, 123, 456, 789, 2026]
    
    all_improvements = []
    
    for seed in seeds:
        print(f"\n  --- Seed {seed} ---")
        
        # Phase 1: Initial training (small dataset)
        X_init, y_init, fnames, _ = generate_training_dataset(n_samples=800, seed=seed)
        X_train_1, X_test, y_train_1, y_test = train_test_split(
            X_init, y_init, test_size=0.30, random_state=seed, stratify=y_init
        )
        
        prec_1, rec_1, f1_1, _ = train_and_evaluate(X_train_1, y_train_1, X_test, y_test, fnames)
        print(f"  Phase 1 (initial, {len(y_train_1)} samples): "
              f"Precision={prec_1:.1%}  Recall={rec_1:.1%}  F1={f1_1:.4f}")
        
        # Phase 2: Accumulate new data (simulate production drift + new incidents)
        X_new, y_new, _, _ = generate_training_dataset(n_samples=1200, seed=seed + 1000, noise_level=0.12)
        
        # Combine original + new data
        X_combined = np.vstack([X_train_1, X_new])
        y_combined = np.concatenate([y_train_1, y_new])
        
        prec_2, rec_2, f1_2, retrained_clf = train_and_evaluate(
            X_combined, y_combined, X_test, y_test, fnames
        )
        print(f"  Phase 2 (retrained, {len(y_combined)} samples): "
              f"Precision={prec_2:.1%}  Recall={rec_2:.1%}  F1={f1_2:.4f}")
        
        delta = f1_2 - f1_1
        improved = delta > 0
        all_improvements.append({
            'seed': seed,
            'f1_initial': round(f1_1, 4),
            'f1_retrained': round(f1_2, 4),
            'delta': round(delta, 4),
            'improved': improved,
        })
        
        status = "IMPROVED" if improved else ("STABLE" if delta == 0 else "REGRESSED")
        print(f"  Result: F1 delta = {delta:+.4f}  [{status}]")
    
    # Summary
    n_improved = sum(1 for r in all_improvements if r['improved'])
    n_stable = sum(1 for r in all_improvements if r['delta'] == 0)
    n_regressed = sum(1 for r in all_improvements if r['delta'] < 0)
    avg_delta = np.mean([r['delta'] for r in all_improvements])
    
    print(f"\n{'=' * 72}")
    print(f"  LEARNING LOOP SUMMARY ({len(seeds)} seed combinations)")
    print(f"{'=' * 72}")
    print(f"\n  {'Seed':<10} {'Initial F1':<15} {'Retrained F1':<15} {'Delta':<12} {'Status':<10}")
    print(f"  {'-' * 60}")
    for r in all_improvements:
        status = "IMPROVED" if r['improved'] else ("STABLE" if r['delta'] == 0 else "REGRESSED")
        print(f"  {r['seed']:<10} {r['f1_initial']:<15.4f} {r['f1_retrained']:<15.4f} {r['delta']:>+.4f}       {status}")
    
    print(f"\n  Improved: {n_improved}/{len(seeds)}  |  Stable: {n_stable}/{len(seeds)}  |  Regressed: {n_regressed}/{len(seeds)}")
    print(f"  Average F1 delta: {avg_delta:+.4f}")
    
    verdict = "VALIDATED" if n_improved >= 3 else "INCONCLUSIVE"
    print(f"\n  Learning Loop Verdict: {verdict}")
    print(f"  (Retraining on accumulated data improves or maintains performance")
    print(f"   across {n_improved + n_stable}/{len(seeds)} seed combinations)")
    
    # Save results
    os.makedirs(os.path.join(project_root, 'output'), exist_ok=True)
    out_path = os.path.join(project_root, 'output', 'learning_loop_results.json')
    with open(out_path, 'w') as f:
        json.dump({
            'seed_results': all_improvements,
            'improved': n_improved,
            'stable': n_stable,
            'regressed': n_regressed,
            'avg_delta': round(avg_delta, 4),
            'verdict': verdict,
        }, f, indent=2)
    
    print(f"\n  Results saved to: output/learning_loop_results.json")
    print(f"{'=' * 72}\n")


if __name__ == '__main__':
    main()
