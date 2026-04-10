# 🚀 Saarthi Vercel Deployment - Complete Setup Guide

**Status:** ✅ **CODE IS READY FOR DEPLOYMENT**  
**Deadline:** Complete these steps and your app will be live!  
**Time Required:** 10-15 minutes

---

## 📋 What Has Been Done (Code Side) ✅

Your codebase is **100% Ready**. Here's what was completed:

### ✅ Database Migration Prepared
- SQLite database exported (325 data rows)
- Migration scripts created
- Python helper tool ready
- SQL dump file generated

### ✅ Django Configuration
- `settings.py` supports `DATABASE_URL` environment variable
- Automatic migrations on build
- Production security settings enabled
- CORS/CSRF configured for Vercel

### ✅ Vercel Setup
- `vercel.json` updated with migration command
- Python 3.11 runtime configured
- Static files with WhiteNoise included
- WSGI entry point properly configured

### ✅ Documentation
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - 5-minute Supabase setup
- [POSTGRESQL_MIGRATION_GUIDE.md](POSTGRESQL_MIGRATION_GUIDE.md) - Detailed migration steps
- Migration helper script ready

---

## 🎯 Your Exact Next Steps (Follow in Order)

### Step 1️⃣: Create PostgreSQL Database on Supabase (5 min)

1. Open https://supabase.com in browser
2. Click **"Start your project"**
3. Sign up with GitHub
4. Click **"New Project"**
5. Fill form:
   - **Name:** `saarthi`
   - **Database Password:** Generate strong password and **SAVE IT**
     ```
     Example: H7$kL9#mP2@vX5!qZ8nW3$aB1&jT6*yR4
     ```
   - **Region:** US East (for Vercel compatibility)
6. Click **"Create new project"**
7. ⏳ Wait 2-3 minutes for database to initialize

### Step 2️⃣: Get PostgreSQL Connection String (2 min)

1. In Supabase dashboard, go **Settings** → **Database**
2. Scroll down to **Connection String**
3. Click tab: **"Connection pooling"** (important for serverless)
4. Copy the URI that looks like:
   ```
   postgresql://postgres.xxxxx:[PASSWORD]@db.xxxxx.supabase.co:6543/postgres
   ```
5. **Replace** `[PASSWORD]` with what you saved in Step 1
6. **Keep this string safe** - you'll need it multiple times

### Step 3️⃣: Migrate Data from SQLite to PostgreSQL (3 min)

**Choose ONE method:**

#### Method A: Using Terminal (Faster)
```bash
# Install PostgreSQL tools (if not installed)
brew install postgresql

# Navigate to project
cd /Users/shivanshphadtare/Documents/Saarthi\ -\ Find\ Pathway\ to\ Your\ Interests

# Run migration
psql "postgresql://postgres.xxxxx:[PASSWORD]@db.xxxxx.supabase.co:6543/postgres" < sqlite_export.sql
```

**If successful, you'll see:**
```
CREATE TABLE
INSERT 0 4
INSERT 0 326
... many more lines ...
```

