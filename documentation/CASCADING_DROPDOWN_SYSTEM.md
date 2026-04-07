# Cascading Dropdown System Documentation

## Overview

This document describes the **Cascading Dropdown System** implemented in the Proyek Management Job application. This system allows dynamic, hierarchical asset selection in job creation forms based on user's department.

**Last Updated:** April 7, 2026  
**Status:** ✅ Working (Both Teknik & Operasional)

---

## 1. Architecture Overview

### 1.1 System Concept

The cascading dropdown system provides **department-specific asset hierarchy** for job creation:

- **Teknik Department Users** → Uses **AsetMesin** tree structure
  - Level 0: Line (e.g., FC, AAC, FS 1)
  - Level 1: Mesin (e.g., Finishing Line)
  - Level 2: Sub Mesin (e.g., Coating, Cutting)

- **Operasional & Other Departments** → Uses **AsetDepartemen** tree structure
  - Level 0: Departemen (e.g., Operasional, Teknik)
  - Level 1: Bagian (e.g., Exim, GBBSC, GPJ)
  - Level 2: Sub Bagian (e.g., Export & Import, Bahan Baku)

### 1.2 Key Components

```
┌─────────────────────────────────────────────────────────┐
│               Frontend (Browser)                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  job_form.html                                   │  │
│  │  - 3 Dropdown Fields (Level 0, 1, 2)           │  │
│  │  - JavaScript Cascade Logic                     │  │
│  │  - Event Listeners & AJAX Calls                 │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬──────────────────────────────────┘
                     │ AJAX Request
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Backend (Django)                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  core/views.py                                   │  │
│  │  - api_aset_children() endpoint                 │  │
│  │  - Returns JSON list of children                │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬──────────────────────────────────┘
                     │ Query Database
                     ▼
┌─────────────────────────────────────────────────────────┐
│          Database (PostgreSQL)                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  core_asetmesin (MPPT Tree)                     │  │
│  │  core_asetdepartemen (MPPT Tree)                │  │
│  │  - Hierarchical parent-child relationships      │  │
│  │  - Auto-generated level field                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Database Models

### 2.1 AsetMesin Model

**File:** `core/models.py`

```python
class AsetMesin(MPTTModel):
    nama = models.CharField(max_length=100)
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    
    class MPTTMeta:
        order_insertion_by = ['nama']
