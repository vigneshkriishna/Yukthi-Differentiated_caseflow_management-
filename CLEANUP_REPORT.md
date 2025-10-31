# 🧹 Project Cleanup Report
**Generated:** October 31, 2025

## 📊 Summary
Your project has several files and directories that can be safely deleted to reduce clutter and improve maintainability.

---

## ❌ **FILES TO DELETE** (Safe to remove)

### 1. **SQLite Database File** (0 MB - Empty)
```
backend/dcm_system.db
```
**Reason:** You're using MongoDB Atlas, not SQLite. This is an empty local database file that's not being used.

**Action:** ✅ SAFE TO DELETE

---

### 2. **Duplicate/Unused Model Files** (SQLModel versions - not used with MongoDB)
```
backend/app/models/case.py          (SQLModel - you use case_mongodb.py)
backend/app/models/hearing.py       (SQLModel - you use hearing_mongodb.py)
backend/app/models/bench.py         (SQLModel - not used in MongoDB setup)
backend/app/models/audit_log.py     (SQLModel - not used in MongoDB setup)
```
**Reason:** Your application uses `main_mongodb.py` with Beanie models (`case_mongodb.py`, `hearing_mongodb.py`). The SQLModel versions are for a different database setup that's not active.

**Action:** ⚠️ KEEP FOR NOW (they're used by routers that aren't active, but you might want them later)

**Alternative:** If you're 100% committed to MongoDB, these can be deleted along with their dependent files.

---

### 3. **Unused Startup Scripts**
```
backend/start_server.py
backend/setup.py
```
**Reason:** These scripts are designed for SQLite/SQLModel setup. You're using `main_mongodb.py` to start your server.

