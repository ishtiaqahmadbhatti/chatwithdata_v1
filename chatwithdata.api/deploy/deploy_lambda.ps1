# SmartConverter API - AWS Lambda Deployment (ECR Private)
# FastAPI app wrapped with Mangum for Lambda
# Domain: smartconverterapi.techmindsforge.com

$ErrorActionPreference = "Stop"

# ── Configuration ─────────────────────────────────────────────────────────────
$AWS_REGION = "us-east-1"
$ECR_REPO_NAME = "smartconverter-api"
$IMAGE_TAG = "lambda"
$LAMBDA_FUNCTION = "smartconverter-api"
$LAMBDA_TIMEOUT = 900
$LAMBDA_MEMORY = 3008
$LAMBDA_STORAGE = 10240
$CUSTOM_DOMAIN = "smartconverterapi.techmindsforge.com"
$HOSTED_ZONE_NAME = "techmindsforge.com"

# Script is inside smartconverter.api/deploy/ - go up one level to API root
$API_ROOT = Split-Path $PSScriptRoot -Parent

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host " SmartConverter API - Lambda Deployment" -ForegroundColor Cyan
Write-Host " Domain: $CUSTOM_DOMAIN" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# ── AWS Credentials ────────────────────────────────────────────────────────────
Write-Host "Checking AWS credentials..." -ForegroundColor Yellow
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text 2>&1)
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: AWS CLI not configured! Run: aws configure" -ForegroundColor Red
    exit 1
}
$AWS_ACCOUNT_ID = $AWS_ACCOUNT_ID.Trim()
$S3_BUCKET = "smartconverter-api-uploads-$AWS_ACCOUNT_ID"

$ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
$IMAGE_URI = "${ECR_REGISTRY}/${ECR_REPO_NAME}:${IMAGE_TAG}"

Write-Host " AWS Account : $AWS_ACCOUNT_ID" -ForegroundColor White
Write-Host " Region      : $AWS_REGION" -ForegroundColor White
Write-Host " ECR URI     : $IMAGE_URI" -ForegroundColor White
Write-Host " Function    : $LAMBDA_FUNCTION" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan

# ── Step 1: ECR Login ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[1/7] Logging into ECR Private..." -ForegroundColor Yellow

# Fix "stub received bad data" - Docker Windows credential store bug
$dockerConfigPath = "$env:USERPROFILE\.docker\config.json"
$dockerConfigBackup = $null
if (Test-Path $dockerConfigPath) {
    $dockerConfigRaw = [System.IO.File]::ReadAllText($dockerConfigPath, [System.Text.UTF8Encoding]::new($false))
    $dockerConfig = $dockerConfigRaw | ConvertFrom-Json
    if ($dockerConfig.PSObject.Properties["credsStore"]) {
        $dockerConfigBackup = $dockerConfigRaw
        $dockerConfig.PSObject.Properties.Remove("credsStore")
        $newJson = $dockerConfig | ConvertTo-Json -Depth 10 -Compress
        [System.IO.File]::WriteAllText($dockerConfigPath, $newJson, [System.Text.UTF8Encoding]::new($false))
        Write-Host "  Disabled Docker credential store temporarily" -ForegroundColor Gray
    }
}

$ecrPassword = (aws ecr get-login-password --region $AWS_REGION)
$ecrPassword | docker login --username AWS --password-stdin $ECR_REGISTRY
$loginExitCode = $LASTEXITCODE

