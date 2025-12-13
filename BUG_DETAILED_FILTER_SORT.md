# 🐛 DETAILED BUG ANALYSIS - Filter & Sort Issues

## 🔴 BUG #1: Pagination Links Don't Preserve Filter & Sort Parameters

### Problem Location
File: [preventive_jobs/templates/preventive_jobs/execution_list.html](preventive_jobs/templates/preventive_jobs/execution_list.html#L262-L310)

### Issue Description
When user applies **filter** (status, month, year, search) + **sort**, then clicks pagination (next/previous page), **ALL filter and sort parameters are LOST**.

### Current Code (BUGGY)
```html
<!-- Line 269-270: Pagination links tanpa preserve parameters -->
<a class="page-link" href="?page=1">Pertama</a>
<a class="page-link" href="?page={{ executions.previous_page_number }}">Sebelumnya</a>
<a class="page-link" href="?page={{ num }}">{{ num }}</a>
```

### Expected Code (FIXED)
```html
<!-- Preserve all filter parameters in pagination links -->
<a class="page-link" href="?page=1{% if tab %}&tab={{ tab }}{% endif %}{% if selected_status %}&status={{ selected_status }}{% endif %}{% if selected_month %}&month={{ selected_month }}{% endif %}{% if selected_year %}&year={{ selected_year }}{% endif %}{% if search_query %}&q={{ search_query }}{% endif %}{% if sort_param %}&sort={{ sort_param }}{% endif %}">Pertama</a>
```

### Test Case
```
1. Go to http://192.168.10.239:4321/preventive/execution/
2. Click tab "ADVANCED FILTER"
3. Set: Status=Done, Month=12, Year=2025, Search="preventive"
4. Click "Filter" button
5. URL now: ?tab=advanced&status=Done&month=12&year=2025&q=preventive
6. Click sort icon on "Scheduled Date" → URL: ?tab=advanced&status=Done&month=12&year=2025&q=preventive&sort=-scheduled_date ✅ OK
7. If more than 20 results, click "Berikutnya" (next page)
   - Current URL becomes: ?page=2 ❌ LOST ALL FILTERS!
   - Should be: ?page=2&tab=advanced&status=Done&month=12&year=2025&q=preventive&sort=-scheduled_date
```

### Impact
- **HIGH SEVERITY**
- User cannot page through filtered results
- Frustrating UX for data analysis with large datasets
- Forces user to re-apply filter for each page

---

## 🔴 BUG #2: Sort Function Might Not Work Correctly with Tab Parameter

### Problem Location
File: [preventive_jobs/templates/preventive_jobs/execution_list.html](preventive_jobs/templates/preventive_jobs/execution_list.html#L412-L433)

### Issue
The `sortBy()` function uses `url.searchParams.set('sort', newSort)` which should preserve other parameters, **BUT** we need to verify it preserves the `tab` parameter correctly.

### Code
```javascript
function sortBy(field) {
    const currentSort = new URLSearchParams(window.location.search).get('sort');
    let newSort = field;
    
    if (currentSort === field) {
        newSort = `-${field}`;
    } else if (currentSort === `-${field}`) {
        newSort = field;
    }
    
    const url = new URL(window.location);
    url.searchParams.set('sort', newSort);  // This SHOULD preserve tab, but verify
    window.location.href = url.toString();
}
```

### Concern
- When switching from `tab=today` to `tab=advanced`, then clicking sort, what happens?
- Need to verify `tab` parameter is preserved

### Test Case
```
1. Start on execution_list default (tab=today)
2. Click "ADVANCED FILTER" tab
3. Apply a filter
4. Click sort on table header
5. Verify tab=advanced is still in URL (should be preserved by URLSearchParams)
```

---

## 📋 QUICK CHECKLIST OF ISSUES

| # | Issue | Severity | Status | Location |
|---|-------|----------|--------|----------|
| 1 | Pagination loses filter/sort parameters | 🔴 HIGH | CONFIRMED | execution_list.html:269-299 |
| 2 | Sort function tab parameter preservation | 🟡 MEDIUM | NEEDS VERIFY | execution_list.html:412-433 |
| 3 | Need to check pagination in other pages | 🟡 MEDIUM | TBD | ALL templates with pagination |

---

## 🔧 REQUIRED FIXES

### Fix #1: Update All Pagination Links

The pagination links need to preserve **tab**, **status**, **month**, **year**, **q**, and **sort** parameters.

**Option A: Add helper template tag** (Cleanest)
```django
{% load core_filters %}

<a class="page-link" href="?page=1&{{ request.GET.urlencode }}">Pertama</a>
```

**Option B: Manually build query string** (More explicit)
```django
<a class="page-link" href="?page=1{% if tab %}&tab={{ tab }}{% endif %}{% if selected_status %}&status={{ selected_status }}{% endif %}{% if selected_month %}&month={{ selected_month }}{% endif %}{% if selected_year %}&year={{ selected_year }}{% endif %}{% if search_query %}&q={{ search_query }}{% endif %}{% if sort_param %}&sort={{ sort_param }}{% endif %}">Pertama</a>
```

**Option C: Use JavaScript to build URL** (Dynamic)
```javascript
function buildPaginationLink(pageNum) {
    const params = new URLSearchParams(window.location.search);
    params.set('page', pageNum);
    return '?' + params.toString();
}
```

**Recommendation:** Use **Option A** with `request.GET.urlencode` - cleanest and most maintainable.

---

## 🎯 RECOMMENDED IMMEDIATE ACTIONS

1. ✅ Fix pagination links in execution_list.html (HIGH PRIORITY)
2. ✅ Check all other templates with pagination for same issue
3. ✅ Add integration tests for filter + sort + pagination flows
4. ✅ Consider using request.GET.urlencode for future pagination links

---

## 📊 Files Affected

- `preventive_jobs/templates/preventive_jobs/execution_list.html` - PRIMARY
- `templates/core/overdue_jobs_list.html` - SIMILAR PATTERN (also has pagination)
- Other templates with pagination TBD

