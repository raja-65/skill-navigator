# Skill Navigator Deployment Guide

This guide will walk you through deploying your application step-by-step.

## Part 1: Deploy Frontend to GitHub Pages

### Step 1: Initialize Git Repository
```bash
cd /d/sideprojects/SkillNavigator
git init
git add .
git commit -m "Initial commit - Skill Navigator"
```

### Step 2: Create GitHub Repository
1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right → "New repository"
3. Name it: `skill-navigator`
4. Keep it **Public** (required for free GitHub Pages)
5. **Do NOT** initialize with README
6. Click "Create repository"

### Step 3: Push to GitHub
```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/skill-navigator.git
git branch -M main
git push -u origin main
```

### Step 4: Enable GitHub Pages
1. Go to your repository on GitHub
2. Click "Settings" tab
3. Click "Pages" in the left sidebar
4. Under "Source", select "main" branch
5. Click "Save"
6. Your site will be live at: `https://YOUR_USERNAME.github.io/skill-navigator/`

---

## Part 2: Prepare Backend for AWS Lambda

### Step 1: Create Lambda Deployment Package

First, we need to install dependencies locally and create a zip file.

```bash
# Create a deployment directory
mkdir lambda_package
cd lambda_package

# Copy your Lambda handler
cp ../lambda_handler.py .

# Install boto3 (already included in Lambda, but we'll add it anyway)
# Install any other dependencies if needed
pip install boto3 -t .

# Create the zip file
# On Windows with Git Bash:
zip -r ../lambda_deployment.zip .

# Or on Windows PowerShell:
# Compress-Archive -Path * -DestinationPath ../lambda_deployment.zip

cd ..
```

**Note**: `boto3` is already available in AWS Lambda, so you don't need to include it. The zip will mainly contain `lambda_handler.py`.

---

## Part 3: AWS Setup (Backend Infrastructure)

### Step 1: Create DynamoDB Table

1. **Sign in to AWS Console**: Go to [console.aws.amazon.com](https://console.aws.amazon.com)
2. **Navigate to DynamoDB**: Search for "DynamoDB" in the search bar
3. **Create Table**:
   - Click "Create table"
   - **Table name**: `SkillNavigatorUsers`
   - **Partition key**: `user_id` (String)
   - Leave other settings as default
   - Click "Create table"

### Step 2: Create S3 Bucket

1. **Navigate to S3**: Search for "S3" in the search bar
2. **Create Bucket**:
   - Click "Create bucket"
   - **Bucket name**: `skill-navigator-roadmaps-YOUR_UNIQUE_ID` (must be globally unique)
   - **Region**: Choose your preferred region (e.g., us-east-1)
   - **Uncheck** "Block all public access" (we need pre-signed URLs to work)
   - Acknowledge the warning
   - Click "Create bucket"

### Step 3: Create Lambda Function

1. **Navigate to Lambda**: Search for "Lambda" in the search bar
2. **Create Function**:
   - Click "Create function"
   - Choose "Author from scratch"
   - **Function name**: `SkillNavigatorGenerator`
   - **Runtime**: Python 3.11 (or latest Python 3.x)
   - **Architecture**: x86_64
   - Click "Create function"

3. **Upload Code**:
   - In the "Code" tab, click "Upload from" → ".zip file"
   - Upload the `lambda_deployment.zip` file
   - Click "Save"

4. **Set Environment Variables**:
   - Click "Configuration" tab → "Environment variables"
   - Click "Edit" → "Add environment variable"
   - Add these three variables:
     - `GROQ_API_KEY`: Your Groq API key (get from [console.groq.com](https://console.groq.com))
     - `DYNAMODB_TABLE`: `SkillNavigatorUsers`
     - `S3_BUCKET_NAME`: Your bucket name from Step 2
   - Click "Save"

5. **Increase Timeout**:
   - Click "Configuration" tab → "General configuration"
   - Click "Edit"
   - Set **Timeout** to `30 seconds` (Groq API might take time)
   - Click "Save"

6. **Add Permissions**:
   - Click "Configuration" tab → "Permissions"
   - Click on the role name (opens in new tab)
   - Click "Add permissions" → "Attach policies"
   - Search and attach:
     - `AmazonDynamoDBFullAccess`
     - `AmazonS3FullAccess`
   - Click "Attach policies"

### Step 4: Create API Gateway

1. **Navigate to API Gateway**: Search for "API Gateway"
2. **Create API**:
   - Click "Create API"
   - Choose "HTTP API" (simpler than REST API)
   - Click "Build"

3. **Configure API**:
   - **Add integration**: Choose "Lambda"
   - **Lambda function**: Select `SkillNavigatorGenerator`
   - **API name**: `SkillNavigatorAPI`
   - Click "Next"

4. **Configure Routes**:
   - **Method**: POST
   - **Resource path**: `/generate`
   - Click "Next"

5. **Configure Stages**:
   - **Stage name**: `prod`
   - Click "Next" → "Create"

6. **Enable CORS**:
   - Click on your API
   - Click "CORS" in the left sidebar
   - Click "Configure"
   - **Access-Control-Allow-Origin**: `*` (or your GitHub Pages URL)
   - **Access-Control-Allow-Headers**: `content-type`
   - **Access-Control-Allow-Methods**: `POST, OPTIONS`
   - Click "Save"

7. **Get Your API URL**:
   - You'll see an "Invoke URL" like: `https://abc123.execute-api.us-east-1.amazonaws.com/prod`
   - Your full endpoint is: `https://abc123.execute-api.us-east-1.amazonaws.com/prod/generate`

---

## Part 4: Update Frontend Configuration

1. **Edit index.html**:
   - Open `index.html`
   - Find line with `const API_ENDPOINT = "YOUR_API_GATEWAY_URL/generate";`
   - Replace with your actual API Gateway URL
   - Find `const RAZORPAY_KEY_ID = "YOUR_RAZORPAY_KEY_ID";`
   - Replace with your Razorpay Key ID (get from [dashboard.razorpay.com](https://dashboard.razorpay.com))

2. **Push Changes to GitHub**:
```bash
git add index.html
git commit -m "Update API endpoints"
git push
```

3. **Wait 1-2 minutes** for GitHub Pages to rebuild

---

## Part 5: Testing

1. Visit your GitHub Pages URL
2. Enter a skill (e.g., "Python")
3. Select a level
4. Click "Generate Roadmap"
5. Check if the roadmap is generated and downloadable

---

## Troubleshooting

### Frontend Issues
- **Page not loading**: Wait a few minutes after enabling GitHub Pages
- **API errors**: Check browser console (F12) for error messages

### Backend Issues
- **Check Lambda Logs**: Go to Lambda → Monitor → View logs in CloudWatch
- **Test Lambda**: Use the "Test" tab in Lambda console
- **CORS errors**: Ensure CORS is properly configured in API Gateway

### Common Errors
- **"Insufficient credits"**: Add credits to a test user in DynamoDB manually
- **"GROQ_API_KEY not set"**: Check Lambda environment variables
- **S3 upload fails**: Check Lambda IAM role has S3 permissions

---

## Next Steps

1. **Get Groq API Key**: Sign up at [console.groq.com](https://console.groq.com)
2. **Get Razorpay Account**: Sign up at [razorpay.com](https://razorpay.com)
3. **Add test credits**: Manually add credits to your user in DynamoDB for testing
