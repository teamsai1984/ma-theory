#!/usr/bin/env python3
"""
Ma v0.3 Cross-validation: Seed C runner
"""
import ma_v03
import os
import json
import asyncio
from datetime import datetime

ma_v03.SEED = "経済的合理性と倫理的判断は、原理的に両立可能か？"

async def run():
    session = await ma_v03.run_session()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        f"seed_c_raw_results_{ts}.json",
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)
    print(f"\nSeed C results saved: {out_path}")
    return session, out_path

if __name__ == "__main__":
    asyncio.run(run())
