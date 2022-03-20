## 機能要件

- ストック数でフィルタリング
- LGMT 数でフィルタリング
- 各月のランキングが閲覧できる（その月に作成された記事で）

## Todo

- リッチデザイン採用（bootstrap など）
- s3 and lambda で公開
- portfolio 連携
- 更新は週１でリクエストのたびに API を使用しないようにする（閲覧できるのは半年前まで）
- 各記事の作成日、更新日表示
- ページ遷移が遅い

## ローカル動作確認

```bash
cahlice local
```

## デプロイ

```bash
cahlice deploy
```

## Tips

- response に utf を指定しないと日本語が文字化けする
