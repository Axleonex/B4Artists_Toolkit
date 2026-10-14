# はじめに

[← 目次](index.md)

## BoneCraft とは

BoneCraft は Bforartists 用のアドオンで、キャラクターや小道具のリギングと、VRChat・VRoid / VRM・MMD 向けの 3D アバターの準備を手伝います。リグの作成、ウェイトの設定、ボーン名の修正、リップシンクとアイトラッキングの設定、エクスポートといった手間のかかる作業を自動化するパネルとボタンを追加します。

**BoneCraft にできないこと：**
- アバターの体の形をモデリングしたりスカルプトしたりすることはできません
- テクスチャやマテリアルを一から作ることはできません
- VRChat へ直接アップロードすることはできません（VRChat Creator Companion / SDK が必要です）

---

## BoneCraft と BoneForge

BoneCraft は Bforartists（Blender のフォーク）でのみ動作します。通常の Blender 向けには、ツールの少ない別のアドオン BoneForge があります。どちらか一方だけをインストールし、両方は入れないでください。通常の Blender では BoneCraft は読み込まれず、Bforartists を入手するためのボタンが付いたお知らせを 1 つ表示するだけです。

BoneForge 9.0.0 以降は標準 Blender 用です。BoneCraft は独立した Bforartists 用アドオンです。両方に Auto-Rig Wizard、Quick Rig、Mannequin、共有 CATS/Material Atlas ツールがあります。BoneCraft にはさらに Mechanisms、Control Picker、制作向け制御リグ、関節検出、プロファイル別エクスポートがあります。同じ配置にしてもこれらは BoneForge に追加されません。

## BoneCraft のインストール

**必要なもの：**
- Bforartists（BoneCraft は Bforartists 5.2 でテストされています）
- BoneCraft の `.zip` ファイル

**手順：**

1. Bforartists を開きます。
2. **編集**（Edit）→ **プリファレンス**（Preferences）→ **アドオン**（Add-ons）を開きます。
3. **ディスクからインストール…**（Install from Disk…）をクリックし、BoneCraft の `.zip` ファイルを選びます。
4. BoneCraft の横にあるチェックボックスをオンにして有効にします。
5. BoneCraft の項目を展開すると設定が表示されます：**Tabs**（タブ）、**Show Helpers**（ヘルパーを表示）、**Language**（言語）、そして **ツール** の一覧です。

**表示されるもの：** 左のツールシェルフ（**T** キー）に BoneCraft タブと Rig Builder タブ、右のサイドバー（**N** キー）に CATS タブが表示されます。

## 各機能の場所

タブで機能グループを選びます。Setup Rigging、Skin、Review、Avatar Tools、Facial はタブ内の展開可能なセクションで、独立したタブではありません。以下は英語 UI のラベルです。翻訳名は Language 設定に従います。

| タブ | 初期位置 | セクション |
| --- | --- | --- |
| Rig Builder | 左ツールシェルフ（T） | Auto-Rig Wizard, Quick Rig - premade armatures, Mannequin |
| BoneCraft | 左ツールシェルフ（T） | Overview, Setup Rigging, Skin, Mechanisms, Review |
| CATS | 右サイドバー（N） | CATS, Avatar Tools, VRChat Tools, Import / Export |

| ツール | 開く場所 |
| --- | --- |
| Bone Merge | BoneCraft → Setup Rigging → Bone Merge |
| Delta Mush / Proximity Wrap | BoneCraft → Skin → Delta Mush / Proximity Wrap |
| Viseme Library / Lip Sync | CATS → Avatar Tools → Viseme Library → Lip Sync |
| VRChat Viseme Mapping / Face Tracking | CATS → VRChat Tools → Facial |
| Humanoid / Hair | CATS → Avatar Tools → Set Up Humanoid Bones / Add Hair Physics |
| VRChat export | CATS → Import / Export → Unity / VRChat |
| VRM / MMD / I/O Hub | CATS → Import / Export → VRM / VRoid, MMD / PMX, Game Engine Export |
| Performance / Clothing / Naming | CATS → VRChat Tools → Check Performance / Attach Clothing / VRChat Naming Extras |

リグとビジェームライブラリにはアーマチュアを選択します。Delta Mush と Proximity Wrap にはオブジェクトモードのメッシュが必要です。Lip Sync はポーズモードのアーマチュアで使います。三角を押して展開します。Options は任意設定です。即時実行ツールは、次の操作の前に「最後の操作を調整」で設定を変更できます。

設定：Edit → Preferences → Add-ons → BoneCraft → Tabs でタブの表示を変更します。Scene Properties は Properties → Scene の Rig Builder、Mechanisms と CATS パネルを個別に制御します。Show Helpers は説明表示、Language は表示言語、Tools は各パッケージの有効化です。Ctrl+Shift+R でクイックパネルを開きます。

BoneCraft のタブは Preferences → Tabs の Left / Right で移動できます。Scene Properties → Show は初期状態でオンです。アーマチュアデータのパネルと、標準 Pose / Weights ツールシェルフ内のボタンもあります。これらは Bforartists 固有の入口です。

顔の操作は三種類です。CATS のビジェーム生成は口のシェイプキーを作成し、Viseme Library / Lip Sync はポーズ保存とアニメーションキー生成を行い、Facial は既存キーの VRChat 対応付けと顔トラッキング設定を行います。UVToolkit 由来の設定は CATS → Material Atlas → Override Inherited Settings → UV Packing にあります。共有アトラス機能であり、独立した UVToolkit 全体ではありません。

---

## どこから始めればよいか

あなたに最も近い説明を選んでください：

> **「新しい 3D モデルのファイル（FBX、OBJ、Blender ファイル）があり、VRChat 用に一からリギングしたい」**
> → [ガイド 1：最初のアバターを VRChat へ](02-guides-a.md#ガイド-1最初のアバターを-vrchat-へ)

> **「VRoid Studio でアバターを作り、VRM ファイルとして書き出した」**
> → [ガイド 2：VRoid のアバターを VRChat へ](02-guides-a.md#ガイド-2vroid-のアバターを-vrchat-へ)

> **「MMD モデル（PMX ファイル）があり、VRChat で使いたい」**
> → [ガイド 3：MMD のアバターを VRChat へ](02-guides-a.md#ガイド-3mmd-のアバターを-vrchat-へ)

> **「リギング済みのアバターがあるが、ボーン名が間違っていてアップロードできない」**
> → [ガイド 4：アバターのボーン名を修正する](02-guides-a.md#ガイド-4アバターのボーン名を修正する)

> **「リギング済みのアバターを、リップシンク、アイトラッキング、きれいなメッシュまで一度に VRChat 対応にしたい」**
> → [ガイド 13：CATS でアバターを VRChat 対応にする](03-guides-b.md#ガイド-13cats-でアバターを-vrchat-対応にする)

> **「特定の問題を解決したい」**
> → [クイック修正インデックス](10-reference.md#クイック修正インデックス)へ

次へ: [ガイド 1–7](02-guides-a.md)
