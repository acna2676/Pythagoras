[dynamodb]
aws cloudformation create-stack --stack-name pythagoras-dev-dynamodb --template-body file://template.yml
aws cloudformation update-stack --stack-name pythagoras-dev-dynamodb --template-body file://template.yml

