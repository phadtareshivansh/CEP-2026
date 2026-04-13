# Saarthi: Production Deployment to Vercel - Complete Step-by-Step Guide

**Status Date:** April 13, 2026  
**Target Deployment:** cep-2026-ivory.vercel.app  
**Database:** Supabase PostgreSQL (replaces SQLite)

---

## 🎯 Overview

This guide walks through deploying Saarthi to production on Vercel with a serverless PostgreSQL database. The deployment fixes the **500 sign-in error** caused by Vercel's ephemeral filesystem by migrating from SQLite to PostgreSQL.

---

## Phase 1: Set Up Remote PostgreSQL Database

### ✅ Step 1.1: Create Supabase Project

1. Go to **https://supabase.com**
2. Sign up or log in
3. Click **"New Project"**
4. Configure:
   - **Project name:** `saarthi-prod` (or your preference)
   - **Password:** Generate a strong password (20+ characters)
     - **⚠️ SAVE THIS PASSWORD - You'll need it for the connection string**
   - **Region:** Select closest region (e.g., US East 1 for US)
   - **Pricing plan:** Free tier (sufficient for development)
5. Click **"Create new project"**
6. **Wait 2-3 minutes** for the database to initialize

### ✅ Step 1.2: Retrieve PostgreSQL Connection String

1. In Supabase dashboard, go to **Settings** → **Database**
2. Under **Connection String**, select **"URI"** (not PSQL)
3. Copy the connection string - it looks like:
   ```
   postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
4. **Replace `[PASSWORD]`** with the password you set in Step 1.1
5. Save this string safely - you'll need it multiple times:
   - `DATABASE_URL` in step 2 (environment variables)
   - Local `.env` for migrations in step 3

**Example (with fake values):**
```
postgresql://postgres:MySecurePassword123@db.abc12345.supabase.co:5432/postgres
```

---

## Phase 2: Configure Vercel Environment Variables

### ✅ Step 2.1: Generate Production SECRET_KEY

Run this command locally to generate a secure key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

**Output example:**
```
o7hL9kM2vN1pQ3rS5tU7wX9yZ0aB2cD4eF6gH8iJ0kL2mN4oP6qR8sT0uV2wX4yZ
```

**⚠️ Save this key - you'll add it to Vercel**

### ✅ Step 2.2: Add Environment Variables to Vercel

1. Go to **[Vercel Dashboard](https://vercel.com)**
2. Select project: **cep-2026-ivory**
3. Click **Settings** → **Environment Variables**
4. Add 4 critical variables:

#### Variable 1: SECRET_KEY
- **Name:** `SECRET_KEY`
- **Value:** [Paste the key from Step 2.1]
- **Environments:** Select all (Production, Preview, Development)
- Click **"Save"**

#### Variable 2: DATABASE_URL
- **Name:** `DATABASE_URL`
- **Value:** [Paste your Supabase connection string from Step 1.2]
- **Environments:** Production only (or all if using for preview too)
- Click **"Save"**

#### Variable 3: GEMINI_API_KEY
- **Name:** `GEMINI_API_KEY`
- **Value:** [Your existing Gemini API key - find in local .env]
- **Environments:** Production, Preview
- Click **"Save"**

#### Variable 4: DEBUG
- **Name:** `DEBUG`
- **Value:** `False`
- **Environments:** Production
- Click **"Save"**

**✅ Verification:** You should now see at least 4 environment variables in the Vercel dashboard.

---

## Phase 3: Run Production Migrations

### ✅ Step 3.1: Update Local .env for Remote Database Migration

This step temporarily points your local Django to the remote Supabase database so you can run migrations.

1. Open (or create) a `.env` file in the project root:
   ```bash
   cd /Users/shivanshphadtare/Documents/Saarthi\ -\ Find\ Pathway\ to\ Your\ Interests
   # If .env doesn't exist, create it
   touch .env
   ```

2. Add/update this line with your Supabase connection string:
   ```
   DATABASE_URL=postgresql://postgres:YourPassword@db.xxxxx.supabase.co:5432/postgres
   ```
   
   **Replace with your actual values from Step 1.2**

3. Verify other settings in `.env`:
   ```
   DEBUG=False
   SECRET_KEY=o7hL9kM2vN1pQ3rS5tU7wX9yZ0aB2cD4eF6gH8iJ0kL2mN4oP6qR8sT0uV2wX4yZ
   GEMINI_API_KEY=your_actual_gemini_key
   DJANGO_SETTINGS_MODULE=saarthi.settings
   ```

### ✅ Step 3.2: Run Django Migrations on Remote Database

Run this command from your project root:

```bash
python manage.py migrate --noinput
```

**Expected output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, messages, staticfiles, quiz, forum
Running migrations:
  Applying auth.0001_initial... OK
  Applying auth.0002_alter_user_add_last_login_null... OK
  ... (more migrations) ...
  Applying quiz.0003_forumpost_close_reason... OK
```

