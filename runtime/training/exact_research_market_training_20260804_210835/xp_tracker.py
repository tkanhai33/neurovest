#!/usr/bin/env python3

from pathlib import Path
from collections import defaultdict, deque
import pandas as pd
import json
import time
import os

campaign = Path("runtime/training/exact_research_market_training_20260804_210835/campaign")

seen = set()

# Initialize statistics tracking
xp = defaultdict(int)
gens = defaultdict(int)
wins = defaultdict(int)
peak_sharpe = defaultdict(float)
peak_generation = defaultdict(int)
best_candidate = defaultdict(dict)
history = defaultdict(list)
rolling_last_5 = defaultdict(lambda: deque(maxlen=5))
rolling_last_10 = defaultdict(lambda: deque(maxlen=10))
trend = defaultdict(float)
average_improvement = defaultdict(float)

# Feature families to track
FEATURE_FAMILIES = {
    "base",
    "base_plus_interactions",
    "base_plus_cross_section",
    "full_evolved",
    "research_053_only",
    "market_plus_research_053",
    "full_market_plus_research_053"
}

print("="*110, flush=True)
print("NEUROVEST EVOLUTION XP TRACKER V2", flush=True)
print("="*110, flush=True)

# Ensure campaign directories exist
campaign.mkdir(parents=True, exist_ok=True)
xp_history_path = campaign / "xp_history.jsonl"
xp_summary_path = campaign / "xp_summary.json"
xp_leaderboard_path = campaign / "xp_leaderboard.csv"

# Initialize history file
if not xp_history_path.exists():
    xp_history_path.write_text("")

