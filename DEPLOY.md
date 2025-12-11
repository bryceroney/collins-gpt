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

## Quick Deployment (Recommended)

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
```

### Step 2: Build Frontend Assets

Before deploying, build the production frontend assets:

```bash
cd frontend
pnpm install
pnpm run build:prod
cd ..
```

### Step 3: Deploy to Cloud Run

Deploy directly from source (Cloud Build will handle the Docker build):

```bash
# Deploy with environment variables (Sydney region)
gcloud run deploy collins-gpt \
  --source . \
  --platform managed \
  --region australia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars OPENROUTER_API_KEY="your-api-key-here" \
  --set-env-vars SECRET_KEY="your-production-secret-key-here" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

**Important:** Replace the placeholders:
- `your-api-key-here` with your actual OpenRouter API key
- `your-production-secret-key-here` with a secure random string (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)

### Step 4: Get Your Service URL

After deployment completes, you'll receive a URL like:
```
https://collins-gpt-<hash>-ts.a.run.app
```

Visit this URL to access your deployed application!

## Using Secret Manager (Recommended for Production)

For better security, store sensitive values in Google Secret Manager:

### Step 1: Enable Secret Manager API

```bash
gcloud services enable secretmanager.googleapis.com
```

### Step 2: Create Secrets

```bash
# Create OPENROUTER_API_KEY secret
echo -n "your-api-key-here" | gcloud secrets create openrouter-api-key --data-file=-

# Create SECRET_KEY secret
python -c "import secrets; print(secrets.token_hex(32), end='')" | gcloud secrets create flask-secret-key --data-file=-
```

### Step 3: Deploy with Secret Manager

```bash
gcloud run deploy collins-gpt \
  --source . \
  --platform managed \
  --region australia-southeast1 \
  --allow-unauthenticated \
  --set-secrets OPENROUTER_API_KEY=openrouter-api-key:latest \
  --set-secrets SECRET_KEY=flask-secret-key:latest \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

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
gcloud run deploy collins-gpt \
  --image gcr.io/${PROJECT_ID}/collins-gpt:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars OPENROUTER_API_KEY="your-api-key-here" \
  --set-env-vars SECRET_KEY="your-production-secret-key-here"
```

## Configuration Options

### Memory & CPU

Adjust based on your needs:

```bash
# More resources for higher traffic
--memory 1Gi --cpu 2

# Cost-optimized for low traffic
--memory 256Mi --cpu 1
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

Control auto-scaling behavior:

```bash
# Minimum instances (keeps app warm, costs more)
--min-instances 1

# Maximum instances (prevent runaway costs)
--max-instances 100

# CPU throttling when no requests (saves cost)
--cpu-throttling
```

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

### Tips to Reduce Costs:

1. **Scale to zero** - Set `--min-instances 0` (default) to scale down when idle
2. **Right-size resources** - Start with `--memory 256Mi --cpu 1` and adjust based on metrics
3. **Enable CPU throttling** - Use `--cpu-throttling` to reduce CPU usage when idle
4. **Use caching** - Cache AI responses to reduce OpenRouter API calls
5. **Optimize Docker image** - Multi-stage builds reduce image size (already implemented)

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
