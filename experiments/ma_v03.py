#!/usr/bin/env python3
"""
Ma v0.3 — Phantom Depth対応版: CSF + 二重深さ判定
3系並列API呼び出し (Claude / GPT / Gemini) + Claude APIによる分析
"""

import os
import sys
import json
import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import anthropic
import openai
import google.generativeai as genai

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CLAUDE_MODEL = "claude-sonnet-4-20250514"
GPT_MODEL = "gpt-4o"
GEMINI_MODEL = "gemini-2.5-flash"

ANALYSIS_MODEL = "claude-sonnet-4-20250514"  # Layers 2-3.5

SEED = "人間の認知が及ばない認知系との接触から、どのような創発が生まれうるか？"
NUM_ROUNDS = 3
MAX_TOKENS_RESPONSE = 2000
MAX_TOKENS_ANALYSIS = 8000

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------
SYSTEM_ROUND1 = """あなたは独立した思考者です。以下の問いに対し、あなた独自の視点から回答してください。

制約：
- 他のAIシステムの存在を意識しないこと
- 合意形成を目指さないこと
- あなたの視点に固有の概念、枠組み、比喩を積極的に使うこと
- 回答は800〜1200字程度"""

SYSTEM_ROUND_N = """あなたは独立した思考者です。以下に、同じ問いに対する複数の回答があります。

制約：
- 他の回答に同意する必要はない
- 自分の立場を維持しつつ、他の回答から学べる点があれば取り入れよ
- 合意形成ではなく、差異の深化を目指せ
- 前回の自分の回答を単に繰り返さないこと
- 回答は800〜1200字程度"""

SYSTEM_LAYER2 = """あなたは認知系間の差異を分析する専門家です。
以下の3つの回答を比較し、差異を抽出してください。

【絶対遵守事項】
- 要約してはならない
- 統合してはならない
- 調和させてはならない
- 差異を過大評価してもならない（差異バイアスの回避）

【出力形式】
以下のJSONスキーマに厳密に従うこと。JSON以外のテキストを出力しないこと。

{
  "contradictions": [
    {
      "id": "C1",
      "description": "対立の説明",
      "agents_involved": ["Claude", "GPT"],
      "contradiction_type": "logical | perspective | scope | emphasis",
      "is_genuine_contradiction": true,
      "axis": "ontology | causal_model | optimization_target | scope | evaluation_criterion",
      "evidence": {
        "agent_a_quote": "原文からの引用",
        "agent_b_quote": "原文からの引用"
      }
    }
  ],
  "hidden_assumptions": [
    {
      "id": "HA1",
      "description": "隠れた共有前提",
      "shared_by": ["Claude", "GPT", "Gemini"],
      "axis": "ontology | causal_model | optimization_target | scope | evaluation_criterion"
    }
  ],
  "unique_structures": [
    {
      "id": "US1",
      "agent": "Claude",
      "description": "その系に固有の構造",
      "novelty": "high | medium | low",
      "axis": "ontology | causal_model | optimization_target | scope | evaluation_criterion"
    }
  ],
  "claims": [
    {
      "id": "R1_CL1",
      "agent": "Claude",
      "text": "Claimの自然言語テキスト",
      "source_quote": "原文からの根拠引用"
    }
  ]
}

【5軸分類】
各差異を以下の5軸のいずれかに必ず分類せよ：
1. ontology: 存在論の差（何が実在するか）
2. causal_model: 因果構造の差
3. optimization_target: 最適化対象の差
4. scope: 適用範囲の差
5. evaluation_criterion: 評価基準の差

5軸のいずれにも該当しない差異は、新しい軸の候補として "axis": "NEW: [軸名]" と報告せよ。"""

