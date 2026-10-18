# リグビルダー

[← 目次](index.md)

両方式の音声付き実演は [IK/FK 入門動画と練習ファイル](https://github.com/Axleonex/B4Artists_Toolkit/blob/main/bonecraft/docs/tutorials/ikfk-beginner.md) を参照。

## 新しいリグを作る

Rig Builder はキャラクターのリグを作ります。左 Tool Shelf（**T**）の **Rig Builder** と、Preferences → Tabs → Scene Properties → Show がオンの **Properties → Scene** にあります。狭い棚は短いラベルになります。Auto-Rig Wizard、Quick Rig、Mannequin の順です。視点の **Add → Armature** からもウィザードや Quick Rig を起動できます。

---

### オートリグウィザード

**機能：** メッシュにマーカーを置きウェイト付きのリグを生成する、ゼロからの主な手順です。

[ガイド 1](02-guides-a.md#ガイド-1最初のアバターを-vrchat-へ) に手順があります。

**手順：** Select Mesh → Rig Type → Body Markers → Finger Markers → Face Markers → Review → Generate

**主な操作：**
- **Start Auto-Rig** で開始。上に **Back / Cancel**、メッシュ・種類・マーカー手順の下に **Next**。確認段階は **Generate Rig**、最後は **Close Wizard**。
- メッシュを選び **Body + Face / Body Only**、既存アーマチュア用の **Face Only** を指定。
- Smart Detection の **Detect Markers** は手足を追い信頼度付きで配置。**Accept High** は高信頼を保持、**Reset Low** は低信頼を消去。
- 体は **Guess Markers from Mesh / Guess Precision**、手形から指を推定する **Guess Finger Markers**、顔は **Guess Face Markers**。
- Finger Detail は `0 — No Fingers` ～ `5 — Full Human Hand`。
- 行ごとに **Place Marker**（矢印）、**Confirm Marker**（チェック）、**Reset Marker**（丸矢印）、左右の先頭は **Toggle Symmetry**。
- **Mirror L to R / Mirror R to L** は確定位置を反対側へ複製。
- **Confirm All Placed** で配置済みをすべて確定。
- **Generate Rig** の後、最終段階の **Build Control Rig / Close Wizard**。

**Generate Rig の生成物：**
- 指定した背骨・首の分割と **Kinematics** の IK/FK、IK のみ、FK のみの四肢。
- 指定本数の指ボーン。
- **Body + Face** では顔も生成し、**Generate Control Shapes** がオンなら形状も追加。
- 指定品質のウェイト。高密度形状は軽い代理メッシュを使い、678,000 頂点を約1分で処理し無言の失敗を防ぎます。

**Build Control Rig：** 確認画面の **Twist Bones、Skirt Bones、Face Controls、Joint Correctives** は Generate Rig では適用されず、エンジン制御リグ（ねじり、脚追従のスカート、視線・瞬き、関節補正シェイプキー）の設定です。生成後の最終段階で **Build Control Rig** を押して適用します。**Close Wizard** で選択がリセットされる前に実行。この方法のリグにだけ Rig Tools の Control Layer が出ます。

**場所：** Rig Builder → Auto-Rig Wizard

**視点で連続配置：** ウィザードを体・指・顔マーカー段階まで進め、Object Mode のツールバーで **Place Rig Markers** を有効化。ヘッダーに次の未確定マーカー、軸ロック、ミラーを表示します。指定メッシュをクリックして配置・確定。対称はウィザード設定に従い、行ごとの Place も使えます。完了表示後に **Next**。他所をクリックしても配置されません。

---

### Quick Rig

**機能：** BoneCraft Basic Humanoid（19 ボーン、Rigify 不要）や Rigify メタリグを一度で追加。速い分、個別調整は少なめです。

**主な操作：**
- Basic Humanoid と Rigify プリセット。後者が無効なら **Enable Rigify**。
- ボタンで即追加後 **Adjust Last Operation** でフィット、自動ウェイト、**Add IK/FK Controllers**、**Initial Pose** を調整。
- **T-Pose / A-Pose** でレストポーズ変更。
- Troubleshooting に **Diagnose Quick Rig (print to console)**、非メタリグ選択時は **Inspect Active Rig Controls**。
- Rigify メタリグ選択時は代わりに **Generate Control Rig (active metarig)** で Rigify 制御リグを生成。

**BoneCraft Rigs のカタログ：** 9 種類は下部の標準アセットシェルフの **Starter Rigs** にまとまります。左のカタログメニューでライブラリ **All**、**Starter Rigs** を一度有効化すると他のタブ横に表示。タブで閲覧します。**Add → Armature → Starter Rig Catalog** は依存関係を確認するフィット・追加ポップアップです。

Basic Humanoid は Rigify 不要。他は **Rigify** と表示され、無効時は選択・ドロップで **Enable Rigify & Add Rig** または Cancel。承認で既存 Rigify を有効化して続行、取消は何も追加しません。Quick Rig や必要時のポップアップ右クリックでも Enable Rigify を使えます。9.2.5 で視点左上の開始コントロールは撤去。依存不足や未収録プリセットは説明され、代替リグは追加しません。

クリックか視点へのドラッグで追加。メッシュ選択時はフィットし、自動ウェイトと制御生成は初期オフ、**Adjust Last Operation** で変更します。未選択なら新リグを選び Quick Rig の **Mesh**、**Fit Dropped Rig**。フィットは拡縮と配置なので制御・ウェイト前に関節を確認編集。領域外へのドロップ、Esc、右クリックは追加せず取消します。

**場所：** Rig Builder → Quick Rig、または Add → Armature → Quick Rig。

---

### マネキン

**機能：** 既存リグの周囲にプレビューを作り、完成メッシュなしで変形を確認。アーマチュアかその子メッシュを選択。リグがなければ Quick Rig で追加。本番では自作メッシュへ置換します。

**主な操作：**
- **Quick Mannequin** は固定の既定値で旧プレビューを置換。
- **Add Mannequin** はシーン設定を使い既定で置換、実行後の Adjust Last Operation に Replace Existing。
- **Regenerate** は保存済み設定で再生成。
- **Remove** はメッシュだけ削除しアーマチュアを保持。
- Options に **Mode、Body Type**、密度、**Radius Scale**。Advanced に領域倍率と出力。変更したシーン設定を使うには再度 **Add Mannequin**。

**場所：** Rig Builder → Mannequin

---

## 図解マネキン実習

<!-- Keep each illustrated step together and preserve the manual's print scale. -->
<style> section.chapter:has(#ch-06-rig-builder) img { max-width: 100%; max-height: 155mm; width: auto; height: auto; } @media print {   [id="06-rig-builder--図解マネキン実習"] { break-before: page; break-after: avoid; }   h4[id^="06-rig-builder--"] { break-before: page; break-after: avoid; }   h3[id^="06-rig-builder--パート"] { break-before: page; break-after: avoid; }   h3[id^="06-rig-builder--パート"] + h4 { break-before: avoid; }   section.chapter:has(#ch-06-rig-builder) h4 + p { break-after: avoid; }   section.chapter:has(#ch-06-rig-builder) p:has(> img) { break-before: avoid; break-after: avoid; }   section.chapter:has(#ch-06-rig-builder) p:has(> img) + p { break-before: avoid; } } </style>

[A：Simple Human からマネキン](#パートasimple-human-からマネキン)、[B：リグなしメッシュの-auto-rig](#パートbリグなしメッシュの-auto-rig)、[C：ウェイトと-ikfk](#パートcウェイトと-ikfk) の順です。全番号に実画面があり赤番号が説明に対応。撮影は **BoneCraft 9.1.2**、`Bforartists 5.2.0`。Blender の配置とキーは異なる場合があり、コマンド名を基準にします。

練習はカプセルのプレビューです。頭・手・胴体は仮形状で完成キャラクターではありません。新規ファイルで始め、2 保存点を保って元メタリグを失わず繰り返せるようにします。

`examples/mannequin/` に両例があります。`SimpleHuman_Mannequin.blend` は A の中立状態、`Mannequin_AutoRig.blend` は C のウェイト修正・ポーズ済み例です。

### パートA：Simple Human からマネキン

#### A1. Rigify を有効化

新規シーンで **Scene Properties → Rig Builder → Quick Rig**。未使用なら **Enable Rigify**。この実習は Rigify `Simple Human` で、**BoneCraft Basic Humanoid (19 bones)** とは別です。

![A1. Rigify を有効化：操作画面](../images/rig-builder/en/a01-enable-rigify.png)

*1：Scene Properties。2：Enable Rigify。*

#### A2. Simple Human を追加

Quick Rig の `Simple Human` で編集可能なメタリグを追加。まだメッシュではなく、この版では 29 ボーンです。

![A2. Simple Human を追加：操作画面](../images/rig-builder/en/a02-simple-human.png)

*1：Simple Human プリセット。*

#### A3. メタリグを確認

視点上で `Numpad 1` の正面正投影へ。ホイールで全体を表示します。最初は Pose Mode の場合があります。

![A3. メタリグを確認：操作画面](../images/rig-builder/en/a03-metarig.png)

*1：正面。2：Simple Human 骨格。*

#### A4. Object Mode へ戻る

モードメニューを **Object Mode** にし `SimpleHumanArmature` を選択したままにします。レスト姿勢変更・生成の前に Object Mode に戻します。

![A4. Object Mode へ戻る：操作画面](../images/rig-builder/en/a04-object-mode.png)

*1：モードメニュー。2：Object Mode。*

#### A5. T ポーズを使用

Quick Rig の **T-Pose** で腕が水平に。独自体形なら生成前に Edit Mode でフィットし、この練習では左右対称を保ちます。

![A5. T ポーズを使用：操作画面](../images/rig-builder/en/a05-t-pose.png)

*1：T-Pose コマンド。*

#### A6. マネキンを生成

**Mannequin → Options** で `Mode: Universal`、`Body Type: Neutral`、**Medium**、`Radius Scale: 1.00`。Advanced の領域倍率 1.00、`Joined (non-manifold)`、**Flat colour**、**Joint Smoothing** オン、Unified Volume オフ。**Add Mannequin** を実行。画像はカプセル結果です。Add は現在設定、Regenerate は保存済み設定を使います。

![A6. マネキンを生成：操作画面](../images/rig-builder/en/a06-final-settings.png)

*1：Add Mannequin。2：Universal と体形。3：Joined 出力と平滑化。*

#### A7. ボーンを動かす

アーマチュアの **Pose Mode** で左前腕（正面では画面右）を選び Rotate で少し回します。メタリグのウェイト付きプレビューが追従。C のアニメーター制御はまだありません。

![A7. ボーンを動かす：操作画面](../images/rig-builder/en/a07-select-forearm.png)

*1：Pose Mode。2：前腕と変換ギズモ。*

#### A8. 復元して保存

視点で全ポーズボーンを選び **F3** の `Clear Pose Transforms`、**All**。T ポーズを確認し **File → Save As** で `SimpleHuman_Mannequin.blend` を保存。この状態を保ちます。

![A8. 復元して保存：操作画面](../images/rig-builder/en/a09-clear-pose.png)

*1：Clear Pose Transforms を検索。2：All で選択ポーズをリセット。*

### パートB：リグなしメッシュの Auto-Rig

#### B1. マネキンメッシュを選択

A の中立状態から **Object Mode**、Outliner の `SimpleHumanArmature_Mannequin`。今回は意図的にリグを除去して再生成するため別名で保存し A を保ちます。

![B1. マネキンメッシュを選択：操作画面](../images/rig-builder/en/b01-select-mesh.png)

*1：アーマチュアではなくメッシュを選択。*

#### B2. プレビューをメッシュ化

マネキンのみ選び **F3** の `Convert Mesh`。表示中の中立形状を保持し Armature モディファイアーを除きます。必ず T ポーズに復元して実行。

![B2. プレビューをメッシュ化：操作画面](../images/rig-builder/en/b02-convert-mesh.png)

*1：Convert Mesh コマンド。*

#### B3. 親を解除

**Alt+P**、`Clear and Keep Transformation` で位置を保って親を解除。

![B3. 親を解除：操作画面](../images/rig-builder/en/b03-clear-parent.png)

*1：Clear and Keep Transformation。*

#### B4. 旧ウェイトを削除

**Object Data Properties → Vertex Groups** のメニューで `Delete All Groups`。旧メタリグのグループを除去し新しいものを生成します。この破棄可能な練習用メッシュだけで行います。

![B4. 旧ウェイトを削除：操作画面](../images/rig-builder/en/b04-clear-groups.png)

*1：Vertex Groups メニュー。2：Delete All Groups。*

#### B5. リグなし状態を確認

Outliner の目で旧 `SimpleHumanArmature` を隠します。マネキンは見え、Modifiers に Armature がなく Vertex Groups が空なら準備完了。BoneCraft 9.1.2 はアーマチュアから生成するため、この解除でリグなし練習形状を作ります。

![B5. リグなし状態を確認：操作画面](../images/rig-builder/en/b05-rigless-check.png)

*1：旧メタリグを隠す。2：空のモディファイアー。*

#### B6. 視点の Rig Builder を有効化

**Edit → Preferences → Add-ons → BoneCraft → Tabs** で **Rig Builder**、**Left**。閉じて視点上で **T**。このタブから配置します。検証した 9.1.2 ホストでは Scene Properties からの Place Marker は視点クリックを受け付けませんでした。

![B6. 視点の Rig Builder を有効化：操作画面](../images/rig-builder/en/b10a-enable-rig-builder-tab.png)

*1：Rig Builder を有効化。2：左 Tool Shelf。*

#### B7. Auto-Rig を開始

リグなしメッシュを選び **Start Auto-Rig**。画像は同じ Scene Properties のボタンですが、前手順の視点 Rig Builder 上部にもあります。

![B7. Auto-Rig を開始：操作画面](../images/rig-builder/en/b06-start-wizard.png)

*1：Start Auto-Rig。*

#### B8. 入力メッシュを選択

`Select Mesh` でマネキンを選び選択チェック、**Next**。ウィジェットや他のプレビューは選びません。

![B8. 入力メッシュを選択：操作画面](../images/rig-builder/en/b07-select-input.png)

*1：入力マネキン。2：Next。*

#### B9. 両方式のボディリグ

**Body Only**、`Kinematics: IK + FK`、**Generate Control Shapes** オンで **Next**。顔の形状がないので Body + Face は不要です。

![B9. 両方式のボディリグ：操作画面](../images/rig-builder/en/b08-body-ikfk.png)

*1：Body Only。2：IK + FK。3：Next。*

#### B10. 体マーカーを検出

Body Markers の Smart Detection で **Detect Markers**。推定は出発点です。対称メッシュは **Mirror Symmetry** をオンにし、全推定を確認します。

![B10. 体マーカーを検出：操作画面](../images/rig-builder/en/b09-detect-markers.png)

*1：Detect Markers。2：Mirror Symmetry。*

#### B11. 検出位置を確認

頭頂、首の根元、骨盤、手首、足首を形状と照合。分割形状は低信頼推定が出るため、主要と任意精密マーカーを修正。信頼度は元の検出結果で、行頭の緑チェックが現在位置の確定です。

![B11. 検出位置を確認：操作画面](../images/rig-builder/en/b10-review-markers.png)

*1：検出信頼度。2：体マーカー行。*

#### B12. 手首を配置

視点 **Rig Builder** の Wrist Left で **Place Marker** スポイト、手首表面をクリック。確定済みなら先に Reset してボタンを表示。正面の左手首は画面右です。

![B12. 手首を配置：操作画面](../images/rig-builder/en/b11-place-wrist.png)

*1：Wrist Left の配置。2：手首表面。*

#### B13. 鏡像の手首と足首

両手首に緑チェック、X が正負対称。`Ankle Left` も配置し Ankle Right は対称で生成。つま先ではなく足首へ。別サイズに例の座標を転記せず形状で確認します。

![B13. 鏡像の手首と足首：操作画面](../images/rig-builder/en/b12-mirrored-wrist.png)

*1：確定した手首対。2：鏡像手首。*

#### B14. 肩と肘を調整

Precision Markers の `Shoulder Left` を上腕支点、`Elbow Left` を肘の隙間へ再配置。鏡像を確認し手首は前腕の手側へ。この点が腕のチェーンを決めるので誤ったカプセル位置は修正します。

![B14. 肩と肘を調整：操作画面](../images/rig-builder/en/b13-arm-precision.png)

*1：肩と肘の行。2：肩。3：肘。*

#### B15. 股と膝を調整

`Hip Left` を太もも上、`Knee Left` を太ももとすねの間へ。鏡像を確認し、骨盤は両股の中央線に保ちます。

![B15. 股と膝を調整：操作画面](../images/rig-builder/en/b14-leg-precision.png)

*1：股と膝の行。2：股表面。3：膝の隙間。*

#### B16. 側面で深さとつま先を確認

視点上で `Numpad 3`。正面だけでなく Right Orthographic で確認。`Toe Left` を足先付近へ、鏡像も確認。正面で正しくても前後にずれている場合があります。

![B16. 側面で深さとつま先を確認：操作画面](../images/rig-builder/en/b15-side-depth.png)

*1：Right Orthographic。2：Toe 行。3：足表面。*

#### B17. かかとを配置

誤った推定をリセットし側面で `Heel Left` を足後方へ、Heel Right を確認。任意ですが検証版では両方 0 だと近接警告、足へ配置すると解消しました。

![B17. かかとを配置：操作画面](../images/rig-builder/en/b16-place-heels.png)

*1：確定したかかと対。2：位置。*

#### B18. 確定して次へ

頭頂、首根元、骨盤、全ペアを確認し **Confirm All Placed**、**Next**。緑チェックが確定で、9.1.2 では元の REVIEW/ADJUST 表示が残る場合があります。

![B18. 確定して次へ：操作画面](../images/rig-builder/en/b17-confirm-markers.png)

*1：Confirm All Placed。2：Next。*

#### B19. 指を省略

`0 — No Fingers`、**Next**。手はカプセルで指形状がありません。実際の手なら本数と指マーカーを設定します。

![B19. 指を省略：操作画面](../images/rig-builder/en/b18-no-fingers.png)

*1：No Fingers。2：Next。*

#### B20. 確認して生成

**All checks passed** が条件です。**IK + FK**、形状オン、`Spine Segments: 3`、`Neck Segments: 1`、`No Fingers`、**Game Ready**。Twist Bones、Skirt Bones、Preserve Volume、Joint Correctives はオフ、**Generate Rig**。これは単純な練習用で汎用出力設定ではありません。

![B20. 確認して生成：操作画面](../images/rig-builder/en/b19-review-generate.png)

*1：マーカー検査。2：生成設定。3：Generate Rig。*

#### B21. 制御リグを構築

生成後 **Build Control Rig**。Generate Rig は身体とウェイト、Build Control Rig は次の制御層を追加します。完了画面に一般的な案内が出ても、入力メッシュはあるので Quick Mannequin を再実行しません。

![B21. 制御リグを構築：操作画面](../images/rig-builder/en/b20-build-controls.png)

*1：Build Control Rig。*

#### B22. ウィザードを終了

完了表示後 **Close Wizard**。Outliner に新アーマチュア。旧 Simple Human は隠したまま。実際に変形することを確認し、ボーンが見えるだけで合格にしません。

![B22. ウィザードを終了：操作画面](../images/rig-builder/en/b21-close-wizard.png)

*1：構築ボタン無効。2：Close Wizard。*

### パートC：ウェイトと IK/FK

検証版の生成アーマチュア名は以下です。Outliner とウェイトツールで使います。

```text
BoneForge_Rig
```

`FK (Forward Kinematics)` は上腕→前腕→手と親から回転を伝え、大きな振りや自由な手足に適します。`IK (Inverse Kinematics)` は手首・足首の端点を動かし、そこへ届くようチェーンを解きます。接地や面に触れる手に向きます。

| 作業 | 制御 | 確認 |
|---|---|---|
| 腕を振る | FK 肩と肘 | 子が親に追従 |
| 手を置く | IK 手首 | 肩肘が目標へ解かれる |
| 足を接地 | 脚の IK 足首 | 到達可能な目標を保ち体を移動 |
| 肘膝の向き | IK ポール | 曲がる方向を指定、手足の目標とは別 |
| 方式変更 | 各肢の IK/FK | キー前にスナップ姿勢を確認 |

同じ腕で比較します。切替は四肢ごと。`Bake IK / Bake FK` はアニメーション変換で、単一ポーズ切替はベイクやキーの代わりになりません。他は [Control Layer](05-rig-tools.md#control-layerコントロールレイヤーikfk)。

#### C1. 制御層を開く

**生成アーマチュア**を **Pose Mode**、**BoneCraft → Review → Control Layer**。四肢ごとに切替、まず **arm-L → FK**。左右はキャラクター基準で arm-L は正面の画面右です。

![C1. 制御層を開く：操作画面](../images/rig-builder/en/c02-control-layer.png)

*1：Pose Mode。2：Control Layer と arm-L。*

#### C2. コントロールを表示

**Object Data Properties → Bone Collections** の `Controls` と **FK** の Solo 星で制御形状を分離。隠れるなら Viewport Display の **In Front**。後で **IK** も表示。このホストで BoneCraft Collections が描画できなくても標準一覧を使えます。

![C2. コントロールを表示：操作画面](../images/rig-builder/en/c03-visible-controls.png)

*1：Controls/FK の Solo 星。2：In Front。*

#### C3. 前腕 FK を選択

正面の左肘の丸を選び **forearm.fk-L** を確認。肘で回ります。肩を選ぶと上腕と子全体が回ります。

![C3. 前腕 FK を選択：操作画面](../images/rig-builder/en/c04-select-fk.png)

*1：forearm.fk-L。2：arm-L の FK が有効。*

#### C4. 回転して変形を確認

全体 **Y** で約 `−45°`。Rotate ツール、図のキーマップなら **Ctrl+E、Y、-45、Enter**。Blender 標準は **R**。画像は上腕まで傾く初期ウェイトの問題を示し、このまま完成にしません。

![C4. 回転して変形を確認：操作画面](../images/rig-builder/en/c05-fk-weight-check.png)

*1：FK テストで上腕が誤追従。*

#### C5. ウェイトを再計算

失敗したら **Object Mode** でメッシュを選び **BoneCraft → Skin → Weight Tools → Automatic Bone Weight Recalculation**。Mesh to Reweight はマネキン、Existing Armature は**生成アーマチュア**。**Body**、`Body Method: Bone Heat`、`New Weight Strength: 1.00`、`Smooth Passes: 0`、`Max Bones per Vertex: 0`、`Minimum Weight: 0.001`、**Keep Weight Backup** オンで再計算。検証版の分割形状を修復できました。

![C5. ウェイトを再計算：操作画面](../images/rig-builder/en/b23-recalculate-weights.png)

*1：メッシュとリグ。2：Bone Heat。3：置換設定とバックアップ。4：再計算。*

#### C6. 修復した FK を確認

生成リグの **Pose Mode** へ。上腕は水平のまま前腕が肘から上がること。隠れた `WEIGHTS_BACKUP_…` が旧ウェイトを保持。自作キャラクターも全肢を確認し、骨格生成だけでスキニング正常と判断しません。

![C6. 修復した FK を確認：操作画面](../images/rig-builder/en/c05-fk-result.png)

*1：上腕はそのまま。2：前腕が肘で曲がる。*

#### C7. 同じ腕を IK へ

**arm-L → IK** でターゲットが現在ポーズへスナップし、腕の姿勢を保ちます。隠れるなら Solo に **IK**。駆動が変わるだけでアニメーション記録ではありません。

![C7. 同じ腕を IK へ：操作画面](../images/rig-builder/en/c06-switch-ik.png)

*1：arm-L IK。2：切替でも姿勢保持。*

#### C8. 手首 IK ターゲット

手首を選び **forearm.ik-L**。名前は前腕ですが腕の端点ターゲットです。手の位置を動かすと肩・肘角が解かれます。

![C8. 手首 IK ターゲット：操作画面](../images/rig-builder/en/c07-select-ik.png)

*1：選択した手首目標。2：選択名。*

#### C9. 動かして比較

全体 **X** に少し内側、例は `−0.15 m`。図のキーは **Ctrl+W、X、-0.15、Enter**、または Move の X 矢印。Blender 標準は **G**。FK と比べ端点が両段を導きます。到達できる範囲に保ちます。

![C9. 動かして比較：操作画面](../images/rig-builder/en/c08-move-ik.png)

*1：手首端点。2：チェーンの応答。3：X 移動例。*

#### C10. 戻して保存

再び **arm-L → FK**。FK が IK 姿勢へ合います。飛びがないことを確認し **File → Save As** で `Mannequin_AutoRig.blend`。図は FK の保存例です。中立コピーなら全肢 FK、可視制御を全選択して A と同じ **F3 → Clear Pose Transforms → All**、別名保存。

![C10. 戻して保存：操作画面](../images/rig-builder/en/c10-save-complete.png)

*1：FK に復帰。2：姿勢保持。3：保存名。*

**完了確認：** 元メタリグ例を保持し、リグなし化、新しい身体と制御生成、ウェイト修正、FK 回転と IK 移動を比較しました。練習例として保管し、本番では適切なキャラクター形状へ置換します。

---

### アニメーションのリターゲット

あるスケルトンから別のスケルトンへのアニメーションの移し替えは、[リグツール：リターゲット](05-rig-tools.md#リターゲット) で説明しています。

---

## ボーンマージ

**できること：** 2 つのアーマチュアを 1 つにまとめます（例：体のリグと、衣装や髪のリグ）。ウェイトはすべて保たれます。

[ガイド 11](03-guides-b.md#ガイド-112-つのリグを-1-つにまとめる) で手順を順に説明しています。

**3 つの段階：**
1. 範囲 — 2 つのアーマチュアを選び、違いを確認する
2. 名前の変更 — 名前の衝突を解決し、新しいボーンに印を付ける
3. マージ — プレビューしてからマージする

**主な操作：**
- **ベース** — 残るアーマチュア。もう一方のアーマチュアはこれにマージされた後、非表示になります
- **Analyze**（解析）— 2 つのスケルトンを比べます。**Acknowledge Scope — Proceed to Rename**（範囲を確認 — 名前の変更へ進む）で段階 2 が開きます
- **Normalize Both Armatures**（両方のアーマチュアを正規化）— 両方のリグの標準のボーンを、1 つの命名規則（Mixamo Prefixed、Mixamo Stripped、またはカスタム）に合わせて名前を変更します
- **Auto-Propose Renames**（名前の変更を自動提案）— マージされる側のリグ独自のボーンに名前を提案します
- **Apply Rename**（名前の変更を適用）— 1 項目の名前を変更します（元に戻す 1 回分）。**Apply Batch Pattern**（一括パターンを適用）はパターン（`{bone}`、`{side}`、`{index}` を使用）で多くの名前を変更します
- **Mark as Unique**（固有として指定）— ボーンをマージせず、新しいボーンとして残します
- **Verify Rename — Proceed to Merge**（名前の変更を確認 — マージへ進む）— 段階 3 を開きます
- **Run Merge Preview**（マージのプレビューを実行）— 何も変えずに、マージで何が起きるかを報告します
- **アーマチュアをマージ** — 両方のアーマチュアをバックアップしてからマージします

**場所：** BoneCraft → Setup Rigging → Bone Merge

次へ: [Mechanisms（メカニズム）](07-mechanisms.md)
