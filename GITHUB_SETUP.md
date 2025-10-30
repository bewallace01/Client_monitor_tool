# GitHub Setup Guide

This guide will help you prepare the Client Monitor project for GitHub upload without exposing sensitive data.

## What's Already Protected

The project includes a `.gitignore` file that automatically excludes:

- **Environment files**: `.env`, `.env.local`
- **Database files**: `data/`, `*.db`, `*.sqlite`, `*.sqlite3`
- **API configurations**: `backend/api_configs/*.json`
- **Log files**: `logs/`, `*.log`
- **Virtual environments**: `venv/`, `env/`
- **Node modules**: `node_modules/`
- **IDE settings**: `.vscode/`, `.idea/`

## Before Uploading to GitHub

### 1. Review Your .env Files

Make sure your `.env` files contain **NO real API keys**. They should only have placeholder values:

```bash
# ✅ GOOD - Safe to commit (but already excluded by .gitignore)
GOOGLE_API_KEY=
NEWSAPI_KEY=
SECRET_KEY=your-secret-key-here-change-in-production

# ❌ BAD - Contains real API keys (NEVER commit this)
GOOGLE_API_KEY=AIzaSyC_ActualKeyHere
NEWSAPI_KEY=a1b2c3d4actualkey
```

### 2. Check Docker Compose

The `docker-compose.yml` now uses environment variables with safe defaults:

```yaml
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-change_me_in_production}
SECRET_KEY: ${SECRET_KEY:-change-this-secret-key-in-production}
```

**Production users should override these via environment variables!**

### 3. Verify No Sensitive Data in Code

Search for any hardcoded credentials:

```bash
# Search for potential API keys or passwords in Python files
cd backend
grep -r "api_key\|password\|secret" --include="*.py" app/

# Should only find variable names, not actual values
```

## Setting Up from GitHub

### For New Users Cloning This Repository

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Client\ Monitor
   ```

2. **Copy example environment files**
   ```bash
   # Backend
   cp backend/.env.example backend/.env

   # Frontend (if exists)
   cp frontend/.env.example frontend/.env 2>/dev/null || true
   ```

3. **Add your API keys to backend/.env**
   ```bash
   # Edit the .env file and add your actual keys:
   GOOGLE_API_KEY=your_actual_google_api_key_here
   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
   NEWSAPI_KEY=your_newsapi_key_here
   SECRET_KEY=generate_a_random_secret_key_here
   ```

4. **Generate a secure SECRET_KEY**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

5. **Set production passwords for Docker**
   ```bash
   export POSTGRES_PASSWORD="your_strong_password_here"
   export SECRET_KEY="your_generated_secret_key"
   ```

6. **Start the application**
   ```bash
   # With Docker
   docker-compose up -d

   # Or locally (backend)
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

## API Keys You'll Need

### Required APIs (for production use)

1. **NewsAPI** (Free tier available)
   - Sign up: https://newsapi.org/
   - Get your API key from the dashboard
   - Free tier: 100 requests/day

2. **Google Custom Search API** (Optional)
   - Create project: https://console.cloud.google.com/
   - Enable Custom Search API
   - Create credentials (API Key)
   - Create Custom Search Engine: https://programmablesearchengine.google.com/

3. **OpenAI or Anthropic** (Optional - for AI features)
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

4. **Salesforce** (Optional - for CRM integration)
   - Create Connected App in Salesforce
   - Get Client ID and Client Secret

### Mock Mode (No APIs Required)

The application can run in **mock mode** for testing without any API keys:

```bash
# In backend/.env
USE_MOCK_APIS=True
```

## Security Checklist Before Pushing

- [ ] Verified `.env` files are listed in `.gitignore`
- [ ] Checked no API keys in Python code
- [ ] Ensured `data/` folder is excluded
- [ ] Confirmed `backend/api_configs/*.json` files are ignored
- [ ] Verified no database files (`.db`, `.sqlite`) will be committed
- [ ] Checked `docker-compose.yml` uses environment variables
- [ ] Removed any test API keys from code comments
- [ ] Updated README with setup instructions

## Recommended: Use Environment Variables for Production

Instead of `.env` files in production, use:

- **Docker**: Pass via `docker-compose` environment or `--env-file`
- **Cloud platforms**: Use built-in secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
- **CI/CD**: Store secrets in GitHub Secrets, GitLab CI/CD Variables, etc.

## Need Help?

See the main [README.md](README.md) for full setup instructions.
