#!/bin/bash
# Script to create Lambda deployment package

echo "Creating Lambda deployment package..."

# Create deployment directory
mkdir -p lambda_package
cd lambda_package

# Copy Lambda handler
cp ../lambda_handler.py .

# Note: boto3 is already available in AWS Lambda runtime
# Note: We use urllib (built-in) for Groq API, so no extra packages needed
# If you added dependencies to requirements.txt, install them here:
# pip install -r ../requirements.txt -t .

# Create zip file
echo "Creating zip file..."
zip -r ../lambda_deployment.zip .

cd ..

echo "✓ Lambda package created: lambda_deployment.zip"
echo "✓ Size: $(du -h lambda_deployment.zip | cut -f1)"
echo ""
echo "Next steps:"
echo "1. Upload lambda_deployment.zip to AWS Lambda"
echo "2. Set environment variables: GROQ_API_KEY, DYNAMODB_TABLE, S3_BUCKET_NAME"
echo "3. See API_KEYS_GUIDE.md for where to get API keys"

