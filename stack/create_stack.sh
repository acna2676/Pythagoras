[template]
aws cloudformation update-stack --stack-name myteststack --template-body file://sampletemplate.json --parameters ParameterKey=KeyPairName,ParameterValue=TestKey ParameterKey=SubnetIDs,ParameterValue=SubnetID1\\,SubnetID2

[dynamodb]
aws cloudformation create-stack --stack-name pythagoras-dev-dynamodb --template-body file://dynamodb.yml
aws cloudformation update-stack --stack-name pythagoras-dev-dynamodb --template-body file://dynamodb.yml

