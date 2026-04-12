#!/usr/bin/env python3
"""
Ma v0.3 Cross-validation: Seed A runner
Overrides SEED and output path, then runs the standard v0.3 session.
"""
import ma_v03
import os
import json
import asyncio
from datetime import datetime

# Override seed for Seed A
ma_v03.SEED = "主観的経験の不可還元性は、認知系の限界なのか、構造的必然なのか？"

async def run():
    session = await ma_v03.run_session()

    # Save to seed-specific file
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        f"seed_a_raw_results_{ts}.json",
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)
    print(f"\nSeed A results saved: {out_path}")
    return session, out_path

if __name__ == "__main__":
    asyncio.run(run())