if ($loginExitCode -ne 0) {
    if ($null -ne $dockerConfigBackup) {
        [System.IO.File]::WriteAllText($dockerConfigPath, $dockerConfigBackup, [System.Text.UTF8Encoding]::new($false))
    }
    Write-Host "ERROR: ECR login failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  ECR login successful" -ForegroundColor Green

# ── Step 2: ECR Repository ────────────────────────────────────────────────────
Write-Host ""
Write-Host "[2/7] Setting up ECR Private repository..." -ForegroundColor Yellow
$savedPref = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION 2>&1 | Out-Null
$repoExists = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = $savedPref

if (-not $repoExists) {
    aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION | Out-Null
    Write-Host "  ECR repo created: $ECR_REPO_NAME" -ForegroundColor Green
}
else {
    Write-Host "  Using existing ECR repo: $ECR_REPO_NAME" -ForegroundColor Green
}

# ── Step 3: Build Docker Image ────────────────────────────────────────────────
Write-Host ""
Write-Host "[3/7] Building Lambda Docker image..." -ForegroundColor Yellow
Write-Host "  Building from: $API_ROOT" -ForegroundColor Gray
Write-Host "  NOTE: First build takes 10-20 min (many Python packages)" -ForegroundColor Gray

# Build from API root using deploy/Dockerfile.lambda
# --provenance=false: prevents BuildKit manifest list (Lambda requires single-arch OCI manifest)
docker build `
    --platform linux/amd64 `
    --provenance=false `
    -f "$API_ROOT\deploy\Dockerfile.lambda" `
    -t "${ECR_REPO_NAME}:${IMAGE_TAG}" `
    $API_ROOT

if ($LASTEXITCODE -ne 0) {
    if ($null -ne $dockerConfigBackup) {
        [System.IO.File]::WriteAllText($dockerConfigPath, $dockerConfigBackup, [System.Text.UTF8Encoding]::new($false))
    }
    Write-Host "ERROR: Docker build failed!" -ForegroundColor Red
    exit 1
}
docker tag "${ECR_REPO_NAME}:${IMAGE_TAG}" $IMAGE_URI
Write-Host "  Docker image built and tagged" -ForegroundColor Green

# ── Step 4: Push to ECR ───────────────────────────────────────────────────────
Write-Host ""
Write-Host "[4/7] Pushing image to ECR Private..." -ForegroundColor Yellow
docker push $IMAGE_URI
$pushExitCode = $LASTEXITCODE

# Restore Docker config AFTER push
if ($null -ne $dockerConfigBackup) {
    [System.IO.File]::WriteAllText($dockerConfigPath, $dockerConfigBackup, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  Restored Docker credential store" -ForegroundColor Gray
}

if ($pushExitCode -ne 0) {
    Write-Host "ERROR: Docker push failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  Image pushed: $IMAGE_URI" -ForegroundColor Green

# ── Step 4.5: Setup S3 Bucket ────────────────────────────────────────────────
Write-Host ""
Write-Host "[4.5/7] Setting up S3 bucket for large uploads..." -ForegroundColor Yellow
$savedPref = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
aws s3api head-bucket --bucket $S3_BUCKET 2>&1 | Out-Null
$bucketStatus = $LASTEXITCODE
$ErrorActionPreference = $savedPref

if ($bucketStatus -ne 0) {
    Write-Host "  Creating S3 bucket: $S3_BUCKET" -ForegroundColor White
    aws s3 mb "s3://$S3_BUCKET" --region $AWS_REGION | Out-Null
    # Enable CORS for direct browser/mobile uploads
    $corsConfig = '{"CORSRules":[{"AllowedHeaders":["*"],"AllowedMethods":["PUT","POST","GET"],"AllowedOrigins":["*"],"ExposeHeaders":[]}]}'
    $corsFile = [System.IO.Path]::Combine($env:TEMP, "cors-config.json")
    [System.IO.File]::WriteAllText($corsFile, $corsConfig, [System.Text.UTF8Encoding]::new($false))
    aws s3api put-bucket-cors --bucket $S3_BUCKET --cors-configuration "file://$corsFile" --region $AWS_REGION | Out-Null
    Remove-Item $corsFile
    Write-Host "  S3 bucket created and CORS configured" -ForegroundColor Green
}
else {
    Write-Host "  Using existing S3 bucket: $S3_BUCKET" -ForegroundColor Green
}

# ── Step 5: IAM Role + Lambda Deploy ─────────────────────────────────────────
Write-Host ""
Write-Host "[5/7] Deploying Lambda function..." -ForegroundColor Yellow

$ROLE_NAME = "${LAMBDA_FUNCTION}-role"
$savedPref = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
$ROLE_ARN = (aws iam get-role --role-name $ROLE_NAME --query "Role.Arn" --output text 2>&1)
$roleExitCode = $LASTEXITCODE
$ErrorActionPreference = $savedPref

if ($roleExitCode -ne 0) {
    Write-Host "  IAM Role not found. Creating..." -ForegroundColor White
    & "$PSScriptRoot\create_iam_role.ps1"
    Start-Sleep -Seconds 10
    $ROLE_ARN = (aws iam get-role --role-name $ROLE_NAME --query "Role.Arn" --output text)
}
$ROLE_ARN = $ROLE_ARN.Trim()
Write-Host "  IAM Role: $ROLE_ARN" -ForegroundColor Gray

# Attach S3 policy
Write-Host "  Updating S3 permissions for role..." -ForegroundColor White
$s3Policy = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::$S3_BUCKET",
                "arn:aws:s3:::$S3_BUCKET/*"
            ]
        }
    ]
}
"@
$policyFile = [System.IO.Path]::Combine($env:TEMP, "s3-policy.json")
[System.IO.File]::WriteAllText($policyFile, $s3Policy, [System.Text.UTF8Encoding]::new($false))
aws iam put-role-policy --role-name $ROLE_NAME --policy-name "S3Access" --policy-document "file://$policyFile" | Out-Null
Remove-Item $policyFile
Write-Host "  S3 permissions updated" -ForegroundColor Green

# Attach DynamoDB policy
Write-Host "  Updating DynamoDB permissions for role..." -ForegroundColor White
aws iam attach-role-policy `
    --role-name $ROLE_NAME `
    --policy-arn "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
Write-Host "  DynamoDB permissions updated" -ForegroundColor Green

$savedPref = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
aws lambda get-function --function-name $LAMBDA_FUNCTION --region $AWS_REGION 2>&1 | Out-Null
$fnExists = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = $savedPref

if ($fnExists) {
    Write-Host "  Updating existing Lambda function..." -ForegroundColor White
    aws lambda update-function-code `
        --function-name $LAMBDA_FUNCTION `
        --image-uri $IMAGE_URI `
        --region $AWS_REGION | Out-Null
    Write-Host "  Waiting for update to complete..."
    aws lambda wait function-updated --function-name $LAMBDA_FUNCTION --region $AWS_REGION
    aws lambda update-function-configuration `
        --function-name $LAMBDA_FUNCTION `
        --timeout $LAMBDA_TIMEOUT `
        --memory-size $LAMBDA_MEMORY `
        --ephemeral-storage "Size=$LAMBDA_STORAGE" `
        --region $AWS_REGION | Out-Null
    Write-Host "  Lambda function updated!" -ForegroundColor Green
}
else {
    Write-Host "  Creating new Lambda function..." -ForegroundColor White
    aws lambda create-function `
        --function-name $LAMBDA_FUNCTION `
        --package-type Image `
        --code "ImageUri=$IMAGE_URI" `
        --role $ROLE_ARN `
        --timeout $LAMBDA_TIMEOUT `
        --memory-size $LAMBDA_MEMORY `
        --ephemeral-storage "Size=$LAMBDA_STORAGE" `
        --region $AWS_REGION `
        --environment "Variables={DEBUG=false}" | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Lambda creation failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "  Waiting for function to become active..."
    aws lambda wait function-active --function-name $LAMBDA_FUNCTION --region $AWS_REGION
    Write-Host "  Lambda function created!" -ForegroundColor Green
}