```

**Structure Example:**
```
AAC (level=0)
├── FC (level=1)
│   ├── Finishing Line (level=2)
│   │   ├── Coating (level=3)
│   │   ├── Cutting (level=3)
│   │   └── ...
├── FS 1 (level=0)
├── FS 2 (level=0)
└── ...
```

### 2.2 AsetDepartemen Model

**File:** `core/models.py`

```python
class AsetDepartemen(MPTTModel):
    nama = models.CharField(max_length=100)
    departemen = models.ForeignKey(
        Departemen,
        on_delete=models.CASCADE,
        related_name='aset_departemen'
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    
    class MPTTMeta:
        order_insertion_by = ['nama']
```

**Structure Example:**
```
Operasional (level=0)
├── Exim (level=1)
│   ├── Export & Import (level=2)
├── GBBSC (level=1)
│   ├── Bahan Baku (level=2)
│   └── Suku Cadang (level=2)
├── GPJ (level=1)
│   ├── GPJ AAC & Mortar (level=2)
│   └── GDI SF (level=2)
└── HRD & Umum (level=1)
    ├── Ketenagakerjaan (level=2)
    └── Pelatihan (level=2)
```

### 2.3 IMPORTANT: Parent-Child Relationships

**Critical Rule:** Each parent-child relationship must be correctly defined in admin panel:

1. **Level 0 items** MUST have `parent = NULL`
2. **Level 1 items** MUST have `parent = Level 0 item`
3. **Level 2 items** MUST have `parent = Level 1 item`

If parent-child relationships are wrong, cascading will return incorrect hierarchies.

---

## 3. Form Implementation

### 3.1 JobForm Fields

**File:** `core/forms.py`

For **AsetMesin (Teknik):**
```python
line = forms.ModelChoiceField(
    queryset=AsetMesin.objects.filter(level=0),  # Level 0 items
    required=False
)
mesin = forms.ModelChoiceField(
    queryset=AsetMesin.objects.none(),  # Empty, filled by JS
    required=False
)
sub_mesin = forms.ModelChoiceField(
    queryset=AsetMesin.objects.none(),  # Empty, filled by JS
    required=False
)
```

For **AsetDepartemen (Operasional):**
```python
aset_departemen_display = forms.ModelChoiceField(
    queryset=AsetDepartemen.objects.filter(level=0),  # Level 0 items
    required=False
)
aset_departemen_bagian = forms.ModelChoiceField(
    queryset=AsetDepartemen.objects.none(),  # Empty, filled by JS
    required=False
)
aset_departemen_sub = forms.ModelChoiceField(
    queryset=AsetDepartemen.objects.none(),  # Empty, filled by JS
    required=False
)
```

### 3.2 Form Logic in __init__ Method

**Key Pattern:**
- Level 0 dropdown: Pre-populated with `queryset=AsetMesin.objects.filter(level=0)` or `AsetDepartemen.objects.filter(level=0)`
- Level 1 dropdown: `queryset=AsetMesin.objects.none()` (JavaScript will populate)
- Level 2 dropdown: `queryset=AsetMesin.objects.none()` (JavaScript will populate)

**Why?** Initial page load should show Level 0 options, but Level 1 and 2 must be empty until user selects parent.

### 3.3 Conditional Display

**In __init__ method:**
```python
is_teknik = (
    user_departemen is not None and 
    user_departemen.nama_departemen.strip().lower() == 'teknik'
)

if is_teknik:
    # Hide AsetDepartemen fields
    self.fields['aset_departemen_display'].widget = forms.HiddenInput()
    self.fields['aset_departemen_bagian'].widget = forms.HiddenInput()
    self.fields['aset_departemen_sub'].widget = forms.HiddenInput()
else:
    # Hide AsetMesin fields
    self.fields['line'].widget = forms.HiddenInput()
    self.fields['mesin'].widget = forms.HiddenInput()
    self.fields['sub_mesin'].widget = forms.HiddenInput()
```

---

## 4. API Endpoint

### 4.1 Endpoint Definition

**File:** `core/views.py`

```python
def api_aset_children(request):
    """
    AJAX endpoint untuk fetch children dari parent node.
    Query params: parent_id (required)
    Returns: JSON array of children [{id, nama, level}, ...]
    """
    parent_id = request.GET.get('parent_id')
    
    if not parent_id:
        return JsonResponse({"error": "parent_id required"}, status=400)
    
    children = AsetDepartemen.objects.filter(
        parent_id=parent_id
    ).order_by('nama').values('id', 'nama', 'level')
    
    data = list(children)
    return JsonResponse(data, safe=False)
```

**URL Registration:**
```python
# core/urls.py
path('api/aset-children/', views.api_aset_children, name='api_aset_children'),
```

### 4.2 Response Format

**Expected Response:**
```json
[
  {"id": 2, "nama": "Exim", "level": 1},
  {"id": 3, "nama": "GBBSC", "level": 1},
  {"id": 4, "nama": "GPJ", "level": 1},
  {"id": 5, "nama": "HRD & Umum", "level": 1}
]
```

**IMPORTANT:** Response is a **direct array**, NOT wrapped in an object with `{success, children}` key.

---

## 5. JavaScript Implementation

### 5.1 AsetMesin Cascade (Teknik Users)

**File:** `templates/job_form.html` (lines ~397-520)

**Logic:**
1. Get all 3 elements by ID
2. Define helper functions: `updateDropdown()`, `loadChildren()`
3. Attach change event listeners ONLY if elements exist (null check)
4. When Level 0 changes → fetch Level 1 children
5. When Level 1 changes → fetch Level 2 children

**Critical Part:**
```javascript
// MUST have null check to prevent crash on Operasional users
if (lineSelect && mesinSelect && subMesinSelect) {
    lineSelect.addEventListener('change', function() {
        const lineId = this.value;
        const selectedMesinId = mesinSelect.value;
        loadChildren(lineId, mesinSelect, selectedMesinId);
        updateDropdown(subMesinSelect, [], null);  // Clear Level 2
    });
    
    mesinSelect.addEventListener('change', function() {
        const mesinId = this.value;
        const selectedSubMesinId = subMesinSelect.value;
        loadChildren(mesinId, subMesinSelect, selectedSubMesinId);
    });
}
```

### 5.2 AsetDepartemen Cascade (Operasional Users)

**File:** `templates/job_form.html` (lines ~524-600)

**Logic:** Identical to AsetMesin, but:
- Uses different element IDs
- Uses different API endpoint (same endpoint, different data)
- Uses different element references

**Critical Implementation:**
```javascript
function updateDepartemenDropdown(selectElement, options, selectedId) {
    selectElement.innerHTML = '<option value="">---------</option>';
    options.forEach(function(option) {
        const opt = document.createElement('option');
        opt.value = option.id;
        opt.textContent = option.nama;
        if (option.id == selectedId) opt.selected = true;
        selectElement.appendChild(opt);
    });
}

function loadDepartemenChildren(parentId, targetSelect, selectedId) {
    if (!parentId) {
        updateDepartemenDropdown(targetSelect, [], null);
        return;
    }
    
    targetSelect.innerHTML = '<option value="">Loading...</option>';
    
    fetch(`/api/aset-children/?parent_id=${parentId}`)
        .then(response => response.json())
        .then(data => {
            updateDepartemenDropdown(targetSelect, data, selectedId);
            if (selectedId) {
                targetSelect.dispatchEvent(new Event('change'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            targetSelect.innerHTML = '<option value="">Error loading</option>';
        });
}
```

---

## 6. Troubleshooting Guide

### Issue 1: Cascading Not Working

**Symptoms:** Select Level 0, Level 1 dropdown stays empty

**Debug Steps:**
1. Open F12 Console
2. Select Level 0 item
3. Check Network tab for `/api/aset-children/` request
4. Check Response tab - should return JSON array

**Common Causes:**
- [ ] Parent-child relationships wrong in database (check admin panel)
- [ ] API endpoint not registered in urls.py
- [ ] JavaScript error (check Console tab for red errors)
- [ ] Element IDs don't match (check Form field IDs vs JavaScript getElementById)

### Issue 2: "Cannot read properties of null (reading 'addEventListener')"

**Symptoms:** Console error, cascading crashes

**Cause:** JavaScript trying to attach event listener to non-existent element

**Fix:** Ensure NULL CHECK before addEventListener:
```javascript
if (element && otherElement) {
    element.addEventListener('change', ...);
}
```

### Issue 3: All Level 2 Items Showing Regardless of Level 1 Selection

**Symptoms:** Sub Bagian dropdown shows ALL items instead of filtered

**Cause:** Form initially loads ALL Level 2 items into queryset

**Fix:** In form `__init__`, set Level 2 queryset to `.none()`:
```python
self.fields['aset_departemen_sub'].queryset = AsetDepartemen.objects.none()
```

### Issue 4: Form Shows Wrong Dropdowns for User

**Symptoms:** Teknik user sees Operasional dropdowns (or vice versa)

**Cause:** `is_teknik` check broken

**Fix:** Verify user.departemen is set and check string comparison:
```python
is_teknik = (
    user_departemen is not None and 
    user_departemen.nama_departemen.strip().lower() == 'teknik'
)
```

---

## 7. Database Management

### 7.1 Adding New Assets

**Via Django Admin Panel:**
1. Go to Core > Daftar Aset Mesin or Daftar Aset Departemen
2. Click "Add Aset Mesin" / "Add Aset Departemen"
3. Fill Name and select Parent
4. Save (MPPT auto-calculates level)

**Via Management Command (Bulk):**
```python
# Create in Python shell
from core.models import AsetDepartemen, Departemen

operasional = Departemen.objects.get(nama_departemen='Operasional')
parent = AsetDepartemen.objects.create(nama='MySection', departemen=operasional, parent=None)
child = AsetDepartemen.objects.create(nama='MySubsection', departemen=operasional, parent=parent)
```

### 7.2 Verifying Tree Structure

```python
# In Django shell
from core.models import AsetDepartemen

# Get all Level 0 items
level0 = AsetDepartemen.objects.filter(level=0)

# Get children of specific item
children = AsetDepartemen.objects.filter(parent_id=X)

# Get full tree for specific departemen
operasional_tree = AsetDepartemen.objects.filter(departemen__nama_departemen='Operasional')
```

---

## 8. Performance Considerations

### 8.1 Database Queries

- `AsetDepartemen.objects.filter(level=0)` - Used on page load (low cost)
- `AsetDepartemen.objects.filter(parent_id=X)` - Called via AJAX per dropdown change (minimal cost)

**Optimization:** Consider adding `select_related('departemen')` if needed in future.

### 8.2 Frontend Performance

- Cascading uses vanilla JavaScript (no jQuery dependency)
- AJAX requests are lightweight (only fetch id, nama, level)
- No page reload required

---

## 9. Testing Checklist

- [ ] Teknik user can select Line → Mesin → Sub Mesin
- [ ] Operasional user can select Departemen → Bagian → Sub Bagian
- [ ] Level 1 stays empty until Level 0 selected
- [ ] Level 2 stays empty until Level 1 selected
- [ ] Console has no errors when selecting dropdowns
- [ ] Network shows API requests going to `/api/aset-children/`
- [ ] API returns correct children based on parent_id
- [ ] Form submission saves correct aset reference

---

## 10. Future Enhancements

1. **Caching:** Add Redis cache for frequently accessed trees
2. **Search:** Add search/autocomplete for large trees
3. **Bulk Operations:** Management command to reorganize trees
4. **Audit Trail:** Log changes to tree structure
5. **Permissions:** Restrict who can add/edit assets by department

---

## 11. References

- **MPPT Library Docs:** https://django-mppt.readthedocs.io/
- **Django Models - ForeignKey:** https://docs.djangoproject.com/en/5.0/ref/models/fields/#foreignkey
- **Fetch API:** https://developer.mdn.org/en-US/docs/Web/API/Fetch_API

---

**Document Version:** 1.0  
**Last Update:** April 7, 2026  
**Author:** AI Assistant (GitHub Copilot)
