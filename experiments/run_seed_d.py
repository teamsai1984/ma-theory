#!/usr/bin/env python3
"""
Ma v0.3 Cross-validation: Seed D runner
Domain: 言語・情報
Strategy: 反例要求 → 固有構造衝突
"""
import ma_v03
import os
import json
import asyncio
from datetime import datetime

# Override seed for Seed D
ma_v03.SEED = "言語は思考を制約するのか、思考が言語を超越するのか？"

async def run():
    session = await ma_v03.run_session()

    # Save to seed-specific file
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        f"seed_d_raw_results_{ts}.json",
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)
    print(f"\nSeed D results saved: {out_path}")
    return session, out_path

if __name__ == "__main__":
    asyncio.run(run())
