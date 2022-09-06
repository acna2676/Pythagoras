# S3 bucket for sam package
aws cloudformation create-stack --stack-name  pythagoras-dev-sam-package --template-body file://cfn_sam_package_bucket.yml

# eventbridge and lambda package
sam package --template-file articles_crawler.yml --output-template-file packaged_dev-articles_crawler.yml --s3-bucket pythagoras-dev-sam-package

sam deploy --template-file packaged_dev-articles_crawler.yml --stack-name pythagoras-dev-articlesCrawler --capabilities CAPABILITY_IAM --parameter-overrides ApiKey=38b71e80eb38b29f4c9dfe728b2817121754038c

aws cloudformation delete-stack --stack-name pythagoras-dev-articlesCrawler