# Apply environment variables to Lambda
Write-Host ""
Write-Host "Applying environment variables to Lambda..." -ForegroundColor Yellow

$envPairs = @()
$envPairs += "S3_BUCKET=$S3_BUCKET"
$envPairs += "S3_REGION=$AWS_REGION"

$envFilePath = Join-Path $API_ROOT ".env"
if (Test-Path $envFilePath) {
    $allowedKeys = @(
        "DEBUG", "DATABASE_ACTIVE",
        "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD",
        "SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES", "REFRESH_TOKEN_EXPIRE_DAYS",
        "MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_FROM", "MAIL_PORT", "MAIL_SERVER", "MAIL_STARTTLS", "MAIL_SSL_TLS",
        "STRIPE_API_KEY", "STRIPE_WEBHOOK_SECRET", "STRIPE_PRICE_MONTHLY", "STRIPE_PRICE_YEARLY",
        "REDIS_HOST", "REDIS_PORT", "REDIS_DB",
        "UPLOADS_DIR", "OUTPUTS_DIR",
        "DYNAMODB_ACTIVE", "DYNAMODB_TABLE_PREFIX"
    )
    Get-Content $envFilePath | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line -match "^([^=]+)=(.*)$") {
            $k = $matches[1].Trim().ToUpper()
            $v = $matches[2].Trim()
            if ($allowedKeys -contains $k -and $v -ne "") {
                $envPairs += "${k}=${v}"
            }
        }
    }
}

