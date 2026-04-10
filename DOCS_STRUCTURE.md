# 📚 Documentation Structure

**Updated:** April 10, 2026  
**Total Docs:** 22 (reduced from ~43 duplicates & outdated files)

---

## 📁 Root Level (7 docs)
Core application documentation and guides.

| File | Purpose |
|------|---------|
| `README.md` | Main project overview & setup |
| `DEPARTEMEN_BAGIAN_USAGE_GUIDE.md` | How to use Departemen/Bagian features |
| `DEPARTEMEN_IMPLEMENTATION.md` | Technical details of Departemen implementation |
| `FEATURE_NAVBAR_MAPPING.md` | Navbar menu structure mapping |
| `PERMISSION_GUIDE.md` | User permission & access control guide |
| `OVERDUE_JOBS.md` | Overdue jobs notification system |
| `TOOLKEEPER.md` | Tool lending/keeper management system |

---

## 📂 /documentation (7 docs)
Technical implementation and architecture details.

| File | Purpose |
|------|---------|
| `CASCADING_DROPDOWN_SYSTEM.md` | Cascading dropdown implementation for asset hierarchy |
| `DASHBOARD_COLUMN_FILTERING.md` | Dashboard column filtering system |
| `DEPLOYMENT_GUIDE.md` | Production deployment checklist & guide |
| `HIERARCHY_ACCESS.md` | Hierarchy-based access control architecture |
| `MULTI_DEPARTEMEN.md` | Multi-departemen asset management system |
| `TESTING_GUIDE.md` | Unit & integration testing guide |
| `TOOLKEEPER_FEATURE.md` | Tool keeper feature implementation |

---

## 📋 /panduan (8 docs)
Setup guides and operational procedures for specific features.

| File | Purpose |
|------|---------|
| `README.md` | Panduan folder overview |
| `SETUP_CHECKLIST.md` | Initial Django/database setup checklist |
| `BACKUP.md` | Database backup quick start |
| `GDRIVE_BACKUP.md` | Google Drive backup automation setup |
| `NGROK.md` | Ngrok tunneling setup for external access |
| `NGROK_QR.md` | QR code configuration with ngrok |
| `CREATE_JOB_FROM_MEETING.md` | Creating jobs from meeting notulen |
| `MEETINGS.md` | Meetings & notulen management system |

---

## ✅ What Was Removed (50% reduction)
- ❌ **Analysis docs** - DEPARTEMEN_BAGIAN_IMPLEMENTATION_ANALYSIS.md, BUG_ANALYSIS_*, etc.
- ❌ **Outdated status docs** - IMPLEMENTATION_STATUS_*, READY_FOR_DEPLOYMENT.md, etc.
- ❌ **Old test/QA reports** - QA_TESTING_REPORT.md, TEST_RESULTS_SUMMARY.md, etc.
- ❌ **Duplicate guides** - QUICK_START_NGROK.md, MEETINGS_WORKFLOW.md (consolidated into main versions)
- ❌ **Redundant implementation docs** - IMPLEMENTATION_CREATE_JOB_FROM_NOTULEN.md (kept only guide version)

---

## 🎯 Quick Navigation

**First Time Setup?** → Start with `/panduan/SETUP_CHECKLIST.md` + `root: README.md`

**Need to understand a feature?** → Check `root:` docs first (DEPARTEMEN_*, PERMISSION_*, etc.)

**Technical implementation details?** → Check `/documentation:` folder

**Setting up a specific service?** → Check `/panduan:` folder

---

## 📌 Notes

- All application functionality remains **unchanged**
- This is purely documentation cleanup & reorganization
- Core docs are now at root level for easy access
- Feature-specific implementation details in `/documentation/`
- Setup guides grouped in `/panduan/`
