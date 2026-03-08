# App Store審査ノウハウ（実体験ベース）

iOSアプリ（特にサブスクリプション付き）をApp Storeに提出する際のノウハウ集。
実際のリジェクト対応から得た知見をまとめています。

---

## サブスクリプションアプリ必須要件（Guideline 3.1.2(c)）

### App Store説明文（概要欄）に必ず含めること
```
【法的情報】
利用規約: https://[your-domain]/terms
プライバシーポリシー: https://[your-domain]/privacy
```
- App Store Connect → iOSアプリ → バージョン → 「概要」欄の末尾に追記
- 「説明」欄ではなく「概要」欄（英語UIでは "Description"）
- プライバシーポリシーURLは「アプリのプライバシー」設定でも別途設定が必要

### アプリ内に必要な表示
- サブスクリプションのタイトル
- 契約期間
- 価格（必要に応じて単価表示）
- プライバシーポリシーへのリンク
- 利用規約（EULA）へのリンク

### In-App Purchase / サブスクリプションのメタデータ
- タイトル、期間、価格を明記（App Store Connect上で設定）
- 各サブスクリプション商品にプロモーション画像が必要

---

## IAPプロモーション画像（Guideline 2.3.2）

### 要件
- サイズ: **1024 x 1024 px**
- スクリーンショットはNG（「アプリのスクリーンショット」と見なされてリジェクト）
- テキストは大きく・読みやすく（小さい文字はリジェクト理由になる）
- そのIAPを「直接的に」表現すること（Proプランなら機能一覧など）

### 画像生成例（Python PIL）

macOSのヒラギノフォントを使って日本語対応の画像を生成：

```python
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
# macOS日本語フォント（文字化け防止）
FONT = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"
FONT_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc"

img = Image.new("RGB", (W, H), (10, 10, 9))
draw = ImageDraw.Draw(img)

# タイトル・バッジ・機能リスト・価格を大きなフォントで配置
f_title = ImageFont.truetype(FONT_BOLD, 84)
draw.text((W//2, 165), "AppName", font=f_title, fill=(245,240,232), anchor="mm")

# ... 機能リスト、価格などを追加 ...

img.save("iap_promo.png", "PNG")
```

### 注意点
- `PIL.ImageFont` でシステムフォントを指定しないと日本語が文字化けする（□□□になる）
- macOSの場合: `/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc` を使用
- App Store Connect → 収益化 → **サブスクリプション**（「アプリ内課金」ではない）→ 各プラン → プロモーション画像

---

## EAS Build / Submit フロー（Expo React Native）

### iOSビルド & 提出
```bash
cd mobile
eas build --platform ios --profile production
eas submit --platform ios --latest
```
- `buildNumber` はリジェクト後も同じバージョンで再提出可能（incrementは不要）
- 再提出時は App Store Connect の「審査内容を更新」ボタンから

### Androidビルド & 提出
```bash
eas build --platform android --profile production
eas submit --platform android --latest
```
- `versionCode` はビルドごとにインクリメントが必要（同じ値だとGoogle Playが拒否）

### EAS Build Tips
- Free tierではビルドキューが1時間以上かかることがある
- 前のビルドをキャンセルして再ビルドすると早い場合がある

---

## App Store Connect ナビゲーション

| やること | 場所 |
|--------|------|
| 説明文・概要の編集 | iOSアプリ → バージョン（却下済みの場合「編集」）→ 下にスクロール |
| 再提出 | バージョン画面右上 **「審査内容を更新」** |
| プロモーション画像 | 収益化 → **サブスクリプション**（アプリ内課金ではない！） |
| プライバシーポリシーURL | App Store → **アプリのプライバシー** |
| 審査メッセージ確認 | 一般 → App Review → メッセージ欄 |
| 利用規約（EULA）設定 | App Store → アプリ情報 → EULA 、または概要欄にリンク記載 |

---

## Railway デプロイ

### 注意点
- `railway redeploy` は **前回の成功デプロイを再実行** する（最新コミットではない！）
- `railway up` はローカルファイルをアップロード（macOSのPhotosライブラリ権限エラーに注意）
- GitHub自動デプロイが動かない場合は、新しいコミットをpushして強制トリガー
- `prisma db push` はビルド時ではなく `start.sh` で実行（Dockerビルド時はDB接続不可）

### 確実なデプロイ手順
```bash
# 何か小さな変更を加えてコミット＆プッシュ → GitHub自動デプロイをトリガー
git add [変更ファイル]
git commit -m "fix: ..."
git push origin main
```

---

## 利用規約に含めるべき内容（サブスクアプリ）

1. **サービスの説明**（アプリの機能一覧）
2. **アカウント管理**（登録・削除方法）
3. **サブスクリプション詳細**
   - プラン名・価格・期間
   - 自動更新の説明
   - キャンセル方法（「設定 → Apple ID → サブスクリプション」）
   - 無料トライアルの扱い
   - 返金ポリシー（Apple経由: https://reportaproblem.apple.com）
4. **AI機能の免責事項**（AI出力の正確性は保証しない等）
5. **Apple条項**（Guideline 12）
   - Appleはアプリ提供者ではない
   - Appleの保証義務の範囲
   - Appleとその子会社は本規約の第三者受益者

---

## 初回審査での注意事項

- **利用規約リンク**はApp説明文（概要）に必ず入れる
- **IAPプロモーション画像**はスクリーンショット不可・文字は大きく読みやすく
- **プライバシーポリシーURL**はApp Storeのプライバシー設定にも設定する
- サブスクリプションの自動更新・キャンセル方法を利用規約に明記する
- Apple条項（Guideline 12 相当）を利用規約に含める
- 13歳以上の利用制限を記載する

---

## チェックリスト（審査提出前）

- [ ] App Store概要欄に利用規約・プライバシーリンクを追記
- [ ] プライバシーポリシーURLがApp Storeプライバシー設定に設定済み
- [ ] IAPプロモーション画像（1024x1024）が各サブスクリプション商品にアップロード済み
- [ ] プロモーション画像がスクリーンショットではなく専用画像
- [ ] プロモーション画像の文字が大きく読みやすい
- [ ] 利用規約ページがライブで正しく表示される（文字化けなし）
- [ ] サブスクリプション情報（価格・期間・キャンセル方法）が利用規約に明記
- [ ] Apple条項が利用規約に含まれている
- [ ] アプリ内Paywall画面にサブスク名・価格・期間・利用規約リンクが表示される