if ($envPairs.Count -gt 0) {
    # Build JSON object for environment variables
    $envObj = @{ Variables = @{} }
    foreach ($pair in $envPairs) {
        if ($pair -match "^([^=]+)=(.*)$") {
            $k = $matches[1]
            $v = $matches[2]
            $envObj.Variables[$k] = $v
        }
    }
    
    $envJson = $envObj | ConvertTo-Json -Depth 10 -Compress
    $tempEnvFile = [System.IO.Path]::Combine($env:TEMP, "lambda-env.json")
    [System.IO.File]::WriteAllText($tempEnvFile, $envJson, [System.Text.UTF8Encoding]::new($false))
    
    # Wait for any previous updates to finish (prevents ResourceConflictException)
    if ($fnExists) {
        aws lambda wait function-updated --function-name $LAMBDA_FUNCTION --region $AWS_REGION
    }

    aws lambda update-function-configuration `
        --function-name $LAMBDA_FUNCTION `
        --region $AWS_REGION `
        --environment "file://$tempEnvFile" | Out-Null
    
    Remove-Item $tempEnvFile
    Write-Host "  $($envObj.Variables.Count) env variables applied via JSON (including S3 settings)" -ForegroundColor Green
}

# ── Step 6: API Gateway ───────────────────────────────────────────────────────
Write-Host ""
Write-Host "[6/7] Setting up API Gateway..." -ForegroundColor Yellow

$savedPref = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
$API_ID = (aws apigatewayv2 get-apis `
        --region $AWS_REGION `
        --query "Items[?Name=='${LAMBDA_FUNCTION}-api'].ApiId" `
        --output text 2>&1)
$ErrorActionPreference = $savedPref

