# Vercel Routing Configuration Verification

**File:** vercel.json  
**Status:** ✅ VERIFIED FOR DJANGO-ONLY DEPLOYMENT  
**Updated:** April 13, 2026

---

## Current Configuration (Verified Correct)

```json
{
  "buildCommand": "pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput",
  "devCommand": "python manage.py runserver 8000",
  "env": {
    "DJANGO_SETTINGS_MODULE": "saarthi.settings",
    "DEBUG": "False"
  },
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "saarthi/wsgi.py"
    }
  ]
}
```

---

## ✅ Verification Checklist

### Build Command
- [x] Installs dependencies: `pip install -r requirements.txt`
- [x] Runs migrations: `python manage.py migrate --noinput`
- [x] Collects static files: `python manage.py collectstatic --noinput`
- [x] Flags: `--noinput` prevents prompts (required for CI/CD)

**Status:** ✅ CORRECT - Ensures schema is created on production

### Development Command
- [x] `python manage.py runserver 8000`
- [x] Used for local `vercel dev` testing

**Status:** ✅ CORRECT

### Environment Variables
- [x] `DJANGO_SETTINGS_MODULE=saarthi.settings` - Tells Django which settings to use
- [x] `DEBUG=False` - Production security setting
- [x] Both set in vercel.json env section

**Status:** ✅ CORRECT - See environment variables guide for Vercel dashboard overrides

### Static Files Routing
- [x] Route: `/static/(.*)` matches all static file requests
- [x] Destination: Serves from `/static/$1` 
- [x] Cache headers: 1 year (31536000 seconds)
- [x] Immutable flag: Browser won't revalidate cached files
- [x] Efficient for images, CSS, JS that don't change per deploy

**Status:** ✅ CORRECT - WhiteNoise middleware in Django handles actual file serving

### Django WSGI Routing
- [x] Catch-all route: `/(.*)`
- [x] Routes to: `saarthi/wsgi.py`
- [x] Handles all non-static requests

**Status:** ✅ CORRECT

---

## 📊 Request Flow

### Static File Request
```
Client Request: GET /static/style.css
       ↓
Vercel Router matches: /static/(.*)
       ↓
Route to: /static/ (static hosting)
       ↓
Returns: File from staticfiles/ directory with 1-year cache header
```

### Page/API Request
```
Client Request: GET /dashboard/
       ↓
Vercel Router matches: /(.*) [catch-all]
       ↓
Route to: saarthi/wsgi.py (Django WSGI application)
       ↓
Django processes request, queries PostgreSQL database
       ↓
Returns: HTML/JSON response
```

### Authentication Flow (with Database)
```
Client Request: POST /api/auth/login (with credentials)
       ↓
Routes to: saarthi/wsgi.py
       ↓
Django view processes credentials
       ↓
Queries: PostgreSQL database (DATABASE_URL from env vars)
       ↓
Returns: Session token or error
```

---

## 🔧 Future Configuration (If Adding Node.js API)

If you later add a separate Node.js API server, update routing:

```json
"routes": [
  {
    "src": "/static/(.*)",
    "dest": "/static/$1",
    "headers": {"cache-control": "public, max-age=31536000, immutable"}
  },
  {
    "src": "/api/(.*)",
    "dest": "server/app.js"
  },
  {
    "src": "/(.*)",
    "dest": "saarthi/wsgi.py"
  }
]
```

This would:
1. Serve static files directly
2. Route `/api/*` to Node.js server
3. Route everything else to Django

**Current status:** Not implemented - all requests go to Django

---

## 🚀 Deployment Process

### Build Phase (runs once per deployment)
```
1. Vercel receives git push from GitHub
2. Executes buildCommand:
   - pip install packages
   - python manage.py migrate (creates tables in PostgreSQL)
   - python manage.py collectstatic (optimizes static files)
3. Generates build artifact with application code + staticfiles
4. Deploys to Vercel serverless functions
```

### Runtime Phase (runs on each request)
```
1. Request arrives at Vercel edge
2. Router matches route pattern (static or /(.*))
3. Invokes target:
   - Static file: Returns cached file
   - saarthi/wsgi.py: Cold starts Python/Django, then processes request
4. Django uses DATABASE_URL from environment variable
5. Response returned to client
```

---

## 📝 Important Notes

### Cold Starts
- First request after deployment takes 2-5 seconds (Python startup)
- Subsequent requests are faster (if container stays warm)
- This is normal for serverless; can be mitigated with cronjobs

### Session Storage
- Django default: In-database sessions
- Uses PostgreSQL table: `django_session`
- Benefits: Persists across restarts, shared across replicas
- Verification: Sessions stored automatically, no config needed

### Static Files
- Collected into `/staticfiles` directory
- WhiteNoise middleware serves them
- Vercel caches for 1 year
- Version hash in filename ensures cache busting

### Database Persistence
- PostgreSQL on Supabase: Persistent (won't be deleted)
- Data survives deployment restarts
- Same database used across all Vercel function invocations

---

## ✅ Pre-Deployment Verification

Before pushing to production:

```
[ ] vercel.json has buildCommand with migrations
[ ] BUILD ENVIRONMENT VARIABLES SET:
    [ ] SECRET_KEY - Generated and added to Vercel env vars
    [ ] DATABASE_URL - Supabase PostgreSQL connection string set
    [ ] GEMINI_API_KEY - Set in Vercel env vars
    [ ] DEBUG=False - Set for production
[ ] Routes correctly define:
    [ ] /static/(.*) → static files
    [ ] /(.*) → Django WSGI
[ ] Static files directory exists: static/
[ ] Django WSGI configured: saarthi/wsgi.py exists
[ ] PostgreSQL database created and running: Supabase project active
```

---

## 🔴 Common Mistakes

❌ **Forgetting DATABASE_URL** → All database queries fail, 500 errors  
✅ **Fix:** Add DATABASE_URL to Vercel env vars before deploying

❌ **Using SQLite path in DATABASE_URL** → Still fails, needs postgresql://  
✅ **Fix:** Use Supabase PostgreSQL URI from connection string

❌ **Not running migrations before deployment** → Schema doesn't exist  
✅ **Fix:** Added to buildCommand - runs automatically now

❌ **Setting DEBUG=True in production** → Exposes sensitive info  
✅ **Fix:** Set DEBUG=False in Vercel env vars

---

## 📞 Verification Commands

### Verify Supabase connection locally
```bash
export DATABASE_URL="postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres"
python manage.py dbshell
# If successful, you can type SQL commands
```

### Verify migrations would run
```bash
python manage.py migrate --noinput --plan
# Shows what would be migrated without actually running
```

### Verify static files collected
```bash
ls -la staticfiles/
# Should show CSS, JS, and other static files
```

---

**Status:** ✅ Configuration is correct for production deployment  
**Last Verified:** April 13, 2026
