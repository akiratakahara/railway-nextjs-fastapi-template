# EAS Build & Submit ガイド

Expo (React Native) アプリの EAS Build・Submit・署名に関するノウハウ集。
ビルド時にハマりやすいポイントと対策をまとめています。

---

## 目次

1. [EAS Build コマンド](#1-eas-build-コマンド)
2. [ビルド番号の管理](#2-ビルド番号の管理)
3. [Expo prebuild のハマりどころ](#3-expo-prebuild-のハマりどころ)
4. [署名設定](#4-署名設定)
5. [輸出コンプライアンス](#5-輸出コンプライアンス)
6. [デバッグコードの除去](#6-デバッグコードの除去)
7. [EAS Build Tips](#7-eas-build-tips)

---

## 1. EAS Build コマンド

### iOSビルド & 提出

```bash
cd mobile

# Development Build（デバッグ可能・実機テスト用）
eas build --platform ios --profile development

# Preview Build（TestFlight配布用）
eas build --platform ios --profile preview

# Production Build（App Store提出用）
eas build --platform ios --profile production

# App Store Connect に提出
eas submit --platform ios --latest
```

### Androidビルド & 提出

```bash
# Production Build
eas build --platform android --profile production

# Google Play に提出
eas submit --platform android --latest
```

### iOS / Android の違い

| 項目 | iOS | Android |
|------|-----|---------|
| ビルド番号 | `buildNumber`（リジェクト後も同値で再提出可能） | `versionCode`（ビルドごとにインクリメント必須） |
| 提出先 | App Store Connect → TestFlight → 審査 | Google Play Console → 内部テスト → 審査 |
| IAPテスト環境 | Sandbox（自動） | テストトラック |

---

## 2. ビルド番号の管理

### app.json の設定

```json
{
  "expo": {
    "version": "1.0.0",
    "ios": {
      "buildNumber": "27"
    },
    "android": {
      "versionCode": 3
    }
  }
}
```

### ルール

- **iOS `buildNumber`**: 同じバージョン内で一意であれば良い。リジェクト後も同じ番号で再提出可能
- **Android `versionCode`**: **ビルドごとにインクリメント必須**。同じ値だとGoogle Playが拒否

---

## 3. Expo prebuild のハマりどころ

### CFBundleVersion がリセットされる

```bash
# prebuild --clean するたびにビルド番号が 1 に戻る！
npx expo prebuild --clean
```

**対策**: prebuild 後にビルド番号を `sed` で再設定するスクリプトを用意。

```bash
# 例: ビルド番号を 28 に設定
sed -i '' 's|<string>1</string>|<string>28</string>|' ios/YourApp/Info.plist
```

### prebuild 後の注意

- `ios/` ディレクトリ配下の設定が初期化される
- `Info.plist` のカスタム設定（`ITSAppUsesNonExemptEncryption` 等）も消える
- **prebuild 後は必ず設定を再適用する**

---

## 4. 署名設定

### 手動署名（Manual Signing）

`automatic` で「No profiles for」エラーが出る場合は `manual` に切り替える。

```xml
<!-- ExportOptions.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>method</key><string>app-store</string>
  <key>signingStyle</key><string>manual</string>
  <key>teamID</key><string>YOUR_TEAM_ID</string>
  <key>uploadSymbols</key><true/>
  <key>provisioningProfiles</key>
  <dict>
    <key>com.yourapp.id</key><string>Profile Name</string>
  </dict>
</dict>
</plist>
```

### In-App Purchase Capability

IAPを使うアプリは、Xcode の Signing & Capabilities で「In-App Purchase」を追加する必要がある。
EAS Build の場合は `app.json` の `ios.entitlements` または `expo-build-properties` で設定可能。

---

## 5. 輸出コンプライアンス

### ITSAppUsesNonExemptEncryption

App Store提出時に暗号化に関する質問が表示される。HTTPS/TLSのみ使用の場合:

```json
// app.json
{
  "expo": {
    "ios": {
      "infoPlist": {
        "ITSAppUsesNonExemptEncryption": false
      }
    }
  }
}
```

**判断基準**:
- HTTPS/TLS通信のみ → `false`（免除対象: EAR 740.17(b)）
- 独自の暗号化を実装している → `true`（追加書類が必要）
- bcryptがサーバーサイドのみ → アプリバイナリに含まれないため対象外

---

## 6. デバッグコードの除去

審査提出前に必ず確認:

### チェック項目

```bash
# デバッグログの検索
grep -rn "console.log" mobile/app/ mobile/services/
grep -rn "console.warn" mobile/app/ mobile/services/
grep -rn "console.error" mobile/app/ mobile/services/

# デバッグ用UI・テスト用コードの検索
grep -rn "__DEV__" mobile/app/ mobile/services/
grep -rn "debug" mobile/app/ mobile/services/

# テスト用エンドポイントの検索
grep -rn "/api/debug" mobile/ backend/
```

### ルール

- `__DEV__` ガードで囲んだログは残してOK（リリースビルドで除去される）
- テスト用エンドポイント（`/api/debug/*`）は本番環境で無効化 or 削除
- テスト用のUIやボタンは完全に除去

---

## 7. EAS Build Tips

### ビルド時間の短縮

- Free tierではビルドキューが**1時間以上**かかることがある
- 前のビルドをキャンセルして再ビルドすると早い場合がある
- `--clear-cache` オプションでキャッシュをクリアすると問題解決する場合がある

### eas.json のプロファイル例

```json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "simulator": false
      }
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {
      "autoIncrement": false
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your@email.com",
        "ascAppId": "1234567890",
        "appleTeamId": "YOUR_TEAM_ID"
      }
    }
  }
}
```

### 提出前の最終チェック

```bash
# 1. プロダクションビルド
eas build --platform ios --profile production

# 2. ビルド完了を確認
eas build:list --platform ios --limit 1

# 3. App Store Connect に提出
eas submit --platform ios --latest

# 4. App Store Connect でビルドを確認
#    → バージョンに紐付け → IAPプロダクトを追加 → 審査に提出
```

---

*実戦経験に基づく*
