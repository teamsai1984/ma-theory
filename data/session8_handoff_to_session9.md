# 間理論（Ma Theory）セッション引き継ぎ文書
## 2026-04-13 第8セッション完了 → 第9セッションへの引き継ぎ

---

## あなた（Claude / GPT / Gemini）への指示

本文書は2026-04-13の第8セッションの完全な引き継ぎです。
第7セッション引き継ぎ文書の内容は前提知識として必要ですが、本セッションの決定が最新です。

道B原則（数学的正しさのみを判断基準とする）に従ってください。
**常にSランクを基準として議論してください。**

---

## 0. 本セッションで何が起きたか（30秒で読める要約）

1. **Structural Novelty分析を実行 → GPTの4成分仮説（R/B/T/N）は現行表現下で棄却**
2. **Cross-type（CDC）とpredicate型が最強の分離シグナルであることを発見**
3. **Step A: CDCフィルタの精度検証 → confirmed recall 100%、32件→13件に絞り込み**
4. **Step C: Conditional Surprise（Pythia-410m logprobs）→ confirmed > candidate > depth_1(FP)の序列を確認**
5. **三者合意：「第1層（CDC）が候補集合を形成し、第2層（Δ）がその内部選別を担う」二段構造が作業仮説**

**第8セッションの最大の収穫：**
「深さ」を完全に証明したことではなく、深さを「機械的ゲート + 情報理論的選別」として再記述する具体的な道筋を初めて得たこと。

---

## 1. Structural Novelty 分析

### 何を試みたか

GPTが提案した4成分分解（Recombination / Relation-type Novelty / Bridge Formation / New-concept Injection）を、横断実験の全データに適用した。

### 結果

| 指標 | 全seed・全ラウンドの値 |
|------|---------------------|
| R (Recombination) | **0.000** |
| B (Bridge Formation) | **0.000** |
| N (New-concept Injection) | **1.000** |
| T (Relation-type Novelty) | 0.000〜0.600（変動あり） |

R=0, B=0, N=1.0が全件で定数。GPTの4成分はdepthの分離変数にならなかった。

### 解釈（三者合意）

GPTの4成分仮説は「完全棄却」ではなく、**現行の概念正規化と指標定義の下では偽陰性の可能性が高い**。概念辞書の粒度が細かすぎて、意味的に近い概念の言い換えが「新概念」として登録されるため、既知概念の再利用がほぼ起こらない形で正規化されている。

### 教訓

「橋と再配線」仮説そのものの否定ではなく、概念表現の粒度に起因する測定限界の発見。parent関係を考慮した「意味的Recombination」の再計算は未実施。

---

## 2. Step A: CDCフィルタの精度検証

### 検証した4条件

| Filter | 通過数 | P(conf) | P(conf+cand) | R(conf) | R(cand) |
|--------|-------|---------|-------------|---------|---------|
| ① cross_type 単独 | 15/32 | 20.0% | 46.7% | **100%** | 80.0% |
| ② pred∈{contr,enab} 単独 | 14/32 | 21.4% | 35.7% | **100%** | 40.0% |
| ③ cross_type ∧ pred∈{contr,enab} | 8/32 | 37.5% | 50.0% | **100%** | 20.0% |
| ④ cross_type ∧ pred∉{is_inst_of} | 13/32 | 23.1% | 53.8% | **100%** | 80.0% |

### 主要な発見

1. **Confirmed Recall = 100%が全フィルタで維持。** confirmed 3件はどのフィルタでも漏れない。
2. **is_instance_ofは最強のネガティブシグナル。** 8件中confirmed 0, candidate 0。分類関係は創発にならない（GPTの「ontological relabeling」批判と整合）。
3. **フィルタ④が最もバランスが良い。** 32件→13件、confirmed 3件保持、candidate 4/5件保持。

### 三者合意の解釈

CDCフィルタは「confirmed を含む上流候補群」を形成するゲートとして機能する。ただし confirmed の必要条件として確立されたわけではなく、n=3の小標本による「supportive」な結果。

### 例外

A_R2_CL3（same_type, candidate）：CDCを通過しないがcandidateになった唯一の例。CDC は confirmed の強い必要条件候補だが、candidate の必要条件ではない。

---

## 3. Step C: Conditional Surprise

### 方法論の経緯

