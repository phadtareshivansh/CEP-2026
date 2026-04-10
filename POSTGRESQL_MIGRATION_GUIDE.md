# PostgreSQL Migration Guide for Saarthi

## Step 1: Create Free PostgreSQL Database on Supabase

1. Go to https://supabase.com
2. Click **"Start your project"** or sign in
3. Create new project:
   - **Project name:** `saarthi-prod`
   - **Database password:** Generate secure password and SAVE IT
   - **Region:** Choose closest to you (US East recommended)
4. Wait 2-3 minutes for database to initialize
5. Go to **Project Settings** → **Database**
6. Copy the connection string (looks like below):
   ```
   postgresql://postgres:[PASSWORD]@db.[RANDOM].supabase.co:5432/postgres
   ```

**CRITICAL:** Replace `[PASSWORD]` with the password you set during setup.

---

## Step 2: Create Database Dump from SQLite

Run this command locally (you have the SQLite file):

```bash
cd /Users/shivanshphadtare/Documents/Saarthi\ -\ Find\ Pathway\ to\ Your\ Interests

# Install dump tool if needed
pip install db-json-dump

# Export SQLite as SQL (creates migration-dump.sql)
sqlite3 db.sqlite3 .dump > sqlite_dump.sql
```

This creates `sqlite_dump.sql` with all your data.

---

## Step 3: Update Django Settings (DONE ✅)

Your `saarthi/settings.py` already supports `DATABASE_URL`:
```python
if os.environ.get('DATABASE_URL'):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(...)
    }
```

✅ **No code changes needed!**

---

## Step 4: Set DATABASE_URL on Vercel

1. Go to [Vercel Dashboard](https://vercel.com)
2. Project: **cep-2026-ivory**
3. Settings → **Environment Variables**
4. Add: 
   - **Name:** `DATABASE_URL`
   - **Value:** `postgresql://postgres:[YOUR_PASSWORD]@db.[RANDOM].supabase.co:5432/postgres`

---

## Step 5: Import Data to PostgreSQL

### Option A: Using psql (Recommended)

```bash
# Install PostgreSQL client (if not installed)
brew install postgresql

# Import data
psql "postgresql://postgres:[PASSWORD]@db.[RANDOM].supabase.co:5432/postgres" < sqlite_dump.sql
```

### Option B: Using DBeaver (GUI)

1. Download [DBeaver](https://dbeaver.io)
2. Create connection to Supabase PostgreSQL
3. Copy tables from SQLite to PostgreSQL

---

## Step 6: Run Migrations on Vercel

After deploying, run migrations to ensure schema is updated:

```bash
# You can add this to vercel.json buildCommand OR run after deployment:
python manage.py migrate --noinput
```

Or add to `vercel.json`:
```json
{
  "buildCommand": "pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput"
}
```

---

## Step 7: Verify Deployment

After Vercel redeploys:

1. Visit https://cep-2026-ivory.vercel.app
2. Check if no database errors appear
3. Try login (uses auth_user table)
4. Check admin panel (uses django_admin_log)

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| `permission denied` | Check PASSWORD in DATABASE_URL is correct |
| `could not connect to server` | Check Supabase firewall (allow all IPs for now) |
| `column does not exist` | Run migrations: `python manage.py migrate` |
| `relation does not exist` | Reimport SQL dump or run migrations |

---

## Environment Variables Summary

After setup, Vercel should have:

```
SECRET_KEY         ✅ Already set
DEBUG              ✅ Already set to False
ALLOWED_HOSTS      ✅ Already set
DATABASE_URL       🔄 ADD THIS (PostgreSQL connection)
GOOGLE_API_KEY     ✅ Already set
```

---

## Quick Checklist

- [ ] Create Supabase PostgreSQL database
- [ ] Copy PostgreSQL connection string
- [ ] Add DATABASE_URL to Vercel env vars
- [ ] Import SQLite data to PostgreSQL (psql or DBeaver)
- [ ] Update vercel.json with migrations command (optional)
- [ ] Trigger Vercel redeploy
- [ ] Test deployment at https://cep-2026-ivory.vercel.app

---

**After completing these steps, your Saarthi app will be fully deployed on Vercel with PostgreSQL! 🚀**
