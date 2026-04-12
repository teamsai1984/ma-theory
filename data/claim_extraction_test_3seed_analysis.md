# Ma Telescope — 3 Seed 自動抽出テスト統合分析

## 1. Seed別サマリ比較

| Seed | Domain | 手動件数 | 自動抽出数 | 完全一致 | 部分一致 | 見逃し | 過剰 | Recall | Precision | F1 |
|------|--------|---------|-----------|---------|---------|-------|------|--------|-----------|-----|
| A | 意識・主観性 | 19 | 18 | 17 | 1 | 1 | 0 | 94.7% | 100.0% | 97.3% |
| B | 数学・物理 | 18 | 16 | 12 | 3 | 3 | 1 | 83.3% | 93.8% | 88.2% |
| C | 社会・制度 | 18 | 19 | 18 | 0 | 0 | 1 | 100.0% | 94.7% | 97.3% |
| **Total** | | **55** | **53** | **47** | **4** | **4** | **2** | **92.7%** | **96.2%** | **94.4%** |

---

## 2. depth別 Recall（3 seed統合）

| depth | 手動件数 | 自動で拾えた数 | Recall |
|-------|---------|--------------|--------|
| depth_0 | 20 | 19 | 95.0% |
| depth_1 | 10 | 10 | 100.0% |
| depth_2plus_candidate | 2 | 2 | 100.0% |
| depth_2plus_confirmed | 23 | 20 | 87.0% |
| **Total** | **55** | **51** | **92.7%** |

### depth別 Recall（Seed別）

| depth | Seed A | Seed B | Seed C |
|-------|--------|--------|--------|
| depth_0 | 6/6 (100%) | 6/7 (85.7%) | 7/7 (100%) |
| depth_1 | 3/3 (100%) | 4/4 (100%) | 3/3 (100%) |
| depth_2plus_candidate | 1/1 (100%) | 0/0 (-) | 1/1 (100%) |
| depth_2plus_confirmed | 8/9 (88.9%) | 5/7 (71.4%) | 7/7 (100%) |

---

## 3. predicate別 Recall（3 seed統合）

| predicate | 手動件数 | 自動で拾えた数 | Recall |
|-----------|---------|--------------|--------|
| is_instance_of | 19 | 17 | 89.5% |
| contradicts | 13 | 13 | 100.0% |
| causes | 12 | 11 | 91.7% |
| enables | 7 | 7 | 100.0% |
| requires | 1 | 1 | 100.0% |
| transforms | 1 | 1 | 100.0% |

### predicate別 Recall（Seed別）

| predicate | Seed A | Seed B | Seed C |
|-----------|--------|--------|--------|
| is_instance_of | 5/5 (100%) | 5/7 (71.4%) | 7/7 (100%) |
| contradicts | 5/5 (100%) | 4/4 (100%) | 4/4 (100%) |
| causes | 6/7 (85.7%) | 3/5 (60.0%) | 1/1 (100%) |
| enables | 1/1 (100%) | 0/1 (0%) | 5/5 (100%) |
| requires | 1/1 (100%) | - | - |
| transforms | 1/1 (100%) | - | - |

Note: Seed A R1_CL5 (enables→is_instance_of) は部分一致。enables missed扱いで計算。

---

## 4. 見逃しClaimの特性分析（全4件）

| Claim | Seed | depth | 単文内明示? | 概念名明示? | 後付け命名? | CDC? |
|-------|------|-------|-----------|-----------|-----------|------|
| R2_CL1: irreducibility→unique_perspective_relation | A | depth_2plus_confirmed | No (推論が必要) | Partial | Yes | No |
| R1_CL4: irrational_numbers→boundary_band | B | depth_0 | Yes | Yes | No | No |
| R3_CL1: boundary_resonance→membrane_potential_oscillation | B | depth_2plus_confirmed | Yes | Yes (括弧付) | Partial | Yes |
| R3_CL1_2: membrane_potential_oscillation→observation_independent_phenomenon | B | depth_2plus_confirmed | No (二次的) | Yes | Yes | No |

### 見逃しパターンの分類

| パターン | 件数 | 該当 |
|---------|------|------|
| 二次的Claim（概念Aが概念BのinstanceであるとB自体から導出） | 1 | B-R3_CL1_2 |
| predicate誤認（causes↔contradicts等） | 1 | B-R3_CL1 |
| 推論が必要な暗黙的関係 | 1 | A-R2_CL1 |
| 具体例のinstance_of関係の見落とし | 1 | B-R1_CL4 |

---

## 5. 過剰抽出の分析（全2件）

| Claim | Seed | subject | predicate | object | 備考 |
|-------|------|---------|-----------|--------|------|
| R3_CL1 | B | boundary_resonance | contradicts | quantum_superposition | 「通常の量子重ね合わせと異なり」をcontradictsと独自解釈。手動はcausesで別のobject |
| R1_CL3 | C | short_term_conflict | transforms | long_term_convergence | 「短期的対立→長期的一致の時間的収束現象」から独自にClaim生成。手動Ground Truthにない追加抽出 |

---

## 6. GPT予測の検証

| 予測 | 予測値 | 実測値 | 判定 |
|------|--------|--------|------|
| 生の抽出Recall順位 | C ≥ B > A | C(100%) > A(94.7%) > B(83.3%) | × (Bが最低、Aは高い) |
| 深いclaim安定抽出 | C ≈ B > A (Aが苦戦) | C(100%) > A(88.9%) > B(71.4%) | × (Bが最も苦戦) |

### 予測が外れた理由（事実のみ）
- GPTは「Seed Aの高抽象概念が抽出困難」と予測したが、議論要約に概念名が明示されていたためSeed Aの抽出精度は高かった
- Seed Bの見逃し3件中2件はdepth_2plus_confirmedであり、形式ドメインでの深いClaimが最も抽出困難だった
- Seed Cは議論要約中に全概念が括弧付きで明示されており、完全一致率が最高

---

## 7. 発見（事実のみ）

1. **3 seed統合でRecall 92.7%, Precision 96.2%, F1 94.4%** — 自動抽出はベースライン性能として十分に高い
2. **contradicts の Recall = 100%** — 対立関係は全seedで完璧に抽出された
3. **depth_2plus_confirmed の Recall = 87.0%** — 深いClaimほど抽出が難しい傾向がある（depth_0: 95%, depth_1: 100%, depth_2+: 87%）
4. **Seed Bが唯一Recall < 90%** — 形式科学ドメインでの抽出が最も困難
5. **見逃し4件中3件がSeed B** — 形式ドメイン特有の「二次的Claim」と「predicate誤認」が集中
6. **概念名の明示度がRecallと強く相関** — 括弧付きで概念名が明示されたSeed Cは100%、暗黙的推論が必要なClaimが見逃された
7. **過剰抽出は2件のみ** — 自動抽出は保守的で、手動にない独自解釈は最小限

---

## テスト条件

| 項目 | 値 |
|------|-----|
| 使用モデル | claude-sonnet-4-20250514（全seedで同一） |
| 入力形式 | 議論要約（各Round 2-3文、概念名括弧付き明示） |
| Ground Truth | v0.3パイプライン + 手動正規化による確定Claim |
| 実行回数 | 各seed 1回 |
| 実行日 | 2026-04-12 |

---

*Note: 結果の解釈・理論的意味づけはclaude.aiセッションで三者査読にて実施。本ファイルはraw測定結果のみ。*
