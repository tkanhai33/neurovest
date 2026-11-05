#!/usr/bin/env python3

from pathlib import Path
from collections import defaultdict, deque
import pandas as pd
import json
import time
import os
import signal
import sys

# Global state
campaign = Path("runtime/training/exact_research_market_training_20260804_210835/campaign")
seen = set()
FEATURE_FAMILIES = {
    "base",
    "base_plus_interactions",
    "base_plus_cross_section",
    "full_evolved",
    "research_053_only",
    "market_plus_research_053",
    "full_market_plus_research_053"
}

# Initialize statistics tracking
xp = defaultdict(int)
gens = defaultdict(int)
wins = defaultdict(int)
peak_sharpe = defaultdict(float)
peak_test_sharpe = defaultdict(float)
peak_generation = defaultdict(int)
best_candidate = defaultdict(dict)
history = defaultdict(list)
rolling_last_5 = defaultdict(lambda: deque(maxlen=5))
rolling_last_10 = defaultdict(lambda: deque(maxlen=10))
trend = defaultdict(float)
average_improvement = defaultdict(float)

# Required columns for leaderboard validation
REQUIRED_COLUMNS = {
    "rank", "candidate_id", "model_name", "feature_family", "feature_count",
    "scope", "mode", "threshold", "validation_eligible", "validation_score",
    "validation_trades", "validation_coverage", "validation_accuracy_delta",
    "validation_roc_auc", "validation_net_annualized_return",
    "validation_net_sharpe", "validation_maximum_drawdown", "test_trades",
    "test_coverage", "test_accuracy_delta", "test_roc_auc",
    "test_net_annualized_return", "test_net_sharpe", "test_maximum_drawdown",
    "training_seconds", "promotion_authorized", "paper_execution_authorized",
    "broker_execution_authorized", "live_execution_authorized"
}

def handle_stop(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_stop)
signal.signal(signal.SIGINT, handle_stop)

def calculate_xp(metrics):
    """Calculate XP based on metrics with explicit weights."""
    # Base components
    validation_sharpe_xp = max(0, metrics["best_validation_sharpe"] * 100)
    test_sharpe_xp = max(0, metrics["best_test_sharpe"] * 100)
    validation_return_xp = max(0, metrics["average_validation_return"] * 50)
    test_return_xp = max(0, metrics["average_test_return"] * 50)
    roc_auc_xp = max(0, (metrics["average_validation_roc_auc"] - 0.5) * 200)
    coverage_xp = max(0, metrics["average_validation_coverage"] * 100)
    
    # Penalty for drawdowns
    drawdown_penalty = max(0, -metrics["average_validation_drawdown"] * 100)
    
    # Consistency bonus
    consistency_bonus = max(0, (metrics["positive_validation_sharpe_rate"] + 
                               metrics["positive_test_sharpe_rate"]) * 50)
    
    # Participation bonus (capped)
    participation_bonus = min(100, metrics["candidate_count"])
    
    total_xp = (
        validation_sharpe_xp +
        test_sharpe_xp +
        validation_return_xp +
        test_return_xp +
        roc_auc_xp +
        coverage_xp +
        consistency_bonus +
        participation_bonus +
        drawdown_penalty
    )
    
    return int(max(0, total_xp))

