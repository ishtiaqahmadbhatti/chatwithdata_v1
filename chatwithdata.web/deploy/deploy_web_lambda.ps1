# ChatWithData Web - AWS Lambda Deployment
# Angular app served via Node.js Lambda bootstrap
# Domain: chatwithdata.techmindsforge.com

$ErrorActionPreference = "Stop"

# ── Configuration ─────────────────────────────────────────────────────────────
$AWS_REGION = "us-east-1"
$ECR_REPO_NAME = "chatwithdata-web"
$IMAGE_TAG = "lambda"
$LAMBDA_FUNCTION = "chatwithdata-web"
$LAMBDA_TIMEOUT = 10
$LAMBDA_MEMORY = 256
$CUSTOM_DOMAIN = "chatwithdata.techmindsforge.com"
$HOSTED_ZONE_NAME = "techmindsforge.com"

# Script is inside chatwithdata.web/deploy/ - go up one level to web root
$WEB_ROOT = Split-Path $PSScriptRoot -Parent

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host " ChatWithData Web - Lambda Deployment" -ForegroundColor Cyan
Write-Host " Domain: $CUSTOM_DOMAIN" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# ── AWS Credentials ────────────────────────────────────────────────────────────
Write-Host "Checking AWS credentials..." -ForegroundColor Yellow
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: AWS CLI not configured! Run: aws configure" -ForegroundColor Red
    exit 1
}

$ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
$IMAGE_URI = "${ECR_REGISTRY}/${ECR_REPO_NAME}:${IMAGE_TAG}"

Write-Host " AWS Account : $AWS_ACCOUNT_ID" -ForegroundColor White
Write-Host " Region      : $AWS_REGION" -ForegroundColor White
Write-Host " Image URI   : $IMAGE_URI" -ForegroundColor White
Write-Host " Function    : $LAMBDA_FUNCTION" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan

# ── Step 1: ECR Login ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[1/7] Logging into ECR Private..." -ForegroundColor Yellow

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
Write-Host "[2/7] Setting up ECR repository..." -ForegroundColor Yellow
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
Write-Host "[3/7] Building Docker image (Angular build inside Docker)..." -ForegroundColor Yellow
Write-Host "  Building from: $WEB_ROOT" -ForegroundColor Gray
Write-Host "  NOTE: First build takes 5-10 min (npm install + ng build)" -ForegroundColor Gray

# Build from web root using deploy/Dockerfile.lambda
docker build `
    --platform linux/amd64 `
    --provenance=false `
    -f "$WEB_ROOT\deploy\Dockerfile.lambda" `
    -t "${ECR_REPO_NAME}:${IMAGE_TAG}" `
    $WEB_ROOT

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
Write-Host "[4/7] Pushing image to ECR..." -ForegroundColor Yellow
docker push $IMAGE_URI
$pushExitCode = $LASTEXITCODE

if ($null -ne $dockerConfigBackup) {
    [System.IO.File]::WriteAllText($dockerConfigPath, $dockerConfigBackup, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  Restored Docker credential store" -ForegroundColor Gray
}

if ($pushExitCode -ne 0) {
    Write-Host "ERROR: Docker push failed!" -ForegroundColor Red
    exit 1
}
Write-Host "  Image pushed: $IMAGE_URI" -ForegroundColor Green

# ── Step 5: IAM Role + Lambda Deploy ─────────────────────────────────────────
Write-Host ""
Write-Host "[5/7] Deploying Lambda function..." -ForegroundColor Yellow

$ROLE_NAME = "${LAMBDA_FUNCTION}-role"
$savedPref = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
$ROLE_ARN = (aws iam get-role --role-name $ROLE_NAME --query "Role.Arn" --output text 2>&1)
$roleExists = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = $savedPref

if (-not $roleExists) {
    Write-Host "  Creating IAM role..." -ForegroundColor White
    & "$PSScriptRoot\create_iam_role_web.ps1"
    Start-Sleep -Seconds 10
    $ROLE_ARN = (aws iam get-role --role-name $ROLE_NAME --query "Role.Arn" --output text)
}
$ROLE_ARN = $ROLE_ARN.Trim()
Write-Host "  IAM Role: $ROLE_ARN" -ForegroundColor Gray

$savedPref = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
aws lambda get-function --function-name $LAMBDA_FUNCTION --region $AWS_REGION 2>&1 | Out-Null
$fnExists = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = $savedPref

# Lambda env vars - write to JSON file to avoid AWS CLI parsing issues
$envJson = '{"Variables":{"PORT":"8080","READINESS_CHECK_PATH":"/"}}'
$envFile = [System.IO.Path]::Combine($env:TEMP, "lambda-web-env.json")
[System.IO.File]::WriteAllText($envFile, $envJson, [System.Text.UTF8Encoding]::new($false))

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
        --environment "file://$envFile" `
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
        --environment "file://$envFile" `
        --region $AWS_REGION | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Lambda creation failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "  Waiting for function to become active..."
    aws lambda wait function-active --function-name $LAMBDA_FUNCTION --region $AWS_REGION
    Write-Host "  Lambda function created!" -ForegroundColor Green
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
            --cors-configuration "AllowOrigins=*,AllowMethods=*,AllowHeaders=*" `
            --region $AWS_REGION `
            --query "ApiId" --output text)

    $LAMBDA_ARN = (aws lambda get-function `
            --function-name $LAMBDA_FUNCTION `
            --region $AWS_REGION `
            --query "Configuration.FunctionArn" --output text)

    $INT_ID = (aws apigatewayv2 create-integration `
            --api-id $API_ID `
            --integration-type AWS_PROXY `
            --integration-uri $LAMBDA_ARN `
            --payload-format-version "2.0" `
            --region $AWS_REGION `
            --query "IntegrationId" --output text)

    aws apigatewayv2 create-route `
        --api-id $API_ID --route-key "ANY /{proxy+}" `
        --target "integrations/$INT_ID" --region $AWS_REGION | Out-Null

    aws apigatewayv2 create-route `
        --api-id $API_ID --route-key "ANY /" `
        --target "integrations/$INT_ID" --region $AWS_REGION | Out-Null

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

        $f = [System.IO.Path]::Combine($env:TEMP, "r53-chatwithdata-web.json")
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
Write-Host " Site URL : https://$CUSTOM_DOMAIN" -ForegroundColor Cyan
Write-Host " Default  : $DEFAULT_URL" -ForegroundColor Gray
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Cost breakdown:" -ForegroundColor Yellow
Write-Host "  ECR Private   : ~0.02/month (web image)" -ForegroundColor White
Write-Host "  Lambda        : FREE (1M requests/month)" -ForegroundColor White
Write-Host "  API Gateway   : FREE (1M calls/month)" -ForegroundColor White
Write-Host "  Route53       : ~0.50/month (hosted zone)" -ForegroundColor White
