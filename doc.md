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

## 環境変数

以下に記載
.chalice/config.json

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

## crowler のデプロイ

EventBridge + Lambda を SAM でデプロイ

- 1. デプロイパッケージ格納用の S3 バケットを作成

```
aws cloudformation create-stack
```

- 2. テンプレートのパッケージ化

```
sam package
```

- 3. パッケージのデプロイ

```
sam deploy
```

## Tips

- response に utf を指定しないと日本語が文字化けする
- [Qiita API V2 の利用制限](https://qiita.com/api/v2/docs#%E6%A6%82%E8%A6%81)
  認証している状態ではユーザごとに 1 時間に 1000 回まで、認証していない状態では IP アドレスごとに 1 時間に 60 回までリクエストを受け付けます。
