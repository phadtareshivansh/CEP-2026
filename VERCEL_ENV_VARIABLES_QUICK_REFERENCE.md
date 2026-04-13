# Vercel Environment Variables Quick Reference

**Updated:** April 13, 2026  
**Purpose:** Quick checklist of all environment variables needed for production deployment

---

## 🔴 CRITICAL VARIABLES (Must set before deploying)

### 1. SECRET_KEY (Django)
- **Where to get:** Run locally:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(50))"
  ```
- **Where to set:** Vercel Dashboard → Settings → Environment Variables
- **Environments:** Production, Preview, Development (all)
- **Example value:** `o7hL9kM2vN1pQ3rS5tU7wX9yZ0aB2cD4eF6gH8iJ0kL2mN4oP6qR8sT0uV2wX4yZ`
- **Why:** Django crashes on startup if missing
- **Status in your app:** ❌ NOT SET (will cause deployment to fail)

### 2. DATABASE_URL (PostgreSQL)
- **Where to get:** Supabase dashboard (Settings → Database → Connection String)
- **Where to set:** Vercel Dashboard → Settings → Environment Variables
- **Environments:** Production (at minimum)
- **Format:** `postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres`
- **Example:**
  ```
  postgresql://postgres:MySecure123Password@db.abc12345.supabase.co:5432/postgres
  ```
- **Why:** ❗ CRITICAL - Without this, all database writes fail (sign-in, user creation fails)
- **Note:** Replace `[PASSWORD]` with your actual Supabase password
- **Status in your app:** ❌ NOT SET (causes 500 errors on sign-in)

### 3. GEMINI_API_KEY (AI Career Pathway)
- **Where to get:** https://makersuite.google.com/app/apikey
- **Where to set:** Vercel Dashboard → Settings → Environment Variables
- **Environments:** Production, Preview
- **Example:** `AIzaSyD7wXX_XX...` (long alphanumeric string)
- **Why:** Enables AI-powered career pathway generation
- **Status in your app:** ❌ NOT SET (will fall back to mock data)

---

## 🟡 HIGH PRIORITY VARIABLES

### 4. DEBUG (Django)
- **Where to get:** Fixed value: `False`
- **Where to set:** Vercel Dashboard → Settings → Environment Variables
- **Environments:** Production
- **Why:** Security - hides sensitive debug info in error pages
- **Status in your app:** ⚠️ Set in vercel.json but should also be in env vars

### 5. DJANGO_SETTINGS_MODULE
- **Where to get:** Fixed value: `saarthi.settings`
- **Where to set:** Vercel Dashboard → Settings → Environment Variables
- **Environments:** All
- **Why:** Tells Django which settings module to use
- **Status in your app:** ✅ SET in vercel.json

---

## 📋 Vercel Dashboard Setup Instructions

### Step 1: Open Environment Variables
1. Go to https://vercel.com
2. Select project: **cep-2026-ivory**
3. Click **Settings** (top menu)
4. Click **Environment Variables** (left sidebar)

### Step 2: Add Each Variable

For each variable below, click **"Add New"** and fill in:
- **Name:** (exactly as shown)
- **Value:** (your actual value)
- **Environments:** Select checkboxes

#### Add: SECRET_KEY
```
Name:          SECRET_KEY
Value:         [Output from: python -c "import secrets; print(secrets.token_urlsafe(50))"]
Environments:  ✓ Production
               ✓ Preview
               - Development (optional)
Click:         "Add"
```

#### Add: DATABASE_URL
```
Name:          DATABASE_URL
Value:         postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
Environments:  ✓ Production
               ✓ Preview (if you want preview deployments to use same DB)
Click:         "Add"
```

#### Add: GEMINI_API_KEY
```
Name:          GEMINI_API_KEY
Value:         [Your API key from makersuite.google.com]
Environments:  ✓ Production
               ✓ Preview
               - Development
Click:         "Add"
```

#### Add: DEBUG (if not set properly)
```
Name:          DEBUG
Value:         False
Environments:  ✓ Production
Click:         "Add"
```

### Step 3: Verify All Variables
1. You should see at least 4 variables listed
2. Verify values are correct (don't edit inline - delete and re-add if wrong)
3. Click **"Save"**

---

## 🔐 Security Checklist

Before deploying:
- [ ] SECRET_KEY is unique and 50+ characters
- [ ] DATABASE_URL has correct password with special characters properly formatted
- [ ] API keys are not shared in version control
- [ ] DEBUG is False for production
- [ ] ALLOWED_HOSTS includes your Vercel domain

---

## ⚡ Quick Deployment Checklist

```
Before pushing to production:

1. Locally generate SECRET_KEY: python -c "import secrets; print(secrets.token_urlsafe(50))"
2. Get DATABASE_URL from Supabase (Settings → Database → Connection String → URI)
3. Open Vercel Dashboard → cep-2026-ivory → Settings → Environment Variables
4. Add: SECRET_KEY (Production + Preview)
5. Add: DATABASE_URL (Production + Preview)
6. Add: GEMINI_API_KEY (Production + Preview)
7. Commit changes to git
8. Push to GitHub
9. Vercel auto-deploys
10. Check build logs (should see: "✓ Deployment complete")
11. Test sign-up/sign-in at https://cep-2026-ivory.vercel.app
12. If 500 error: Check all env vars are set correctly, verify database exists

DEPLOYMENT COMPLETE ✅
```

---

## 🔧 Troubleshooting

### Deployment Fails: "SECRET_KEY environment variable is required"
**Fix:** Add SECRET_KEY to Vercel Environment Variables (Production)

### 500 Error on sign-in after deployment
**Fix:** Check DATABASE_URL is set correctly in Vercel Environment Variables

### Build succeeds but queries timeout
**Fix:** Verify DATABASE_URL format and that Supabase database is running

### API calls return "403 Forbidden"
**Fix:** Add GEMINI_API_KEY to Vercel Environment Variables

---

## 📞 Reference Docs

- [Django Settings](../saarthi/settings.py)
- [Full Deployment Guide](VERCEL_PRODUCTION_DEPLOYMENT_STEPS.md)
- [PostgreSQL Migration Guide](POSTGRESQL_MIGRATION_GUIDE.md)
- [Vercel Docs](https://vercel.com/docs)
- [Supabase Docs](https://supabase.com/docs)

---

**Last Updated:** April 13, 2026
