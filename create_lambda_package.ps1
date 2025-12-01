# PowerShell script to create Lambda deployment package

Write-Host "Creating Lambda deployment package..." -ForegroundColor Green

# Create deployment directory
New-Item -ItemType Directory -Force -Path "lambda_package" | Out-Null
Set-Location lambda_package

# Copy Lambda handler
Copy-Item ../lambda_handler.py .

# Note: boto3 is already available in AWS Lambda runtime
# Note: We use urllib (built-in) for Groq API, so no extra packages needed
# If you added dependencies to requirements.txt, install them here:
# pip install -r ../requirements.txt -t .

# Create zip file
Write-Host "Creating zip file..." -ForegroundColor Yellow
Compress-Archive -Path * -DestinationPath ../lambda_deployment.zip -Force

Set-Location ..

$zipSize = (Get-Item lambda_deployment.zip).Length / 1KB
Write-Host "✓ Lambda package created: lambda_deployment.zip ($([math]::Round($zipSize, 2)) KB)" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Upload lambda_deployment.zip to AWS Lambda"
Write-Host "2. Set environment variables: GROQ_API_KEY, DYNAMODB_TABLE, S3_BUCKET_NAME"
Write-Host "3. See API_KEYS_GUIDE.md for where to get API keys"

