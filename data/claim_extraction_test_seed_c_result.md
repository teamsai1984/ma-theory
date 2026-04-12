# Ma Telescope — Seed C 自動Claim抽出テスト結果

## 結果サマリ

| 指標 | 値 |
|------|-----|
| 手動Claim数 | 18 |
| 自動抽出数 | 19 |
| 完全一致 | 18 |
| 部分一致 | 0 |
| 再現率 (Recall) | 100.0% (18/18) |
| 適合率 (Precision) | 94.7% (18/19) |
| F1 | 97.3% |

---

## 一致詳細

### 完全一致（18件）

| # | 手動Claim | subject | predicate | object |
|---|-----------|---------|-----------|--------|
| 1 | R1_CL1 | economic_rationality | contradicts | ethical_judgment |
| 2 | R1_CL2 | complete_compatibility | contradicts | quantifiability |
| 3 | R1_CL3 | economic_rationality | causes | short_term_orientation |
| 4 | R1_CL4 | economic_rationality | enables | complementary_relationship |
| 5 | R1_CL5 | economic_rationality | is_instance_of | means |
| 6 | R1_CL5_2 | economic_rationality | is_instance_of | value_neutrality |
| 7 | R1_CL6 | ethical_judgment | is_instance_of | control_system |
| 8 | R2_CL1 | ethical_values | contradicts | quantifiability |
| 9 | R2_CL2_P1 | economic_rationality | is_instance_of | point_thinking |
| 10 | R2_CL2_P2 | ethical_judgment | is_instance_of | linear_thinking |
| 11 | R2_CL3 | whole_brain_thinking | enables | same_dimension_hypothesis |
| 12 | R2_CL4 | modern_policies | is_instance_of | integrative_approach |
| 13 | R2_CL5 | ethical_values | enables | economic_integration |
| 14 | R2_CL6 | dual_systems | is_instance_of | survival_modules |
| 15 | R3_CL1 | qualitative_transformation_of_action | contradicts | quantifiability |
| 16 | R3_CL1_sup | qualitative_transformation_of_action | contradicts | economic_rationality |
| 17 | R3_CL2 | integrated_value_criteria | enables | comprehensive_evaluation |
| 18 | R3_CL3 | complete_information_system | enables | immediate_optimal_solution |

---

## 手動にあるが自動で見逃したClaim（0件）

見逃しなし。全18件を完全一致で抽出。

## 自動抽出で見つかったが手動にないClaim（1件）

| # | subject | predicate | object | 備考 |
|---|---------|-----------|--------|------|
| 1 | short_term_conflict | transforms | long_term_convergence | Claudeの「短期的対立→長期的一致の時間的収束現象」から独自に生成。手動Ground Truthではこの「時間的収束」はClaimとして抽出されていない |

---

## テスト条件

| 項目 | 値 |
|------|-----|
| 使用モデル | claude-sonnet-4-20250514 |
| 入力 | Seed C議論要約（再構成データ使用 — handoff文書の情報を基に概念名を括弧付きで明示） |
| Ground Truth | v0.3パイプライン + 手動正規化による確定18件 |
