# Cascading Dropdown System - Implementation Reference Guide

## Quick Reference for Developers

**For quick fixes and common tasks related to cascading dropdowns.**

---

## File Locations

| Component | File Path |
|-----------|-----------|
| Model Definitions | `core/models.py` (AsetMesin, AsetDepartemen) |
| Form Logic | `core/forms.py` (JobForm) |
| API Endpoint | `core/views.py` (api_aset_children) |
| Frontend UI | `templates/job_form.html` |
| Admin Panel | `core/admin.py` (AsetMesinAdmin, AsetDepartemenAdmin) |
| URL Routes | `core/urls.py` |

---

## Common Tasks

### Task 1: Add New Asset/Sub-Asset Branch

**Situation:** Need to add new Bagian (Level 1) under Operasional

**Steps:**
1. Go to Django admin: `/admin/core/asetdepartemen/`
2. Click "Add Aset Departemen"
3. Fill:
   - **Nama:** (e.g., "Quality Control")
   - **Departemen:** Operasional
   - **Parent:** Select Operasional (Level 0)
4. Save

**Result:** Level 1 item created, MPPT auto-calculates `level=1`

---

### Task 2: Fix Broken Cascade (Level 2 Empty)

**Symptom:** User selects Level 1, but Level 2 stays empty

**Debugging:**
```
Step 1: F12 Console → Check for red errors
Step 2: F12 Network → Look for /api/aset-children/ request
Step 3: Click Network request → Response tab → See JSON?
Step 4: If no request firing → Check event listener (null check might be missing)
Step 5: If request fires but returns empty → Check parent_id in database (parent-child relationships)
```

**Common Fix #1 - Null Check Missing:**
```javascript
// OLD (BROKEN)
bagianSelect.addEventListener('change', function() { ... });

// NEW (FIXED)
if (bagianSelect) {
    bagianSelect.addEventListener('change', function() { ... });
}
```

**Common Fix #2 - Wrong Parent-Child Relationship:**
```python
# In Django shell - verify relationships
from core.models import AsetDepartemen

# Check children of parent_id=24 (Operasional)
children = AsetDepartemen.objects.filter(parent_id=24)
for child in children:
    print(f"{child.nama} (level={child.level})")
    
# Check children of parent_id=3 (GBBSC)
subchildren = AsetDepartemen.objects.filter(parent_id=3)
for subchild in subchildren:
    print(f"  {subchild.nama} (level={subchild.level})")
```

---

### Task 3: Change Form Field Labels

**File:** `core/forms.py` (around lines 220-240)

**Example - Change "Bagian (Level 1)" to "Section":**
```python
# OLD
aset_departemen_bagian = forms.ModelChoiceField(
    queryset=AsetDepartemen.objects.none(),
    label="Bagian (Level 1)"  # ← Change this
)

# NEW
aset_departemen_bagian = forms.ModelChoiceField(
    queryset=AsetDepartemen.objects.none(),
    label="Section"
)
```

**Refresh browser and changes appear instantly.**

---

### Task 4: Add Required Validation

**Situation:** Want Level 1 selection to be mandatory if form rendered

**File:** `core/forms.py`

```python
# Change required=False to required=True
aset_departemen_bagian = forms.ModelChoiceField(
    queryset=AsetDepartemen.objects.none(),
    required=True,  # ← Change this
    label="Bagian"
)
```

**Note:** Restart Django server for changes to take effect.

---

### Task 5: Add New Department with Assets

**Situation:** New department "Maintenance" needs cascading dropdowns

**Steps:**

1. **Create Department (if not exists):**
   ```python
   # In Django shell
   from core.models import Departemen
   maintenance = Departemen.objects.create(
       nama_departemen='Maintenance',
       # ... other fields
   )
   ```

2. **Create Level 0 Asset:**
   ```python
   from core.models import AsetDepartemen
   
   aset_l0 = AsetDepartemen.objects.create(
       nama='Maintenance',
       departemen=maintenance,
       parent=None  # Level 0 has no parent
   )
   ```

3. **Create Level 1 Assets:**
   ```python
   aset_l1_1 = AsetDepartemen.objects.create(
       nama='Preventive Maintenance',
       departemen=maintenance,
       parent=aset_l0
   )
   ```

4. **Create Level 2 Assets:**
   ```python
   aset_l2_1 = AsetDepartemen.objects.create(
       nama='Equipment Inspection',
       departemen=maintenance,
       parent=aset_l1_1
   )
   ```

5. **Verify in Admin:**
   - Go to `/admin/core/asetdepartemen/`
   - Drag-drop to organize (if using drag_tree)
   - Check levels are correct (L0=0, L1=1, L2=2)

6. **Test Cascade:**
   - User from Maintenance logs in
   - Create new job
   - Should see Maintenance → Preventive Maintenance → Equipment Inspection

---

### Task 6: Debug JavaScript Event Listeners

**File:** `templates/job_form.html`

**Common Pattern - Check What's Executing:**
```javascript
// Add console.log to trace execution
departemenSelect.addEventListener('change', function() {
    console.log('Departemen changed to:', this.value);  // ← Add this
    loadDepartemenChildren(this.value, bagianSelect, null);
});

bagianSelect.addEventListener('change', function() {
    console.log('Bagian changed to:', this.value);  // ← Add this
    loadDepartemenChildren(this.value, subBagianSelect, null);
});
```

**Open F12 Console, select dropdowns, see console.log output.**

---

### Task 7: Modify API Response

**Situation:** API returns id, nama, level but you need additional fields

**File:** `core/views.py` (~line 580)