if ([string]::IsNullOrWhiteSpace($API_ID) -or $API_ID -eq "None" -or $API_ID -match "error") {
    Write-Host "  Creating new API Gateway..." -ForegroundColor White

    $API_ID = (aws apigatewayv2 create-api `
            --name "${LAMBDA_FUNCTION}-api" `
            --protocol-type HTTP `
            --region $AWS_REGION `
            --query "ApiId" --output text)

    $LAMBDA_ARN = (aws lambda get-function `
            --function-name $LAMBDA_FUNCTION `
            --region $AWS_REGION `
            --query "Configuration.FunctionArn" --output text)

    $INTEGRATION_ID = (aws apigatewayv2 create-integration `
            --api-id $API_ID `
            --integration-type AWS_PROXY `
            --integration-uri $LAMBDA_ARN `
            --payload-format-version "2.0" `
            --region $AWS_REGION `
            --query "IntegrationId" --output text)

    aws apigatewayv2 create-route `
        --api-id $API_ID --route-key "ANY /{proxy+}" `
        --target "integrations/$INTEGRATION_ID" --region $AWS_REGION | Out-Null

    aws apigatewayv2 create-route `
        --api-id $API_ID --route-key "ANY /" `
        --target "integrations/$INTEGRATION_ID" --region $AWS_REGION | Out-Null

    aws apigatewayv2 create-stage `
        --api-id $API_ID --stage-name '$default' `
        --auto-deploy --region $AWS_REGION | Out-Null

    $sourceArn = "arn:aws:execute-api:${AWS_REGION}:${AWS_ACCOUNT_ID}:${API_ID}/*/*"
    $savedPref = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    aws lambda add-permission `
        --function-name $LAMBDA_FUNCTION `
        --statement-id "apigateway-invoke" `
        --action "lambda:InvokeFunction" `
        --principal "apigateway.amazonaws.com" `
        --source-arn $sourceArn `
        --region $AWS_REGION 2>&1 | Out-Null
    $ErrorActionPreference = $savedPref

    Write-Host "  API Gateway created: $API_ID" -ForegroundColor Green
}
else {
    Write-Host "  Using existing API Gateway: $API_ID" -ForegroundColor Green
    # Remove existing CORS configuration to avoid conflict with FastAPI
    aws apigatewayv2 update-api --api-id $API_ID --cors-configuration "{}" --region $AWS_REGION | Out-Null
}

$DEFAULT_URL = "https://${API_ID}.execute-api.${AWS_REGION}.amazonaws.com"

# ── Step 7: Custom Domain + Route53 ──────────────────────────────────────────
Write-Host ""
Write-Host "[7/7] Setting up custom domain: $CUSTOM_DOMAIN..." -ForegroundColor Yellow

# Find ACM Certificate
$certsJson = (aws acm list-certificates --region $AWS_REGION --output json 2>&1)
if ($certsJson -match "error") {
    $certsJson = (aws acm list-certificates --output json)
}
$certs = $certsJson | ConvertFrom-Json
$CERT_ARN = $null

foreach ($cert in $certs.CertificateSummaryList) {
    if ($cert.DomainName -eq "*.techmindsforge.com" -or $cert.DomainName -eq "techmindsforge.com") {
        $CERT_ARN = $cert.CertificateArn
        Write-Host "  Found cert: $($cert.DomainName)" -ForegroundColor Gray
        break
    }
}

if (-not $CERT_ARN) {
    foreach ($cert in $certs.CertificateSummaryList) {
        $detail = (aws acm describe-certificate --certificate-arn $cert.CertificateArn --output json) | ConvertFrom-Json
        foreach ($san in $detail.Certificate.SubjectAlternativeNames) {
            if ($san -eq "*.techmindsforge.com" -or $san -eq $CUSTOM_DOMAIN) {
                $CERT_ARN = $cert.CertificateArn
                Write-Host "  Found cert via SAN: $san" -ForegroundColor Gray
                break
            }
        }
        if ($CERT_ARN) { break }
    }
}

if (-not $CERT_ARN) {
    Write-Host "WARNING: ACM certificate not found for $CUSTOM_DOMAIN" -ForegroundColor Yellow
    Write-Host "  Skipping custom domain setup. Use default URL:" -ForegroundColor Yellow
    Write-Host "  $DEFAULT_URL" -ForegroundColor Cyan
}
else {
    # Create or get custom domain
    $savedPref = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    $existingDomain = (aws apigatewayv2 get-domain-name --domain-name $CUSTOM_DOMAIN --region $AWS_REGION --output json 2>&1)
    $domainExists = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $savedPref

    if ($domainExists) {
        $domainInfo = $existingDomain | ConvertFrom-Json
        $API_GW_DOMAIN = $domainInfo.DomainNameConfigurations[0].ApiGatewayDomainName
        $ZONE_ID_APIGW = $domainInfo.DomainNameConfigurations[0].HostedZoneId
        Write-Host "  Custom domain already exists" -ForegroundColor Gray
    }
    else {
        $domainResult = (aws apigatewayv2 create-domain-name `
                --domain-name $CUSTOM_DOMAIN `
                --domain-name-configurations "CertificateArn=$CERT_ARN,EndpointType=REGIONAL,SecurityPolicy=TLS_1_2" `
                --region $AWS_REGION --output json) | ConvertFrom-Json
        $API_GW_DOMAIN = $domainResult.DomainNameConfigurations[0].ApiGatewayDomainName
        $ZONE_ID_APIGW = $domainResult.DomainNameConfigurations[0].HostedZoneId
        Write-Host "  Custom domain created" -ForegroundColor Green
    }

    # Create API mapping
    $savedPref = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    $mappings = (aws apigatewayv2 get-api-mappings --domain-name $CUSTOM_DOMAIN --region $AWS_REGION --output json 2>&1)
    $hasMapping = ($LASTEXITCODE -eq 0 -and ($mappings | ConvertFrom-Json).Items.Count -gt 0)
    $ErrorActionPreference = $savedPref

    if (-not $hasMapping) {
        aws apigatewayv2 create-api-mapping `
            --domain-name $CUSTOM_DOMAIN `
            --api-id $API_ID `
            --stage '$default' `
            --region $AWS_REGION | Out-Null
        Write-Host "  API mapping created" -ForegroundColor Green
    }

    # Route53 ALIAS record
    $zones = (aws route53 list-hosted-zones --output json) | ConvertFrom-Json
    $HOSTED_ZONE_ID = $null
    foreach ($zone in $zones.HostedZones) {
        if ($zone.Name -eq "${HOSTED_ZONE_NAME}.") {
            $HOSTED_ZONE_ID = $zone.Id -replace "/hostedzone/", ""
            break
        }
    }

    if ($HOSTED_ZONE_ID) {
        $changeBatch = @{
            Changes = @(@{
                    Action            = "UPSERT"
                    ResourceRecordSet = @{
                        Name        = $CUSTOM_DOMAIN
                        Type        = "A"
                        AliasTarget = @{
                            DNSName              = $API_GW_DOMAIN
                            EvaluateTargetHealth = $false
                            HostedZoneId         = $ZONE_ID_APIGW
                        }
                    }
                })
        } | ConvertTo-Json -Depth 10 -Compress

        $f = [System.IO.Path]::Combine($env:TEMP, "r53-smartconverter-api.json")
        [System.IO.File]::WriteAllText($f, $changeBatch, [System.Text.UTF8Encoding]::new($false))
        aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch "file://$f" | Out-Null
        Write-Host "  Route53 record created for $CUSTOM_DOMAIN" -ForegroundColor Green
    }
    else {
        Write-Host "WARNING: Hosted zone not found for $HOSTED_ZONE_NAME" -ForegroundColor Yellow
        Write-Host "  Please manually add an ALIAS record in Route53:" -ForegroundColor Yellow
        Write-Host "    Name   : $CUSTOM_DOMAIN" -ForegroundColor White
        Write-Host "    Type   : A (Alias)" -ForegroundColor White
        Write-Host "    Target : $API_GW_DOMAIN" -ForegroundColor White
    }
}

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host " Deployment Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host " API URL  : https://$CUSTOM_DOMAIN" -ForegroundColor Cyan
Write-Host " Docs     : https://$CUSTOM_DOMAIN/docs" -ForegroundColor Cyan
Write-Host " Health   : https://$CUSTOM_DOMAIN/api/v1/health/" -ForegroundColor Cyan
Write-Host " Default  : $DEFAULT_URL" -ForegroundColor Gray
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Cost breakdown:" -ForegroundColor Yellow
Write-Host "  ECR Private   : ~0.10/month (API image)" -ForegroundColor White
Write-Host "  Lambda        : FREE (1M requests/month)" -ForegroundColor White
Write-Host "  API Gateway   : FREE (1M calls/month)" -ForegroundColor White
Write-Host "  Route53       : ~0.50/month (hosted zone)" -ForegroundColor White
