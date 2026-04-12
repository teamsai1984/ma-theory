# Ma Telescope — 自動Claim抽出テスト結果
## Seed B議論データ × Claude Sonnet API

---

## 結果サマリ

| 指標 | 値 |
|------|-----|
| 手動Claim数 | 18 |
| 自動抽出数 | 16 |
| 完全一致 | 12 |
| 部分一致 | 3 |
| 再現率 (Recall) | 83.3% (15/18) |
| 適合率 (Precision) | 93.8% (15/16) |
| F1 | 88.2% |

---

## 一致詳細

### 完全一致（12件）

| # | 手動Claim | Auto Claim | subject | predicate | object |
|---|-----------|------------|---------|-----------|--------|
| 1 | R1_CL1_B | Auto R1_CL2 | boundary_band | causes | emergence |
| 2 | R1_CL2 | Auto R1_GP2 | boundary | is_instance_of | dynamic_filter |
| 3 | R1_CL3 | Auto R1_GE2 | boundary | is_instance_of | interface_phenomenon |
| 4 | R1_CL6 | Auto R1_GE1 | digital_existence | causes | discrete_recognition |
| 5 | R2_CL1 | Auto R2_CL2 | critical_boundary | contradicts | resolution |
| 6 | R2_CL2 | Auto R2_CL1 | boundary | contradicts | observer_dependent_change |
| 7 | R2_GP2 | Auto R2_GP1 | boundary_behavior | contradicts | resolution |
| 8 | R2_GE1 | Auto R2_GE1 | rigid_boundary | contradicts | recognition_system |
| 9 | R2_GE2 | Auto R2_GE2 | boundary | is_instance_of | dual_nature_entity |
| 10 | R3_CL2 | Auto R3_CL2 | observation_intensity_increase | causes | interference_pattern_clarity |
| 11 | R3_CL4 | Auto R3_GP1 | observation_technology_advancement | enables | experimental_theory_evaluation |
| 12 | R3_CL3 | Auto R3_GE1 | cell_membrane | is_instance_of | composite_boundary_system |

### 部分一致（3件）

| # | 手動Claim | Auto Claim | 一致箇所 | 手動 | 自動 |
|---|-----------|------------|----------|------|------|
| 1 | R1_CL1: boundary_band \| is_instance_of \| **boundary** | Auto R1_CL1: boundary_band \| is_instance_of \| **third_reality_mode** | subject+predicate | object差異: boundary vs third_reality_mode |  |
| 2 | R1_CL5: resolution \| causes \| **mutual_conversion** | Auto R1_GP1: resolution \| causes \| **boundary** | subject+predicate | object差異: mutual_conversion vs boundary |  |
| 3 | R2_GP1: **zeno_paradox** \| causes \| new_motion_form | Auto R2_GP2: **boundary_resonance** \| causes \| new_motion_form | predicate+object | subject差異: zeno_paradox vs boundary_resonance |  |

---

## 手動にあるが自動で見逃したClaim（3件）

| # | Claim ID | subject | predicate | object | depth | 見逃し理由（推測） |
|---|----------|---------|-----------|--------|-------|------------------|
| 1 | R1_CL4 | irrational_numbers | is_instance_of | boundary_band | depth_0 | 議論要約中に「無理数を境界帯域の例として挙げた」と記載あるが、具体例のinstance_of関係として抽出されなかった |
| 2 | R3_CL1 | boundary_resonance | causes | membrane_potential_oscillation | depth_2plus_confirmed | 自動はboundary_resonanceを拾ったが、predicate=contradicts, object=quantum_superpositionと誤認。causesではなくcontradictsと解釈 |
| 3 | R3_CL1_2 | membrane_potential_oscillation | is_instance_of | observation_independent_phenomenon | depth_2plus_confirmed | membrane_potential_oscillationが主語になる二次的Claimを抽出できなかった |

---

## 自動抽出で見つかったが手動にないClaim（1件）

| # | Auto Claim ID | subject | predicate | object | 備考 |
|---|---------------|---------|-----------|--------|------|
| 1 | R3_CL1 | boundary_resonance | contradicts | quantum_superposition | 手動ではboundary_resonance→causes→membrane_potential_oscillation。自動は「通常の量子重ね合わせと異なり」をcontradictsと解釈した |

---

## ラウンド別の精度

| Round | 手動Claims | 自動抽出 | 完全一致 | 部分一致 | 見逃し |
|-------|-----------|---------|---------|---------|-------|
| R1 | 7 | 6 | 4 | 2 | 1 (irrational_numbers) |
| R2 | 6 | 6 | 5 | 1 | 0 |
| R3 | 5 | 4 | 3 | 0 | 2 (membrane_potential系) |

---

## Predicate別の精度

| Predicate | 手動件数 | 完全一致 | 部分一致 | 見逃し |
|-----------|---------|---------|---------|-------|
| is_instance_of | 7 | 5 | 1 | 1 |
| causes | 5 | 3 | 1 | 1 |
| contradicts | 4 | 4 | 0 | 0 |
| enables | 1 | 1 | 0 | 0 |

---

## テスト条件

| 項目 | 値 |
|------|-----|
| 使用モデル | claude-sonnet-4-20250514 |
| 入力 | Seed B議論要約（Round 1-3, 各2-3文） |
| Ground Truth | v0.3パイプラインによる手動抽出18件 |
| 実行回数 | 1回 |
| 実行日 | 2026-04-12 |

---

*Note: 結果の解釈・評価はclaude.aiセッションで実施。本ファイルはraw測定結果のみ。*