```python
# OLD
def api_aset_children(request):
    parent_id = request.GET.get('parent_id')
    children = AsetDepartemen.objects.filter(parent_id=parent_id).values('id', 'nama', 'level')
    return JsonResponse(list(children), safe=False)

# NEW - Add department info
def api_aset_children(request):
    parent_id = request.GET.get('parent_id')
    children = AsetDepartemen.objects.filter(
        parent_id=parent_id
    ).values('id', 'nama', 'level', 'departemen__nama_departemen')  # ← Add this
    return JsonResponse(list(children), safe=False)
```

**Response now includes department name:**
```json
[
  {"id": 2, "nama": "Exim", "level": 1, "departemen__nama_departemen": "Operasional"}
]
```

---

## Code Snippets

### Snippet 1: Get Department Assets Programmatically

```python
from core.models import AsetDepartemen, Departemen

def get_department_tree(department_name):
    """Get full asset tree for specific department"""
    dept = Departemen.objects.get(nama_departemen=department_name)
    return AsetDepartemen.objects.filter(departemen=dept).order_by('level')

# Usage
operasional_assets = get_department_tree('Operasional')
for asset in operasional_assets:
    print(f"{'  ' * asset.level}{asset.nama} (L{asset.level})")
```

### Snippet 2: Validate Cascade Structure

```python
def validate_cascade_structure(departemen):
    """Check if department has correct L0→L1→L2 structure"""
    level_0 = AsetDepartemen.objects.filter(departemen=departemen, level=0)
    
    for l0 in level_0:
        print(f"✓ {l0.nama} (L0)")
        level_1 = AsetDepartemen.objects.filter(departemen=departemen, parent=l0)
        for l1 in level_1:
            print(f"  ├─ {l1.nama} (L1)")
            level_2 = AsetDepartemen.objects.filter(departemen=departemen, parent=l1)
            for l2 in level_2:
                print(f"  │  └─ {l2.nama} (L2)")

# Usage
validate_cascade_structure(Departemen.objects.get(nama_departemen='Operasional'))
```

### Snippet 3: JavaScript - Manual Cascade Test

```javascript
// Paste in F12 Console to manually test cascade

// Test 1: Get children of parent_id=24
fetch('/api/aset-children/?parent_id=24')
    .then(r => r.json())
    .then(data => console.log('Children of 24:', data));

// Test 2: Check HTML elements exist
console.log('Departemen select:', document.getElementById('id_aset_departemen_display'));
console.log('Bagian select:', document.getElementById('id_aset_departemen_bagian'));

// Test 3: Manually trigger change
document.getElementById('id_aset_departemen_display').value = '24';
document.getElementById('id_aset_departemen_display').dispatchEvent(new Event('change'));
```

---

## Critical Code Locations (By Issue)

| Issue | File | Line Range | Fix |
|-------|------|-----------|-----|
| Cascading not firing | `templates/job_form.html` | ~509-530 | Check null condition before addEventListener |
| Level 2 shows all items | `core/forms.py` | ~250 | Change queryset to `.none()` |
| Wrong API format | `core/views.py` | ~590 | Ensure `safe=False` in JsonResponse |
| Wrong form fields display | `core/forms.py` | ~100-120 | Check `is_teknik` logic |
| Parent-child broken | `core/admin.py` | Tree drag-drop | Use admin panel to manually verify |

---

## Testing Cascade Locally

### Test Case 1: Operasional User Cascade

```
1. Log in as Operasional user
2. Go to Create Job page
3. Verify form shows:
   - Departemen dropdown (should be hidden/not selected)
   - Bagian dropdown (should be empty)
   - Sub Bagian dropdown (should be empty)
   - AsetMesin fields (should be hidden)
   
4. Select "Operasional" in Departemen → Should see Level 1 items appear
5. Select "GBBSC" in Bagian → Should see "Bahan Baku", "Suku Cadang" in Sub Bagian
6. Console should show NO errors
7. Network tab should show request to `/api/aset-children/?parent_id=3`
```

### Test Case 2: Teknik User Cascade

```
1. Log in as Teknik user
2. Go to Create Job page
3. Verify form shows:
   - Line dropdown (should show Level 0 items: FC, AAC, FS 1, etc.)
   - Mesin dropdown (should be empty)
   - Sub Mesin dropdown (should be empty)
   - AsetDepartemen fields (should be hidden)

4. Select "FC" in Line → Should see Level 1 items appear
5. Select "Finishing Line" in Mesin → Should see Sub Mesin items
6. Console should show NO errors
7. Network tab should show request to `/ajax/load-children/?parent_id=X`
```

---

## Debugging Console Commands

When cascade not working, paste these in F12 Console:

```javascript
// Check if selects exist
console.log('Departemen:', document.getElementById('id_aset_departemen_display'));
console.log('Bagian:', document.getElementById('id_aset_departemen_bagian'));
console.log('Sub Bagian:', document.getElementById('id_aset_departemen_sub'));

// Manually call API
fetch('/api/aset-children/?parent_id=24').then(r => r.json()).then(d => console.log(d));

// Check if event listeners attached
// (Libraries like jQuery can capture this, but vanilla JS requires breakpoints)
```

---

## Related Documentation

- [CASCADING_DROPDOWN_SYSTEM.md](./CASCADING_DROPDOWN_SYSTEM.md) - Full system architecture
- [FEATURE_PERMISSION_MANAGEMENT_GUIDE.md](./FEATURE_PERMISSION_MANAGEMENT_GUIDE.md) - How user permissions affect field visibility
- [README.md](../README.md) - Project overview

---

**Last Updated:** April 7, 2026  
**Quick Reference Version:** 1.0