**Action:** ✅ SAFE TO DELETE (if you're committed to MongoDB-only)

---

### 4. **Development/Test Scripts** (Keep if needed for development)
```
backend/test_enhanced_integration.py
backend/fix_lint_errors.py
backend/seed_basic_data.py           (for SQLite, not MongoDB)
backend/create_large_dataset.py      (generates test data)
backend/train_enhanced_bns_model.py
backend/train_with_database_cases.py
backend/check_case_count.py
backend/quick_check_db.py            (just created for testing)
```
**Reason:** These are development/testing utilities. Keep them if you need to:
- Generate test data
- Train ML models
- Debug database issues
- Run integration tests

**Action:** 
- ✅ DELETE: `fix_lint_errors.py`, `seed_basic_data.py` (SQLite-specific)
- ⚠️ KEEP: Others if you're still developing/testing
- ✅ DELETE LATER: Once project is stable, remove test scripts

---

## 🗑️ **CACHE DIRECTORIES TO DELETE** (Regenerated automatically)

### Python Cache Files (7 directories)
```
backend/__pycache__/
backend/app/__pycache__/
backend/app/core/__pycache__/
backend/app/models/__pycache__/
backend/app/routers/__pycache__/
backend/app/services/__pycache__/
backend/app/services/nlp/__pycache__/
```
**Reason:** These are compiled Python bytecode caches. They're automatically regenerated when you run Python.

**Action:** ✅ SAFE TO DELETE (regenerated automatically)

**Command to delete all:**
```powershell
Get-ChildItem -Path "backend" -Directory -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force
```

---

## 📁 **EMPTY/MINIMAL DIRECTORIES**

### Storage Documents (Sample files only)
```
backend/storage/documents/
  ├── affidavit/
  ├── bail_application/
  ├── case_file/
  ├── charge_sheet/
  ├── evidence/
  ├── forensic_report/
  ├── judgment/
  ├── notice/
  ├── order/
  ├── other/
  ├── petition/
  ├── witness_statement/
  └── sample_witness_statement.txt
```
**Reason:** These folders are for uploaded documents. Most are likely empty except for the sample file.

**Action:** ⚠️ KEEP (needed for document uploads feature)

---

## 📦 **DUPLICATE DEPENDENCIES TO REVIEW**

### Environment Files
```
backend/.env              (your active config - KEEP)
backend/.env.example      (template - KEEP)
backend/.env.mongodb      (MongoDB-specific - KEEP if used)
backend/.env.production   (production config - KEEP)
```
**Action:** ✅ KEEP ALL (they serve different purposes)

### Requirements Files
```
backend/requirements.txt            (main dependencies - KEEP)
backend/requirements-production.txt (production deps - KEEP)
```
**Action:** ✅ KEEP BOTH

---

## 🔧 **INACTIVE ROUTERS/SERVICES**

These files exist but may not be used in your MongoDB setup:
```
backend/app/routers/cases.py     (uses SQLModel Case, not MongoDB)
backend/app/routers/schedule.py  (uses SQLModel)
backend/app/routers/reports.py   (uses SQLModel)
backend/app/routers/nlp.py       (uses SQLModel)
```
**Reason:** Your `main_mongodb.py` defines its own routes inline, not using these router files.

**Action:** 
- ⚠️ INVESTIGATE: Check if these are imported in main_mongodb.py
- If not used: Can be deleted or refactored to use MongoDB models

---

## 📝 **RECOMMENDED CLEANUP ACTIONS**

### 🟢 **Immediate (100% Safe)**
```powershell
# 1. Delete SQLite database
Remove-Item "backend\dcm_system.db"

# 2. Delete all __pycache__ directories
Get-ChildItem -Path "backend" -Directory -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force

# 3. Delete unused test script
Remove-Item "backend\quick_check_db.py"
```

### 🟡 **Medium Priority (Review first)**
```powershell
# Delete SQLite-specific startup scripts (if MongoDB-only)
Remove-Item "backend\start_server.py"
Remove-Item "backend\setup.py"
Remove-Item "backend\seed_basic_data.py"
Remove-Item "backend\fix_lint_errors.py"
```

### 🔴 **Low Priority (Keep for now)**
- Model files (case.py, hearing.py) - might be needed for migration
- Training scripts - keep if ML features are important
- Test scripts - keep during development phase

---

## 💾 **Estimated Space Savings**

- **__pycache__ directories:** ~1-5 MB
- **dcm_system.db:** 0 MB (empty)
- **Unused scripts:** ~50 KB
- **Total:** ~5-10 MB (minimal, but improves project cleanliness)

---

## ⚠️ **IMPORTANT NOTES**

1. **Before deleting anything:** 
   - Commit current changes to git
   - Create a backup or new branch
   
2. **Test after cleanup:**
   - Restart backend server
   - Test all features
   - Check for import errors

3. **Git will track deletions:**
   - Deleted files can be recovered from git history
   - Add deleted file patterns to .gitignore if needed

---

## 🚀 **Recommended Cleanup Script**

```powershell
# Navigate to backend directory
cd "c:\Users\vigne\OneDrive\Desktop\yukthi\caseflow_management_application\backend"

# 1. Clean Python cache
Write-Host "🧹 Cleaning Python cache..." -ForegroundColor Yellow
Get-ChildItem -Directory -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force
Write-Host "✅ Cache cleaned!" -ForegroundColor Green

# 2. Delete SQLite database
Write-Host "🧹 Removing SQLite database..." -ForegroundColor Yellow
Remove-Item "dcm_system.db" -ErrorAction SilentlyContinue
Write-Host "✅ Database removed!" -ForegroundColor Green

# 3. Delete temporary test files
Write-Host "🧹 Removing temporary files..." -ForegroundColor Yellow
Remove-Item "quick_check_db.py" -ErrorAction SilentlyContinue
Write-Host "✅ Temp files removed!" -ForegroundColor Green

Write-Host "`n🎉 Cleanup complete!" -ForegroundColor Cyan
```

---

## 📋 **Summary Table**

| Item | Size | Status | Action |
|------|------|--------|--------|
| `dcm_system.db` | 0 MB | Empty | ✅ DELETE |
| `__pycache__/` (7 dirs) | ~5 MB | Cache | ✅ DELETE |
| `quick_check_db.py` | 2 KB | Test script | ✅ DELETE |
| `start_server.py` | 2 KB | Unused startup | 🟡 REVIEW |
| `setup.py` | 5 KB | SQLite setup | 🟡 REVIEW |
| `case.py`, `hearing.py` | ~10 KB | SQLModel versions | ⚠️ KEEP |
| Test scripts | ~20 KB | Development | ⚠️ KEEP |

**Total Safe to Delete Now:** ~5 MB + empty files
**Total After Review:** Up to 50 KB additional

---

## 🎯 **Next Steps**

1. ✅ Review this report
2. ✅ Create git commit/branch before cleanup
3. ✅ Run the recommended cleanup script
4. ✅ Test your application
5. ✅ Commit cleanup changes

---

**Questions?** Review each file before deleting to ensure you won't need it!
