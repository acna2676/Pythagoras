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

### アプリ起動

```bash
chalice local --stage local --port 8088
```

※--stage local --port 8088
git bash だとエラーになるのでコマンドプロンプトで実行
error: sys.stderr.write → NoneType' object has no attribute 'write'

### DynamoDB Local

```bash
docker-compose up -d
```

### DynamoDB Local admin

```bash
npx dynamodb-admin
```

## mock api

```bash
npm run mock
```

Qiita api の rate limit に引っかかるため
[json-mock-api](https://www.npmjs.com/package/json-mock-api#usage)

## デプロイ

```bash
chalice deploy
```

## lambda layer

[github](https://github.com/keithrozario/Klayers/tree/master/deployments/python3.9)より取得

## Tips

- response に utf を指定しないと日本語が文字化けする
