# App Store 審査つまづきポイント & チェックリスト

MeetToDoの審査で実際にリジェクトされた経験をもとにまとめたノウハウ集。
初回から審査を通すためのガイド。

---

## 目次
1. [提出前チェックリスト](#提出前チェックリスト)
2. [Guideline 2.1 - App Completeness](#guideline-21---app-completeness)
3. [Guideline 2.3.2 - Accurate Metadata（プロモ画像）](#guideline-232---accurate-metadataプロモ画像)
4. [Guideline 2.3.7 - Accurate Metadata（価格表示）](#guideline-237---accurate-metadata価格表示)
5. [Guideline 3.1.2(c) - Subscriptions（EULA）](#guideline-312c---subscriptionseula)
6. [IAP（アプリ内課金）関連](#iapアプリ内課金関連)
7. [iPad対応](#ipad対応)
8. [スクリーンショット](#スクリーンショット)
9. [ビルド・署名](#ビルド署名)

---

## 提出前チェックリスト

### メタデータ（App Store Connect）
- [ ] **全言語の説明文にEULAリンクを記載**（最重要！見落としがち）
  ```
  Terms of Use (EULA): https://www.apple.com/legal/internet-services/itunes/dev/stdeula/
  Privacy Policy: https://example.com/privacy
  ```
- [ ] 説明文にサブスク情報を記載（プラン名、期間、自動更新の説明、キャンセル方法）
- [ ] スクリーンショットに価格表示がない（「¥」「Free」「無料」「$」すべてNG）
- [ ] スクリーンショットが全言語・全デバイス（iPhone/iPad）に設定されている
- [ ] プロモーション画像のテキストが十分に大きい（または画像を設置しない）
- [ ] プライバシーポリシーURLが設定されている
- [ ] IAPプロダクトをバージョンに紐付けている

### アプリ内
- [ ] 利用規約リンクが設定画面にある
- [ ] プライバシーポリシーリンクが設定画面にある
- [ ] 「購入を復元」ボタンがPaywall画面にある
- [ ] サブスク画面にプラン名・期間・自動更新の説明がある
- [ ] iPadでレイアウトが崩れない
- [ ] iPadでIAP購入が動作する
- [ ] アカウント削除機能がある

### ビルド
- [ ] デバッグコードが除去されている
- [ ] テスト用のUIやボタンが除去されている
- [ ] ITSAppUsesNonExemptEncryption = false が設定されている

---

## Guideline 2.1 - App Completeness

### IAPバイナリ未提出
**症状**: 「We have returned your In-App Purchase products to you as the required binary was not submitted」

**原因**: IAPプロダクトだけ提出してアプリのビルドと紐付けていない。

**対策**:
- App Store Connectのバージョンページで、ビルドを選択した上で「App内課金とサブスクリプション」セクションにIAPプロダクトを追加
- IAPプロダクト単体では審査に出せない。**必ずアプリのビルドとセットで提出**する

### iPadでの動作不良
**症状**: iPad実機でクラッシュや機能不全。

**対策**:
- `supportsTablet: true` の場合、iPadでの動作確認は必須
- iPadでIAP購入フローをテスト
- iPadのレイアウトを確認（特にモーダル、ボトムシート）

---

## Guideline 2.3.2 - Accurate Metadata（プロモ画像）

### プロモ画像のテキストが小さい
**症状**: 「Your promotional image includes text that is small or otherwise hard to read」

**何度もリジェクトされたポイント**:
- v2、v3、v4と画像を作り直しても通らなかった
- テキストを大きくしても「まだ小さい」と言われ続けた

**最終的な解決策**:
- **プロモーション画像を削除する**（Appleも「削除してもよい」と明記している）
- プロモ画像は任意なので、なくても審査は通る
- 無理にテキスト入りの画像を作るより、削除する方が確実

**教訓**:
- プロモ画像を設置するなら、テキスト要素は最小限に
- アプリアイコン＋プラン名程度のシンプルなデザインにする
- 迷ったら設置しない

---

## Guideline 2.3.7 - Accurate Metadata（価格表示）

### スクリーンショットに価格表示
**症状**: 「The app screenshots include references to the price of the app or the service it provides」

**NGワード一覧**:
- `¥500`, `$4.99`, `¥4,000` など具体的な金額
- `Free`（英語の「無料」も価格表示に該当！）
- `無料`
- `¥0`
- `Free vs Pro`（「Free」が含まれるためNG）
- `無料で始める`
- その他、割引や値引きに関する表現

**見落としやすいポイント**:
- **全言語のスクリーンショットを確認する**（日本語だけ直しても、英語・韓国語・中国語に残っていたらリジェクト）
- **全デバイスを確認する**（iPhoneは直してもiPadに残っていたらリジェクト）
- **審査用スクリーンショット**（App Review情報セクション）にも価格が写っていないか確認
- **審査メモ**の中にも「Free: 5/month」のような表現はNG

**対策**:
- スクリーンショットを作る段階で価格情報を一切入れない
- 価格はApp Storeの説明文（概要）に書く
- App Store Connectの「メディアマネージャーですべてのサイズを表示」で全サイズ・全言語を一括チェック

---

## Guideline 3.1.2(c) - Subscriptions（EULA）

### EULAリンクが不足
**症状**: 「The submission did not include all the required information for apps offering auto-renewable subscriptions」

**最も見落としやすいポイント**:
> **全言語のApp説明文にEULAリンクを記載する必要がある**

日本語の説明文だけにリンクを入れても、英語・韓国語・中国語の説明文にリンクがなければリジェクトされる。

**必要なリンク**:
```
Terms of Use (EULA): https://www.apple.com/legal/internet-services/itunes/dev/stdeula/
Privacy Policy: https://example.com/privacy
```

**Apple標準EULA vs カスタムEULA**:
- Apple標準EULAを使う場合 → 各言語の説明文にApple標準EULAのURLを記載
- カスタムEULAを使う場合 → App Store Connect「App情報」の「使用許諾契約」でカスタムEULAを設定（App Storeにクリック可能リンクが自動生成される）
- Apple標準EULAのURL: `https://www.apple.com/legal/internet-services/itunes/dev/stdeula/`
- カスタムEULAの最低条件: `https://www.apple.com/legal/internet-services/itunes/dev/minterms/`

**App説明文に必須の情報**:
- サブスクリプションのタイトル（プロダクト名と同じでOK）
- サブスクリプションの期間
- サブスクリプションの価格
- プライバシーポリシーへのリンク
- EULAへのリンク
- 自動更新の説明
- キャンセル方法

**テンプレート（各言語に追加）**:
```
【法的情報】
Terms of Use (EULA): https://www.apple.com/legal/internet-services/itunes/dev/stdeula/
利用規約: https://example.com/terms
プライバシーポリシー: https://example.com/privacy
```

---

## IAP（アプリ内課金）関連

### 「Item already owned」エラー
**症状**: 購入ボタンを押すとApple決済画面が出ずに即座にエラーまたはPro化される。

**原因**: Sandboxアカウントに前回の購入履歴が残っている。

**対策**:
- サイレントに自動復元しない（ユーザーの意図しないPro化は審査で問題になる可能性）
- エラーメッセージをユーザーフレンドリーにする（英語のシステムエラーをそのまま表示しない）
- 「購入を復元」ボタンで明示的に復元する動線を用意

### 購入フローのテスト
- Sandbox環境での月額サブスクは5分ごとに自動更新、最大6〜12回で自動期限切れ
- 新しいSandboxアカウントを作成してテストする（Apple審査員も新しいアカウントでテスト）
- TestFlightビルドのIAPは自動的にSandbox環境

### サーバー側の注意点
- `subscriptionExpiresAt` をDBに保存して期限管理
- Apple Sandbox環境のレシート（JWSトークン）は`eyJ`で始まるBase64URL
- 期限切れ後の自動降格ロジックを実装

---

## iPad対応

### iPadスクリーンショットのサイズ
- 12.9インチ / 13インチ: **2048x2732px** または **2732x2048px**
- App Store Connectでサイズ違いのアップロードはエラーになる
- 1pxでもずれるとアップロードできない

### iPadレイアウト
- `supportsTablet: true` の場合、iPad対応は必須
- 特にPaywall画面、モーダル、入力フォームの動作確認

---

## スクリーンショット

### サイズ一覧
**iPhone 6.5インチ**:
- 1242×2688px, 1284×2778px

**iPhone 6.7インチ / 6.9インチ**:
- 1290×2796px, 1260×2736px, 1320×2868px

**iPad 12.9インチ / 13インチ**:
- 2048×2732px, 2064×2752px

### 多言語対応
- **全言語にスクリーンショットを設定する**
- 言語ごとにiPhoneとiPadの両方が必要
- 古いスクリーンショットが他の言語に残っていないか確認
- 「メディアマネージャーですべてのサイズを表示」で一括管理

---

## ビルド・署名

### Expo prebuildの注意点
- `expo prebuild --clean` するたびに `CFBundleVersion` がリセットされる
- prebuild後に `sed` でビルド番号を再設定する必要がある
```bash
sed -i '' 's|<string>27</string>|<string>N</string>|' ios/MeetToDo/Info.plist
```

### 手動署名（Manual Signing）
- ExportOptions.plistで `signingStyle: manual` を指定
- `provisioningProfiles` で明示的にプロファイルを指定
- `automatic` だと「No profiles for」エラーになる場合がある

### ExportOptions.plist テンプレート
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>method</key><string>app-store</string>
  <key>signingStyle</key><string>manual</string>
  <key>teamID</key><string>YOUR_TEAM_ID</string>
  <key>uploadSymbols</key><true/>
  <key>provisioningProfiles</key>
  <dict>
    <key>com.example.app</key><string>Profile Name</string>
  </dict>
</dict>
</plist>
```

---

## 審査を早く通すコツ

1. **審査メモを活用する**: テストアカウント情報、テスト手順を詳しく書く
2. **リジェクト時は返信する**: 「ここに対応しました」と具体的に説明
3. **一度に全部直す**: 1つだけ直して再提出すると、別の問題で再リジェクトされる
4. **迷ったら削除**: プロモ画像など任意の要素は、リスクがあるなら設置しない
5. **全言語チェック**: メタデータの変更は必ず全言語に反映する
6. **全デバイスチェック**: iPhone/iPad両方のスクリーンショットを確認

---

*最終更新: 2026年3月25日*
*MeetToDo v1.0 審査経験に基づく*
