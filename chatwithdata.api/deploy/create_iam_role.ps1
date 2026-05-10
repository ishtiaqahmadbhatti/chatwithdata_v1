# Create IAM role for smartconverter-api Lambda function
$ROLE_NAME = "smartconverter-api-role"

# Write trust policy file (UTF-8 without BOM)
$trustFile = [System.IO.Path]::Combine($env:TEMP, "lambda-trust.json")
$trustContent = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
[System.IO.File]::WriteAllText($trustFile, $trustContent, [System.Text.UTF8Encoding]::new($false))

Write-Host "Trust policy file: $trustFile"
Write-Host "Contents: $(Get-Content $trustFile)"

# Create IAM Role
Write-Host "`nCreating IAM Role: $ROLE_NAME ..." -ForegroundColor Yellow
$result = aws iam create-role `
    --role-name $ROLE_NAME `
    --assume-role-policy-document "file://$trustFile" `
    --query "Role.Arn" `
    --output text

if ($LASTEXITCODE -eq 0) {
    Write-Host "Role ARN: $result" -ForegroundColor Green

    # Attach Lambda basic execution policy
    aws iam attach-role-policy `
        --role-name $ROLE_NAME `
        --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"

    # Attach DynamoDB full access (or you can create a custom policy)
    aws iam attach-role-policy `
        --role-name $ROLE_NAME `
        --policy-arn "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"

    Write-Host "Policies attached (Basic Execution + DynamoDB Full Access)!" -ForegroundColor Green
    Write-Host "`nRole creation complete. Now run: .\deploy_lambda.ps1" -ForegroundColor Cyan
}
else {
    Write-Host "Failed to create role. Check AWS permissions." -ForegroundColor Red
}

# Cleanup
Remove-Item $trustFile -ErrorAction SilentlyContinue
