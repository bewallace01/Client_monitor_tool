# Security Policy

## Sensitive Data Protection

This project handles sensitive data including API keys, database credentials, and user information. This document outlines security best practices.

## What is Protected

### Automatically Excluded from Git

The following files/folders are **automatically excluded** via `.gitignore`:

- `.env` - Environment variables with API keys
- `data/` - Local database files
- `backend/api_configs/*.json` - API configuration files (may contain keys)
- `logs/` - Log files that may contain sensitive debug information
- `*.db`, `*.sqlite` - Database files
- `venv/`, `node_modules/` - Dependencies

### Never Commit These

**🚫 NEVER commit files containing:**

- API Keys (Google, NewsAPI, OpenAI, Anthropic, Salesforce)
- Database passwords
- SECRET_KEY values
- SMTP passwords
- OAuth tokens or refresh tokens
- Customer data or PII
- Production database dumps

## API Key Management

### Development

1. **Use `.env` files** (already in `.gitignore`)
   ```bash
   cp backend/.env.example backend/.env
   # Add your keys to .env
   ```

2. **Use mock mode for testing**
   ```bash
   USE_MOCK_APIS=True  # No API keys needed
   ```

### Production

**Do NOT use `.env` files in production.** Instead:

1. **Environment Variables**
   ```bash
   export GOOGLE_API_KEY="your-key"
   export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
   ```

2. **Secrets Management Services**
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Secret Manager
   - HashiCorp Vault

3. **Docker Secrets**
   ```yaml
   # docker-compose.yml
   secrets:
     google_api_key:
       external: true
   ```

## Database Security

### PostgreSQL

1. **Change default passwords**
   ```bash
   # Never use default 'postgres' password
   export POSTGRES_PASSWORD="$(openssl rand -base64 32)"
   ```

2. **Use strong passwords**
   - Minimum 20 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Generated randomly

3. **Restrict network access**
   ```yaml
   # docker-compose.yml
   postgres:
     ports:
       - "127.0.0.1:5432:5432"  # Only localhost
   ```

### SQLite (Development Only)

- SQLite is for **development only**
- Database file excluded via `.gitignore`
- Use PostgreSQL for production

## Application Security

### SECRET_KEY

The `SECRET_KEY` is used for:
- Session management
- Password hashing
- Token generation

**Generate a secure key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Production requirements:**
- Minimum 32 characters
- Randomly generated
- Unique per environment
- Never shared between dev/staging/prod

### CORS Configuration

Update `ALLOWED_ORIGINS` for your domain:

```python
# backend/.env
ALLOWED_ORIGINS=["https://your-domain.com"]
```

### Debug Mode

**🚫 Never run with `DEBUG=True` in production**

```bash
# Production
DEBUG=False
LOG_LEVEL=WARNING
```

## Email/SMTP Security

### App-Specific Passwords

If using Gmail SMTP:
1. Enable 2FA on Google account
2. Generate app-specific password
3. Use app password, not account password

### Configuration

```python
# Configure via environment, not code
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password  # NOT your real password
```

## Third-Party API Keys

### NewsAPI
- **Free tier**: 100 requests/day
- **Rate limit**: Store in config, enforce in code
- **Rotate keys** if exposed

### Google Custom Search
- **Quota**: 100 queries/day (free)
- **Restrict by IP** in Google Cloud Console
- **Restrict by referrer** for web apps

### OpenAI / Anthropic
- **Monitor usage** to detect abuse
- **Set spending limits** in provider dashboard
- **Rotate keys** monthly

### Salesforce
- **Use OAuth 2.0** refresh tokens
- **Don't store passwords** - use Connected Apps
- **Implement token refresh** logic

## Incident Response

### If API Key is Exposed

1. **Immediately revoke** the key in provider dashboard
2. **Generate new key** and update `.env`
3. **Review logs** for unauthorized usage
4. **Check billing** for unexpected charges
5. **Rotate dependent secrets** (if cascading)

### If Database is Compromised

1. **Isolate** the database immediately
2. **Assess scope** of data breach
3. **Notify users** if PII affected (legal requirement)
4. **Restore** from clean backup
5. **Change all credentials**

## Security Scanning

### Before Committing

```bash
# Check for accidentally committed secrets
git secrets --scan

# Or use gitleaks
gitleaks detect --source . --verbose
```

### Automated Scanning

Enable GitHub's **Secret Scanning**:
- Automatically detects committed secrets
- Alerts repository admins
- Available for public and private repos

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public issue
2. **Email** the maintainer directly: [your-email@domain.com]
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Headers (Production)

Add these headers to your reverse proxy (nginx, Apache):

```nginx
# nginx example
add_header X-Frame-Options "DENY";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

## Regular Maintenance

- [ ] Rotate API keys **every 90 days**
- [ ] Review access logs **weekly**
- [ ] Update dependencies **monthly**
- [ ] Audit user permissions **quarterly**
- [ ] Test backup/restore **quarterly**
- [ ] Security audit **annually**

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [Docker Security](https://docs.docker.com/engine/security/)
