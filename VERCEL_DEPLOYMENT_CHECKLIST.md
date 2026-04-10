# Vercel Deployment Diagnostic Report & Checklist

**Date:** April 10, 2026  
**Status:** ⚠️ CRITICAL ENVIRONMENT VARIABLES MISSING

---

## 🔴 CRITICAL ISSUES (Must Fix Before Deployment)

### Issue #1: SECRET_KEY Not Set on Vercel
**Severity:** 🔴 CRITICAL - App will crash on startup  
**Location:** `saarthi/settings.py` line 30-36  
**Problem:**
```python
if not DEBUG:
    # DEBUG=False on Vercel
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Returns None
    if not SECRET_KEY:
        raise ValueError('SECRET_KEY environment variable is required for production')
        # ↑ THIS RAISES AND CRASHES THE APP
```

**Solution:**
1. Go to [Vercel Dashboard](https://vercel.com)
2. Select project: **cep-2026-ivory**
3. Click **Settings** → **Environment Variables**
4. Add new variable:
   - **Name:** `SECRET_KEY`
   - **Value:** Generate a secure 50+ character key using:
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(50))"
     ```
   - Example: `o7hL9kM2vN1pQ3rS5tU7wX9yZ0aB2cD4eF6gH8iJ0kL2mN4oP6qR8sT0uV2wX4yZ`

**Status:** ❌ NOT SET

---

### Issue #2: DATABASE_URL Not Set on Vercel
**Severity:** 🔴 CRITICAL - Database queries will fail  
**Location:** `saarthi/settings.py` line 82-92  
**Problem:**
```python
if os.environ.get('DATABASE_URL'):
    # This is None on Vercel, so falls back to SQLite:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # ← Won't persist on Vercel!
        }
    }
```

Vercel has a **read-only filesystem**. SQLite database won't persist between deployments!

**Solution:**
1. Create PostgreSQL database using one of:
   - [Supabase](https://supabase.com) (Recommended - free tier)
   - [Neon](https://neon.tech) (Serverless PostgreSQL)
   - [Railway](https://railway.app)

2. Get connection string in format:
   ```
   postgresql://user:password@host:port/database_name
   ```

3. Go to Vercel Dashboard → Environment Variables
4. Add new variable:
   - **Name:** `DATABASE_URL`
   - **Value:** `postgresql://user:password@host:port/database_name`

**Status:** ❌ NOT SET

---

### Issue #3: DEBUG Not Set Correctly on Vercel
**Severity:** 🟡 MEDIUM - Causes security & performance issues  
**Problem:** `vercel.json` sets `DEBUG: "False"` as string, but also ALLOWED_HOSTS shows development values in error pages

**Solution:**
1. Go to Vercel Environment Variables
2. Add:
   - **Name:** `DEBUG`
   - **Value:** `False`

**Status:** ⚠️ PARTIALLY SET

---

## 🟡 MEDIUM PRIORITY ISSUES

### Issue #4: ALLOWED_HOSTS Needs Update
**Status:** Current: `['localhost', '127.0.0.1', 'cep-2026-ivory.vercel.app']`

These are hardcoded in code. For production, consider using environment variable or verify WSGI wrapper is working.

**Vercel WSGI Wrapper Status:** ✅ Implemented in `saarthi/wsgi.py`  
The `VercelWsgiWrapper` class dynamically allows `*.vercel.app` domains.

---

### Issue #5: Static Files Configuration
**Status:** ✅ Configured  
- WhiteNoise middleware: ✅ Added
- Static storage: ✅ CompressedManifestStaticFilesStorage
- Build command: ✅ Includes `collectstatic --noinput`

---

## ✅ VERIFIED - NO ISSUES

### File Name Case Sensitivity
**Status:** ✅ All Python files use lowercase  
- quiz/models.py ✅
- quiz/views.py ✅
- quiz/urls.py ✅
- quiz/middleware.py ✅
- saarthi/wsgi.py ✅
- saarthi/settings.py ✅

### Import Statements
**Status:** ✅ All imports match file names exactly  
- No case mismatches found
- All relative imports correct

