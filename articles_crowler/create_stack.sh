# S3 bucket for sam package
aws cloudformation create-stack --stack-name  pythagoras-dev-sam-package --template-body file://cfn_sam_package_bucket.yml

# eventbridge and lambda package
sam package --template-file articles_crowler.yml --output-template-file packaged_dev-articles_crowler.yml --s3-bucket pythagoras-dev-sam-package
sam deploy --template-file packaged_dev-articles_crowler.yml --stack-name pythagoras-dev-articlesCrowler --capabilities CAPABILITY_IAM
aws cloudformation delete-stack --stack-name pythagoras-dev-articlesCrowler
