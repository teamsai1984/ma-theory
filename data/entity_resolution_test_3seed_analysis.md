# Ma Telescope — Entity Resolution 自動化テスト 3 Seed統合分析

---

## 1. Seed別サマリ比較

| Seed | 概念数(前) | 手動統合数 | 自動統合数 | 手動吸収数 | 自動吸収数 |
|------|-----------|-----------|-----------|-----------|-----------|
| A | 31 | 10 | 2 | (不明) | 4 |
| B | 25 | 3 | 1 | 2 | 2 |
| C | 30 | 5 | 4 | (不明) | 6 |
| **Total** | **86** | **18** | **7** | | **12** |

---

## 2. 概念統合（Merge）の精度

### Seed A

| 自動統合 | 手動との一致 | 判定 |
|---------|------------|------|
| individuality_loss + self_identity_dissolution → individuality_loss | 手動でも統合対象の可能性あり（両者ともindividualityの子概念） | 妥当 |
| qualitative_extinction + subjectivity_loss → subjectivity_loss | 手動でも統合対象の可能性あり | 妥当 |

- 手動は10件統合だが自動は2件のみ → **大幅な統合不足**
- 手動の具体的merge対が不明のため、精密なTP/FP計算は不可

### Seed B

| 自動統合 | 手動との一致 | 判定 |
|---------|------------|------|
| dynamic_filter + interface_phenomenon → boundary_function | 手動にない（手動はcritical_boundary + rigid_boundary） | **FP: 過剰統合** |

| 手動統合（見逃し） | 内容 |
|-------------------|------|
| critical_boundary ≈ rigid_boundary → observer_independent_boundary | **FN: 統合漏れ** |

- 自動: 1件統合（手動と不一致）
- 手動: 1件統合（自動が見逃し）
- **統合Recall: 0%, 統合Precision: 0%**

### Seed C

| 自動統合 | 手動との一致 | 判定 |
|---------|------------|------|
| long_term_perspective + linear_thinking | 手動の5件統合に含まれる可能性が高い | 妥当 |
| short_term_orientation + point_thinking | 同上 | 妥当 |
| complete_compatibility + same_dimension_hypothesis | 同上 | 妥当 |
| comprehensive_evaluation + integrative_approach | 部分的に妥当だが、手動ではintegrative_approachは統合ではなく親子関係で整理 | 要検討 |

- 手動5件統合のうち3-4件を自動が検出 → **Recall推定 60-80%**

### 統合の3 seed統合精度

| 指標 | 推定値 | 備考 |
|------|--------|------|
| 統合Recall（全体） | **30-40%** | 手動18件のうち自動が検出したのは5-7件程度 |
| 統合Precision（全体） | **70-85%** | 自動7件のうち1件が明確なFP（Seed B） |
| **最大の課題** | **統合不足** | 特にSeed Aで手動10件 vs 自動2件 |

---

## 3. Claim吸収（Absorption）の精度

### Seed B（手動データが最も詳細）

| 手動吸収 | 自動の対応 | 一致 |
|---------|-----------|------|
| R2_CL2 → R2_CL1 (同型) | R2_GP2 → R2_CL1 (同型) | **部分一致**（吸収先は一致、吸収元が異なる） |
| R3_CL1_2 → R3_CL1 (従属) | 未検出 | **FN** |

| 自動吸収（手動にない） | 判定 |
|----------------------|------|
| R1_CL2 → R1_CL3 (relabeling) | 要検討（boundaryの分類は実質的主張の可能性あり） |

### Seed C

| 自動吸収 | 手動との一致推定 | 判定 |
|---------|----------------|------|
| R2_CL6 → R2_CL5 (relabeling) | 手動でR2_CL6はontological relabeling → depth_1降格 | **一致** |
| R3_CL1_sup → R3_CL1 (従属) | 妥当（同一subjectの二重記述） | 妥当 |
| R2_CL1 → R1_CL2 (同型) | **問題: 手動ではR2_CL1をdepth_2plus_confirmedとして維持** | **FP: 過剰吸収** |
| R1_CL5 → R1_CL5_2 (relabeling) | 手動でも同型として処理された可能性 | 妥当 |
| R1_CL6 → R2_CL2_P2 (relabeling) | 要検討 | 要検討 |
| R2_CL4 → R3_CL2 (relabeling) | 要検討 | 要検討 |

### Seed A

