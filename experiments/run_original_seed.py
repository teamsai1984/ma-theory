#!/usr/bin/env python3
"""
Ma v0.3: Original seed re-execution
Saves to a dedicated file to avoid overwriting.
"""
import ma_v03
import os
import json
import asyncio
from datetime import datetime

# Original seed (default in ma_v03.py, but set explicitly)
ma_v03.SEED = "人間の認知が及ばない認知系との接触から、どのような創発が生まれうるか？"

async def run():
    session = await ma_v03.run_session()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        f"original_seed_raw_results_{ts}.json",
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)
    print(f"\nOriginal seed results saved: {out_path}")
    return session, out_path

if __name__ == "__main__":
    asyncio.run(run())