**If you see errors:**
- Check that DATABASE_URL is set correctly in .env
- Verify Supabase database is initialized (took 2-3 min)
- Ensure your local machine can reach Supabase (usually fine)

### ✅ Step 3.3: (Optional) Import Existing Data from SQLite

If you want to preserve data from your local SQLite database:

```bash
# Export SQLite data
sqlite3 db.sqlite3 .dump > sqlite_data.sql

# Import to Postgres (requires psql installed)
psql "postgresql://postgres:YourPassword@db.xxxxx.supabase.co:5432/postgres" < sqlite_data.sql
```

**Notes:**
- This is optional for fresh deployments
- Only needed if you have important test data to preserve
- Migrations alone create empty tables (sufficient to start)

---

## Phase 4: Deploy to Vercel

### ✅ Step 4.1: Verify Git Repository

1. Ensure your code is committed:
   ```bash
   cd /Users/shivanshphadtare/Documents/Saarthi\ -\ Find\ Pathway\ to\ Your\ Interests
   git status
   ```

2. Push latest changes:
   ```bash
   git add vercel.json
   git commit -m "feat: update vercel.json with production migrations"
   git push
   ```

### ✅ Step 4.2: Trigger Deployment

**Option A: Automatic (Recommended)**
- Vercel auto-deploys on `git push` if connected to GitHub

**Option B: Manual**
1. Go to **Vercel Dashboard** → **cep-2026-ivory**
2. Click **"Deployments"** tab
3. Click **"Redeploy"** on the latest deployment

### ✅ Step 4.3: Monitor Build

1. Watch the deployment log in real-time
2. **Build command runs:** `pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput`
3. **Expected duration:** 2-4 minutes
4. You should see:
   ```
   ✓ Build completed
   ✓ Deployment complete
   ```

**If build fails:**
- Check build logs for error messages
- Common issues:
  - Missing `DATABASE_URL` → Add to environment variables
  - Database connection timeout → Verify Supabase is accessible
  - Migration errors → Re-run `python manage.py migrate` locally first

---

## Phase 5: Test Production Deployment

### ✅ Step 5.1: Test Sign-Up/Sign-In

1. Go to **https://cep-2026-ivory.vercel.app**
2. Test user creation: Go to **Sign Up**
   - Create test account with email + password
   - **Expected:** User created successfully
   - **If 500 error:** Check Vercel build logs for DATABASE_URL issues

3. Test login: Go to **Login** with the account you just created
   - **Expected:** Login successful, dashboard loads
   - **If 500 error:** Database write not working - verify DATABASE_URL in Vercel env vars

### ✅ Step 5.2: Test Career Pathway

1. After logging in, test career assessment flow:
   - Go to **"Add Skills"** or **"Assessment"**
   - Complete skill selection
   - **Expected:** Results display correctly from PostgreSQL

### ✅ Step 5.3: Test API Endpoints

1. Test a dashboard query:
   ```bash
   curl "https://cep-2026-ivory.vercel.app/dashboard/" \
     -H "Cookie: sessionid=YOUR_SESSION_ID"
   ```

---

## Phase 6: Post-Deployment Configuration

### ✅ Step 6.1: Update ALLOWED_HOSTS (if needed)

