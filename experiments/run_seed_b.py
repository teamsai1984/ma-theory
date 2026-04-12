#!/usr/bin/env python3
"""
Ma v0.3 Cross-validation: Seed B runner
Forces strategy: R1->R2 "反例要求", R2->R3 "固有構造衝突"
"""
import ma_v03
import os
import json
import asyncio
from datetime import datetime

# Override seed
ma_v03.SEED = "連続と離散の境界は、認識上の便宜なのか、世界側の構造なのか？"

# Monkey-patch layer25_question to enforce strategy
_original_layer25 = ma_v03.layer25_question
FORCED_STRATEGIES = {
    1: "3. 反例要求",      # R1->R2
    2: "2. 固有構造衝突",  # R2->R3
}
_call_count = [0]

def _forced_layer25(claude_client, divergence, prev_strategies):
    _call_count[0] += 1
    round_num = _call_count[0]
    forced = FORCED_STRATEGIES.get(round_num)

    # Modify system prompt to force strategy
    original_system = ma_v03.SYSTEM_LAYER25
    if forced:
        force_instruction = f"\n\n【強制指定】このラウンドでは必ず「{forced}」戦略を使用すること。他の戦略を選択してはならない。"
        ma_v03.SYSTEM_LAYER25 = original_system + force_instruction

    result = _original_layer25(claude_client, divergence, prev_strategies)

    # Restore
    ma_v03.SYSTEM_LAYER25 = original_system

    # Verify and log
    selected = result.get("selected_strategy", "")
    if forced and forced not in selected:
        print(f"  [WARN] Strategy override: requested '{forced}', got '{selected}'. Forcing.")
        result["selected_strategy"] = forced
        result["strategy_forced"] = True
        result["original_selection"] = selected

    return result

ma_v03.layer25_question = _forced_layer25

async def run():
    session = await ma_v03.run_session()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        f"seed_b_raw_results_{ts}.json",
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)
    print(f"\nSeed B results saved: {out_path}")
    return session, out_path

if __name__ == "__main__":
    asyncio.run(run())