while True:
    progress = campaign / "progress.json"

    if progress.exists():
        try:
            p = json.loads(progress.read_text())
            cg = p.get("current_generation", {}).get("generation", "?")
            print(f"[{time.strftime('%H:%M:%S')}] Current Generation {cg}", flush=True)
        except Exception:
            pass

    boards = sorted(campaign.glob("generations/generation_*/output/evolution_leaderboard.csv"))

    new_generations = []
    for board in boards:
        if str(board) not in seen:
            seen.add(str(board))
            new_generations.append(board)

    for board in new_generations:
        print()
        print("="*110, flush=True)
        print(f"GENERATION {len(seen)} COMPLETE", flush=True)
        print("="*110, flush=True)

        df = pd.read_csv(board)

        # Initialize results dictionary
        results = {}

        # Process each feature family
        for family in FEATURE_FAMILIES:
            family_df = df[df["feature_family"] == family]
            
            if family_df.empty:
                continue

            # Compute metrics
            candidate_count = len(family_df)
            average_validation_sharpe = family_df["validation_net_sharpe"].mean()
            median_validation_sharpe = family_df["validation_net_sharpe"].median()
            best_validation_sharpe = family_df["validation_net_sharpe"].max()
            average_test_sharpe = family_df["test_net_sharpe"].mean()
            best_test_sharpe = family_df["test_net_sharpe"].max()
            average_validation_return = family_df["validation_net_annualized_return"].mean()
            average_test_return = family_df["test_net_annualized_return"].mean()
            average_roc_auc = family_df["validation_roc_auc"].mean()
            average_coverage = family_df["validation_coverage"].mean()
            average_drawdown = family_df["validation_maximum_drawdown"].mean()
            top10_validation_sharpe = family_df["validation_net_sharpe"].nlargest(max(1, int(len(family_df) * 0.10))).mean()
            top25_validation_sharpe = family_df["validation_net_sharpe"].nlargest(max(1, int(len(family_df) * 0.25))).mean()

            # Calculate XP using all metrics
            xp_gain = (
                best_validation_sharpe * 100 +
                top10_validation_sharpe * 25 +
                average_validation_return * 50 +
                average_test_return * 50 +
                average_roc_auc * 100 +
                average_coverage * 100
            ).round().clip(lower=1).astype(int)

            # Store results
            results[family] = {
                "candidate_count": candidate_count,
                "average_validation_sharpe": average_validation_sharpe,
                "median_validation_sharpe": median_validation_sharpe,
                "best_validation_sharpe": best_validation_sharpe,
                "average_test_sharpe": average_test_sharpe,
                "best_test_sharpe": best_test_sharpe,
                "average_validation_return": average_validation_return,
                "average_test_return": average_test_return,
                "average_roc_auc": average_roc_auc,
                "average_coverage": average_coverage,
                "average_drawdown": average_drawdown,
                "top10_validation_sharpe": top10_validation_sharpe,
                "top25_validation_sharpe": top25_validation_sharpe,
                "xp_gain": xp_gain
            }

            # Update statistics
            xp[family] += int(xp_gain)
            gens[family] += 1
            history[family].append(float(best_validation_sharpe))
            
            if best_validation_sharpe > peak_sharpe[family]:
                peak_sharpe[family] = float(best_validation_sharpe)
                peak_generation[family] = len(seen)

            # Track rolling averages
            rolling_last_5[family].append(best_validation_sharpe)
            rolling_last_10[family].append(best_validation_sharpe)
            
            # Update trend (slope of last 5 values)
            if len(rolling_last_5[family]) >= 2:
                x = list(range(len(rolling_last_5[family])))
                y = list(rolling_last_5[family])
                # Simple linear regression slope
                n = len(x)
                if n > 1:
                    numerator = n * sum(a*b for a, b in zip(x, y)) - sum(x) * sum(y)
                    denominator = n * sum(a*a for a in x) - sum(x) ** 2
                    if denominator != 0:
                        trend[family] = numerator / denominator

            # Update average improvement
            if len(history[family]) > 1:
                improvement = history[family][-1] - history[family][-2]
                # Use exponential moving average with alpha=0.3
                alpha = 0.3
                if family in average_improvement:
                    average_improvement[family] = (alpha * improvement + 
                                                  (1 - alpha) * average_improvement[family])
                else:
                    average_improvement[family] = improvement

            # Track best candidate for this family
            best_row = family_df.loc[family_df["validation_net_sharpe"].idxmax()]
            if not best_candidate[family] or best_row["validation_net_sharpe"] > best_candidate[family].get("validation_net_sharpe", 0):
                best_candidate[family] = {
                    "generation": len(seen),
                    "validation_net_sharpe": best_row["validation_net_sharpe"],
                    "test_net_sharpe": best_row["test_net_sharpe"],
                    "validation_net_annualized_return": best_row["validation_net_annualized_return"],
                    "test_net_annualized_return": best_row["test_net_annualized_return"],
                    "candidate_id": best_row["candidate_id"]
                }

        # Print generation rankings
        print()
        print("GENERATION RANKINGS")
        print("-"*110)
        
        # Sort by XP gain
        sorted_results = sorted(results.items(), key=lambda x: x[1]["xp_gain"], reverse=True)
        
        for family, metrics in sorted_results:
            print(
                f"{family:<35}"
                f" XP+={metrics['xp_gain']:4d}"
                f" Best={metrics['best_validation_sharpe']:6.3f}"
                f" AvgTest={metrics['average_test_sharpe']:6.3f}",
                flush=True,
            )

        # Print lifetime XP
        print()
        print("LIFETIME XP")
        print("-"*110)
        
        ranking = sorted(xp.items(), key=lambda x: x[1], reverse=True)
        
        for family, total in ranking:
            avg_best = sum(history[family]) / len(history[family]) if history[family] else 0
            
            print(
                f"{family:<35}"
                f" XP={total:<6}"
                f" Gens={gens[family]:3d}"
                f" AvgBest={avg_best:6.3f}"
                f" Peak={peak_sharpe[family]:6.3f}",
                flush=True,
            )

        # Write to history file
        history_entry = {
            "generation": len(seen),
            "timestamp": time.time(),
            "results": results
        }
        
        with open(xp_history_path, "a") as f:
            f.write(json.dumps(history_entry) + "\n")

    # Update summary file
    summary = {
        "timestamp": time.time(),
        "generations_completed": len(seen),
        "feature_families": list(FEATURE_FAMILIES),
        "xp": dict(xp),
        "generations": dict(gens),
        "wins": dict(wins),
        "peak_sharpe": dict(peak_sharpe),
        "peak_generation": dict(peak_generation),
        "best_candidate": {k: v for k, v in best_candidate.items() if v},
        "rolling_last_5": {k: list(v) for k, v in rolling_last_5.items()},
        "rolling_last_10": {k: list(v) for k, v in rolling_last_10.items()},
        "trend": dict(trend),
        "average_improvement": dict(average_improvement)
    }
    
    xp_summary_path.write_text(json.dumps(summary, indent=2))

    # Update leaderboard CSV
    leaderboard_data = []
    for family in FEATURE_FAMILIES:
        if gens[family] > 0:
            avg_best = sum(history[family]) / len(history[family])
            leaderboard_data.append({
                "feature_family": family,
                "total_xp": xp[family],
                "generations": gens[family],
                "wins": wins[family],
                "average_best_sharpe": avg_best,
                "peak_sharpe": peak_sharpe[family],
                "peak_generation": peak_generation[family],
                "trend": trend[family],
                "average_improvement": average_improvement[family]
            })
    
    if leaderboard_data:
        leaderboard_df = pd.DataFrame(leaderboard_data)
        leaderboard_df = leaderboard_df.sort_values("total_xp", ascending=False)
        leaderboard_df.to_csv(xp_leaderboard_path, index=False)

    time.sleep(10)