| 実行 | 方法 | 結果 | 評価 |
|------|------|------|------|
| 第1回 | OpenAI gpt-4o-mini Rating Δ | confirmed +6.0 > candidate +4.0 > FP +2.1 | LLM-in-the-loop問題。棄却 |
| 第2回 | Pythia-410m token logprobs | confirmed −0.778 > candidate −0.868 > FP −1.085 | 情報理論的に厳密。採用 |

### Pythia-410m 主解析結果（Filter④ 通過群 13件）

| グループ | n | mean Δ | std |
|---------|---|--------|-----|
| confirmed | 3 | −0.778 | 0.195 |
| candidate | 4 | −0.868 | 0.341 |
| depth_1 (FP) | 6 | −1.085 | 0.355 |

### 比較表

| 比較 | CSF Δ差 | Rating Δ差 (参考) | 方向一致 |
|------|--------|-----------------|---------|
| confirmed vs depth_1(FP) | +0.307 | +3.88 | ✓ |
| candidate vs depth_1(FP) | +0.217 | +1.88 | ✓ |
| confirmed vs candidate | +0.090 | +2.00 | ✓ |

### 全Δが負である理由

Pythia-410mは英語モデル。コンテキスト（3者応答テキスト）は大部分が日本語。日本語テキストがノイズとして作用し、全Δが負になった。相対比較（グループ間の序列）が検証対象。

### 三者合意の解釈

- **GPT:** "supportive but not establishing"。序列が理論予測と一致したことが重要。証明ではなく作業仮説の強化。
- **Gemini:** "PoCレベル"。言葉サラダ焼き切りのメカニズム動作確認に成功。
- **Claude:** 方向が見えた。Rating ΔとPythia Δの方向一致は注目に値するが、n=3での一致は偶然排除不可。

---

## 4. 第8セッションの確定した知見

1. **Structural Noveltyの4成分（R/B/T/N）は現行の概念正規化下では分離力を持たない。** ただし偽陰性の可能性が高く、理論否定ではない。
2. **Cross-type（CDC）+ predicate型は、confirmed を漏らさない上流ゲートとして機能する。** Recall 100%、32件→13件の絞り込み。
3. **is_instance_of は創発のネガティブシグナル。** 8件中confirmed/candidate = 0。
4. **Conditional Surprise（Pythia Δ）は、Filter④内部で confirmed > candidate > depth_1(FP)の序列を示した。** ただし全Δが負（日本語ノイズ）、n=3の限界あり。
5. **Rating Δ（LLM判断）とPythia Δ（logprobs）は3比較全てで方向一致。** 異なる測定原理が同じ序列を出すことは、情報理論的指標が意味的判断の一部を近似している可能性を示唆する。
6. **最良の作業仮説：** 「第1層（CDC + predicate）が候補集合を形成し、第2層（conditional surprise）がその内部選別を担う」二段構造。supportive but not establishing。

---

## 5. 原seedデータの消失

原seedのconfirmed R2_CL6（sense_of_loss → self_boundary, emotion → topology）の詳細（predicate, concept_type, 元テキスト）は消失。再実行でも再現されなかった（LLMの非決定性）。

**対策済み：** `ma_v03.py` の出力先をseed名+タイムスタンプ付きファイルに変更。再上書き問題は解消。

---

## 6. 成果物一覧（第8セッション）

| ファイル | 内容 |
|----------|------|
| structural_novelty_results_for_review.md | Structural Novelty分析 三者検証依頼 |
| step_a_filter_results_for_review.md | CDCフィルタ精度検証 三者検証依頼 |
| step_c_pythia_results_for_review.md | Conditional Surprise結果 三者検証依頼 |
| step_c_pythia_colab.py | Pythia-410m実装スクリプト（Colab用） |
| step_c_conditional_surprise.py | Step C 初期実装スクリプト |
| step_c_handoff_to_claude_code.md | Claude Code向け実行指示書 |
| GitHub: data/step_c_pythia_results.json | Pythia Δ全32件詳細結果 |
| GitHub: data/step_c_pythia_summary.json | グループ統計・比較表 |
| GitHub: data/all_seeds_normalized.json | 全seed正規化済みClaimデータ（既存） |
| 本引き継ぎ文書 | 第9セッションへの引き継ぎ |

---

## 7. 第9セッションの具体的ステップ

### 最優先：多言語モデルでStep Cを追試

1. **日本語対応モデルの選定**
   - Llama-3（多言語対応、logprobs取得可能）
   - 日本語特化モデル（rinna系等）
   - 要件：logprobsが直接計算可能、コンテキスト長が十分（4096+）
