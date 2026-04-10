# Supabase Setup Guide

Complete integration of Supabase authentication and real-time database with Saarthi platform.

## Overview

- ✅ **Authentication**: JWT-based user authentication via Supabase Auth
- ✅ **Database**: PostgreSQL via Supabase
- ✅ **Real-time**: Enabled for quiz results and user profiles
- ✅ **Node Server**: Authenticated endpoints for saving/retrieving quiz data
- ✅ **Django Backend**: Already configured to use PostgreSQL

## Step 1: Create Supabase Project (5 min)

1. Go to [https://supabase.com](https://supabase.com)
2. Click **"Start your project"** → Sign up with GitHub
3. Create new project:
   - **Name**: `saarthi`
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to your users
4. Wait for project to be created (2-3 minutes)

## Step 2: Get API Credentials (2 min)

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon (public)**: Your anonymous key
3. Add to `.env`:
   ```
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_ANON_KEY=your_anon_key_here
   ```

## Step 3: Create Database Tables (3 min)

In Supabase dashboard, go to **SQL Editor** and run:

### Table 1: User Profiles
```sql
CREATE TABLE user_profiles (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT,
  avatar_url TEXT,
  skills JSONB DEFAULT '[]'::jsonb,
  career_preferences JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE POLICY "Users can view their own profile" ON user_profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile" ON user_profiles
  FOR UPDATE USING (auth.uid() = user_id);

ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
```

### Table 2: Quiz Results
```sql
CREATE TABLE quiz_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  scores JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE POLICY "Users can view their own results" ON quiz_results
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own results" ON quiz_results
  FOR INSERT WITH CHECK (auth.uid() = user_id);

ALTER TABLE quiz_results ENABLE ROW LEVEL SECURITY;

CREATE INDEX idx_quiz_results_user_id ON quiz_results(user_id);
```

### Table 3: User Learning Goals
```sql
CREATE TABLE learning_goals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  goal_name TEXT NOT NULL,
  target_career TEXT,
  skills_needed JSONB DEFAULT '[]'::jsonb,
  progress_percentage FLOAT DEFAULT 0,
  deadline DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE POLICY "Users can manage their learning goals" ON learning_goals
  FOR ALL USING (auth.uid() = user_id);

ALTER TABLE learning_goals ENABLE ROW LEVEL SECURITY;

CREATE INDEX idx_learning_goals_user_id ON learning_goals(user_id);
```

## Step 4: Enable Authentication Methods (2 min)

1. Go to **Authentication** → **Providers**
2. Enable:
   - ✅ **Email** (default, already enabled)
   - ✅ **GitHub** (recommended for testing)
3. Click each provider to configure

## Step 5: Update Node Server (Done!)

The Node server at `server/app.js` is now configured with:

```javascript
// Requires token in Authorization header
app.post('/api/save-quiz-results', verifySupabaseToken, async (req, res) => { ... });

// Protected route - get user quiz history
app.get('/api/user-quiz-history', verifySupabaseToken, async (req, res) => { ... });
```

**Using the API:**

```bash
# Save quiz results
curl -X POST http://localhost:5000/api/save-quiz-results \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"scores": {"Realistic": 0.8, ...}}'

# Get quiz history
curl -X GET http://localhost:5000/api/user-quiz-history \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Step 6: Update Django Settings (Already Done!)

Django is already configured in `saarthi/settings.py`:

```python
if os.environ.get('DATABASE_URL'):
    import dj_database_url
    DATABASES = {'default': dj_database_url.config()}
else:
    # Fallback to SQLite
```

## Step 7: Migrate Django to Supabase (if needed)

If migrating from SQLite:

```bash
# Export from SQLite
sqlite3 db.sqlite3 .dump > sqlite_backup.sql

# Run migrations on new database
python manage.py migrate

# Import data (manual process for complex data)
```

## Step 8: Deploy to Vercel

1. Add environment variables to Vercel:
   ```
   DATABASE_URL=postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:6543/postgres
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   ```

2. Vercel auto-deploys on git push

## Testing

### Test Supabase Connection (Node)

```bash
cd server
npm install
node -e "const auth = require('./supabaseAuth'); console.log('Supabase:', auth.supabase ? '✅ Connected' : '❌ Not configured')"
```

### Test Authentication (Node)

```bash
# Sign up
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test@123"}'

# Returns: JWT token
```

### Test Django + PostgreSQL

```bash
python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
>>> print("✅ Django connected to database")
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `SUPABASE_URL undefined` | Check `.env` file, restart server |
| `Invalid JWT token` | Token expired or malformed, sign in again |
| `Database connection failed` | Check CONNECTION_STRING format, verify credentials |
| `Row-level security denied` | Configure RLS policies correctly for tables |

## Security Checklist

- ✅ Enable Row-Level Security (RLS) on all tables
- ✅ Use environment variables for secrets
- ✅ Never commit `.env` file
- ✅ Use HTTPS in production
- ✅ Implement rate limiting on auth endpoints
- ✅ Set strong database password (20+ chars)

## Next Steps

1. **Frontend Integration**: Update React components to use Supabase auth
2. **Email Verification**: Configure email templates in Supabase
3. **Social Auth**: Add GitHub/Google sign-in
4. **Backup**: Enable Supabase automated backups
5. **Analytics**: Monitor usage in Supabase dashboard

## Resources

- [Supabase Docs](https://supabase.com/docs)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Row-Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