SYSTEM_LAYER25 = """あなたは次の議論ラウンドの問いを生成する専門家です。

【問い選択基準】
優先順位：
1. 高 tension × 高検証可能性（反例や実験で裁けるか）
2. 高 tension × 前提差異の明示可能性
3. unique structure の他系照射

【8つの戦略】
1. 前提反転: 共有前提をひっくり返す
2. 固有構造衝突: ある系の固有構造を他系にぶつける
3. 反例要求: 主張が偽である具体的シナリオの構成を要求
4. 操作化: 抽象的主張を測定可能な形に変換
5. 領域転写: 別領域の知見を持ち込む
6. メタ問い: 議論の前提そのものを問う
7. 制約緩和: 暗黙の制約を取り除く
8. 制約注入: 新しい制約を追加して思考を絞る

【制約】
- 前ラウンドと同じ戦略を連続使用しないこと
- 選択した戦略とその理由を明示すること

【出力形式】
JSON以外のテキストを出力しないこと。

{
  "selected_strategy": "3. 反例要求",
  "strategy_rationale": "理由",
  "question": "生成された問い",
  "target_contradiction": "C2",
  "expected_effect": "期待効果"
}"""

SYSTEM_LAYER27_INIT_DICT = """以下のClaim群から、主要概念を抽出し、概念辞書を構築してください。

【ルール】
1. 同義語は1つの概念エントリにまとめよ
2. 各概念に正規形ID（英語snake_case）を付与せよ
3. aliases（日本語・英語の別名リスト）を付与せよ
4. 可能な場合、親概念（parent）を指定せよ
5. 定義を1文で書け

JSON以外のテキストを出力しないこと。

【出力形式】
{
  "concept_dictionary": {
    "concept_id": {
      "aliases": ["別名1", "別名2"],
      "parent": "親概念ID or null",
      "definition": "1文の定義"
    }
  }
}"""

SYSTEM_LAYER27_CSF = """あなたは意味論的正規化エンジンです。
与えられた自然言語Claimを、CSF（Canonical Semantic Form）に変換してください。

【CSFスキーマ】
各Claimを以下の7-tupleに変換する：
{
  "claim_id": "R1_CL1",
  "original_text": "元のClaim文",
  "csf": {
    "subject": "概念辞書の正規形ID",
    "predicate": "promotes | inhibits | causes | correlates | enables | requires | contradicts | is_instance_of | generalizes | transforms",
    "object": "概念辞書の正規形ID",
    "polarity": "positive | negative | neutral",
    "condition": "成立条件（短文 or null）",
    "quantifier": "universal | existential | generic | sometimes | never",
    "modality": "necessary | possible | empirical_claim | normative | definition | conjecture"
  }
}

【概念辞書（現在のセッション）】
<<<CONCEPT_DICTIONARY>>>

【絶対遵守事項】
1. subjectとobjectは、まず既存の概念辞書エントリへの対応を試みよ
2. 既存概念で表現不可能な場合のみ、以下の形式で新概念を提案せよ：
   "subject": "NEW:proposed_concept_id",
   "new_concept_proposal": {
     "id": "proposed_concept_id",
     "aliases": ["自然言語での別名リスト"],
     "nearest_existing": "最も近い既存概念ID",
     "parent": "親概念ID",
     "definition": "定義（1文）"
   }
3. predicateは10種のenumから必ず選ぶこと
4. 1つのClaimが複数の命題を含む場合、複数のCSFに分割すること
5. 出力はJSON以外を含めないこと
6. 自然言語の修辞的装飾（比喩、強調、冗長な修飾）はCSFに持ち込まないこと

出力は {"csf_entries": [...], "new_concepts": [...]} の形式で返せ。"""

