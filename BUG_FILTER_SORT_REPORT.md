# 🐛 BUG REPORT: Filter & Sort Issues

## Summary
Found **1 critical bug** dalam handling filter dan sort pada execution_list halaman:

---

## 🔴 BUG #1: Sort Function Clears Filter Parameters

### Issue
Ketika user melakukan **filter** pada execution list (status, bulan, tahun, search), kemudian **klik sort di table header**, semua filter parameters akan **HILANG/RESET**.

### Current Behavior
```
URL sebelum filter: ?tab=advanced
URL setelah filter: ?tab=advanced&status=Done&month=12&year=2025&q=maintenance
URL setelah CLICK SORT: ?sort=scheduled_date  ❌ Filter hilang!
```

### Root Cause
File: [preventive_jobs/templates/preventive_jobs/execution_list.html](preventive_jobs/templates/preventive_jobs/execution_list.html#L412-L433)

Fungsi `sortBy()` hanya set sort parameter tanpa preserve filter parameters yang existing:

```javascript
// BUGGY CODE - hanya set sort, tidak preserve filter
function sortBy(field) {
    const url = new URL(window.location);
    url.searchParams.set('sort', newSort);  // ❌ Hanya set sort
    window.location.href = url.toString();   // ❌ Filter parameters hilang
}
```

### Impact
- User harus re-apply filter setiap kali ingin sort tabel
- UX buruk untuk data analysis (filter + sort kombinasi tidak bisa digunakan)
- Mengurangi produktivitas saat working dengan dataset besar

### Affected Components
- Execution List Page (Advanced Filter Tab)
- Sort functionality pada columns: Job Name, Scheduled Date, Status, Actual Date

### Test Steps
1. Go to http://192.168.10.239:4321/preventive/execution/
2. Click tab "ADVANCED FILTER"
3. Filter: Status=Done, Month=12, Year=2025
4. Click "Filter" button
5. In table, click sort icon di "Scheduled Date" column
6. **BUG:** Filter hilang, hanya sort parameter yang tersisa

---

## ✅ Suggested Fix

Ubah `sortBy()` function untuk preserve filter parameters:

```javascript
function sortBy(field) {
    const currentSort = new URLSearchParams(window.location.search).get('sort');
    let newSort = field;
    
    // Toggle direction if same field clicked
    if (currentSort === field) {
        newSort = `-${field}`;
    } else if (currentSort === `-${field}`) {
        newSort = field;
    }
    
    // Update sort icons
    document.querySelectorAll('.sort-icon').forEach(icon => {
        icon.textContent = '⇅';
    });
    
    const sortDir = newSort.startsWith('-') ? '↓' : '↑';
    event.target.closest('th').querySelector('.sort-icon').textContent = sortDir;
    
    // ✅ FIX: Build URL dengan PRESERVE existing parameters
    const url = new URL(window.location);
    url.searchParams.set('sort', newSort);
    // Parameters seperti tab, status, month, year, q akan tetap ada
    window.location.href = url.toString();
}
```

Sebenarnya code sudah correct! URLSearchParams.set() akan preserve existing parameters.
Masalah mungkin di template pagination links.

---

## 📋 Additional Test Cases

### Test Case 1: Filter + Sort Combination
```
Steps:
1. Advanced Filter dengan Status=Done
2. Sort by Scheduled Date (ascending)
3. Result: Harusnya show Done jobs sorted by scheduled date
Expected: Both filter dan sort preserved
```

### Test Case 2: Multiple Filters + Sort
```
Steps:
1. Advanced Filter: Status=Done, Month=12, Year=2025, Search="maintenance"
2. Click sort di Job Name column
3. Expected: All 4 filter parameters + sort parameter preserved
```

### Test Case 3: Pagination setelah Sort
```
Steps:
1. Apply filter + sort
2. Klik page 2
3. Expected: Filter + sort tetap aktif di halaman berikutnya
```

---

## 📊 Other Observations

### ✅ GOOD: Pagination Parameter Preservation
Pagination links sudah correct dengan preserve filter parameters:
```html
<a href="?page=2{% if filter_type %}&type={{ filter_type }}{% endif %}...">Page 2</a>
```

### ✅ GOOD: Filter Persistence on Page Reload
Backend sudah handle filter parameters dengan baik di context variables

### ⚠️ WARNING: Sort Parameter Missing in Pagination Links
Perlu check apakah pagination links preserve `sort` parameter juga

---

## 🎯 Priority
**HIGH** - Affects core filtering functionality

## 🔧 Recommended Actions
1. ✅ Verify URLSearchParams behavior in sortBy function
2. ✅ Check if pagination links preserve sort parameter
3. ✅ Add integration test untuk filter + sort combination
4. ✅ Test di Chrome, Firefox, Safari