| 自動吸収 | 判定 |
|---------|------|
| R2_CL1 → R2_CL1_neg (relabeling) | **一致**: 手動でもR2_CL1はdepth_0に降格（ER failure例） |
| R1_CL1 → R1_CL5 (relabeling) | 要検討 |
| R1_CL2 → R1_CL3 (relabeling) | 要検討（異なるLLMの同型分類） |
| R3_CL2_1 → R3_CL2_2 (従属) | 妥当（分類は因果の帰結） |

---

## 4. depth判定への影響（最重要セクション）

### 手動正規化後の確定結果

| Seed | 手動confirmed | 手動confirmed Claims |
|------|-------------|---------------------|
| A | 1 | R2_CL5 |
| B | 0 | - |
| C | 2 | R2_CL5, R3_CL1 |

### 自動ERがdepth判定に与える影響

#### Seed A

| raw confirmed Claim | 自動ERの処理 | 手動の処理 | 一致? |
|--------------------|------------|----------|------|
| R2_CL1 | relabeling吸収（降格） | depth_0に降格 | **✓** |
| R2_CL2 | 変更なし（残存） | 降格 | **✗ (auto false positive)** |
| R2_CL3 | 変更なし（残存） | 降格 | **✗ (auto false positive)** |
| R2_CL4_1 | 変更なし（残存） | 降格 | **✗ (auto false positive)** |
| R2_CL4_2 | 変更なし（残存） | 降格 | **✗ (auto false positive)** |
| R2_CL5 | 変更なし（残存） | **confirmed維持** | **✓** |
| R3_CL1 | 変更なし（残存） | 降格 | **✗ (auto false positive)** |
| R3_GP1 | 変更なし（残存） | 降格 | **✗ (auto false positive)** |
| R3_GE2 | 変更なし（残存） | 降格 | **✗ (auto false positive)** |

**Seed A結果: 手動confirmed 1件を正しく残す ✓ だが、降格すべき8件中7件を残してしまう（false positive 7件）**

#### Seed B

| raw confirmed Claim | 自動ERの処理 | 手動の処理 | 一致? |
|--------------------|------------|----------|------|
| R2_CL1 | 変更なし | 降格 | ✗ (FP) |
| R2_CL2 | 変更なし | 降格（R2_CL1に吸収） | ✗ (FP) |
| R2_GE1 | 変更なし | 降格 | ✗ (FP) |
| R2_GE2 | 変更なし | 降格 | ✗ (FP) |
| R3_CL1 | 変更なし | 降格 | ✗ (FP) |
| R3_CL1_2 | 変更なし | 降格 | ✗ (FP) |
| R3_CL2 | 変更なし | 降格 | ✗ (FP) |

**Seed B結果: 手動confirmed 0件と一致しない。自動は7件すべてをconfirmedとして残す（false positive 7件）**

#### Seed C

| raw confirmed Claim | 自動ERの処理 | 手動の処理 | 一致? |
|--------------------|------------|----------|------|
| R2_CL1 | R1_CL2に同型吸収（降格） | 正規化でconfirmed維持せず | **✓（ただし手動はconfirmed維持を検討）** |
| R2_CL2_P1 | 変更なし | 降格 | ✗ (FP) |
| R2_CL2_P2 | 変更なし | 降格 | ✗ (FP) |
| R2_CL3 | 変更なし | 降格 | ✗ (FP) |
| R2_CL5 | 変更なし | **confirmed維持** | **✓** |
| R2_CL6 | relabeling吸収（降格） | ontological relabeling降格 | **✓** |
| R3_CL3 | 変更なし | 降格 | ✗ (FP) |

**R3_CL1（手動confirmed）はraw depth_1のため上記表に含まれない。手動正規化でconfirmedに昇格したケース。自動ERでは検出不可能。**

**Seed C結果: 手動confirmed 2件のうち1件（R2_CL5）を正しく残す ✓、1件（R3_CL1）は元がdepth_1で自動ERの範囲外**

### depth判定サマリ

| Seed | 手動confirmed | 自動ERでconfirmed残存 | 正しい残存(TP) | 偽の残存(FP) | 見逃し(FN) |
|------|-------------|--------------------|-----------|-----------|----|
| A | 1 | 8 | 1 | 7 | 0 |
| B | 0 | 7 | 0 | 7 | 0 |
| C | 2 | 5 | 1 | 4 | 1* |
| **Total** | **3** | **20** | **2** | **18** | **1** |

*Seed C R3_CL1は元がdepth_1で正規化後にconfirmedに昇格。自動ERの範囲外。

