# Create IAM role for chatwithdata-web Lambda function
$ROLE_NAME = "chatwithdata-web-role"

Write-Host "Creating IAM role: $ROLE_NAME" -ForegroundColor Yellow

$trustPolicy = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
$trustFile = [System.IO.Path]::Combine($env:TEMP, "web-trust-policy.json")
[System.IO.File]::WriteAllText($trustFile, $trustPolicy, [System.Text.UTF8Encoding]::new($false))

$ROLE_ARN = (aws iam create-role `
        --role-name $ROLE_NAME `
        --assume-role-policy-document "file://$trustFile" `
        --query "Role.Arn" `
        --output text)

aws iam attach-role-policy `
    --role-name $ROLE_NAME `
    --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" | Out-Null

Write-Host "  IAM role created: $ROLE_ARN" -ForegroundColor Green