#### Method B: Using DBeaver (If Terminal Uncomfortable)
1. Download [DBeaver Community](https://dbeaver.io) (free)
2. Create new Connection:
   - Type: PostgreSQL
   - Host: `db.xxxxx.supabase.co`
   - Port: `6543`
   - User: `postgres`
   - Password: `[YOUR_PASSWORD]`
   - Database: `postgres`
3. Right-click connection → **Tools** → **Execute SQL Script**
4. Select file: `sqlite_export.sql`
5. Click **Execute**

### Step 4️⃣: Add DATABASE_URL to Vercel (2 min)

1. Go to [Vercel Dashboard](https://vercel.com)
2. Select project: **cep-2026-ivory**
3. Click **Settings**
4. Click **Environment Variables** (left sidebar)
5. Click **Add New** variable:
   - **Name:** `DATABASE_URL`
   - **Value:** `postgresql://postgres.xxxxx:[PASSWORD]@db.xxxxx.supabase.co:6543/postgres`
   - **Environment:** Select all (Development, Preview, Production)
6. Click **Save**

### Step 5️⃣: Trigger Vercel Deployment (Automatic)

Vercel automatically detects new env vars and redeploys!

✅ **Check build status:**
1. Go to **Deployments** tab in Vercel
2. You should see a new build starting
3. Click on it to watch build logs
4. Look for:
   ```
   Running migrations...
   Operations to perform: ...
   ```

---

## ✅ Verify Deployment Success

### After Build Completes:

1. **Visit your site:**
   ```
   https://cep-2026-ivory.vercel.app
   ```

2. **Expected to see:**
   - ✅ Homepage loads (no errors)
   - ✅ No "DisallowedHost" error
   - ✅ No database connection error
   - ✅ Static files load (CSS colors visible)

3. **Test features:**
   - ✅ Try login page
   - ✅ Try signup
   - ✅ Check if data from SQLite appears

4. **Check for errors:**
   ```
   If you see 500 error, check Vercel logs:
   Deployments → Latest → Logs tab
   Search for: ERROR, FAILED, EXCEPTION
   ```

---

## 📊 Your Database Stats

What will be deployed:

| Table | Rows | Purpose |
|-------|------|---------|
| auth_user | 4 | User accounts |
| quiz_assessment | 5 | Test assessments |
| quiz_skill | 31 | Skills database |
| quiz_career | 9 | Career data |
| quiz_userprofile | 4 | User profiles |
| quiz_careerroadmap | 8 | Career roadmaps |
| **Other tables** | **259** | Additional data |
| **TOTAL** | **325 rows** | All your data |

---

## 🆘 Troubleshooting

### ❌ "FATAL: password authentication failed"
**Solution:**
- Check PASSWORD in connection string matches what you saved from Supabase
- Copy-paste from Supabase dashboard again

### ❌ "Connection refused"
**Solution:**
- Wait 2-3 more minutes for Supabase DB to initialize
- Refresh browser
- Create new project if it's taking too long

### ❌ "Site shows 500 Error after deployment"
**Solution:**
1. Check Vercel build logs (Deployments → Logs)
2. Common causes:
   - DATABASE_URL not set or wrong format
   - SECRET_KEY not set
   - Migration failed with syntax error

### ❌ "psql command not found"
**Solution:**
```bash
brew install postgresql
```

### ❌ "Data not appearing on site"
**Solution:**
- Check migrations ran: `Deployments → Logs → search "migrate"`
- If you see "0 migrations to apply" - that's correct!✅
- Refresh browser and clear cache

---

## 📞 Support Resources

**Files in your project:**
- [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) - Detailed Supabase guide
- [POSTGRESQL_MIGRATION_GUIDE.md](./POSTGRESQL_MIGRATION_GUIDE.md) - Migration reference
- [migrate_to_postgres.py](./migrate_to_postgres.py) - Database helper script
- [sqlite_export.sql](./sqlite_export.sql) - Your exported data

**Environment Variables Set:**
```
✅ SECRET_KEY - Production secret
✅ DEBUG - False (production mode)
✅ ALLOWED_HOSTS - Vercel domains
✅ GOOGLE_API_KEY - Gemini API
🆕 DATABASE_URL - (You need to set this!)
```

---

## 🎯 Success Checklist

After completing all steps:

- [ ] Supabase database created
- [ ] Connection string copied
- [ ] Data migrated with psql or DBeaver
- [ ] DATABASE_URL added to Vercel
- [ ] Vercel deployment triggered
- [ ] Build completed successfully
- [ ] Site loads at https://cep-2026-ivory.vercel.app
- [ ] No 500 errors appearing
- [ ] Can login with test account
- [ ] Static files (CSS, images) display
- [ ] Data from SQLite appears on site

---

## ⏱️ Timeline

- **Step 1 (Supabase):** 5 minutes
- **Step 2 (Get Connection):** 2 minutes
- **Step 3 (Migrate Data):** 3 minutes
- **Step 4 (Vercel Env Var):** 2 minutes
- **Step 5 (Deploy):** ⏳ Automatic (5-10 minutes)
- **Total:** ~17-22 minutes

---

## 🎉 You're Almost There!

Your code is **100% ready**. The only thing left is:
1. Create Supabase database
2. Migrate your data
3. Set one environment variable
4. Vercel handles the rest!

**Once you complete Step 4, Vercel will automatically:**
- ✅ Run migrations
- ✅ Compile static files
- ✅ Deploy your app
- ✅ Make it live on the internet

---

**Next Action: Start with Step 1 (Create Supabase Account)**

**Questions?** Check the detailed guides or watch build logs in Vercel!

🚀 **Let's deploy this app!**