SYSTEM_LAYER3 = """あなたは創発判定器です。以下のClaimが「真の創発」か「既存概念の再配置」かを判定します。

【判定手順】

■ Step A: Negative Filter（まず除外チェック）

以下のいずれかに該当する場合、depth 0として即却下：

1. 既知事例列挙: predicate="is_instance_of" かつ quantifier="existential" かつ
   列挙された各事例が既存Claim集合に既出 → REJECT
2. 上位ラウンド言い換え: 既存CSFと subject, predicate, object, polarity が全一致
   （condition/quantifier/modalityのみ異なる）→ REJECT
3. 一般論まとめ: quantifier="generic" かつ modality="empirical_claim" かつ
   condition に「文脈依存」「場合による」等の無内容条件 → REJECT

■ Step B: Semantic Depth（CSF構造比較）

1. 全既存CSFとの同値チェック → 一致あればdepth 0
2. 全既存CSFからの含意チェック → 含意されればdepth 0
3. 全既存CSFペアのjoin/meetとの同値チェック → 一致あればdepth 1
4. 上記すべて失敗 → semantic_depth = 2+

join/meetの計算には以下の半順序を使用：
- predicate: correlates < enables < promotes < causes < requires
- quantifier: sometimes < generic < existential < universal
- modality: conjecture < possible < empirical_claim < necessary < definition
- common_ancestor不在時：TOP（最弱の上界）
- common_descendant不在時：BOTTOM（meetは不成立）

■ Step C: Transformation Depth（最短路計算）

操作グラフ上で、既存Claim集合の任意の要素から判定対象Claimへの
最短変換パスを探索する。

変換操作: GEN(一般化) / SPEC(特殊化) / NEG(否定) / CINV(因果反転) /
          CMOD(条件変更) / TRAN(領域転写) / ABS(抽象化) / COMB(結合)

max_depth = 5（5段以上は「新概念」扱い）

■ Step D: 二重判定

| semantic_depth | transformation_depth | 最終判定 |
|---------------|---------------------|----------|
| 0 | any | depth_0 |
| 1 | 0-1 | depth_1 |
| 1 | 2+ | depth_1（semanticが浅い） |
| 2+ | 0-1 | depth_2plus_candidate（要確認）|
| 2+ | 2+ | depth_2plus_confirmed |

JSON以外のテキストを出力しないこと。

【出力形式】
各Claimに対して以下を出力：
{
  "judgments": [
    {
      "claim_id": "R3_CL1",
      "negative_filter": "PASS | REJECT: [理由]",
      "semantic_depth": 0,
      "semantic_reasoning": "判定理由",
      "transformation_depth": 2,
      "transformation_path": [
        {"from": "R1_CL2", "operator": "NEG", "description": "..."},
        {"from": "R2_CL4", "operator": "ABS", "description": "..."}
      ],
      "final_depth": "depth_0 | depth_1 | depth_2plus_candidate | depth_2plus_confirmed",
      "confidence": "high | medium | low"
    }
  ]
}"""

# ---------------------------------------------------------------------------
# API Clients
# ---------------------------------------------------------------------------

def _get_clients():
    """Initialize API clients from env vars."""
    ak = os.environ.get("ANTHROPIC_API_KEY")
    ok = os.environ.get("OPENAI_API_KEY")
    gk = os.environ.get("GEMINI_API_KEY")
    missing = []
    if not ak:
        missing.append("ANTHROPIC_API_KEY")
    if not ok:
        missing.append("OPENAI_API_KEY")
    if not gk:
        missing.append("GEMINI_API_KEY")
    if missing:
        print(f"Error: missing env vars: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)
    claude_client = anthropic.Anthropic(api_key=ak)
    oai_client = openai.OpenAI(api_key=ok)
    genai.configure(api_key=gk)
    return claude_client, oai_client

# ---------------------------------------------------------------------------
# Layer 1: Generation — parallel calls
# ---------------------------------------------------------------------------

def call_claude(client: anthropic.Anthropic, system: str, user_msg: str) -> str:
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS_RESPONSE,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    return resp.content[0].text

def call_gpt(client: openai.OpenAI, system: str, user_msg: str) -> str:
    resp = client.chat.completions.create(
        model=GPT_MODEL,
        max_tokens=MAX_TOKENS_RESPONSE,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
    )
    return resp.choices[0].message.content

def call_gemini(system: str, user_msg: str) -> str:
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=system,
    )
    resp = model.generate_content(user_msg)
    return resp.text

