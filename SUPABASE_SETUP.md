# Supabase PostgreSQL Setup Guide for Saarthi

## Quick Setup (5 minutes)

### Step 1: Create Supabase Account
1. Go to https://supabase.com
2. Click **"Start your project"**
3. Sign up with GitHub or email

### Step 2: Create PostgreSQL Database
1. Click **"New Project"**
2. Fill in:
   - **Project name:** `saarthi`
   - **Database password:** Generate strong password
     - Example: `H7$kL9#mP2@vX5!qZ8nW3$aB1&jT6*yR4`
     - **SAVE THIS PASSWORD SOMEWHERE SAFE**
   - **Region:** Choose closest to you
     - US East (recommended for Vercel)
4. Click **"Create new project"**
5. Wait 2-3 minutes for database to initialize

### Step 3: Get PostgreSQL Connection String

1. In Supabase dashboard, go to **Settings** → **Database**
2. Scroll to **Connection string** section
3. Click tab: **"Connection pooling"** (recommended for serverless)
4. Copy the URI shown (looks like this):
   ```
   postgresql://postgres.xxxxx:[YOUR_PASSWORD]@db.xxxxx.supabase.co:6543/postgres
   ```

5. **IMPORTANT:** Replace `[YOUR_PASSWORD]` with the password you created in Step 2

### Step 4: Test Connection Locally

```bash
cd /Users/shivanshphadtare/Documents/Saarthi\ -\ Find\ Pathway\ to\ Your\ Interests

# Copy connection string (from above)
export DATABASE_URL="postgresql://postgres.xxxxx:[PASSWORD]@db.xxxxx.supabase.co:6543/postgres"

# Test connection
python migrate_to_postgres.py "$DATABASE_URL"
```

### Step 5: Migrate Data from SQLite to PostgreSQL

#### Option A: Using psql Command (Easiest)

```bash
# If you don't have psql installed:
brew install postgresql

# Migrate data:
psql "postgresql://postgres.xxxxx:[PASSWORD]@db.xxxxx.supabase.co:6543/postgres" < sqlite_export.sql
```

#### Option B: Using DBeaver (GUI - No Terminal)

1. Download [DBeaver Community](https://dbeaver.io) (free)
2. Create new PostgreSQL connection:
   - Host: `db.xxxxx.supabase.co`
   - Port: `6543`
   - Database: `postgres`
   - Username: `postgres`
   - Password: `[YOUR_PASSWORD]`
3. Right-click connection → **Tools** → **Execute SQL Script**
4. Select `sqlite_export.sql`
5. Click **Execute**

### Step 6: Add to Vercel Environment Variables

1. Go to [Vercel Dashboard](https://vercel.com)
2. Select project: **cep-2026-ivory**
3. **Settings** → **Environment Variables**
4. Add new variable:
   - **Name:** `DATABASE_URL`
   - **Value:** `postgresql://postgres.xxxxx:[PASSWORD]@db.xxxxx.supabase.co:6543/postgres`
   - **Environment:** All (Development, Preview, Production)
5. Click **Save**

### Step 7: Deploy to Vercel

1. Go back to **Deployments** tab
2. Click **Redeploy** on latest deployment
3. Watch build logs to ensure migrations run
4. Once deployed, test at https://cep-2026-ivory.vercel.app

---

## Verification Steps

### After Deployment:

```bash
# Visit the site
https://cep-2026-ivory.vercel.app

# Check if:
✓ No "DisallowedHost" error
✓ No database connection error
✓ Login page loads
✓ Try creating an account or logging in
✓ Check admin panel at /admin (if accessible)
```

### Test Database Connection:

```bash
# Verify migrations ran automatically by checking Vercel logs:
# Deployments → Click latest build → Logs
# Look for: "Running migrations" → "Operations to perform" → "0 migrations to apply"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ERROR: FATAL: password authentication failed` | Check PASSWORD in DATABASE_URL matches what you saved |
| `ERROR: connection refused` | Wait 2-3 mins for Supabase to fully initialize |
| `ERROR: role "postgres" does not exist` | Database didn't initialize; recreate project |
| `ERROR: psycopg2 not found` | Run: `pip install psycopg2-binary` |
| `ERROR: ROLE "postgres" does NOT have CONNECT privilege` | Use admin connection in Supabase (should work automatically) |

---

## Environment Variables Checklist

After setup, Vercel should have **ALL** of these:

```
SECRET_KEY          ✅ Already set
DEBUG               ✅ Set to False
ALLOWED_HOSTS       ✅ Set
DATABASE_URL        🆕 ADD PostgreSQL connection string
GOOGLE_API_KEY      ✅ Already set
CSRF_TRUSTED_ORIGINS ✅ Set
CORS_ALLOWED_ORIGINS ✅ Set
```

---

## Files for Reference

- **[POSTGRESQL_MIGRATION_GUIDE.md](POSTGRESQL_MIGRATION_GUIDE.md)** - Detailed migration steps
- **[migrate_to_postgres.py](migrate_to_postgres.py)** - Python migration helper
- **[sqlite_export.sql](sqlite_export.sql)** - SQLite data dump (generated automatically)
- **[.env.example](.env.example)** - Environment variable template

---

## Success Indicators ✅

After deployment:
- ✅ Site loads without errors
- ✅ Database queries work
- ✅ Users can login/signup
- ✅ No "500: Internal Server Error"
- ✅ Static files (CSS/images) load
- ✅ Admin panel accessible (if needed)

---

**Estimated Time:** 5-10 minutes ⏱️

**Questions?** Check the deployment checklist or migration guide files.
