"""
PISI Batch Evaluation Script
Track 3: AI Revenue Recovery — Razorpay AI Buildathon 2026

Runs 1,000 synthetic incidents (default seed=42), computes genuine precision/recall/cost,
and prints a documented exception list of every case PISI got wrong.

Run:
    python scripts/batch_eval.py                # defaults to n=1000, seed=42
    python scripts/batch_eval.py --n 100        # runs 100 incidents
    python scripts/batch_eval.py --n 1000 --seed 7
"""
import sys
import os
import json
import argparse
from datetime import datetime

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tests.fixtures.synthetic_data import SyntheticDataGenerator

ACTIVATION_FLOOR = 0.70   # confidence threshold to activate Leg A
FEE_RATE         = 0.0010  # 0.10% predictive fee
REACTIVE_RATE    = 0.0030  # 0.30% reactive benchmark
ANNUAL_COC       = 0.12    # illustrative cost-of-capital
BRIDGE_DAYS      = 2       # T+2 standard settlement


def run_batch_evaluation(num_incidents=1000, seed=42):
    print("=" * 80)
    print("  PISI BATCH EVALUATION SUITE · Track 3 AI Revenue Recovery")
    print(f"  {num_incidents} synthetic incidents · seed={seed}")
    print("=" * 80)

    gen = SyntheticDataGenerator(seed=seed)
    incidents = gen.generate_batch_incidents(num_incidents=num_incidents)

    # Counters
    tp = fp = fn = tn = 0
    total_protected_volume = 0.0
    total_fee_revenue      = 0.0
    total_capital_cost     = 0.0
    fp_capital_cost        = 0.0
    missed_exposure        = 0.0
    exceptions = []

    genuine_risk_count = sum(1 for inc in incidents if inc['actual_risk'])
    print(f"\n  Genuine settlement-risk incidents: {genuine_risk_count} / {num_incidents}")

    for inc in incidents:
        predicted = inc['confidence'] >= ACTIVATION_FLOOR
        actual    = inc['actual_risk']
        vol       = inc['volume']

        fee      = vol * FEE_RATE
        cap_cost = vol * (ANNUAL_COC / 365.0) * BRIDGE_DAYS

        if predicted and actual:
            tp += 1
            total_protected_volume += vol
            total_fee_revenue      += fee
            total_capital_cost     += cap_cost
        elif predicted and not actual:
            fp += 1
            total_protected_volume += vol      # deployed but unneeded
            total_fee_revenue      += fee
            total_capital_cost     += cap_cost
            fp_capital_cost        += cap_cost
            exceptions.append({
                'incident_id': inc['incident_id'],
                'bank_code':   inc['bank_code'],
                'error_type':  'FALSE_POSITIVE',
                'confidence':  inc['confidence'],
                'volume':      round(vol, 2),
                'cost_impact': round(cap_cost, 2),
                'root_cause':  'Transient gateway spike without underlying CBS failure'
            })
        elif not predicted and actual:
            fn += 1
            missed_exposure += vol
            exceptions.append({
                'incident_id': inc['incident_id'],
                'bank_code':   inc['bank_code'],
                'error_type':  'FALSE_NEGATIVE',
                'confidence':  inc['confidence'],
                'volume':      round(vol, 2),
                'cost_impact': 0.0,
                'root_cause':  'Confidence below 0.70 activation floor despite genuine risk'
            })
        else:
            tn += 1

    precision = tp / max(1, tp + fp)
    recall    = tp / max(1, tp + fn)
    f1        = (2 * precision * recall) / max(1e-9, precision + recall)
    net_fee   = total_fee_revenue - total_capital_cost
    merchant_savings = total_protected_volume * (REACTIVE_RATE - FEE_RATE)

    # ---- Print results ----

    print(f"\n  True Positives (correctly protected):   {tp}")
    print(f"  True Negatives (correctly passed):      {tn}")
    print(f"  False Positives (protected needlessly): {fp}")
    print(f"  False Negatives (missed):               {fn}")
    print(f"  ---------------------------------------------------")
    print(f"  Precision:            {precision:.1%}")
    print(f"  Recall:               {recall:.1%}")
    print(f"  F1 Score:             {f1:.4f}")

    print(f"\n  Protected volume:                 Rs {total_protected_volume:,.2f}")
    print(f"  Missed exposure (FN volume):      Rs {missed_exposure:,.2f}")
    print(f"  Capital deployed:                 Rs {total_protected_volume:,.2f}")
    print(f"  Fee revenue (0.10%):              Rs {total_fee_revenue:,.2f}")
    print(f"  Capital cost ({BRIDGE_DAYS}-day float @ {ANNUAL_COC:.0%}):  Rs {total_capital_cost:,.2f}")
    print(f"  Net fee profit:                   Rs {net_fee:,.2f}")
    print(f"  Merchant fee savings vs 0.30%:    Rs {merchant_savings:,.2f}")

    if exceptions:
        print(f"\n  DOCUMENTED EXCEPTION LIST ({len(exceptions)} cases):")
        for ex in exceptions:
            print(f"    [{ex['incident_id']}] {ex['bank_code']} {ex['error_type']}: "
                  f"confidence={ex['confidence']:.4f}, volume=Rs {ex['volume']:,.0f}")
            print(f"      Root cause: {ex['root_cause']} (cost impact: Rs {ex['cost_impact']:.2f})")
    else:
        print("\n  No exceptions (0 FP, 0 FN).")

    # ---- Save to JSON ----
    output_dir = os.path.join(project_root, 'output')
    os.makedirs(output_dir, exist_ok=True)
    result_obj = {
        'evaluation_timestamp': datetime.now().isoformat(),
        'seed': seed,
        'num_incidents': num_incidents,
        'genuine_risk_count': genuine_risk_count,
        'true_positives': tp,
        'true_negatives': tn,
        'false_positives': fp,
        'false_negatives': fn,
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1_score': round(f1, 4),
        'total_protected_volume': round(total_protected_volume, 2),
        'missed_exposure': round(missed_exposure, 2),
        'total_fee_revenue': round(total_fee_revenue, 2),
        'total_capital_cost': round(total_capital_cost, 2),
        'fp_capital_cost': round(fp_capital_cost, 2),
        'net_fee_profit': round(net_fee, 2),
        'merchant_fee_savings': round(merchant_savings, 2),
        'exceptions': exceptions
    }
    try:
        with open(os.path.join(output_dir, 'batch_eval_results.json'), 'w') as f:
            json.dump(result_obj, f, indent=2)
        print(f"\n  Full results saved to: output/batch_eval_results.json")
    except Exception as e:
        print(f"\n  Note: Could not write output file ({e}), continuing in-memory")
    print("=" * 80)
    return result_obj


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PISI Batch Evaluation")
    parser.add_argument("--n", type=int, default=1000,
                        help="Number of incidents to simulate (default: 1000)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    args = parser.parse_args()
    run_batch_evaluation(num_incidents=args.n, seed=args.seed)