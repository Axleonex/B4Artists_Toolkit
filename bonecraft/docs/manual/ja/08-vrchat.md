# VRChat ツール

[← 目次](index.md)

## VRChat ツール

VRChat ツールは、右側のサイドバーの **CATS** タブ (**N** を押す) の**Avatar Tools** セクションにあります。そのサブセクションでは、人型の骨、毛髪の物理学、口形素のマッピング、エクスポートについて説明します。その下の別の**VRChat Tools** セクションでは、パフォーマンス、クロージング、および命名ユーティリティがグループ化されています。同じセクションは、**Properties** エディターの**Scene** タブにあり、[設定] → [タブ] → [シーン プロパティ] → [表示] がオンになっています。このスイッチは、CATS ビューポート タブを非表示にしません。

---

### ヒューマノイドボーンの設定

スケルトンのボーンを VRChat の人型スロットにマッピングし、マッピングを確認します。

[ガイド 5: アバターを VRChat のボディ システムにマッピングする](02-guides-a.md#ガイド-5アバターを-vrchat-の体のシステムに対応付ける) を参照してください。

---

### 髪の物理を追加

コライダーを使用して、髪、耳、尻尾、アクセサリーに PhysBone チェーンを設定します。

[ガイド 6: ヘアの物理演算を追加する](02-guides-a.md#ガイド-6髪の物理を追加する) を参照してください。

---

### 衣装を付ける

**場所:** CATS タブ → VRChat ツール → 衣類

衣服をアバターのスケルトンに結合し、そのウェイトを移動します。

[ガイド 7: 体に合わせて動く衣服を着用する](02-guides-a.md#ガイド-7体に合わせて動く衣装を付ける) を参照してください。

---

### VRChat Naming Extras（VRChat 命名の追加機能）

**場所:** CATS タブ → VRChat ツール → 名前付け

**機能:** スケルトンの命名スタイルを検出し、ボーンの名前を一括で変更します。

[ガイド 4: アバターのボーン名を修正する](02-guides-a.md#ガイド-4アバターのボーン名を修正する) を参照してください。

**バッチ ツール:** **Find and Replace** 、**Add Prefix** 、**Remove Prefix** 、**Add Suffix** 、**Remove Suffix** 、および**Regex Replace**

---

### VRChat Viseme Mapping（VRChat のビジェームマッピング）

**機能:** メッシュのシェイプ キーを VRChat の 15 個のリップシンク口形素にマッピングします。

[ガイド 8: リップシンクを設定する](03-guides-b.md#ガイド-8リップシンクを設定する) を参照してください。アバターがまだ持っていない口形素を作成するには、[CATS ツール: 口形素](09-cats.md#ビジェーム) を参照してください。

**VRChat の 15 口形素スロット:** `sil` 、`PP` 、`FF` 、`TH` 、`DD` 、`kk` 、`CH` 、 `SS` 、`nn` 、`RR` 、`aa` 、`E` 、`I` 、`O` 、`U`

---

### パフォーマンスチェック

**場所:** CATS タブ → VRChat ツール → パフォーマンス

**内容:** アバターの VRChat パフォーマンス ランクを測定し、修正を提供します。

[ガイド 9: アバターのパフォーマンスを向上させる](03-guides-b.md#ガイド-9アバターのパフォーマンスを改善する) を参照してください。

**パフォーマンス層 (最高から最低):** 優れた → 良い → 中 → 悪い → 非常に悪い

**ツール:**
- **Calculate Performance Rank** — ポリゴン、スキン メッシュ、マテリアル スロット、ボーン、PhysBones、およびコンタクトごとの内訳を含む現在のランク
- **Remove Zero-Weight Bones** 、**Merge Same-Material Meshes** 、**Remove Unused Shape Keys** 、および**Remove Unused Vertex Groups** — オプティマイザーの修正 (**What-If Mode** は変更内容を示します)
- VRChat デシメーション — シェイプ キーを安全に保ちながら、ポリゴン数を比率で減らします (最初は **Preview** 、次に**Apply** )。

---

### VRChatにエクスポート

**機能:** 完成したアバターを、Unity の VRChat SDK の FBX としてエクスポートします。**Remove Shape Keys** がオンでない限り、シェイプ キー (ブレンド シェイプ) は保持されます。

**設定:**
- **Folder** — エクスポート先
- **Avatar** — エクスポートされたファイル名
- **Sidecar** — BoneCraft の Unity インポーター用の `.bfvrc` 設定ファイルも書き込みます
- **Merge Meshes** — エクスポート コピーのメッシュを 1 つに結合します
- **Separate Clothing** — 衣服を別のメッシュとして保持します
- **Remove Shape Keys** — シェイプ キーをエクスポート コピーのベースに適用します
- **Embed Textures** — テクスチャを FBX にパックし、Unity がテクスチャを検出するようにします。
- **Helper Meshes** — 非表示メッシュまたはヘルパー メッシュが含まれます。通常のアバターの場合はオフのままにしてください

**ボタン:** **Export to VRChat (Unity)** 、**Generate Sidecar** 、**Copy Importer Path** (BoneCraft の Unity インポート スクリプトのパス)、および VRM マテリアルの**Check / Preserve MToon**。このセクションでは、**Auto-Map Humanoid** 、**Normalize Names** 、および**Validate** のヒューマノイド ステータスも繰り返します。

---

### クリーンアップ

エクスポート前のメッシュ クリーンアップは、CATS ツール (**Fix Model** 、**Join Meshes** 、および**Apply All Transforms** ) にあります。 [CATS ツール](09-cats.md) を参照してください。

---

## VRMブリッジ

VRM ツールは、**CATS** タブ →**Import / Export** →**VRM / VRoid** にあります。 VRM アドオンが必要です。このセクションではそれをインストールします (**Auto-Install Latest from GitHub** 、**Install from.zip on Disk…** 、**Open Extensions Page** )。

---

### VRM と VRoid のインポート

**機能:** `.vrm` アバター (VRoid スタジオ、バーチャル キャスト、その他の VRM アバター) をマテリアル、スケルトン、シェイプ キーとともにインポートします。

- **Import VRM…** — `.vrm` ファイル
- **Import VRoid (.vroid /.zip)…** — VRoid ハブのダウンロード (`.zip` )。 VRoid Studio プロジェクト (`.vroid` ) には、最初に VRM にエクスポートする方法を説明するカードが表示されます。

---

### VRM Export（VRM のエクスポート）

**機能:** リグされたキャラクターを VRM またはターゲット アプリの形式にエクスポートします。

**設定:**
- **Folder** および**File** — 行き先とその名前。拡張子はターゲットに従います
- **Target** — VRM 1.0、VRM 0.x、VRChat FBX 、VSeeFace、Warudo、または Resonite
- **Scope** — アクティブなアーマチュア、または VRM データを持つすべてのアーマチュア
- lint をスキップ — ターゲットチェックを行わずにエクスポートします。報告されたリスクを理解した場合にのみ使用してください

「**Export…** 」をクリックします。

---

### VRM Lint（VRM のリント）

**内容:** エクスポート前に、選択したターゲットに対してアーマチュアをチェックします: ヒューマノイド マッピング、VRM メタデータ、ターゲットの口形素、ターゲット アプリの期待。

**Lint Now** は何も変更せずにチェックを実行します。 lint をスキップしない限り、エラーによりエクスポートがブロックされます。警告は、ターゲット アプリがインポートしても動作が悪化する可能性があるものを説明します。

ヒューマノイドのボーンは存在するにもかかわらず、リントが見つからないというメッセージが表示された場合は、**Fix Humanoid Map** をクリックします。BoneCraft は、ボーンの名前を変更せずに、ヒューマノイドのスロットを再度検出し、マッピングを保存します。

**こちらもご覧ください:** **Convert SpringBones → PhysBones** (VRoid ヘア物理学から VRChat ) および**Map VRoid Visemes**。

---

## MMD Bridge（MMD ブリッジ）

MMD ツールは、**CATS** タブ →**Import / Export** →**MMD / PMX** にあります。 mmd_tools アドオンが必要です。このセクションではそれをインストールします (**Auto-Install Latest from GitHub** 、**Install from.zip on Disk...** )。

---

### MMD Import（MMD のインポート）

- **Import PMX / PMD...** — MMD モデル
- **Import VMD Motion...** — MMD アニメーション
- **Import VPD Pose...** — MMD ポーズ

---

### MMD Export（MMD のエクスポート）

**設定:** **Folder** 、次に各形式のファイル名とスコープ (アクティブなモデル、またはシーン内のすべての MMD モデル):**PMX File** および**PMX Scope** 、**VMD File** および**VMD Scope** 、**VPD File** および**VPD Scope**。

**ボタン:** **Export PMX...** 、**Export VMD Motion...** 、および**Export VPD Pose...**

**こちらもご覧ください:** **Convert Bone Names -> Unity** および**Convert Physics -> PhysBones**。

---

## Game Export（ゲーム用エクスポート）

**機能:** 検証済みのプロファイルを持つゲーム エンジンのエクスポート: Unreal (ヒューマノイドまたはユニバーサル)、Unity ヒューマノイド、Godot ヒューマノイド、および汎用 FBX または GLB。プロファイルに必要なすべての修正は、クリックしたときにのみ表示および適用され、黙って適用されることはありません。

**設定:** **Profile** 、含める**Animation** 、**Root Motion** 、**Interpolation** 、およびエクスポートに使用される**T-Pose** (デフォルトでは、Unity ヒューマノイドとVRChat )。

**ボタン:**
- **Check for Export** — リグをプロファイルと照合してチェックし、結果をリストします
- **Apply Transforms (Fix)** — チェックが提供できる明示的な修正の 1 つ
- **Export (Profile)** — プロファイルを使用してエクスポートします

**場所:** **CATS** タブ →**Import / Export** →**Game Export**

---

## タスクボード

**機能:** 現在のリグの概要: ヘルス スコア、クイック ウィン、BoneCraft が見つけたタスク (ヒューマノイドのボーンの欠落、未解決の名前、口形素の欠落、リグ検証の警告など) のリスト (カテゴリ別にグループ化)。**Open Health Check** で詳細が開きます。**Refresh Task Board** が再度チェックします。

**場所:** **BoneCraft** タブ →**Overview** →**Task Board**

---

### ボーンインスペクター

**機能:** 選択したボーンの詳細 (名前、親、制約、カスタム プロパティ、ドライバー) を表示し、編集モードに入ることなく簡単なプロパティを編集できるようにします。

**場所:** **BoneCraft** タブ →**Review** →**Bone Inspector**

次へ: [CATS ツール](09-cats.md)