def process_leaderboard(board_path, generation):
    """Process a single leaderboard file."""
    try:
        df = pd.read_csv(board_path)
        
        # Validate required columns
        missing_cols = REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            print(f"WARNING: Missing columns in {board_path}: {missing_cols}", flush=True)
            return None
            
        # Filter for eligible candidates only
        eligible_df = df[df["validation_eligible"] == True]
        
        if eligible_df.empty:
            print(f"WARNING: No eligible candidates in {board_path}", flush=True)
            return None
            
        results = {}
        
        # Process each feature family
        for family in FEATURE_FAMILIES:
            family_df = eligible_df[eligible_df["feature_family"] == family]
            
            if family_df.empty:
                continue
                
            # Calculate metrics
            candidate_count = len(family_df)
            average_validation_sharpe = family_df["validation_net_sharpe"].mean()
            median_validation_sharpe = family_df["validation_net_sharpe"].median()
            best_validation_sharpe = family_df["validation_net_sharpe"].max()
            average_test_sharpe = family_df["test_net_sharpe"].mean()
            median_test_sharpe = family_df["test_net_sharpe"].median()
            best_test_sharpe = family_df["test_net_sharpe"].max()
            average_validation_return = family_df["validation_net_annualized_return"].mean()
            average_test_return = family_df["test_net_annualized_return"].mean()
            average_validation_roc_auc = family_df["validation_roc_auc"].mean()
            average_test_roc_auc = family_df["test_roc_auc"].mean()
            average_validation_coverage = family_df["validation_coverage"].mean()
            average_test_coverage = family_df["test_coverage"].mean()
            average_validation_drawdown = family_df["validation_maximum_drawdown"].mean()
            average_test_drawdown = family_df["test_maximum_drawdown"].mean()
            
            # Calculate top percentages
            top10_validation_sharpe = family_df["validation_net_sharpe"].nlargest(max(1, int(len(family_df) * 0.10))).mean()
            top25_validation_sharpe = family_df["validation_net_sharpe"].nlargest(max(1, int(len(family_df) * 0.25))).mean()
            
            # Calculate positive Sharpe rates
            positive_validation_sharpe_rate = (family_df["validation_net_sharpe"] > 0).mean()
            positive_test_sharpe_rate = (family_df["test_net_sharpe"] > 0).mean()
            
            # Store metrics
            metrics = {
                "candidate_count": candidate_count,
                "average_validation_sharpe": average_validation_sharpe,
                "median_validation_sharpe": median_validation_sharpe,
                "best_validation_sharpe": best_validation_sharpe,
                "average_test_sharpe": average_test_sharpe,
                "median_test_sharpe": median_test_sharpe,
                "best_test_sharpe": best_test_sharpe,
                "average_validation_return": average_validation_return,
                "average_test_return": average_test_return,
                "average_validation_roc_auc": average_validation_roc_auc,
                "average_test_roc_auc": average_test_roc_auc,
                "average_validation_coverage": average_validation_coverage,
                "average_test_coverage": average_test_coverage,
                "average_validation_drawdown": average_validation_drawdown,
                "average_test_drawdown": average_test_drawdown,
                "top10_validation_sharpe": top10_validation_sharpe,
                "top25_validation_sharpe": top25_validation_sharpe,
                "eligible_candidate_count": candidate_count,
                "positive_validation_sharpe_rate": positive_validation_sharpe_rate,
                "positive_test_sharpe_rate": positive_test_sharpe_rate
            }
            
            # Calculate XP
            xp_gain = calculate_xp(metrics)
            
            results[family] = {
                "metrics": metrics,
                "xp_gain": xp_gain
            }
            
            # Update statistics
            xp[family] += int(xp_gain)
            gens[family] += 1
            history[family].append(float(best_validation_sharpe))
            
            if best_validation_sharpe > peak_sharpe[family]:
                peak_sharpe[family] = float(best_validation_sharpe)
                peak_test_sharpe[family] = float(best_test_sharpe)
                peak_generation[family] = generation

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
                    "generation": generation,
                    "validation_net_sharpe": best_row["validation_net_sharpe"],
                    "test_net_sharpe": best_row["test_net_sharpe"],
                    "validation_net_annualized_return": best_row["validation_net_annualized_return"],
                    "test_net_annualized_return": best_row["test_net_annualized_return"],
                    "candidate_id": best_row["candidate_id"],
                    "model_name": best_row["model_name"],
                    "scope": best_row["scope"],
                    "mode": best_row["mode"]
                }
            
        return results
        
    except Exception as e:
        print(f"ERROR processing {board_path}: {e}", flush=True)
        return None

