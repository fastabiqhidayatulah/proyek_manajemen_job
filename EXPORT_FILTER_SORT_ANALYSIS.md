# 🔍 EXPORT FILTER & SORT ANALYSIS - Dashboard

## Summary

Tested export functionality (PDF & Excel) pada dashboard untuk verify apakah sudah respect dengan filter dan sort.

---

## ✅ FILTER SUPPORT - WORKS CORRECTLY

Export links **SUDAH INCLUDE filters** dan backend **PROCESS filters** dengan benar:

### Filters yang di-support:
✅ **Bulan** (month)  
✅ **Tahun** (year)  
✅ **Date Range** (date_from, date_to)  
✅ **PIC** (pic - siapa yang assign)  
✅ **Line** (line filter)  
✅ **Mesin** (mesin filter)  
✅ **Sub Mesin** (sub_mesin filter)

### How it works:
1. User filter di dashboard (contoh: Bulan=December, Tahun=2025)
2. User klik "Export PDF" atau "Export Excel"
3. Export links include filter_params: `?month=12&year=2025`
4. Backend receive parameters dan apply filter ke query
5. Export file hanya contain **filtered data** ✅

---

## ⚠️ SORT SUPPORT - PARTIAL/MISSING

Export links **PASS sort parameters** tetapi backend **TIDAK RESPECT** sort preference.

### Current Behavior:
```
User sort tabel di Dashboard:
- Klik "Nama Pekerjaan" → Sort ascending
- URL: ?month=12&year=2025&sort=nama_pekerjaan

User klik "Export PDF":
- PDF export links include: ?month=12&year=2025&sort=nama_pekerjaan
- TETAPI... backend ignore sort parameter
- PDF always ordered by: nama_pekerjaan (default)
```

### Code Issue:
File: [core/views.py](core/views.py#L863) - `export_daily_jobs_pdf()`

```python
# Line 863: Always use fixed sort order
daily_job_data = all_jobs_team_base.select_related(...).order_by('nama_pekerjaan').distinct()
```

Backend doesn't check for `sort_by` parameter from request.GET.

---

## 📋 Comparison Table

| Feature | PDF Export | Excel Export | Status |
|---------|-----------|--------------|--------|
| Filter by Month | ✅ YES | ✅ YES | WORKING |
| Filter by Year | ✅ YES | ✅ YES | WORKING |
| Filter by Date Range | ✅ YES | ✅ YES | WORKING |
| Filter by PIC | ✅ YES | ✅ NO | PARTIAL |
| Filter by Line/Mesin | ✅ YES | ✅ NO | PARTIAL |
| **Sort by preference** | ❌ NO | ❌ NO | **MISSING** |

---

## 🎯 Recommended Fixes

### Priority 1: Add Sort Support to Export
The export functions should respect `sort_by` parameter from URL:

```python
def export_daily_jobs_pdf(request):
    # ... existing filter code ...
    
    # Get sort parameter from URL
    sort_by = request.GET.get('sort_by', 'nama_pekerjaan')
    sort_order = request.GET.get('sort_order', 'asc')
    
    # Apply sort logic
    if sort_order == 'desc':
        sort_field = f'-{sort_by}'
    else:
        sort_field = sort_by
    
    # Use dynamic sort instead of fixed 'nama_pekerjaan'
    daily_job_data = all_jobs_team_base.select_related(...).order_by(sort_field).distinct()
```

### Priority 2: Add Missing Filters to Excel Export
Excel export missing:
- ❌ PIC filter
- ❌ Line/Mesin filter

Should add same filter logic as PDF export.

### Priority 3: Update Dashboard Template
Template sudah correct - passes `filter_params` via `request.GET.urlencode()`

---

## 🧪 Test Cases

### Test 1: Export with Filter
```
1. Dashboard → Filter: December 2025
2. Click "Export PDF"
3. Result: PDF contains only jobs from December 2025 ✅ PASS
```

### Test 2: Export with Sort (CURRENTLY FAILS)
```
1. Dashboard → Sort: By "Prioritas"
2. Click "Export PDF"
3. Expected: PDF sorted by Prioritas
4. Actual: PDF sorted by Nama Pekerjaan (ignores sort) ❌ FAIL
```

### Test 3: Export with Multiple Filters
```
1. Dashboard → Filter: December 2025 + Line FC
2. Click "Export PDF"
3. Result: PDF has both filters applied (but missing sort) ⚠️ PARTIAL
```

---

## 📊 Impact

**Severity:** 🟡 **MEDIUM**

**User Impact:**
- User filters data and exports → Works ✅
- User sorts data and exports → Exports ignore sort ❌
- User wants export in same order as table → Not working ❌

**Workaround:** User can manually re-sort in Excel after export

---

## 🔧 Action Items

- [ ] **Add sort parameter handling to export_daily_jobs_pdf()**
- [ ] **Add sort parameter handling to export_daily_jobs_excel()**
- [ ] **Add missing filters to Excel export (PIC, Line, Mesin)**
- [ ] **Test export with sort + filter combinations**
- [ ] **Update documentation if sort behavior intentional**

