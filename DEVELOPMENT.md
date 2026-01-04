# Development Guide

This guide is for developers who want to set up, develop, and contribute to Gather.

## Quick Links

- [Installation for End Users](../README.md#installation-for-end-users) - Install Gather without any setup
- [Project Structure](../README.md#project-structure) - Overview of the codebase
- [Key Features](../README.md#key-features) - What Gather can do

## Quickstart Guide for Developers

### Prerequisites

- Python 3.8+
- Google Cloud account
- API keys:
  - OpenAI API key (required)
  - OpenWeatherMap API key (optional, for weather features)
  - Google Places API key (optional, for location features)
- Google Cloud SDK (`gcloud`) - **Optional** (you can use the web console instead)
- ngrok (for local testing, optional)

### 1. Clone and Set Up Python Environment

```bash
git clone <repository-url>
cd gather

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your actual API keys:
   ```bash
   # REQUIRED
   OPENAI_API_KEY=your_openai_api_key_here

   # OPTIONAL (but recommended)
   OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here
   GOOGLE_PLACES_API_KEY=your_google_places_api_key_here
   N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-webhook-id
   ```

### 3. Set Up Google Cloud Project

You can do this via the web console (no CLI required) or using the Google Cloud SDK CLI.

#### 3.1 Create/Select Project

**Option A: Web Console (No CLI Required)**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the project dropdown at the top
3. Click **New Project**
4. Enter project name: "Gather API"
5. Click **Create**
6. Note your **Project ID** and **Project Number** (you'll need these later)

**Option B: Using gcloud CLI (Optional)**
```bash
# Install Google Cloud SDK (if not already installed)
# macOS: brew install google-cloud-sdk

# Authenticate
gcloud auth login
gcloud auth application-default login

# Create or select a project
gcloud projects create gather-api-project --name="Gather API"
gcloud config set project gather-api-project
```

#### 3.2 Enable Required APIs

**Option A: Web Console (No CLI Required)**
1. Go to [APIs & Services > Library](https://console.cloud.google.com/apis/library)
2. Search for and enable each API:
   - **Cloud Run API**
   - **Cloud Build API**
   - **Container Registry API**
   - **Google Calendar API**
   - **Google Places API (New)** (if using maps features)

**Option B: Using gcloud CLI (Optional)**
```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Google Calendar API
gcloud services enable calendar-json.googleapis.com

# Enable Google Places API (if using maps features)
gcloud services enable places-backend.googleapis.com
```

#### 3.3 Configure OAuth Consent Screen

1. Go to [Google Cloud Console > APIs & Services > OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Select **External** (unless you have Google Workspace)
3. Fill in required information:
   - App name: "Gather Assistant"
   - User support email: your email
   - Developer contact: your email
4. Add scopes:
   - `https://www.googleapis.com/auth/calendar.readonly`
   - `https://www.googleapis.com/auth/calendar.events`
   - `https://www.googleapis.com/auth/userinfo.email`
5. Add test users (your email address)

### 4. Deploy Backend API to Cloud Run

You can deploy via the web console (no CLI required) or using the Google Cloud SDK CLI.

#### Option A: Deploy via Web Console (No CLI Required)

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click **Create Service**
3. Configure the service:
   - **Service name**: `gather-api`
   - **Region**: `us-central1` (or your preferred region)
   - **Authentication**: Allow unauthenticated invocations
4. Under **Container**, click **Select** and choose **Continuously deploy new revisions from a source repository** OR **Deploy one revision from a container image**
5. If deploying from source:
   - Connect your repository (GitHub, etc.) or upload your code
   - Set build configuration to use the `Dockerfile` in the root
6. Under **Variables & Secrets**, add environment variables:
   - `OPENAI_API_KEY` = your OpenAI API key
   - `OPENWEATHERMAP_API_KEY` = your OpenWeatherMap API key (optional)
   - `GOOGLE_PLACES_API_KEY` = your Google Places API key (optional)
7. Click **Create**
8. Wait for deployment to complete
9. Your API URL will be shown on the service page: `https://gather-api-xxxxx-uc.a.run.app`

#### Option B: Deploy via gcloud CLI 

**Quick Deploy:**
```bash
# Build and deploy in one command
gcloud run deploy gather-api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="OPENAI_API_KEY=your-key-here,OPENWEATHERMAP_API_KEY=your-key-here,GOOGLE_PLACES_API_KEY=your-key-here" \
  --memory 512Mi \
  --timeout 300 \
  --max-instances 10
```

**Build Container First:**
```bash
# Set your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Build the container
gcloud builds submit --tag gcr.io/$PROJECT_ID/gather-api

# Deploy to Cloud Run
gcloud run deploy gather-api \
  --image gcr.io/$PROJECT_ID/gather-api \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="OPENAI_API_KEY=your-key-here" \
  --memory 512Mi \
  --timeout 300
```

**Get Your API URL (CLI):**
```bash
gcloud run services describe gather-api --region us-central1 --format 'value(status.url)'
```

### 5. Set Up Apps Script Add-On

#### 5.1 Create Apps Script Project

1. Go to [script.google.com](https://script.google.com)
2. Click **New Project**
3. Name it "Gather Calendar Add-On"

#### 5.2 Link to Your Google Cloud Project

1. In Apps Script, click the **Project Settings** (gear icon)
2. Under **Google Cloud Platform (GCP) Project**, click **Change Project**
3. Enter your **Project Number** (not Project ID)
   - Find it: `gcloud projects describe gather-api-project --format='value(projectNumber)'`
4. Click **Set Project**

#### 5.3 Copy Add-On Code

1. Copy contents of `addon/Code.gs` to your Apps Script `Code.gs` file
2. Copy contents of `addon/utils.gs` to a new file `utils.gs` in Apps Script
3. Copy contents of `addon/appsscript.json` to your Apps Script manifest:
   - Click **Project Settings** (gear icon)
   - Check **Show "appsscript.json" manifest file in editor**
   - Replace the manifest content

#### 5.4 Update API URL

In `Code.gs`, update the API URL:

```javascript
const API_BASE_URL = 'https://your-api-url.run.app';  // Your Cloud Run URL
```

#### 5.5 Deploy Add-On

1. Click **Deploy > Test deployments**
2. Click **Install** to install the add-on
3. Grant necessary permissions
4. Open Google Calendar and look for the Gather add-on in the sidebar

### 6. Local Development (Optional)

For local development and testing:

#### Start Local API Server

```bash
# Activate virtual environment
source .venv/bin/activate

# Start FastAPI server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Expose Local Server with ngrok

```bash
# Install ngrok: brew install ngrok (macOS)

# Sign up for free account and get authtoken
ngrok config add-authtoken your-authtoken

# Start tunnel
ngrok http 8000
```

Update `Code.gs` in Apps Script to use the ngrok URL for local testing.

### 7. Test Your Setup

```bash
# Test health endpoint
curl https://your-api-url.run.app/api/health

# Test chat endpoint
curl -X POST https://your-api-url.run.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": "test", "oauth_token": "test-token"}'
```

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
   - Click the "Fork" button on GitHub
   - Clone your fork locally

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, well-documented code
   - Follow existing code style
   - Add tests if applicable

4. **Test thoroughly**
   - Test your changes locally
   - Ensure existing functionality still works
   - Test edge cases

5. **Submit a pull request**
   - Push your branch to your fork
   - Open a pull request on the main repository
   - Describe your changes clearly
   - Reference any related issues

### Development Workflow

- Create an issue first to discuss major changes
- Keep pull requests focused and small
- Write clear commit messages
- Update documentation as needed

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small

## Additional Resources

- [Deployment Status](DEPLOYMENT_STATUS.md) - Current deployment status and checklist
- [Deployment Guide](DEPLOY_CLOUD_RUN.md) - Detailed Cloud Run deployment instructions
- [Feature Ideas](FEATURE_IDEAS.md) - Potential enhancements and ideas