def write_json_atomic(path, data):
    """Write JSON data atomically."""
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with open(temp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(temp_path, path)

def write_csv_atomic(path, df):
    """Write CSV data atomically."""
    temp_path = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(temp_path, index=False)
    os.replace(temp_path, path)

def rebuild_state():
    """Rebuild state from all existing completed generations."""
    print("Rebuilding state from existing generations...", flush=True)
    
    # Reset state
    global xp, gens, wins, peak_sharpe, peak_test_sharpe, peak_generation, best_candidate, history, rolling_last_5, rolling_last_10, trend, average_improvement
    xp.clear()
    gens.clear()
    wins.clear()
    peak_sharpe.clear()
    peak_test_sharpe.clear()
    peak_generation.clear()
    best_candidate.clear()
    history.clear()
    rolling_last_5.clear()
    rolling_last_10.clear()
    trend.clear()
    average_improvement.clear()
    
    # Process all completed generations
    boards = sorted(campaign.glob("generations/generation_*/output/evolution_leaderboard.csv"))
    
    for board in boards:
        if str(board) not in seen:
            seen.add(str(board))
            result = process_leaderboard(board, len(seen))
            if result is None:
                print(f"Failed to process {board}", flush=True)
    
    print("State rebuilt successfully.", flush=True)

def print_generation_rankings(results, generation):
    """Print generation rankings."""
    print()
    print("="*110)
    print(f"GENERATION {generation} COMPLETE")
    print("="*110)
    
    print()
    print("GENERATION RANKINGS")
    print("-"*110)
    
    # Sort by XP gain
    sorted_results = sorted(results.items(), key=lambda x: x[1]["xp_gain"], reverse=True)
    
    for family, data in sorted_results:
        print(
            f"{family:<35}"
            f" XP+={data['xp_gain']:4d}"
            f" Best={data['metrics']['best_validation_sharpe']:6.3f}"
            f" AvgTest={data['metrics']['average_test_sharpe']:6.3f}",
            flush=True,
        )

def print_lifetime_leaderboard():
    """Print lifetime leaderboard."""
    print()
    print("LIFETIME XP")
    print("-"*110)
    
    # Calculate win rate and average generation XP
    win_rate = {}
    avg_generation_xp = {}
    
    for family in FEATURE_FAMILIES:
        if gens[family] > 0:
            win_rate[family] = wins[family] / gens[family] if gens[family] > 0 else 0
            avg_generation_xp[family] = xp[family] / gens[family] if gens[family] > 0 else 0
    
    # Sort by total XP
    ranking = sorted(xp.items(), key=lambda x: x[1], reverse=True)
    
    for family, total in ranking:
        avg_best = sum(history[family]) / len(history[family]) if history[family] else 0
        
        print(
            f"{family:<35}"
            f" XP={total:<6}"
            f" Gens={gens[family]:3d}"
            f" Wins={wins[family]:2d}"
            f" WinRate={win_rate.get(family, 0):.2f}"
            f" AvgGenXP={avg_generation_xp.get(family, 0):6.1f}",
            flush=True,
        )

def update_artifacts(generation, results):
    """Update all artifacts."""
    # Write history file
    history_entry = {
        "generation": generation,
        "timestamp": time.time(),
        "results": {family: data["metrics"] for family, data in results.items()}
    }
    
    history_path = campaign / "xp_history.jsonl"
    with open(history_path, "a") as f:
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
        "peak_test_sharpe": dict(peak_test_sharpe),
        "peak_generation": dict(peak_generation),
        "best_candidate": {k: v for k, v in best_candidate.items() if v},
        "rolling_last_5": {k: list(v) for k, v in rolling_last_5.items()},
        "rolling_last_10": {k: list(v) for k, v in rolling_last_10.items()},
        "trend": dict(trend),
        "average_improvement": dict(average_improvement)
    }
    
    summary_path = campaign / "xp_summary.json"
    write_json_atomic(summary_path, summary)

    # Update leaderboard CSV
    leaderboard_data = []
    for family in FEATURE_FAMILIES:
        if gens[family] > 0:
            avg_best = sum(history[family]) / len(history[family]) if history[family] else 0
            leaderboard_data.append({
                "feature_family": family,
                "total_xp": xp[family],
                "generations_participated": gens[family],
                "wins": wins[family],
                "win_rate": wins[family] / gens[family] if gens[family] > 0 else 0,
                "average_generation_xp": xp[family] / gens[family] if gens[family] > 0 else 0,
                "rolling_last_5_xp": list(rolling_last_5[family]),
                "rolling_last_10_xp": list(rolling_last_10[family]),
                "rolling_last_5_best_validation_sharpe": list(rolling_last_5[family]),
                "rolling_last_10_best_validation_sharpe": list(rolling_last_10[family]),
                "peak_validation_sharpe": peak_sharpe[family],
                "peak_test_sharpe": peak_test_sharpe[family],
                "peak_generation": peak_generation[family],
                "trend": trend[family],
                "average_improvement": average_improvement[family]
            })
    
    if leaderboard_data:
        leaderboard_df = pd.DataFrame(leaderboard_data)
        leaderboard_df = leaderboard_df.sort_values("total_xp", ascending=False)
        leaderboard_path = campaign / "xp_leaderboard.csv"
        write_csv_atomic(leaderboard_path, leaderboard_df)

def main():
    """Main tracking loop."""
    print("="*110, flush=True)
    print("NEUROVEST EVOLUTION XP TRACKER V2", flush=True)
    print("="*110, flush=True)
    
    # Ensure campaign directories exist
    campaign.mkdir(parents=True, exist_ok=True)
    
    # Check if --once flag is used
    once_mode = "--once" in sys.argv
    
    # Rebuild state from existing generations
    rebuild_state()
    
    # Print initial leaderboard
    print_generation_rankings({}, 0)  # Placeholder for initial state
    print_lifetime_leaderboard()
    
    # If in --once mode, exit after rebuilding
    if once_mode:
        print("Exiting after rebuilding state (--once mode).", flush=True)
        return 0
    
    # Start monitoring loop
    print("Starting monitoring loop...", flush=True)
    
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
            result = process_leaderboard(board, len(seen))
            if result is None:
                print(f"Failed to process {board}", flush=True)
                continue
                
            print_generation_rankings(result, len(seen))
            
            # Determine winner (family with highest XP gain)
            winner_family = max(result.keys(), key=lambda f: result[f]["xp_gain"])
            xp_gain = result[winner_family]["xp_gain"]
            
            if xp_gain > 0:
                wins[winner_family] += 1
                print(f"Generation {len(seen)} winner: {winner_family} (+{xp_gain} XP)", flush=True)
            
            # Update artifacts
            update_artifacts(len(seen), result)
        
        # Print lifetime leaderboard periodically
        if len(seen) % 5 == 0:
            print_lifetime_leaderboard()
        
        time.sleep(10)

if __name__ == "__main__":
    raise SystemExit(main())
