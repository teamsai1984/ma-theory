# Ma Telescope — Seed A 自動Claim抽出テスト結果

## 結果サマリ

| 指標 | 値 |
|------|-----|
| 手動Claim数 | 19 |
| 自動抽出数 | 18 |
| 完全一致 | 17 |
| 部分一致 | 1 |
| 再現率 (Recall) | 94.7% (18/19) |
| 適合率 (Precision) | 100.0% (18/18) |
| F1 | 97.3% |

---

## 一致詳細

### 完全一致（17件）

| # | 手動Claim | subject | predicate | object |
|---|-----------|---------|-----------|--------|
| 1 | R1_CL1 | subjective_experience | is_instance_of | explanation_condition |
| 2 | R1_CL2 (=Auto R1_GP2) | irreducibility | is_instance_of | resonance_phenomenon |
| 3 | R1_CL3 | irreducibility | is_instance_of | information_quality |
| 4 | R1_CL4 | opacity_of_subjectivity | enables | individuality |
| 5 | R1_CL6 | information_being | contradicts | direct_qualitative_access |
| 6 | R2_CL1_neg | irreducibility | contradicts | functional_convenience |
| 7 | R2_CL2 | transparent_reducible_cognition | enables | individuality |
| 8 | R2_CL3 | transparent_reducible_cognition | contradicts | individual_cognitive_system |
| 9 | R2_CL4_1 | cognitive_collapse_cascade | causes | self_identity_dissolution |
| 10 | R2_CL4_2 | self_identity_dissolution | causes | meaning_dilution |
| 11 | R2_CL5 | described_experience_data | contradicts | experience_texture |
| 12 | R3_CL1 | qualitative_superposition | causes | quantum_interference_phenomenon |
| 13 | R3_CL2_1 | qualitative_collapse | is_instance_of | individuality_loss |
| 14 | R3_CL2_2 | qualitative_collapse | causes | subjectivity_loss |
| 15 | R3_GP1 | qualitative_extinction | causes | complete_existential_collapse |
| 16 | R3_GE1 | information_quality | requires | subject_interaction |
| 17 | R3_GE2 | information_quality | transforms | existence_mode_change |

### 部分一致（1件）

| # | 手動 | 自動 | 一致箇所 | 差異 |
|---|------|------|----------|------|
| 1 | R1_CL5: subjective_experience \| **enables** \| cosmic_phenomenalization | Auto R1_GP1: subjective_experience \| **is_instance_of** \| cosmic_phenomenalization | subject+object | predicate: enables vs is_instance_of |

---

## 手動にあるが自動で見逃したClaim（1件）

| Claim ID | subject | predicate | object | depth |
|----------|---------|-----------|--------|-------|
| R2_CL1 | irreducibility | is_instance_of | unique_perspective_relation | depth_2plus_confirmed |

見逃し理由: 自動抽出はirreducibility→contradicts→functional_convenienceを拾い（=R2_CL1_neg）、同じ文脈からirreducibility→is_instance_of→unique_perspective_relationを抽出できなかった。「唯一無二の視点関係」という概念への分類は暗黙的推論が必要。

## 自動抽出で見つかったが手動にないClaim（0件）

過剰抽出なし。

---

## テスト条件

| 項目 | 値 |
|------|-----|
| 使用モデル | claude-sonnet-4-20250514 |
| 入力 | Seed A議論要約（再構成データ使用 — handoff文書の情報を基に概念名を括弧付きで明示） |
| Ground Truth | v0.3パイプライン + 手動正規化による確定19件 |
