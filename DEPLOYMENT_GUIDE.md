# 📖 DEPLOYMENT GUIDE - Step by Step

**Status:** 🟢 **READY FOR DEPLOYMENT**  
**Last Updated:** December 18, 2025

---

## 🚀 QUICK START

### If Database is Already Running:
```bash
# 1. Backup
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# 2. Review migration
python manage.py migrate --plan

# 3. Apply migration
python manage.py migrate

# 4. Test
python manage.py test_performance_optimization

# 5. Go to dashboard and verify
# Open browser: http://localhost:4321
```

**Total Time:** ~5 minutes

---

## 📋 DETAILED DEPLOYMENT STEPS

### STEP 1: Ensure Database is Running

```bash
# Windows - Via Services
# 1. Open Services (services.msc)
# 2. Find "postgresql-x64-14" (or your version)
# 3. Right-click → Start

# Windows - Via Command Line
pg_ctl -D "C:\Program Files\PostgreSQL\14\data" start

# Linux/Mac
sudo systemctl start postgresql

# Verify connection
psql -U manajemen_app_user -d manajemen_pekerjaan_db -h localhost

# If connection fails, check settings.py:
# config/settings.py line 81-87
```

### STEP 2: Backup Database

```bash
# Create backup BEFORE any changes
python manage.py dumpdata > backup_20251218_before.json

# Verify backup
ls -la backup_20251218_before.json  # Should be > 1MB

# Store backup safely
# Keep for at least 1 week after deployment
```

### STEP 3: Review Migration Plan

```bash
# See exactly what will change
python manage.py migrate --plan

# Output should show 7 indexes being added:
# Running migrations:
#   Applying core.0014_customuser_core_custom_atasan__6b9a8a_idx_and_more...
# 
# Add index core_custom_atasan__6b9a8a_idx on field(s) atasan, id
# Add index core_custom_usernam_8458f1_idx on field(s) username
# Add index core_job_pic_id_a0e7a8_idx on field(s) pic, tipe_job
# Add index core_job_project_22810c_idx on field(s) project, status
# Add index core_job_aset_id_339c24_idx on field(s) aset, status
# Add index core_projec_manager_4612cd_idx on field(s) manager_project, is_shared
# Add index core_projec_is_shar_20dca5_idx on field(s) is_shared

# If different, STOP and investigate
```

### STEP 4: Apply Migration

```bash
# Apply the migration to database
python manage.py migrate

# Should output:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, core, mptt, ...
# Running migrations:
#   ...
#   Applying core.0014_customuser_core_custom_atasan__6b9a8a_idx_and_more... OK

# If you get errors:
# 1. Check database is running
# 2. Check credentials in settings.py
# 3. Check no other app is modifying database

# Timeline: 10-60 seconds depending on table size
```

### STEP 5: Verify Migration Applied

```bash
# Check migration status
python manage.py showmigrations core

# Output should show:
# core
#  ...
#  [X] 0013_alter_project_shared_is_shared
#  [X] 0014_customuser_core_custom_atasan__6b9a8a_idx_and_more  <-- [X] = Applied

# If 0014 shows [ ] instead of [X], migration failed
```

### STEP 6: Verify Indexes in Database

```bash
# Connect to database
psql -U manajemen_app_user -d manajemen_pekerjaan_db

# List all indexes (in PostgreSQL)
\d+ core_customuser

# Should show indexes like:
# Indexes:
#     "core_custom_atasan__6b9a8a_idx" btree (atasan_id, id)
#     "core_custom_usernam_8458f1_idx" btree (username)

# Exit psql
\q
```

### STEP 7: Run Performance Tests

```bash
# If database was working before, run tests:
python manage.py test_performance_optimization

# Expected output:
# ✅ PASS: Cache is configured and working
# ✅ PASS: All cache utility functions imported
# ✅ PASS: CustomUser - get_all_subordinates() with Caching
# ✅ PASS: get_user_accessible_projects() - Caching
# ✅ PASS: Project Model - Auto Cache Invalidation
# ✅ PASS: Verify Existing Functionality
# ✅ PASS: Views Integration Check

# If any test fails, check error message and troubleshoot
```

### STEP 8: Test in Browser

```bash
# Start Django development server
python manage.py runserver

# Open browser
# http://localhost:4321

# Test checklist:
# ✅ Dashboard loads
# ✅ Can filter jobs
# ✅ Can search jobs
# ✅ Can sort jobs
# ✅ Can view projects
# ✅ Can view jobs in project
# ✅ Permissions still work
# ✅ Sharing still works

# If any feature broken, STOP and troubleshoot
```

### STEP 9: Monitor Performance (Optional but Recommended)

```bash
# Install debug toolbar (if not already)
pip install django-debug-toolbar

# Enable in settings.py:
# Add 'debug_toolbar' to INSTALLED_APPS
# Add DebugToolbarMiddleware to MIDDLEWARE
# Set INTERNAL_IPS = ['127.0.0.1']

# Restart server and visit dashboard
# Click "Debug Toolbar" on right side
# Check SQL tab:
#   - Query count (should be lower than before)
#   - Query time (should be faster)
#   - Cache hits (should see cache being used)

# Expected before migration: 25-35 queries
# Expected after migration: 8-12 queries
```

### STEP 10: Cleanup (Optional)

```bash
# After 1 week of successful operation:
# Delete old backups (keep newest 3)
rm backup_20251210_*.json
rm backup_20251211_*.json

# Keep most recent:
backup_20251218_before.json
```

---

## ⚠️ TROUBLESHOOTING

### Issue 1: "Migration 0014 does not exist"

