# 🚀 Vercel Environment Variables Setup Guide

**Status:** Code pushed to GitHub ✅  
**Next Step:** Add environment variables to Vercel dashboard

---

## 📋 Your Environment Variables (Ready to Add)

### Critical Variables (Must Set Before Deploy)

| Variable | Value | Type |
|----------|-------|------|
| `SECRET_KEY` | `3XXfgnul8uwDg0icGhwXeAIy16kVEKgfBCnNLbXDvmfnJ3XD_pCcGqN3r6Isbz515LU` | Production Key ✅ |
| `DATABASE_URL` | *See Step 1 below* | Supabase Connection |
| `GEMINI_API_KEY` | *See Step 2 below* | API Key |
| `DEBUG` | `False` | Boolean |

---

## 🔐 Step 1: Get Your DATABASE_URL

1. Go to https://supabase.com/dashboard/project/gskthamwhsvqzjhhyzzz
2. Navigate: **Settings** → **Database**
3. Click: **Connection String** tab (default)
4. Select: **URI** option
5. Copy the connection string:
   ```
   postgresql://postgres:[PASSWORD]@db.gskthamwhsvqzjhhyzzz.supabase.co:5432/postgres
   ```
6. **Replace `[PASSWORD]`** with your Supabase database password
7. **Save this for Step 3**

Example (with fake values):
```
postgresql://postgres:MySecurePassword123abc@db.gskthamwhsvqzjhhyzzz.supabase.co:5432/postgres
```

---

## 🔑 Step 2: Get Your GEMINI_API_KEY

Your Gemini API key from your local `.env` file or:
1. Go to https://makersuite.google.com/app/apikey
2. Copy your existing API key
3. **Save this for Step 3**

---

## 🌐 Step 3: Add Variables to Vercel Dashboard

### 3A: Navigate to Vercel Settings

1. Open https://vercel.com/dashboard
2. Select project: **cep-2026-ivory**
3. Click **Settings** (top menu)
4. Click **Environment Variables** (left sidebar)

### 3B: Add Each Variable

Click **"Add New"** and fill in each variable below:

#### Variable 1: SECRET_KEY
```
Name:          SECRET_KEY
Value:         3XXfgnul8uwDg0icGhwXeAIy16kVEKgfBCnNLbXDvmfnJ3XD_pCcGqN3r6Isbz515LU
Environments:  ✓ Production
               ✓ Preview
               - Development (optional)
Click:         "Add"
```

#### Variable 2: DATABASE_URL
```
Name:          DATABASE_URL
Value:         postgresql://postgres:PASSWORD@db.gskthamwhsvqzjhhyzzz.supabase.co:5432/postgres
               (Replace PASSWORD with your actual password from Step 1)
Environments:  ✓ Production
               ✓ Preview
Click:         "Add"
```

#### Variable 3: GEMINI_API_KEY
```
Name:          GEMINI_API_KEY
Value:         [Your API key from Step 2]
Environments:  ✓ Production
               ✓ Preview
Click:         "Add"
```

#### Variable 4: DEBUG
```
Name:          DEBUG
Value:         False
Environments:  ✓ Production
Click:         "Add"
```

#### Variable 5: DJANGO_SETTINGS_MODULE (Optional - already in vercel.json)
```
Name:          DJANGO_SETTINGS_MODULE
Value:         saarthi.settings
Environments:  ✓ Production
               ✓ Preview
Click:         "Add"
```

---

## ⏱️ Step 4: Monitor Vercel Deployment

After adding all variables:

1. Go to **Vercel Dashboard** → **cep-2026-ivory**
2. Click **Deployments** tab
3. Watch the latest deployment

**Expected Build Output:**
```
✓ npm install (or pip install if using Python runtime)
✓ python manage.py migrate --noinput
✓ python manage.py collectstatic --noinput
✓ Build completed successfully
✓ Deployment complete
```

**Build takes:** 2-4 minutes

---

## ✅ Step 5: Test Production Deployment

Once build completes:

1. Go to https://cep-2026-ivory.vercel.app
2. **Test Sign-Up:**
   - Click "Sign Up"
   - Create test account
   - **Expected:** Success (user created in PostgreSQL)
   - **If 500 error:** Check all variables are set correctly

3. **Test Sign-In:**
   - Use credentials from sign-up
   - **Expected:** Dashboard loads
   - **If 500 error:** Check DATABASE_URL in Vercel env vars

---

## 🔴 Troubleshooting

### Build Fails: "SECRET_KEY environment variable is required"
**Fix:** Verify `SECRET_KEY` is added to Vercel (Settings → Environment Variables)

### 500 Error on Sign-In
**Check:**
1. Is `DATABASE_URL` set in Vercel env vars?
2. Does it have correct format? (Should start with `postgresql://`)
3. Is password URL-encoded if it has special characters?
4. Has Supabase database finished initializing?

**Fix:** 
- Verify DATABASE_URL, then redeploy:
  - Vercel Dashboard → Deployments → Redeploy

### Build Fails: "Migration errors"
**Check:**
1. Did migrations run locally first? (Required for schema validation)
2. Is DATABASE_URL format correct?

**Fix:**
- Test locally: `python manage.py migrate --noinput`
- Then redeploy from Vercel

### Static Files Return 404
**Status:** ✅ Should work (WhiteNoise + vercel.json configured)
- collectstatic runs automatically in build
- Verify build logs show "Collecting static files"

---

## 🎯 What Happens Next

### Automatic Process:
1. ✅ Environment variables set on Vercel
2. ✅ Vercel detects deployment (already triggered by git push)
3. ✅ Runs build command: `pip install && python manage.py migrate && collectstatic`
4. ✅ Deploys to serverless functions
5. ✅ Ready for user access

### Your Production Setup:
```
User Browser
    ↓
https://cep-2026-ivory.vercel.app
    ↓
Vercel Edge Network
    ↓
Django WSGI Application
    ↓
PostgreSQL (Supabase)
    ↓
Response back to user
```

---

## 📞 Reference

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Supabase Dashboard:** https://supabase.com/dashboard
- **Full Guide:** [DEPLOYMENT_READY.md](DEPLOYMENT_READY.md)
- **Environment Variables Reference:** [VERCEL_ENV_VARIABLES_QUICK_REFERENCE.md](VERCEL_ENV_VARIABLES_QUICK_REFERENCE.md)

---

## ✨ Summary

✅ Code pushed to GitHub  
⏳ Waiting for: Environment variables added to Vercel dashboard  
🚀 Result: Automatic deployment + live production site

**Estimated time to complete:** ~10 minutes (just adding variables via dashboard)

---

**Status:** Ready for Dashboard Setup ✅
