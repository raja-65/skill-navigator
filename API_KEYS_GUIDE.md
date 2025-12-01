# API Keys and Configuration Guide

## 🔑 Where to Get API Keys

### 1. Groq API Key (for AI Roadmap Generation)
- **Sign up**: [console.groq.com](https://console.groq.com)
- **Get Key**: Dashboard → API Keys → Create API Key
- **Where to use**: AWS Lambda Environment Variable `GROQ_API_KEY`
- **Cost**: Free tier available

### 2. Razorpay Keys (for Payment Processing)
- **Sign up**: [dashboard.razorpay.com](https://dashboard.razorpay.com)
- **Get Keys**: Settings → API Keys
  - **Key ID** (starts with `rzp_test_` or `rzp_live_`)
  - **Key Secret** (keep this SECRET, only use on backend if needed)
- **Where to use**: 
  - `index.html` line 108: Replace `YOUR_RAZORPAY_KEY_ID` with your Key ID
- **Cost**: Transaction fees apply

### 3. AWS Credentials
- **Already configured** if you're signed into AWS Console
- **No API keys needed** in code (Lambda uses IAM roles)

---

## 📝 Configuration Checklist

### Backend (AWS Lambda)
Set these **Environment Variables** in Lambda:
```
GROQ_API_KEY = gsk_xxxxxxxxxxxxxxxxxxxxx
DYNAMODB_TABLE = SkillNavigatorUsers
S3_BUCKET_NAME = skill-navigator-roadmaps-raja65
```

### Frontend (index.html)
Update these lines in `index.html`:
```javascript
// Line 107
const API_ENDPOINT = "https://YOUR_API_ID.execute-api.REGION.amazonaws.com/prod/generate";

// Line 108
const RAZORPAY_KEY_ID = "rzp_test_xxxxxxxxxxxxx";
```

---

## 🔒 Security Notes

### ✅ Safe to Expose (Frontend)
- Razorpay **Key ID** (starts with `rzp_test_` or `rzp_live_`)
- API Gateway URL

### ❌ NEVER Expose (Keep Secret)
- Groq API Key (only in Lambda environment variables)
- Razorpay **Key Secret** (never put in frontend)
- AWS Access Keys (use IAM roles instead)

---

## 📦 Dependencies Explained

### Why No Extra Packages?
Our Lambda code uses **built-in Python libraries**:
- `urllib.request` - for HTTP calls to Groq API (built-in)
- `json` - for JSON parsing (built-in)
- `boto3` - for AWS services (pre-installed in Lambda)

### If You Want to Use Groq SDK (Optional)
If you prefer the official Groq client library:
1. Uncomment `groq>=0.4.0` in `requirements.txt`
2. Update Lambda code to use Groq SDK
3. Rebuild the Lambda package with dependencies

**Current implementation is simpler and works perfectly!**
