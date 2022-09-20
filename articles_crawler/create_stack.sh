sam package --template-file template.yml --output-template-file template-packaged.yml --s3-bucket pythagoras-dev-sam-package
./set_env_variable.sh
sam deploy --template-file template-packaged.yml --stack-name pythagoras-dev-articlesCrawler --capabilities CAPABILITY_IAM --parameter-overrides ApiKey=$API_KEY UrlQiitaApiV2=$URL_QIITA_API_V2

aws cloudformation delete-stack --stack-name pythagoras-dev-articlesCrawler