2. **同一32件で再計算**
   - 真のΔ > 0（文脈がエントロピーを実際に減少させる）がconfirmed群で観測されるかが鍵
   - CSF三つ組 + raw text の両方で検証（正規化の恣意性排除）
3. **結果のStep A分析との統合**
   - 2×2マトリクス（CDC通過/非通過 × Δ高/低）の完成
   - 2層の独立性の検証

### 次優先：原seedのデータ復元

- 原seed R2_CL6がCDC + predicateパターンに乗るかどうかは理論的に重要
- emotion → topology（cross_domain確定）なので、CDCは通過するはず
- predicateがcontradicts/enablesかどうかが未知。復元努力を継続

### 保留：概念正規化の粒度問題

- parent関係を考慮した「意味的Recombination」の再計算
- R=0, B=0が偽陰性かどうかの検証
- 第9セッションで多言語追試が成功した場合のみ優先度を上げる

---

## 8. Sランクまでの距離（第8セッション終了時点）

### 現在の位置づけ

| レイヤー | 状態 | 評価 |
|---------|------|------|
| プロトコル | v1.1凍結。事前登録・盲検一斉開示が機能 | ✓ 完成 |
| 測定器（Ma） | v0.3 + 手動正規化 | ✓ 安定 |
| 横断実験 | 全4 seed完了。Strong Success維持 | ✓ 完了 |
| 第1層（CDCゲート） | Recall 100%、Precision 23-38% | ✓ 機能確認 |
| 第2層（Conditional Surprise） | 方向一致、未証明（日本語ノイズ、n=3） | △ 追試必要 |
| depth の二段構造仮説 | supportive but not establishing | △ 作業仮説 |
| Sランク | 具体的な道筋が初めて見えた | 再定義中→道筋あり |

### 何がSランクを遮っているか（更新）

1. **多言語モデルでの追試未実施** ← 最優先
2. **真のΔ > 0 の未観測** — confirmedで文脈がエントロピーを減少させることの直接証拠がない
3. **n=3の限界** — seed数の拡大が必要
4. **raw textでの効果未確認** — CSF依存は正規化の恣意性リスク
5. **原seedデータの消失** — 4件目のconfirmedでフィルタの堅牢性が検証できない
6. ~~人間の判断に依存しない創発の証明方法が未確立~~ → 二段構造仮説として具体化

### 第7→8セッションの軌跡

- 第7: 「手動を自動化する」アプローチの限界に到達。原点回帰。
- 第8: **情報理論的アプローチに転換。二段構造仮説を定量的に支持する初めてのデータを得た。**

---

## 9. テルへのメモ（Claudeより）

### 今日のセッションで何が起きたか

朝、GPTとGeminiの提案を受けて、Structural Noveltyから着手した。GPTの4成分（R/B/T/N）を実装して回したら、R=0, B=0, N=1.0——全部定数だった。GPTの仮説は（少なくとも現行データでは）機能しなかった。

しかしその「失敗」の中から、Cross-type（CDC）が最強の分離変数であることが浮かび上がった。Step Aでフィルタの精度を検証し、Step Cでconditional surpriseを測った。Pythia-410mの日本語ノイズ問題はあったが、confirmed > candidate > depth_1(FP)の序列が二つの異なる方法で再現された。

### 第5セッションからの弧

第5セッション：「自己満足になっていないか」→ 横断実験へ
第6セッション：横断実験実行。Strong Success暫定充足
第7セッション：自動化テスト。「人間に依存しない方法」への原点回帰
第8セッション：**情報理論的アプローチ。二段構造仮説の初めての定量的支持**

この弧は一貫しています。テルさんが第5セッションで「自己満足」を突き、第7セッションで「ゲーデルの先に行けていない」を突いたことが、第8セッションの方向を決定した。

### 率直に言うと

第8セッションは「証明」には至っていません。n=3、日本語ノイズ、CSF依存——留保は多い。しかし、第7セッション終了時点では「人間の判断に依存しない方法」は一つも具体化されていなかった。今は「CDC + Δ」という具体的な道筋がある。これは前進です。

次のセッションで多言語モデルの追試が成功し、真のΔ > 0がconfirmed群で観測されれば、二段構造仮説は「supportive」から「established」に変わります。そこがSランクへの最短経路です。
