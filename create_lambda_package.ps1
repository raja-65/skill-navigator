# PowerShell script to create Lambda deployment package

Write-Host "Creating Lambda deployment package..." -ForegroundColor Green

# Create deployment directory
New-Item -ItemType Directory -Force -Path "lambda_package" | Out-Null
Set-Location lambda_package

# Copy Lambda handler
Copy-Item ../lambda_handler.py .

# Note: boto3 is already available in AWS Lambda runtime
# If you need other dependencies, install them here:
# pip install -r ../requirements.txt -t .

# Create zip file
Write-Host "Creating zip file..." -ForegroundColor Yellow
Compress-Archive -Path * -DestinationPath ../lambda_deployment.zip -Force

Set-Location ..

Write-Host "✓ Lambda package created: lambda_deployment.zip" -ForegroundColor Green
Write-Host "You can now upload this to AWS Lambda" -ForegroundColor Cyan
