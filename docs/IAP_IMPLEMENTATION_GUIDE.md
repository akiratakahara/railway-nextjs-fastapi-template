# iOS In-App Purchase (IAP) 実装ガイド

React Native (Expo) + バックエンドでの Apple IAP サブスクリプション実装の全体像。
実装時のハマりポイントと設計パターンをまとめています。

---

## 目次

1. [全体アーキテクチャ](#1-全体アーキテクチャ)
2. [App Store Connect 設定](#2-app-store-connect-設定)
3. [react-native-iap v14 の注意点](#3-react-native-iap-v14-の注意点)
4. [フロントエンド実装](#4-フロントエンド実装)
5. [バックエンド実装（レシート検証）](#5-バックエンド実装レシート検証)
6. [データベース設計](#6-データベース設計)
7. [プラン制限の適用](#7-プラン制限の適用)
8. [Sandbox テスト](#8-sandbox-テスト)
9. [エラーハンドリング](#9-エラーハンドリング)
10. [トラブルシューティング](#10-トラブルシューティング)

---

## 1. 全体アーキテクチャ

```
┌─────────────────┐       ┌─────────────────┐       ┌──────────────┐
│   Mobile App    │       │    Backend API   │       │  Apple IAP   │
│  (React Native) │──────>│   (API Server)   │       │  (StoreKit)  │
│                 │       │                  │       │              │
│  react-native-  │       │  POST /api/      │       │  App Store   │
│  iap v14+       │<----->│  subscription/   │<----->│  Connect     │
│  (StoreKit 2)   │       │  verify          │       │              │
└─────────────────┘       └─────────────────┘       └──────────────┘
```

**購入フロー:**
1. ユーザーがPaywall画面でプランを選択
2. `react-native-iap` が StoreKit 2 経由で Apple に購入リクエスト
3. Apple が購入を処理し、JWS (JSON Web Signature) トークンを返却
4. `purchaseUpdatedListener` で JWS トークン (`purchase.purchaseToken`) を取得
5. JWS トークンをバックエンドに送信
6. バックエンドが JWS をデコードし、bundleId・有効期限を検証
7. DB のユーザープランを更新
8. フロントエンドが結果を受け取りUI更新

---

## 2. App Store Connect 設定

### サブスクリプション商品の設定

App Store Connect > アプリ > サブスクリプション:

| 項目 | 月額プラン例 | 年額プラン例 |
|------|-------------|-------------|
| Product ID | `com.yourapp.pro.monthly` | `com.yourapp.pro.yearly` |
| 参照名 | AppName Pro Monthly | AppName Pro Yearly |
| サブスクリプショングループ | AppName Pro |
| 価格ティア | Tier 1相当 | Tier 6相当 |

> **注意:** Product ID は一度作成すると**変更・削除不可**。命名規則: `com.{bundleId}.{plan}.{period}`

### サブスクリプショングループ

同一グループ内のプランはアップグレード/ダウングレード可能。異なるグループは同時購入可能。
通常は1つのグループに全プランをまとめる。

---

## 3. react-native-iap v14 の注意点

### v12/v13 → v14 の破壊的変更

react-native-iap v14 は Nitro Modules ベースに刷新され、多くの API が変更された。

| 項目 | v12/v13 (旧) | v14+ (新) |
|------|-------------|-----------|
| 商品取得 | `getSubscriptions({ skus })` | `fetchProducts({ skus, type: 'subs' })` |
| 購入リクエスト | `requestSubscription({ sku })` | `requestPurchase({ request: { apple: { sku } }, type: 'subs' })` |
| 商品ID | `product.productId` | `product.id` |
| 価格表示 | `product.localizedPrice` | `product.displayPrice` |
| レシート | `purchase.transactionReceipt` | `purchase.purchaseToken` |
| トランザクション完了 | `finishTransaction(purchase)` | `finishTransaction({ purchase, isConsumable: false })` |

### 最重要: `purchaseToken` を使う

v14 では StoreKit 2 ベースになり、`transactionReceipt` プロパティは**存在しない**。

```typescript
// ❌ v12/v13 (動かない)
const receipt = purchase.transactionReceipt;

// ✅ v14+ (正しい)
const receipt = purchase.purchaseToken;
// iOS: JWS signed transaction (3パートのBase64url)
// Android: Google Play purchase token
```

これを間違えると `receipt` が `undefined` になり、「検証に失敗しました」エラーが発生する。

### 購入リクエストのプラットフォーム分岐

```typescript
await RNIap.requestPurchase({
  request: Platform.OS === 'ios'
    ? { apple: { sku } }
    : { google: { skus: [sku], subscriptionOffers: [{ sku, offerToken: '' }] } },
  type: 'subs',
});
```

### Expo Go では動かない

react-native-iap はネイティブモジュールなので Expo Go では使用不可。EAS Build (Development Build) が必要。

---

## 4. フロントエンド実装

### 推奨ファイル構成

```
mobile/
├── services/
│   ├── iap.ts          # IAP ロジック（初期化・購入・リストア・リスナー）
│   └── api.ts          # バックエンドAPI呼び出し（verifyReceipt含む）
├── app/
│   ├── paywall.tsx     # 課金画面UI
│   └── (tabs)/
│       └── settings.tsx # 設定画面（プラン表示）
└── i18n/
    ├── ja.ts           # 日本語（課金関連テキスト）
    └── en.ts           # 英語
```

### iap.ts の主要関数

```typescript
initIAP(): Promise<boolean>                           // IAP接続初期化
getProducts(): Promise<Product[]>                      // 商品情報取得
purchaseSubscription(sku: string): Promise<void>       // サブスクリプション購入
restorePurchases(): Promise<boolean>                   // 購入復元
setupPurchaseListeners(onSuccess, onError): void       // 購入リスナー設定
cleanupIAP(): Promise<void>                           // IAP接続解除
```

### react-native-iap の遅延読み込み（Expo Go対応）

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

### 価格表示

StoreKit から動的に取得した価格をそのまま表示する。ハードコードしない。

```typescript
// ✅ 正しい: StoreKitの表示価格を使用
const monthlyPrice = monthlyProduct?.displayPrice || '¥500';

// ✅ 月あたり価格の計算（通貨フォーマット対応）
const currency = yearlyProduct.currency || 'JPY';
const monthly = Math.floor(Number(yearlyProduct.price) / 12);
new Intl.NumberFormat(undefined, {
  style: 'currency',
  currency,
  maximumFractionDigits: 0,
}).format(monthly);

// ❌ 間違い: 通貨記号をハードコード
const price = `¥${product.price}`;  // USDの場合に ¥2.99 と表示されてしまう
```

### Paywall 画面の必須要素（App Store審査対応）

- サブスクリプションの価格と期間
- 自動更新の説明
- 無料トライアルがある場合その期間
- 利用規約へのリンク
- プライバシーポリシーへのリンク
- 「購入を復元」ボタン

### 購入リスナーのライフサイクル管理

```typescript
// Setup（Paywall画面マウント時）
export function setupPurchaseListeners(onSuccess, onError) {
  purchaseUpdateSubscription = RNIap.purchaseUpdatedListener(async (purchase) => {
    const receipt = purchase.purchaseToken;
    const result = await api.verifyReceipt(receipt);
    await RNIap.finishTransaction({ purchase, isConsumable: false });
    onSuccess(result);
  });
  purchaseErrorSubscription = RNIap.purchaseErrorListener(async (error) => {
    onError(error);
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

### 「購入を復元」は必須機能

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

**Apple審査で必須**: Paywall画面に「購入を復元」ボタンがないとリジェクトされる。

---

## 5. バックエンド実装（レシート検証）

### 設計原則

```
❌ クライアントだけで課金状態を管理
✅ サーバーでレシートを検証 → DBに状態保存 → クライアントに結果返却
```

**理由**: クライアント側の課金状態は改ざん可能。レシート検証はサーバーでやらないとセキュリティホールになる。

### エンドポイント

```
POST /api/subscription/verify
Body: { "receiptData": "<JWS token or legacy receipt>" }
Response: { "plan": "pro", "active": true, "expiresAt": "...", "originalTransactionId": "..." }
```

### StoreKit 2 JWS トークンの検証

```typescript
// JWS かどうか判定
function isJWSToken(data: string): boolean {
  const parts = data.split('.');
  return parts.length === 3 && parts.every(p => p.length > 0);
}

// JWS ペイロードをデコード
function decodeJWSPayload(jws: string): any {
  const parts = jws.split('.');
  const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
  const json = Buffer.from(base64, 'base64').toString('utf8');
  return JSON.parse(json);
}
```

**JWS ペイロードの主要フィールド:**

| フィールド | 説明 |
|-----------|------|
| `bundleId` | アプリの Bundle ID（検証に使用） |
| `productId` | 購入した商品ID |
| `expiresDate` | 有効期限（ミリ秒） |
| `originalTransactionId` | 元のトランザクションID（更新追跡用） |
| `environment` | "Sandbox" or "Production" |

### StoreKit 2 (JWS) と Legacy Receipt の両対応

```typescript
// JWS → StoreKit 2 処理
if (isJWSToken(receiptData)) {
  return handleJWSTransaction(receiptData, userId);
}

// レガシー → Apple verifyReceipt API
const appleRes = await fetch(APPLE_VERIFY_URL, { ... });
```

### Sandbox ↔ Production の自動フォールバック

```typescript
// Production に送って 21007 が返ったら Sandbox にリトライ
if (appleData.status === 21007) {
  const sandboxRes = await fetch('https://sandbox.itunes.apple.com/verifyReceipt', ...);
  return handleAppleResponse(sandboxData, userId);
}
```

**なぜ必要か**: TestFlight ビルドや Apple 審査員はSandbox環境を使う。本番URLに送ると `21007` が返るので、自動的にSandboxにフォールバックする。

---

## 6. データベース設計

### サブスク関連カラム

```
User {
  id                          String    PK
  plan                        String    default("free")    // "free" | "pro"
  subscriptionExpiresAt       DateTime? // サブスク有効期限
  appleOriginalTransactionId  String?   // Apple IAP トランザクションID
  analyzeCount                Int       default(0)         // 月間利用回数
  analyzeCountResetAt         DateTime  default(now())     // 月次リセット日時
}
```

### 自動降格ロジック

```typescript
// プラン取得時に毎回チェック
if (user.plan === 'pro') {
  if (user.subscriptionExpiresAt && user.subscriptionExpiresAt < now) {
    // 期限切れ → freeに降格
    await updateUser({ plan: 'free' });
  } else if (!user.subscriptionExpiresAt && user.appleOriginalTransactionId) {
    // IAP購入済みだが期限情報なし（旧データ）→ freeに降格
    await updateUser({ plan: 'free' });
  }
}
```

**ポイント**:
- `subscriptionExpiresAt` をDBに保存して期限管理
- プラン情報を返すAPI（`getUserPlan()`）で毎回期限チェック → 期限切れなら自動降格
- 期限情報がない古いデータも安全にハンドリング

---

## 7. プラン制限の適用

### プラン定義例

```typescript
const PLAN_LIMITS = {
  free: {
    maxChars: 200,              // テキスト入力上限
    analyzePerMonth: 5,         // 月間AI分析回数
    geminiModel: 'gemini-2.5-flash',
    imageAnalysis: false,
    maxItems: 3,
    reportCopy: false,
    reminder: false,
  },
  pro: {
    maxChars: 10_000,
    analyzePerMonth: Infinity,
    geminiModel: 'gemini-2.5-pro',
    imageAnalysis: true,
    maxItems: Infinity,
    reportCopy: true,
    reminder: true,
  },
};
```

---

## 8. Sandbox テスト

### Sandbox アカウントの作成

App Store Connect > ユーザーとアクセス > Sandbox テスター:
- テスト用のメールアドレスで作成
- 国/地域を「日本」に設定すると日本円表示
- **米国アカウントだとUSD表示になる（これは正常動作）**

### テスト時の注意

| 項目 | 値 |
|------|----|
| 月額サブスクの更新間隔 | 5分 |
| 年額サブスクの更新間隔 | 1時間 |
| 1週間サブスクの更新間隔 | 3分 |
| 自動更新の最大回数 | 6〜12回で自動期限切れ |
| TestFlightビルドのIAP | 自動的にSandbox環境 |
| Apple審査員のテスト | 新規Sandboxアカウントで実施 |

**Tip**: テスト時は毎回新しいSandboxアカウントを作成するのがベスト。古いアカウントは購入履歴が残っていて `Item already owned` が発生しやすい。

---

## 9. エラーハンドリング

課金まわりのエラーは種類が多い。以下を全てハンドリングする:

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

---

## 10. トラブルシューティング

### 「Product not found」エラー
**原因**: Paid Applications Agreement（有料App契約）が未完了
**対策**: App Store Connect > ビジネス で有料App契約を完了する

### 「Item already owned」エラー
**原因**: Sandboxアカウントに前回の購入履歴が残っている
**対策**: 新しいSandboxアカウントでテストする

### `receipt` が `undefined`
**原因**: `purchase.transactionReceipt`（v13以前のAPI）を使っている
**対策**: `purchase.purchaseToken` に変更する（v14+）

### Expo Go でクラッシュ
**原因**: react-native-iap をトップレベルで `import` している
**対策**: `require()` による遅延読み込みに変更する

---

*実戦経験に基づく*