### Dependencies
**Status:** ✅ All required packages in requirements.txt:
- Django==4.2.0 ✅
- whitenoise==6.6.0 ✅
- dj-database-url==2.1.0 ✅
- psycopg2-binary==2.9.9 ✅
- gunicorn==21.2.0 ✅

### WSGI Configuration
**Status:** ✅ Ready:
- Runtime: `python@3.11` ✅ (correct format)
- Entry point: `saarthi/wsgi.py` → `app` ✅
- VercelWsgiWrapper implemented ✅

### Middleware Stack
**Status:** ✅ Correct order:
1. SecurityMiddleware ✅
2. WhiteNoiseMiddleware ✅
3. CorsMiddleware ✅
4. CommonMiddleware ✅
5. SessionMiddleware ✅
6. AuthenticationMiddleware ✅
7. MessagesMiddleware ✅
8. XFrameOptionsMiddleware ✅
9. SessionTimeoutMiddleware ✅

---

## 🚀 DEPLOYMENT Steps

### Step 1: Set Environment Variables ⚠️ YOU ARE HERE
```bash
# On Vercel Dashboard:
SECRET_KEY = <generate secure key>
DATABASE_URL = postgresql://...
DEBUG = False
```

### Step 2: Create & Setup PostgreSQL Database
- Choose provider (Supabase/Neon/Railway)
- Create new database
- Get connection string
- Add to Vercel env vars

### Step 3: Trigger Deployment
- Push any commit to GitHub
- Vercel automatically redeploys
- Monitor build logs (Settings → Deployments)

### Step 4: Run Initial Migrations
Once site is live:
```bash
python manage.py migrate
python manage.py createsuperuser
```

Or use management command in Vercel Functions (advanced).

### Step 5: Verify Site
- Visit https://cep-2026-ivory.vercel.app
- Test login
- Check static files (CSS/images loading)
- Check database queries working

---

## 🔍 How to Monitor Vercel Logs

**Build Logs (Errors during deployment):**
1. Go to Vercel Dashboard
2. Select project: cep-2026-ivory
3. Click Deployments tab
4. Click latest deployment
5. Expand "Building" section
6. Search for: `ERROR`, `FAILED`, `Exited with 1`

**Runtime Logs (Errors after deployment):**
1. Dashboard → Project
2. Click "Functions" tab
3. Click "Logs"
4. Filter by timestamp
5. Search for: `ERROR`, `EXCEPTION`, `Traceback`

---

## ✅ Verification Checklist

Complete before deployment:

- [ ] `SECRET_KEY` set in Vercel env vars
- [ ] `DATABASE_URL` set in Vercel env vars
- [ ] `DEBUG` set to `False` in Vercel env vars
- [ ] PostgreSQL database created & working
- [ ] `.env.local` has matching variables (for local testing)
- [ ] Latest commits pushed to GitHub
- [ ] No syntax errors in Python files
- [ ] vercel.json is valid JSON
- [ ] requirements.txt has all dependencies

---

## 🎯 Expected Outcome After Fix

✅ Vercel build succeeds  
✅ No "DisallowedHost" errors  
✅ No "SECRET_KEY not set" crashes  
✅ Site loads at https://cep-2026-ivory.vercel.app  
✅ Database queries work without errors  
✅ Static files (CSS/images) load correctly  
✅ Authentication (login/signup) works  

---

## 📞 Common Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `SECRET_KEY environment variable is required` | SECRET_KEY not on Vercel | Set in Environment Variables |
| `DISALLOWED_HOST` | Domain not in ALLOWED_HOSTS | Already fixed with WSGI wrapper |
| `operator error: FATAL: password authentication failed` | DATABASE_URL invalid | Check PostgreSQL credentials |
| `No route to host` | DATABASE_URL unreachable | Check PostgreSQL firewall settings |
| `ModuleNotFoundError: No module named 'xyz'` | Missing dependency | Check requirements.txt |

---

**Last Updated:** April 10, 2026  
**Next Step:** Set environment variables on Vercel dashboard
