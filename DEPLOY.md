# Google Cloud Run Deployment Guide

This guide explains how to deploy Collins-GPT to Google Cloud Run, a fully managed serverless platform.

**Region:** This guide uses `australia-southeast1` (Sydney) for optimal performance in Australia.

## Prerequisites

1. **Google Cloud Account** - [Sign up for free](https://cloud.google.com/free)
2. **Google Cloud CLI (gcloud)** - [Install instructions](https://cloud.google.com/sdk/docs/install)
3. **Docker** - For local testing (optional)
4. **Project Requirements:**
   - OpenRouter API key
   - Production-ready `SECRET_KEY` for Flask

## Quick Deployment (Recommended - Using Secret Manager)

This is the **recommended production deployment method** using Google Secret Manager for secure credential storage.

### Step 1: Set up Google Cloud

```bash
# Authenticate with Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create collins-gpt-prod --name="Collins GPT Production"

# Set the project as active
gcloud config set project collins-gpt-prod

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Step 2: Create Secrets in Secret Manager

Store your sensitive credentials securely:

```bash
# Create OPENROUTER_API_KEY secret
echo -n "your-api-key-here" | gcloud secrets create openrouter-api-key --data-file=-

# Create SECRET_KEY secret (auto-generates a secure random key)
python -c "import secrets; print(secrets.token_hex(32), end='')" | gcloud secrets create flask-secret-key --data-file=-
```

**Important:** Replace `your-api-key-here` with your actual OpenRouter API key.

### Step 3: Build Frontend Assets

Before deploying, build the production frontend assets:

```bash
cd frontend
pnpm install
pnpm run build:prod
cd ..
```

### Step 4: Deploy to Cloud Run

Deploy directly from source with Secret Manager integration:

```bash
gcloud run deploy collins-gpt \
  --source . \
  --platform managed \
  --region australia-southeast1 \
  --allow-unauthenticated \
  --set-secrets OPENROUTER_API_KEY=openrouter-api-key:latest \
  --set-secrets SECRET_KEY=flask-secret-key:latest \
  --memory 256Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --cpu-throttling
```

Cloud Build will:
1. Build your frontend assets (if not already built)
2. Create a Docker container
3. Push to Artifact Registry
4. Deploy to Cloud Run with secrets mounted as environment variables

**Cost-Optimized Configuration:**
- `--memory 256Mi` - Minimal memory for this Flask app
- `--cpu 1` - Single vCPU (sufficient for low-moderate traffic)
- `--min-instances 0` - Scales to zero when idle (no charges when not in use)
- `--max-instances 10` - Prevents runaway scaling costs
- `--cpu-throttling` - Reduces CPU usage when idle
- `--timeout 300` - 5 minute timeout for streaming AI responses

**Expected Cost:** With these settings, the app will likely run **for free** under Cloud Run's generous free tier (2M requests/month). Even with moderate traffic, costs typically remain under $5/month.

### Step 5: Get Your Service URL

After deployment completes, you'll receive a URL like:
```
https://collins-gpt-<hash>-ts.a.run.app
```

Visit this URL to access your deployed application!

## Alternative: Deploy with Direct Environment Variables

**⚠️ Not recommended for production** - Use this only for testing or development deployments.

```bash
# Build frontend first
cd frontend && pnpm install && pnpm run build:prod && cd ..

# Deploy with direct environment variables
gcloud run deploy collins-gpt \
  --source . \
  --platform managed \
  --region australia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars OPENROUTER_API_KEY="your-api-key-here" \
  --set-env-vars SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')" \
  --memory 256Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --cpu-throttling
```

**Why Secret Manager is better:**
- Secrets aren't stored in command history
- Secrets aren't visible in deployment logs
- Easier secret rotation without redeployment
- Audit logging of secret access
- Centralized secret management

## Manual Docker Build & Deploy

If you prefer more control over the build process:

### Step 1: Build Frontend

```bash
cd frontend && pnpm install && pnpm run build:prod && cd ..
```

### Step 2: Build Docker Image

```bash
# Set your project ID and region
export PROJECT_ID=collins-gpt-prod
export REGION=australia-southeast1

# Build and tag the image
docker build -t gcr.io/${PROJECT_ID}/collins-gpt:latest .

# Push to Google Container Registry
docker push gcr.io/${PROJECT_ID}/collins-gpt:latest
```

### Step 3: Deploy from Container Registry

```bash
# Deploy with Secret Manager (recommended) and cost-optimized settings
gcloud run deploy collins-gpt \
  --image gcr.io/${PROJECT_ID}/collins-gpt:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-secrets OPENROUTER_API_KEY=openrouter-api-key:latest \
  --set-secrets SECRET_KEY=flask-secret-key:latest \
  --memory 256Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --cpu-throttling
```

**Note:** Ensure you've created the secrets first (see Step 2 in Quick Deployment above).

## Configuration Options

### Memory & CPU

**Default (recommended):** `--memory 256Mi --cpu 1`

Adjust based on your needs:

```bash
# Default - Cost-optimized for low-moderate traffic (RECOMMENDED)
--memory 256Mi --cpu 1

# More resources for higher traffic or complex AI workloads
--memory 512Mi --cpu 2

# Maximum resources (expensive, rarely needed)
--memory 1Gi --cpu 2
```

### Concurrency

Control how many requests a single container handles:

```bash
# Default: 80 concurrent requests per container
--concurrency 80

# Higher concurrency (more efficient, uses more memory)
--concurrency 250

# Lower concurrency (more stable, more containers needed)
--concurrency 10
```

### Scaling

**Default (recommended):** `--min-instances 0 --max-instances 10 --cpu-throttling`

Control auto-scaling behavior:

```bash
# Scale to zero when idle (RECOMMENDED - no cost when unused)
--min-instances 0

# Keep 1 instance warm (eliminates cold starts, but costs ~$5-10/month)
--min-instances 1

# Maximum instances (prevent runaway costs)
--max-instances 10  # Default
--max-instances 100 # For high-traffic scenarios

# CPU throttling when no requests (RECOMMENDED - saves cost)
--cpu-throttling
```

**Note:** With `--min-instances 0`, the first request after idle period may take 2-5 seconds (cold start). This is normal and acceptable for most use cases.

### Request Timeout

For streaming AI responses, you may need longer timeouts:

```bash
# Maximum timeout (5 minutes)
--timeout 300

# Default timeout (5 minutes)
--timeout 300
```

## Environment Variables

Required environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | `sk-or-v1-...` |
| `SECRET_KEY` | Flask secret key | `a1b2c3d4e5f6...` |
| `PORT` | Port to listen on | `8080` (set by Cloud Run) |

Optional environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `production` |

## Testing Locally with Docker

Test your Docker image locally before deploying:

```bash
# Build frontend
cd frontend && pnpm install && pnpm run build:prod && cd ..

# Build Docker image
docker build -t collins-gpt:local .

# Run container locally
docker run -p 8080:8080 \
  -e OPENROUTER_API_KEY="your-api-key" \
  -e SECRET_KEY="your-secret-key" \
  collins-gpt:local

# Visit http://localhost:8080
```

## Continuous Deployment

### Option 1: GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Setup pnpm
      uses: pnpm/action-setup@v2
      with:
        version: 8

    - name: Build frontend
      run: |
        cd frontend
        pnpm install --frozen-lockfile
        pnpm run build:prod

    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}

    - name: Deploy to Cloud Run
      uses: google-github-actions/deploy-cloudrun@v2
      with:
        service: collins-gpt
        region: australia-southeast1
        source: .
        secrets: |
          OPENROUTER_API_KEY=openrouter-api-key:latest
          SECRET_KEY=flask-secret-key:latest
```

### Option 2: Cloud Build Trigger

1. Connect your GitHub repository to Cloud Build
2. Create a trigger on the `main` branch
3. Use the default `Dockerfile` configuration

## Monitoring & Logs

### View Logs

```bash
# Stream logs in real-time
gcloud run services logs tail collins-gpt --region australia-southeast1

# View logs in Cloud Console
gcloud run services describe collins-gpt --region australia-southeast1 --format="value(status.url)"
```

### Monitoring Dashboard

View metrics in the Cloud Console:
```
https://console.cloud.google.com/run?project=YOUR_PROJECT_ID
```

Metrics available:
- Request count
- Request latency
- Container CPU utilization
- Container memory utilization
- Container instance count
- Billable container instance time

## Cost Optimization

Cloud Run pricing is based on:
1. **Request time** - How long requests take
2. **Container memory** - How much RAM you allocate
3. **Container CPU** - CPU allocation
4. **Networking** - Outbound data transfer

### Cost-Optimized Defaults (Already Configured)

Our deployment commands already include these cost optimizations:

1. ✅ **Scale to zero** - `--min-instances 0` scales down when idle (no cost when unused)
2. ✅ **Right-sized resources** - `--memory 256Mi --cpu 1` (minimal resources for this Flask app)
3. ✅ **CPU throttling enabled** - `--cpu-throttling` reduces CPU usage when idle
4. ✅ **Optimized Docker image** - Multi-stage builds minimize image size
5. ✅ **Reasonable limits** - `--max-instances 10` prevents runaway scaling costs

### Additional Optimization Tips:

- **Use caching** - Implement Flask-Caching or Redis to cache AI responses and reduce OpenRouter API calls
- **Monitor usage** - Review Cloud Run metrics to identify opportunities for further optimization
- **Use Secret Manager** - Free secret storage with automatic rotation capabilities

### Free Tier

Cloud Run offers a generous free tier:
- 2 million requests per month
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds of compute time

For a low-traffic app, this is likely free!

## Custom Domain

Map a custom domain to your Cloud Run service:

```bash
# Map domain
gcloud run domain-mappings create \
  --service collins-gpt \
  --domain www.yourdomain.com \
  --region australia-southeast1

# Follow the instructions to update your DNS records
```

## Security Best Practices

1. **Use Secret Manager** - Never commit API keys to git
2. **Enable IAM Authentication** - For internal apps, remove `--allow-unauthenticated`
3. **Use HTTPS** - Cloud Run provides free SSL certificates automatically
4. **Set up Cloud Armor** - Add DDoS protection and WAF rules
5. **Rotate secrets regularly** - Update API keys and secret keys periodically

## Troubleshooting

### Deployment Fails

Check build logs:
```bash
gcloud builds list --limit=5
gcloud builds log <BUILD_ID>
```

### Container Crashes

Check service logs:
```bash
gcloud run services logs read collins-gpt --region australia-southeast1 --limit=50
```

### Slow Responses

- Increase memory allocation (`--memory 1Gi`)
- Check OpenRouter API latency
- Enable request tracing in Cloud Trace

### Port Issues

Cloud Run sets the `PORT` environment variable automatically. Ensure your app listens on `0.0.0.0:$PORT`.

## Rollback

Revert to a previous revision:

```bash
# List revisions
gcloud run revisions list --service collins-gpt --region australia-southeast1

# Rollback to specific revision
gcloud run services update-traffic collins-gpt \
  --to-revisions REVISION_NAME=100 \
  --region australia-southeast1
```

## Updating the App

To deploy updates:

```bash
# Build frontend (if changed)
cd frontend && pnpm run build:prod && cd ..

# Deploy updated code
gcloud run deploy collins-gpt \
  --source . \
  --region australia-southeast1
```

Cloud Run creates a new revision and gradually shifts traffic to it (zero-downtime deployment).

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/best-practices)
- [Secret Manager Guide](https://cloud.google.com/secret-manager/docs)

## Support

For issues specific to this deployment:
1. Check the logs: `gcloud run services logs tail collins-gpt --region australia-southeast1`
2. Review Cloud Run metrics in the Cloud Console
3. Open an issue in the project repository

---

**Last Updated:** 2025-12-11
**Tested With:** Google Cloud Run (Gen 2), gcloud CLI 500.0.0+
