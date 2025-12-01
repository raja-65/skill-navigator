#!/bin/bash
# Script to create Lambda deployment package

echo "Creating Lambda deployment package..."

# Create deployment directory
mkdir -p lambda_package
cd lambda_package

# Copy Lambda handler
cp ../lambda_handler.py .

# Note: boto3 is already available in AWS Lambda runtime
# If you need other dependencies, install them here:
# pip install -r ../requirements.txt -t .

# Create zip file
echo "Creating zip file..."
zip -r ../lambda_deployment.zip .

cd ..

echo "✓ Lambda package created: lambda_deployment.zip"
echo "You can now upload this to AWS Lambda"