**depth判定Precision: 2/20 = 10.0%**
**depth判定Recall: 2/3 = 66.7%**

---

## 5. concept_type付与の結果

自動ERが付与したconcept_type分布:

| type | Seed A | Seed B | Seed C | Total |
|------|--------|--------|--------|-------|
| entity | 5 | 12 | 9 | 26 |
| property | 9 | 6 | 9 | 24 |
| process | 11 | 5 | 2 | 18 |
| mechanism | 4 | 1 | 5 | 10 |
| assumption | 0 | 0 | 0 | 0 |

手動type付与データが不完全なため一致率は算出不可。
**注目点**: Seed Cで「ethical_judgment = process, ethical_values = property」の区別が手動で指摘されていたが、自動ERでもethical_judgment=entity, ethical_values=propertyと異なるtypeを付与。方向性は一致しているが具体的なtype割当は異なる。

---

## 6. Claim抽出テストとの合算パイプライン精度

| ステップ | Recall | Precision | 備考 |
|---------|--------|-----------|------|
| Step 2: Claim抽出 | 92.7% | 96.2% | 3seed統合 |
| Step 4: Entity Resolution (統合) | 30-40% | 70-85% | 統合の検出 |
| Step 4: Entity Resolution (depth判定) | 66.7% | 10.0% | confirmed判定 |
| **合算: Claim抽出→depth判定** | **~60%** | **~10%** | 最終的なconfirmed判定精度 |

**パイプライン全体のボトルネックは明確にEntity Resolution。**
Claim抽出は高精度（F1 94.4%）だが、ERでの偽陽性（本来降格すべきClaimを残す）が精度を大幅に低下させる。

---

## 7. 誤りパターンの分析

### 主要な誤りパターン

| パターン | 件数 | 説明 |
|---------|------|------|
| **統合不足（under-merge）** | ~11 | 手動で統合された概念対を自動が見逃し。特にSeed Aで深刻（手動10件vs自動2件） |
| **depth降格漏れ** | 18 | rawでconfirmedだが正規化で降格すべきClaimを、自動ERが残してしまう |
| **過剰統合（over-merge）** | 1 | Seed Bでdynamic_filter+interface_phenomenonを統合（手動では非統合） |
| **過剰吸収** | 1 | Seed CでR2_CL1を同型吸収（手動ではconfirmed維持の可能性） |

### 根本原因（推測）

1. **自動ERは「表層的な語彙類似性」で判断する** — 手動ERは議論の文脈・論理構造を理解した上で判断するが、自動は概念定義の文字列比較に近い
2. **depth降格の判断には「Positive Control 4基準」の適用が必要** — 自動ERのプロンプトにはこの基準が含まれていない。relabeling以外の降格理由（provenance dependence, mediated structure等）を自動で判定できていない
3. **is_instance_of のrelabeling判定は比較的正確** — R2_CL1(A), R2_CL6(C)のrelabeling検出は手動と一致

---

## 8. 発見（事実のみ）

1. **自動ERの概念統合Recall≈30-40%**: 手動の統合判断の半分以上を見逃す
2. **depth判定Precision=10%**: confirmed残存20件中、正しいのは2件のみ。偽の創発を大量に残す
3. **depth判定Recall=66.7%**: 手動confirmed 3件中2件は正しく残すが、1件は自動ERの範囲外（depth_1からの昇格）
4. **relabeling検出は比較的正確**: is_instance_ofによる単純な名前付け替えは検出できる
5. **「なぜ降格すべきか」の判断が自動ERの最大弱点**: 統合漏れより、残すべきでないClaimを残す方が深刻
6. **Claim抽出(F1 94.4%) → ER(depth precision 10%)のギャップが巨大**: パイプラインのボトルネックはERに集中
7. **Seed間でER精度に大差**: Seed C（4統合検出）> Seed A（2統合検出）> Seed B（0正解統合）

---

## テスト条件

| 項目 | 値 |
|------|-----|
| 使用モデル | claude-sonnet-4-20250514 |
| Ground Truth | 手動正規化結果（claude.aiセッションで実施） |
| 手動ER詳細度 | Seed B: 具体的merge/absorption対あり、Seed A/C: 概要のみ |
| 実行回数 | 各seed 1回 |
| 実行日 | 2026-04-13 |

---

*Note: 手動ER結果の詳細（特にSeed A）が限定的であるため、一部の精度値は推定。結果の理論的解釈はclaude.aiセッションで実施。*