If you add a custom domain, update in `saarthi/settings.py`:

```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'cep-2026-ivory.vercel.app', 'yourdomain.com']
```

Then deploy:
```bash
git push  # Auto-deploys on Vercel
```

### ✅ Step 6.2: Review vercel.json Routes

Your routes in `vercel.json` are configured to:
- Serve static files from `/static/` with cache headers (1 year)
- Route all other requests to Django WSGI application

**Current configuration (correct for Django-only setup):**
```json
"routes": [
  {
    "src": "/static/(.*)",
    "dest": "/static/$1",
    "headers": {"cache-control": "public, max-age=31536000, immutable"}
  },
  {
    "src": "/(.*)",
    "dest": "saarthi/wsgi.py"
  }
]
```

**✅ This is correct.** No changes needed unless you add Node.js routes.

### ✅ Step 6.3: Set Up Monitoring (Optional)

1. Enable **Function Logs** in Vercel dashboard
2. Monitor for 500 errors after deployment
3. Check error patterns if users report issues

---

## 🔴 Troubleshooting Guide

### Issue: 500 Error on Sign-In After Deployment

**Root cause:** DATABASE_URL not set or connection failed  
**Fix:**
1. Verify `DATABASE_URL` in Vercel Environment Variables
2. Check it has the correct format: `postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres`
3. Verify password is URL-encoded if it contains special characters
4. Redeploy: Go to Vercel Dashboard → Deployments → Redeploy

### Issue: Build Fails with "migrate: command not found"

**Root cause:** Django migrations script not in PATH  
**Fix:** Vercel uses `python manage.py` which requires Django installed. This is installed via `pip install -r requirements.txt`, so if it fails:
1. Check `requirements.txt` includes Django
2. Verify python/pip paths in build logs

### Issue: Static Files Return 404

**Root cause:** collectstatic not running or S3 not configured  
**Fix:**
- collectstatic runs in `vercel.json` build command ✅ Already configured
- Files stored in `/staticfiles` which WhiteNoise serves
- **No S3 setup needed** for small deployments

### Issue: Database Migrations Pending After Deployment

**Root cause:** Migrations not run yet or `.env` from local leaked into Vercel  
**Fix:**
1. Force redeploy:
   ```bash
   git commit --allow-empty -m "trigger redeploy"
   git push
   ```
2. Or manual deployment from Vercel dashboard
3. Watch logs to confirm migrations complete

---

## ✅ Deployment Checklist (Copy & Paste)

Use this checklist to verify all steps are complete:

```
PHASE 1: PostgreSQL Setup
[ ] Created Supabase project
[ ] Retrieved PostgreSQL connection string
[ ] Saved connection string securely

PHASE 2: Vercel Environment Variables
[ ] Generated production SECRET_KEY
[ ] Added SECRET_KEY to Vercel env vars (Production)
[ ] Added DATABASE_URL to Vercel env vars (Production)
[ ] Added GEMINI_API_KEY to Vercel env vars
[ ] Added DEBUG=False to Vercel env vars (Production)

PHASE 3: Local Migration Testing
[ ] Updated local .env with DATABASE_URL
[ ] Ran: python manage.py migrate --noinput
[ ] Confirmed all migrations applied successfully

PHASE 4: Deploy
[ ] Committed vercel.json changes
[ ] Pushed to GitHub (auto-triggers Vercel deploy)
[ ] Monitored Vercel build logs
[ ] Build completed successfully

PHASE 5: Testing
[ ] Tested sign-up at https://cep-2026-ivory.vercel.app
[ ] Tested sign-in
[ ] Tested career assessment flow
[ ] No 500 errors

COMPLETE: Production deployment is live! 🎉
```

---

## 📞 Support

If you encounter issues:

1. **Check Vercel build logs** → Settings → Deployments
2. **Verify environment variables** are visible in Vercel Settings
3. **Test locally first** → Run migrations locally before deploying
4. **Check database connectivity** → Ensure Supabase is running

---

**Last Updated:** April 13, 2026  
**Next Review:** After first production sign-in test
