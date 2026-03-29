# App Store 審査ノウハウ集 — MeetToDo v1.0 実戦記録

MeetToDo v1.0 を App Store に出すまでに経験した全リジェクトと解決策。
次回のアプリ開発・アップデートで同じ轍を踏まないためのナレッジベース。

---

## 目次

1. [審査リジェクト年表](#審査リジェクト年表)
2. [最も苦労したポイント TOP5](#最も苦労したポイント-top5)
3. [IAP（課金）システム設計ノウハウ](#iap課金システム設計ノウハウ)
4. [提出前チェックリスト](#提出前チェックリスト)
5. [ビルド・署名のハマりどころ](#ビルド署名のハマりどころ)
6. [審査を早く通すテクニック](#審査を早く通すテクニック)

---

## 審査リジェクト年表

| # | ガイドライン | 内容 | 解決にかかったビルド数 |
|---|-------------|------|---------------------|
| 1 | 3.1.2(c) | EULAリンクが一部の言語に未記載 | 2回 |
| 2 | 2.3.7 | スクリーンショットに価格表示（"Free", "¥500"等） | 3回 |
| 3 | 2.3.2 | プロモーション画像のテキストが小さい | 4回（最終的に画像削除） |
| 4 | 2.1 | IAPバイナリ未提出（プロダクトだけ提出） | 1回 |
| 5 | 2.1 | iPadでの動作不良 | 1回 |

---

## 最も苦労したポイント TOP5

### 1. プロモーション画像のテキストサイズ（Guideline 2.3.2）

**状況**: v2 → v3 → v4 と3回画像を作り直しても「テキストが小さい」でリジェクトされ続けた。

**学び**:
- Apple の「テキストが十分に大きい」の基準は非常に厳しい
- テキスト入りのプロモ画像を通すのは想像以上に難しい
- **プロモーション画像は任意**。Apple自身が「削除しても良い」と明記している

**結論**: **迷ったらプロモ画像を設置しない**。これが最も確実な解決策。

---

### 2. 全言語のメタデータ管理（Guideline 2.3.7 / 3.1.2(c)）

**状況**: 日本語のメタデータだけ修正して再提出 → 英語/韓国語/中国語に問題が残っていてリジェクト。これを何度も繰り返した。

**見落としやすい組み合わせ**:
- スクリーンショット × 4言語 × 2デバイス（iPhone/iPad） = **8パターン**全て確認が必要
- 説明文のEULAリンク × 4言語
- 審査メモ（Review Notes）にも価格表示NG

**NGワード一覧**（スクリーンショット・審査メモ内）:
```
¥500, $4.99, ¥4,000        ← 具体的な金額
Free, 無料, ¥0, 免费       ← 無料表現（全言語）
Free vs Pro                 ← "Free"が含まれるためNG
無料で始める, Try for Free  ← 無料表現を含む文
5回/月（無料）              ← カッコ内も含めNG
```

**対策**:
- スクリーンショット作成段階で**価格情報を一切入れない**設計にする
- App Store Connect の「メディアマネージャーですべてのサイズを表示」で全言語・全デバイスを一括チェック
- 修正は**必ず全言語に同時適用**する

---

### 3. IAPプロダクトとビルドの紐付け（Guideline 2.1）

**状況**: IAPプロダクトだけ先に提出したが、ビルドと紐付けていなかったため「binary was not submitted」エラー。

**対策**:
- App Store Connect のバージョンページで「App内課金とサブスクリプション」セクションにIAPプロダクトを追加
- **IAPプロダクトは必ずアプリのビルドとセットで提出**する
- IAPプロダクト単体では審査に出せない

---

### 4. iPadの動作確認漏れ

**状況**: `supportsTablet: true` にしているのにiPadでの動作確認を怠り、レイアウト崩れや課金フローの不具合。

**対策**:
- `supportsTablet: true` の場合、iPad実機（またはシミュレータ）テストは必須
- 特に Paywall 画面、モーダル、ボトムシートのレイアウト確認
- iPadでIAP購入フロー（Sandbox）をテスト
- iPadスクリーンショットも全言語分用意（サイズ: 2048×2732px / 2064×2752px、1pxでもずれるとアップロード不可）

---

### 5. デバッグコードの混入

**状況**: 開発中のデバッグ用UI・ログ・テストエンドポイントがビルドに残ったまま提出。

**git履歴**:
```
c187ff4 chore: 一時的なサブスクデバッグ用エンドポイント追加
f063fff fix: デバッグコード完全除去 - 審査提出用クリーンビルド
```

**対策**:
- 審査提出前にコードベース全体を `console.log`, `__DEV__`, デバッグ用のAPI呼び出しで検索
- `__DEV__` ガードで囲んだログは残してOK（リリースビルドで除去される）
- テスト用エンドポイント（`/api/debug/*`）は本番環境で無効化 or 削除
- 提出前チェック: `git diff` で不要なデバッグコードが含まれていないか確認

---

## IAP（課金）システム設計ノウハウ

### アーキテクチャ全体像

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   モバイル    │     │   バックエンド  │     │  Apple/Google │
│  (Expo RN)   │────▶│  (Next.js)    │     │   Store API   │
│              │     │              │     │              │
│ react-native │     │ /api/sub/    │     │ verifyReceipt│
│ -iap v14     │     │   verify     │────▶│ (or JWS)     │
│              │     │              │     │              │
│ purchaseToken│────▶│ receipt検証   │◀────│ 有効/無効     │
│              │     │ → DB更新     │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

### 設計原則

#### 1. レシート検証は必ずサーバーサイドで行う

```
❌ クライアントだけで課金状態を管理
✅ サーバーでレシートを検証 → DBに状態保存 → クライアントに結果返却
```

**理由**: クライアント側の課金状態は改ざん可能。レシート検証はサーバーでやらないとセキュリティホールになる。

#### 2. StoreKit 2 (JWS) と Legacy Receipt の両方に対応する

react-native-iap v14+ では `purchaseToken` が統一インターフェースとなった。

```typescript
// JWSトークン判定（3つのdot区切りBase64URL）
function isJWSToken(data: string): boolean {
  const parts = data.split('.');
  return parts.length === 3 && parts.every(p => p.length > 0);
}
```

- **iOS**: StoreKit 2 の JWS 署名済みトランザクション（`eyJ...`で始まる）
- **Android**: Google Play の purchaseToken（プレーンな文字列）
- サーバー側で形式を自動判定し、適切なハンドラーにルーティング

#### 3. Sandbox ↔ Production の自動フォールバック

```typescript
// Status 21007 = sandbox receipt sent to production
if (appleData.status === 21007) {
  // Sandbox URLで再検証
  const sandboxRes = await fetch('https://sandbox.itunes.apple.com/verifyReceipt', ...);
  return handleAppleResponse(sandboxData, userId);
}
```

**なぜ必要か**: TestFlight ビルドや Apple 審査員はSandbox環境を使う。本番URLに送ると `21007` が返るので、自動的にSandboxにフォールバックする。

#### 4. サブスク期限をDBに保存し、自動降格する

```typescript
// DBスキーマ
model User {
  plan                       String    @default("free")
  subscriptionExpiresAt      DateTime?
  appleOriginalTransactionId String?
}

// 自動降格ロジック（プラン取得時に毎回チェック）
if (user.plan === 'pro') {
  if (user.subscriptionExpiresAt && user.subscriptionExpiresAt < now) {
    // 期限切れ → freeに降格
    await prisma.user.update({ data: { plan: 'free' } });
  } else if (!user.subscriptionExpiresAt && user.appleOriginalTransactionId) {
    // IAP購入済みだが期限情報なし（旧データ）→ freeに降格
    await prisma.user.update({ data: { plan: 'free' } });
  }
}
```

**ポイント**:
- `subscriptionExpiresAt` をDBに保存して期限管理
- プラン情報を返すAPI（`getUserPlan()`）で毎回期限チェック → 期限切れなら自動降格
- 期限情報がない古いデータも安全にハンドリング（freeに降格して再購入を促す）

#### 5. エラーハンドリングの網羅的パターン

課金まわりのエラーは種類が多い。以下を全てハンドリングする：

| エラー | コード | 対応 |
|--------|--------|------|
| ユーザーキャンセル | `E_USER_CANCELLED`, `user-cancelled` | サイレントに無視（エラー表示しない） |
| 購入済み | `E_ALREADY_OWNED`, `already owned` | ローカライズされたエラーメッセージ表示 |
| 接続失敗 | initConnection失敗 | 再接続を試みる → 失敗ならエラーメッセージ |
| 商品未取得 | products.length === 0 | 「商品が見つかりません」メッセージ |
| レシート検証失敗 | API呼び出しエラー | 「検証に失敗しました」メッセージ |
| サブスク期限切れ | plan !== 'pro' | 「サブスクリプションの期限が切れています」 |
| Expo Go環境 | `Constants.appOwnership === 'expo'` | IAPモジュールをロードしない、Alert表示 |

```typescript
// ユーザーキャンセルはエラーではない → サイレントリターン
if (e.code === 'E_USER_CANCELLED' || e.code === 'user-cancelled') {
  return null;
}

// 購入済みはユーザーフレンドリーなメッセージに変換
if (e.code === 'E_ALREADY_OWNED' || e.message?.includes('already owned')) {
  throw new Error(i18n.t('iapAlreadyOwned'));
}
```

#### 6. react-native-iap の遅延読み込み（Expo Go対応）

```typescript
// Expo Go ではネイティブモジュールが使えない → 遅延読み込みで安全に回避
const isExpoGo = Constants.appOwnership === 'expo';

function loadIAP() {
  if (isExpoGo) {
    RNIap = {};
    isIAPAvailable = false;
    return false;
  }
  try {
    RNIap = require('react-native-iap');
    isIAPAvailable = true;
  } catch {
    RNIap = {};
    isIAPAvailable = false;
  }
  return isIAPAvailable;
}
```

**なぜ必要か**: `import` 文でトップレベル読み込みすると Expo Go で即クラッシュする。`require()` で遅延読み込みし、Expo Go 検出時はスキップする。

#### 7. 購入リスナーのライフサイクル管理

```typescript
// Setup（Paywall画面マウント時）
export function setupPurchaseListeners(onSuccess, onError) {
  purchaseUpdateSubscription = RNIap.purchaseUpdatedListener(async (purchase) => {
    const receipt = purchase.purchaseToken;
    const result = await api.verifyReceipt(receipt);
    await RNIap.finishTransaction({ purchase, isConsumable: false });
    // ...
  });
  purchaseErrorSubscription = RNIap.purchaseErrorListener(async (error) => {
    // ...
  });
}

// Cleanup（Paywall画面アンマウント時）
export async function cleanupIAP() {
  purchaseUpdateSubscription?.remove();
  purchaseErrorSubscription?.remove();
  await RNIap.endConnection();
}
```

**重要**:
- `finishTransaction()` を呼ばないと Apple から「未完了トランザクション」警告が来る
- アンマウント時にリスナー解除 + `endConnection()` でメモリリーク防止
- Paywall画面に `mounted` フラグを持たせ、アンマウント後の state 更新を防止

#### 8. 「購入を復元」は必須機能

```typescript
export async function restorePurchases(): Promise<boolean> {
  const purchases = await RNIap.getAvailablePurchases();
  if (purchases.length > 0) {
    const receipt = purchases[purchases.length - 1].purchaseToken;
    const result = await api.verifyReceipt(receipt);
    return result.plan === 'pro';
  }
  return false;
}
```

**Apple審査で必須**: Paywall画面に「購入を復元」ボタンがないとリジェクトされる。機種変更やアプリ再インストール時にユーザーが購入を復元できる動線。

### Sandbox テストの注意点

| 項目 | 値 |
|------|----|
| 月額サブスクの更新間隔 | 5分 |
| 年額サブスクの更新間隔 | 1時間 |
| 自動更新の最大回数 | 6〜12回で自動期限切れ |
| TestFlightビルドのIAP | 自動的にSandbox環境 |
| Apple審査員のテスト | 新規Sandboxアカウントで実施 |

**Tip**: テスト時は毎回新しいSandboxアカウントを作成するのがベスト。古いアカウントは購入履歴が残っていて `Item already owned` が発生しやすい。

---

## 提出前チェックリスト

### App Store Connect（メタデータ）
- [ ] **全言語の説明文にEULAリンク記載**（最重要）
- [ ] 説明文にサブスク情報（プラン名・期間・自動更新・キャンセル方法）
- [ ] スクリーンショットに価格表示なし（全言語 × 全デバイス）
- [ ] プロモーション画像なし（or テキスト十分大きい）
- [ ] プライバシーポリシーURL設定済み
- [ ] IAPプロダクトがバージョンに紐付け済み
- [ ] 審査メモにテストアカウント情報とテスト手順

### アプリ内
- [ ] 利用規約リンクあり（設定画面）
- [ ] プライバシーポリシーリンクあり（設定画面）
- [ ] 「購入を復元」ボタンあり（Paywall画面）
- [ ] サブスク画面にプラン名・期間・自動更新の説明
- [ ] アカウント削除機能あり
- [ ] iPadレイアウト正常
- [ ] iPadでIAP購入動作

### ビルド
- [ ] デバッグコード除去（`console.log`, テスト用UI, デバッグ用API）
- [ ] `ITSAppUsesNonExemptEncryption = false` 設定済み
- [ ] ビルド番号が前回より大きい

---

## ビルド・署名のハマりどころ

### Expo prebuild で CFBundleVersion がリセットされる

```bash
# prebuild --clean するたびにビルド番号が 1 に戻る
npx expo prebuild --clean

# 手動で修正が必要
sed -i '' 's|<string>1</string>|<string>27</string>|' ios/MeetToDo/Info.plist
```

**対策**: prebuild 後にビルド番号を `sed` で再設定するスクリプトを用意。

### 手動署名（Manual Signing）

```xml
<!-- ExportOptions.plist -->
<key>signingStyle</key><string>manual</string>
<key>provisioningProfiles</key>
<dict>
  <key>com.meettodo.app</key><string>Profile Name</string>
</dict>
```

`automatic` で「No profiles for」エラーが出る場合は `manual` に切り替える。

---

## 審査を早く通すテクニック

1. **一度に全部直す** — 1つだけ直して再提出すると別の問題で再リジェクト。修正は全言語・全デバイス同時に
2. **迷ったら削除** — プロモ画像など任意要素はリスクがあれば設置しない
3. **審査メモを活用** — テストアカウント、テスト手順、対応内容を具体的に記載
4. **リジェクト時は返信で具体的に説明** — 「ここをこう修正しました」と明示
5. **審査員は新規アカウントでテストする** — Sandboxの購入履歴は引き継がれない前提で設計

---

## 技術スタック別の注意点

| 技術 | バージョン | 注意点 |
|------|-----------|--------|
| react-native-iap | v14+ | `transactionReceipt` 廃止 → `purchaseToken` を使う |
| Expo | SDK 52+ | prebuildでCFBundleVersionリセット |
| Next.js (Backend) | 14+ | Route Handlers でレシート検証 |
| Prisma | 5+ | `subscriptionExpiresAt` を DateTime? で管理 |

---

*最終更新: 2026年3月29日*
*MeetToDo v1.0 App Store 審査経験（リジェクト5回以上）に基づく*
