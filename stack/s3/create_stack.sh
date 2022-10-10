aws cloudformation create-stack --stack-name  pythagoras-dev-sam-package --template-body file://sam_package_bucket.yml
aws cloudformation create-stack --stack-name  pythagoras-dev-content-bucket --template-body file://content_bucket.yml