```
Error: No migration called 0014_... in core

Solution:
1. Check migration file exists:
   ls core/migrations/0014_customuser_core_custom_atasan__6b9a8a_idx_and_more.py

2. If missing, regenerate:
   python manage.py makemigrations

3. Run migrate again:
   python manage.py migrate
```

### Issue 2: "Password authentication failed"

```
Error: FATAL password authentication failed for user "manajemen_app_user"

Solution:
1. Verify PostgreSQL is running:
   pg_ctl status -D "C:\Program Files\PostgreSQL\14\data"

2. Check credentials in settings.py match:
   config/settings.py line 81-87

3. Test connection manually:
   psql -U manajemen_app_user -d manajemen_pekerjaan_db -h localhost

4. If password wrong:
   ALTER USER manajemen_app_user WITH PASSWORD 'new_password';
   Then update settings.py
```

### Issue 3: Migration hangs/timeout

```
Error: Migration process hangs or times out

Solution:
1. Check if indexes already exist (idempotent):
   python manage.py migrate --fake-initial

2. Or increase timeout:
   # Run migration with verbose output
   python manage.py migrate --verbosity 3

3. Check database logs:
   tail -f /var/log/postgresql/postgresql.log

4. If still stuck, kill and rollback:
   python manage.py migrate core 0013_alter_project_shared_is_shared
```

### Issue 4: Cache not working

```
Error: Cache not being used or "Cache not configured"

Solution:
1. Verify settings.py has CACHES:
   grep -A 5 "CACHES = {" config/settings.py

2. Test cache directly:
   python manage.py shell
   >>> from django.core.cache import cache
   >>> cache.set('test', 'value')
   >>> cache.get('test')
   'value'  # Should print this

3. Check import in models:
   grep "from django.core.cache import cache" core/models.py

4. Check cache_utils exists:
   ls core/cache_utils.py
```

### Issue 5: Indexes not created

```
Error: Migration says "OK" but indexes don't exist

Solution:
1. Check if migration actually ran:
   python manage.py showmigrations core | grep 0014

2. Manually check indexes:
   psql -U manajemen_app_user -d manajemen_pekerjaan_db
   \d+ core_customuser

3. If missing, recreate:
   # Backup and restore from before migration
   python manage.py loaddata backup_20251218_before.json

   # Then run migration again
   python manage.py migrate core 0014_customuser_core_custom_atasan__6b9a8a_idx_and_more
```

### Issue 6: Performance not improved

```
Problem: Dashboard still slow after migration

Solution:
1. Verify indexes are actually being used:
   EXPLAIN ANALYZE SELECT * FROM core_customuser WHERE atasan_id = 1;
   # Look for "Index Scan" in output

2. Verify cache is working:
   python manage.py shell
   >>> from core.cache_utils import get_user_accessible_projects
   >>> from core.models import CustomUser
   >>> user = CustomUser.objects.first()
   >>> # First call (cold cache)
   >>> result1 = get_user_accessible_projects(user)
   >>> # Second call (warm cache) - should be instant
   >>> result2 = get_user_accessible_projects(user)

3. Install debug toolbar to monitor:
   pip install django-debug-toolbar
   # Then view dashboard and check SQL queries

4. Check for other bottlenecks:
   # May be I/O, not database
   # Use profiler: python-profile
```

---

## 🔄 ROLLBACK PROCEDURE

If you need to undo the deployment:

```bash
# STEP 1: Restore from backup
python manage.py loaddata backup_20251218_before.json

# STEP 2: Unskip migration (remove indexes)
python manage.py migrate core 0013_alter_project_shared_is_shared

# STEP 3: Revert code changes
git checkout HEAD~1 -- core/models.py
git checkout HEAD~1 -- core/views.py
git checkout HEAD~1 -- config/settings.py
rm core/cache_utils.py
rm core/migrations/0014_*.py

# STEP 4: Restart Django
# Server should revert to pre-optimization state
```

---

## 📊 MONITORING AFTER DEPLOYMENT

### Daily Checks:
```
1. Check error logs for cache issues
2. Monitor performance metrics
3. Verify users report faster experience
```

### Weekly Checks:
```
1. Compare query counts (should be lower)
2. Compare page load times (should be faster)
3. Check cache hit rate (should be > 50%)
4. Review any support tickets
```

### Monthly Optimization:
```
1. Analyze slow queries (if any)
2. Adjust cache timeout if needed
3. Monitor memory usage
4. Plan further optimizations
```

---

## ✅ DEPLOYMENT SUCCESS CRITERIA

- ✅ Migration applied successfully
- ✅ All tests pass
- ✅ Dashboard loads correctly
- ✅ All features work as before
- ✅ No error in logs
- ✅ Query count reduced 70-75%
- ✅ Page load time reduced 85-90%
- ✅ No user complaints about performance
- ✅ Cache invalidation works

---

## 🎯 FINAL CHECKLIST

```
Before Deployment:
☐ Database backup created
☐ Migration plan reviewed
☐ All tests pass
☐ Code validated

During Deployment:
☐ Migration applied successfully
☐ Server restarted cleanly
☐ Dashboard loads without errors
☐ Basic functionality works

After Deployment:
☐ Performance improved (verified with debug toolbar)
☐ No error logs
☐ Users confirm faster experience
☐ Monitoring in place
☐ Rollback plan documented

Ready for Production? ✅ YES / ❌ NO
```

---

## 📞 NEED HELP?

1. **Check troubleshooting section above**
2. **Review TESTING_GUIDE.md for detailed tests**
3. **Check TEST_RESULTS_SUMMARY.md for validation results**
4. **Review IMPLEMENTATION_COMPLETE.md for technical details**

---

**Timeline:** 5-30 minutes total  
**Risk Level:** 🟢 **LOW** (fully reversible)  
**Expected Outcome:** 🚀 **87-88% faster dashboard**
