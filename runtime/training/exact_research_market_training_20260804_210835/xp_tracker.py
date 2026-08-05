#!/usr/bin/env python3

from pathlib import Path
from collections import defaultdict
import pandas as pd
import json
import time
import os

campaign = Path("runtime/training/exact_research_market_training_20260804_210835/campaign")

seen=set()

xp=defaultdict(int)
gens=defaultdict(int)
peak=defaultdict(lambda:-999.0)
history=defaultdict(list)

print("="*110,flush=True)
print("NEUROVEST EVOLUTION XP TRACKER V2",flush=True)
print("="*110,flush=True)

while True:

    progress=campaign/"progress.json"

    if progress.exists():
        try:
            p=json.loads(progress.read_text())
            cg=p.get("current_generation",{}).get("generation","?")
            print(f"[{time.strftime('%H:%M:%S')}] Current Generation {cg}",flush=True)
        except:
            pass

    boards=sorted(campaign.glob("generations/generation_*/output/evolution_leaderboard.csv"))

    for board in boards:

        if str(board) in seen:
            continue

        seen.add(str(board))

        df=pd.read_csv(board)

        grouped=(
            df.groupby("feature_family")
              .agg(
                  best=("validation_net_sharpe","max"),
                  median=("validation_net_sharpe","median"),
                  top10=("validation_net_sharpe",
                         lambda s: s.nlargest(max(1,int(len(s)*0.10))).mean()),
                  candidates=("validation_net_sharpe","count"),
              )
        )

        grouped["xp_gain"]=(grouped["best"]*100+grouped["top10"]*25).round().clip(lower=1).astype(int)
        grouped=grouped.sort_values("xp_gain",ascending=False)

        print()
        print("="*110,flush=True)
        print(f"GENERATION {len(seen)} COMPLETE",flush=True)
        print("="*110,flush=True)

        print()
        print("GENERATION RANKINGS")
        print("-"*110)

        for family,row in grouped.iterrows():

            xp[family]+=int(row["xp_gain"])
            gens[family]+=1
            history[family].append(float(row["best"]))

            if row["best"]>peak[family]:
                peak[family]=float(row["best"])

            print(
                f"{family:<35}"
                f" XP+={int(row["xp_gain"]):4d}"
                f" Best={row["best"]:6.3f}"
                f" Top10={row["top10"]:6.3f}"
                f" Median={row["median"]:6.3f}"
                f" Cand={int(row["candidates"]):4d}",
                flush=True,
            )

        print()
        print("LIFETIME XP")
        print("-"*110)

        ranking=sorted(xp.items(),key=lambda x:x[1],reverse=True)

        for family,total in ranking:

            avg_best=sum(history[family])/len(history[family])

            print(
                f"{family:<35}"
                f" XP={total:<6}"
                f" Gens={gens[family]:3d}"
                f" AvgBest={avg_best:6.3f}"
                f" Peak={peak[family]:6.3f}",
                flush=True,
            )

    time.sleep(10)