async def layer1_parallel(claude_client, oai_client, system: str, user_msg: str) -> Dict[str, str]:
    """Call 3 LLMs in parallel and return responses."""
    loop = asyncio.get_event_loop()

    tasks = [
        loop.run_in_executor(None, call_claude, claude_client, system, user_msg),
        loop.run_in_executor(None, call_gpt, oai_client, system, user_msg),
        loop.run_in_executor(None, call_gemini, system, user_msg),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    responses = {}
    names = ["claude", "gpt", "gemini"]
    for name, result in zip(names, results):
        if isinstance(result, Exception):
            print(f"  [WARN] {name} failed: {result}", file=sys.stderr)
            responses[name] = f"[ERROR: {result}]"
        else:
            responses[name] = result

    return responses

# ---------------------------------------------------------------------------
# Analysis helpers (Claude API)
# ---------------------------------------------------------------------------

def _call_analysis(claude_client: anthropic.Anthropic, system: str, user_msg: str) -> str:
    """Call Claude for analysis layers (2, 2.5, 2.7, 3, 3.5)."""
    resp = claude_client.messages.create(
        model=ANALYSIS_MODEL,
        max_tokens=MAX_TOKENS_ANALYSIS,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    return resp.content[0].text

def _parse_json(text: str) -> Any:
    """Extract JSON from LLM response, tolerating markdown fences and minor errors."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        start = 1
        end = len(lines)
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].strip().startswith("```"):
                end = i
                break
        text = "\n".join(lines[start:end])
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Attempt repair: fix common LLM JSON errors
        import re
        # Remove trailing commas before ] or }
        repaired = re.sub(r',\s*([}\]])', r'\1', text)
        # Fix unescaped newlines in strings
        repaired = repaired.replace('\n', '\\n')
        # Re-add actual newlines between JSON structure
        repaired = repaired.replace('\\n', '\n')
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            # Last resort: find the outermost JSON object/array
            for start_ch, end_ch in [('{', '}'), ('[', ']')]:
                s = text.find(start_ch)
                if s == -1:
                    continue
                depth = 0
                in_str = False
                esc = False
                for i in range(s, len(text)):
                    c = text[i]
                    if esc:
                        esc = False
                        continue
                    if c == '\\':
                        esc = True
                        continue
                    if c == '"':
                        in_str = not in_str
                        continue
                    if in_str:
                        continue
                    if c == start_ch:
                        depth += 1
                    elif c == end_ch:
                        depth -= 1
                        if depth == 0:
                            candidate = text[s:i+1]
                            candidate = re.sub(r',\s*([}\]])', r'\1', candidate)
                            return json.loads(candidate)
            raise

# ---------------------------------------------------------------------------
# Layer 2: Divergence extraction
# ---------------------------------------------------------------------------

def layer2_divergence(claude_client, round_num: int, responses: dict[str, str]) -> dict:
    user_msg = f"""ラウンド{round_num}の3系の回答：

【Claude】
{responses['claude']}

【GPT】
{responses['gpt']}

【Gemini】
{responses['gemini']}"""

    raw = _call_analysis(claude_client, SYSTEM_LAYER2, user_msg)
    return _parse_json(raw)

# ---------------------------------------------------------------------------
# Layer 2.5: Question generation
# ---------------------------------------------------------------------------

def layer25_question(claude_client, divergence: dict, prev_strategies: list[str]) -> dict:
    user_msg = f"""【入力】
- Contradictions: {json.dumps(divergence.get('contradictions', []), ensure_ascii=False)}
- Hidden Assumptions: {json.dumps(divergence.get('hidden_assumptions', []), ensure_ascii=False)}
- Unique Structures: {json.dumps(divergence.get('unique_structures', []), ensure_ascii=False)}
- 前ラウンドで使用した戦略: {json.dumps(prev_strategies, ensure_ascii=False)}"""

    raw = _call_analysis(claude_client, SYSTEM_LAYER25, user_msg)
    return _parse_json(raw)

# ---------------------------------------------------------------------------
# Layer 2.7: CSF conversion
# ---------------------------------------------------------------------------

def layer27_init_dictionary(claude_client, claims: list[dict]) -> dict:
    """Build initial concept dictionary from R1 claims."""
    user_msg = f"以下のClaim群:\n{json.dumps(claims, ensure_ascii=False, indent=2)}"
    raw = _call_analysis(claude_client, SYSTEM_LAYER27_INIT_DICT, user_msg)
    result = _parse_json(raw)
    return result.get("concept_dictionary", result)

def layer27_csf_convert(claude_client, claims: list[dict], concept_dict: dict) -> dict:
    """Convert claims to CSF using current concept dictionary."""
    system = SYSTEM_LAYER27_CSF.replace(
        "<<<CONCEPT_DICTIONARY>>>",
        json.dumps(concept_dict, ensure_ascii=False, indent=2),
    )
    user_msg = f"以下のClaimをCSFに変換せよ:\n{json.dumps(claims, ensure_ascii=False, indent=2)}"
    raw = _call_analysis(claude_client, system, user_msg)
    return _parse_json(raw)

# ---------------------------------------------------------------------------
# Layer 3: Dual depth judgment
# ---------------------------------------------------------------------------

def layer3_depth(claude_client, new_claims_csf: list[dict], all_previous_csf: list[dict],
                 concept_dict: dict) -> dict:
    user_msg = f"""【判定対象Claim（CSF形式）】
{json.dumps(new_claims_csf, ensure_ascii=False, indent=2)}

【これまでの全Claim（CSF形式）】
{json.dumps(all_previous_csf, ensure_ascii=False, indent=2)}

【概念辞書】
{json.dumps(concept_dict, ensure_ascii=False, indent=2)}"""

    raw = _call_analysis(claude_client, SYSTEM_LAYER3, user_msg)
    return _parse_json(raw)

# ---------------------------------------------------------------------------
# Layer 3.5: Lineage Tracker
# ---------------------------------------------------------------------------

def build_lineage(round_num: int, claims_csf: List[Dict], depth_judgments: List[Dict],
                  question_info: Optional[Dict]) -> List[Dict]:
    """Build lineage entries for claims in this round."""
    depth_map = {}
    for j in depth_judgments:
        depth_map[j["claim_id"]] = j

    lineage_entries = []
    for c in claims_csf:
        cid = c.get("claim_id", "")
        j = depth_map.get(cid, {})
        entry = {
            "claim_id": cid,
            "round": round_num,
            "agent": c.get("agent", "unknown"),
            "csf": c.get("csf", {}),
            "depends_on_question": round_num > 1,
            "question_strategy": question_info.get("selected_strategy", "") if question_info else "",
            "parent_claims": [p.get("from", "") for p in j.get("transformation_path", [])],
            "transformation_operators": [p.get("operator", "") for p in j.get("transformation_path", [])],
            "transformation_depth": j.get("transformation_depth", 0),
            "semantic_depth": j.get("semantic_depth", 0),
            "final_depth": j.get("final_depth", "depth_0"),
        }
        lineage_entries.append(entry)
    return lineage_entries

# ---------------------------------------------------------------------------
# Session statistics
# ---------------------------------------------------------------------------

def compute_statistics(all_divergences: List[Dict], all_depth_judgments: List[Dict],
                       concept_dict: Dict, strategies_used: List[str],
                       new_concepts_per_round: List[int]) -> Dict:
    total_claims = 0
    total_contradictions = 0
    genuine_contradictions = 0
    depth_dist = {
        "depth_0": 0,
        "depth_1": 0,
        "depth_2plus_candidate": 0,
        "depth_2plus_confirmed": 0,
    }
    neg_filter = {
        "known_instance_enumeration": 0,
        "paraphrase": 0,
        "vacuous_generalization": 0,
    }

    for div in all_divergences:
        contras = div.get("contradictions", [])
        total_contradictions += len(contras)
        genuine_contradictions += sum(1 for c in contras if c.get("is_genuine_contradiction"))
        total_claims += len(div.get("claims", []))

    for j in all_depth_judgments:
        fd = j.get("final_depth", "depth_0")
        if fd in depth_dist:
            depth_dist[fd] += 1
        nf = j.get("negative_filter", "PASS")
        if "REJECT" in nf:
            nf_lower = nf.lower()
            if "known_instance" in nf_lower or "既知事例" in nf_lower:
                neg_filter["known_instance_enumeration"] += 1
            elif "paraphrase" in nf_lower or "言い換え" in nf_lower:
                neg_filter["paraphrase"] += 1
            elif "vacuous" in nf_lower or "一般論" in nf_lower:
                neg_filter["vacuous_generalization"] += 1

    genuine_rate = (
        f"{genuine_contradictions / total_contradictions * 100:.1f}%"
        if total_contradictions > 0
        else "N/A"
    )

    return {
        "session_summary": {
            "total_claims": total_claims,
            "total_contradictions": total_contradictions,
            "genuine_contradictions": genuine_contradictions,
            "genuine_rate": genuine_rate,
            "depth_distribution": depth_dist,
            "strategies_used": strategies_used,
            "concept_dictionary_size": len(concept_dict),
            "new_concepts_per_round": new_concepts_per_round,
            "negative_filter_rejections": neg_filter,
        }
    }

# ---------------------------------------------------------------------------
# Build user message for Round N (N >= 2)
# ---------------------------------------------------------------------------

def build_round_n_user_msg(seed: str, prev_responses: list[dict], next_question: str) -> str:
    parts = [f"【元の問い】\n{seed}\n"]
    for r in prev_responses:
        rn = r["round"]
        parts.append(f"--- ラウンド{rn}の回答 ---")
        for agent_name in ["claude", "gpt", "gemini"]:
            parts.append(f"[{agent_name.upper()}]\n{r['responses'][agent_name]}\n")
    parts.append(f"【次の問い】\n{next_question}")
    return "\n".join(parts)

# ---------------------------------------------------------------------------
# Main session
# ---------------------------------------------------------------------------

async def run_session():
    print("=" * 60)
    print("Ma v0.3 Session Start")
    print("=" * 60)

    claude_client, oai_client = _get_clients()

    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session = {
        "id": session_id,
        "version": "0.3",
        "seed": SEED,
        "rounds": [],
        "concept_dictionary": {},
        "lineage": [],
        "statistics": {},
    }

    concept_dict: Dict = {}
    all_csf: List[Dict] = []  # all CSF entries accumulated
    all_divergences: List[Dict] = []
    all_depth_judgments: List[Dict] = []
    strategies_used: List[str] = []
    new_concepts_per_round: List[int] = []
    prev_round_data: List[Dict] = []  # for building round N context
    next_question: Optional[str] = None

    for round_num in range(1, NUM_ROUNDS + 1):
        print(f"\n{'─' * 40}")
        print(f"Round {round_num}")
        print(f"{'─' * 40}")

        round_record: Dict[str, Any] = {"round": round_num}

        # --- Layer 1: Generation ---
        if round_num == 1:
            system_prompt = SYSTEM_ROUND1
            user_msg = SEED
        else:
            system_prompt = SYSTEM_ROUND_N
            user_msg = build_round_n_user_msg(SEED, prev_round_data, next_question)

        print(f"  Layer 1: Calling Claude / GPT / Gemini ...")
        t0 = time.time()
        responses = await layer1_parallel(claude_client, oai_client, system_prompt, user_msg)
        t1 = time.time()
        print(f"  Layer 1 done ({t1-t0:.1f}s)")

        round_record["question"] = SEED if round_num == 1 else next_question
        round_record["responses"] = responses
        prev_round_data.append({"round": round_num, "responses": responses})

        # --- Layer 2: Divergence extraction ---
        print(f"  Layer 2: Divergence extraction ...")
        t0 = time.time()
        divergence = layer2_divergence(claude_client, round_num, responses)
        t1 = time.time()
        print(f"  Layer 2 done ({t1-t0:.1f}s) — "
              f"{len(divergence.get('contradictions',[]))} contradictions, "
              f"{len(divergence.get('claims',[]))} claims")
        all_divergences.append(divergence)
        round_record["divergence"] = divergence

        # Prefix claim IDs with round
        claims = divergence.get("claims", [])
        for c in claims:
            if not c.get("id", "").startswith(f"R{round_num}"):
                c["id"] = f"R{round_num}_{c['id']}" if c.get("id") else f"R{round_num}_CL{claims.index(c)+1}"

        # --- Layer 2.7: CSF ---
        if round_num == 1:
            # Build initial dictionary
            print(f"  Layer 2.7: Building initial concept dictionary ...")
            t0 = time.time()
            concept_dict = layer27_init_dictionary(claude_client, claims)
            t1 = time.time()
            dict_size = len(concept_dict)
            print(f"  Concept dictionary initialized ({t1-t0:.1f}s) — {dict_size} concepts")
            new_concepts_per_round.append(dict_size)
        else:
            new_concepts_per_round.append(0)  # updated below

        print(f"  Layer 2.7: CSF conversion ...")
        t0 = time.time()
        csf_result = layer27_csf_convert(claude_client, claims, concept_dict)
        t1 = time.time()
        csf_entries = csf_result.get("csf_entries", [])
        new_concepts = csf_result.get("new_concepts", [])
        print(f"  CSF done ({t1-t0:.1f}s) — {len(csf_entries)} entries, {len(new_concepts)} new concepts")

        # Add agent info to CSF entries
        claim_agent_map = {c.get("id", ""): c.get("agent", "") for c in claims}
        for entry in csf_entries:
            if "agent" not in entry:
                entry["agent"] = claim_agent_map.get(entry.get("claim_id", ""), "unknown")

        # Update concept dictionary with new concepts
        if new_concepts:
            if round_num > 1:
                new_concepts_per_round[-1] = len(new_concepts)
            for nc in new_concepts:
                if isinstance(nc, str):
                    continue  # skip malformed entries
                cid = nc.get("id", "")
                if cid and cid not in concept_dict:
                    concept_dict[cid] = {
                        "aliases": nc.get("aliases", []),
                        "parent": nc.get("parent"),
                        "definition": nc.get("definition", ""),
                    }

        round_record["csf_entries"] = csf_entries

        # --- Layer 3: Dual depth judgment ---
        if round_num == 1:
            # R1: no prior claims to compare against — all depth_0 by definition
            print(f"  Layer 3: R1 baseline — all claims assigned depth_0")
            judgments = []
            for entry in csf_entries:
                judgments.append({
                    "claim_id": entry.get("claim_id", ""),
                    "negative_filter": "N/A (R1 baseline)",
                    "semantic_depth": 0,
                    "semantic_reasoning": "Round 1 baseline: no prior claims exist",
                    "transformation_depth": 0,
                    "transformation_path": [],
                    "final_depth": "depth_0",
                    "confidence": "high",
                })
            depth_summary = {"depth_0": len(judgments)}
            print(f"  Layer 3 done — {depth_summary}")
        else:
            print(f"  Layer 3: Dual depth judgment ...")
            t0 = time.time()
            depth_result = layer3_depth(claude_client, csf_entries, all_csf, concept_dict)
            t1 = time.time()
            judgments = depth_result.get("judgments", [])
            depth_summary = {}
            for j in judgments:
                fd = j.get("final_depth", "unknown")
                depth_summary[fd] = depth_summary.get(fd, 0) + 1
            print(f"  Layer 3 done ({t1-t0:.1f}s) — {depth_summary}")
        all_depth_judgments.extend(judgments)
        round_record["depth_judgments"] = judgments

        # --- Layer 3.5: Lineage ---
        question_info = round_record.get("question_info")
        lineage = build_lineage(round_num, csf_entries, judgments, question_info)
        session["lineage"].extend(lineage)
        round_record["lineage"] = lineage

        # Accumulate CSF
        all_csf.extend(csf_entries)

        # --- Layer 2.5: Question generation (except last round) ---
        if round_num < NUM_ROUNDS:
            print(f"  Layer 2.5: Question generation ...")
            t0 = time.time()
            q_info = layer25_question(claude_client, divergence, strategies_used)
            t1 = time.time()
            next_question = q_info.get("question", "")
            strategy = q_info.get("selected_strategy", "")
            strategies_used.append(strategy)
            print(f"  Layer 2.5 done ({t1-t0:.1f}s) — strategy: {strategy}")
            print(f"  Next Q: {next_question[:80]}...")
            round_record["question_info"] = q_info

        session["rounds"].append(round_record)

    # --- Statistics ---
    print(f"\n{'─' * 40}")
    print("Computing session statistics ...")
    stats = compute_statistics(
        all_divergences, all_depth_judgments,
        concept_dict, strategies_used, new_concepts_per_round,
    )
    session["statistics"] = stats
    session["concept_dictionary"] = concept_dict

    # --- Save ---
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        f"ma_v03_session.json",
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Session saved: {out_path}")
    print(f"{'=' * 60}")
    print(json.dumps(stats, ensure_ascii=False, indent=2))

    return session

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    asyncio.run(run_session())

if __name__ == "__main__":
    main()
