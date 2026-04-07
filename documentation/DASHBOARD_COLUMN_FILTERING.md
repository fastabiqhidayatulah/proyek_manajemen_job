# Dashboard Column Filtering Implementation

## Overview

Implemented conditional column display in the dashboard job tables to show different asset hierarchies based on user's department:

- **Teknik Users** → Display **Line | Mesin | Sub Mesin** columns
- **Operasional & Other Departments** → Display **Departemen | Bagian | Sub Bagian** columns

**Date Implemented:** April 7, 2026  
**Status:** ✅ Complete

---

## Changes Made

### 1. Backend - Dashboard View (`core/views.py`)

**Added Context Variable:**
```python
# === DETERMINE USER DEPARTEMEN TYPE (TEKNIK vs OPERASIONAL, etc) ===
user_departemen = user.departemen
is_teknik = (
    user_departemen is not None and
    user_departemen.nama_departemen.strip().lower() == 'teknik'
)
# ===================================================================
```

**Added to Context Dictionary:**
```python
context = {
    'user': user,
    'is_teknik': is_teknik,  # NEW: For conditional column display
    # ... other context variables
}
```

**Why?**
- Context variable `is_teknik` is passed to both template and included templates
- Determines which asset columns to display based on user's department
- Uses same logic as JobForm for consistency

### 2. Frontend - Job Table Template (`templates/job_table.html`)

#### Table Headers - Conditional Rendering

**Teknik Users (is_teknik=True):**
```html
<th>Line</th>
<th>Mesin</th>
<th>Sub Mesin</th>
```

**Operasional & Other (is_teknik=False):**
```html
<th>Departemen</th>
<th>Bagian</th>
<th>Sub Bagian</th>
```

#### Table Data - Conditional Asset Display

**Teknik Users:**
```html
{% if data.aset %}
    {% if data.aset.level == 0 %}
        <!-- Line level -->
        <td><strong>{{ data.aset.nama }}</strong></td>
        <td class="text-muted">-</td>
        <td class="text-muted">-</td>
    {% elif data.aset.level == 1 %}
        <!-- Mesin level -->
        <td>{{ data.aset.parent.nama|default:'-' }}</td>
        <td><strong>{{ data.aset.nama }}</strong></td>
        <td class="text-muted">-</td>
    {% elif data.aset.level == 2 %}
        <!-- Sub Mesin level -->
        <td>{{ data.aset.parent.parent.nama|default:'-' }}</td>
        <td>{{ data.aset.parent.nama|default:'-' }}</td>
        <td><strong>{{ data.aset.nama }}</strong></td>
    {% endif %}
{% endif %}
```

**Operasional & Other:**
```html
{% if data.aset_departemen %}
    {% if data.aset_departemen.level == 0 %}
        <!-- Departemen level -->
        <td><strong>{{ data.aset_departemen.nama }}</strong></td>
        <td class="text-muted">-</td>
        <td class="text-muted">-</td>
    {% elif data.aset_departemen.level == 1 %}
        <!-- Bagian level -->
        <td>{{ data.aset_departemen.parent.nama|default:'-' }}</td>
        <td><strong>{{ data.aset_departemen.nama }}</strong></td>
        <td class="text-muted">-</td>
    {% elif data.aset_departemen.level == 2 %}
        <!-- Sub Bagian level -->
        <td>{{ data.aset_departemen.parent.parent.nama|default:'-' }}</td>
        <td>{{ data.aset_departemen.parent.nama|default:'-' }}</td>
        <td><strong>{{ data.aset_departemen.nama }}</strong></td>
    {% endif %}
{% endif %}
```

---

## How It Works

### Data Flow

```
User Logs In
    ↓
Django loads user.departemen
    ↓
dashboard_view checks if departemen is "Teknik"
    ↓
Sets is_teknik=True/False in context
    ↓
job_table.html receives is_teknik variable
    ↓
{% if is_teknik %} renders appropriate columns & data
    ↓
Dynamic table appears with correct asset hierarchy
```

### Asset Data Structure

**For Teknik (AsetMesin):**
```
Line (level=0) [Example: FC, AAC, FS 1]
  ├─ Mesin (level=1) [Example: Finishing Line, Coating]
  │   └─ Sub Mesin (level=2) [Example: Coating, Cutting]
```

**For Operasional & Others (AsetDepartemen):**
```
Departemen (level=0) [Example: Operasional]
  ├─ Bagian (level=1) [Example: Exim, GBBSC, GPJ]
  │   └─ Sub Bagian (level=2) [Example: Export & Import, Bahan Baku]
```

---

## Template Inheritance

The dashboard passes `is_teknik` context to included templates:

```django
{% with job_data=daily_job_data filter_params=filter_params %}
    {% include 'job_table.html' with job_type='daily' %}
{% endwith %}
```

Since `is_teknik` is in the main context, it's automatically available in the included `job_table.html` template.

---

## Testing Checklist

- [ ] Log in as **Teknik User** (u: admin_teknik or similar)
  - Dashboard should show: Line | Mesin | Sub Mesin columns
  - Asset values from AsetMesin hierarchy

- [ ] Log in as **Operasional User** (u: admin_operasional or similar)  
  - Dashboard should show: Departemen | Bagian | Sub Bagian columns
  - Asset values from AsetDepartemen hierarchy

- [ ] Verify **Daily Jobs** table columns match user type

- [ ] Verify **Project Jobs** table columns match user type

- [ ] Check **sorting** still works
  - Click column headers to sort by Teknik columns (for Teknik users)
  - Click column headers to sort by Departemen columns (for Operasional users)

- [ ] Check **filtering** still works
  - Filters shouldn't break with new conditional columns

---

## Known Limitations

1. **Sort Queries:** When Teknik user sorts by "Line", database must have indexed `aset__level` for performance
2. **Null Assets:** If job has neither `aset` nor `aset_departemen`, row shows all dashes (-)
3. **Mixed DataSets:** Cannot easily mix Teknik and Operasional jobs in same table (not applicable to current design)

---

## Future Enhancements

1. **Add Export Columns** - Also filter Excel/PDF exports by department
2. **Add Filter UI** - UI controls to filter by Departemen/Bagian (similar to Line/Mesin)
3. **Caching** - Cache `is_teknik` check in user model or session
4. **Dashboard Widgets** - Show Teknik/Operasional specific metrics

---

## Code Files Modified

1. **`core/views.py`**
   - Added `is_teknik` determination logic (~3 lines)
   - Added `is_teknik` to context dictionary (~1 line)

2. **`templates/job_table.html`**
   - Completely rewritten with conditional column display
   - Replaced static Line/Mesin/SubMesin columns with dynamic conditionals
   - Added Departemen/Bagian/SubBagian columns for non-Teknik users

---

## Testing Commands

**To test with Django shell:**
```python
from django.contrib.auth import get_user_model
from core.models import Departemen

User = get_user_model()

# Get Teknik user
teknik_user = User.objects.get(username='admin_teknik')
print(f"Is Teknik: {teknik_user.departemen.nama_departemen.lower() == 'teknik'}")

# Get Operasional user
operasional_user = User.objects.get(username='admin_operasional')
print(f"Is Teknik: {operasional_user.departemen.nama_departemen.lower() == 'teknik'}")
```

---

## Related Documentation

- [CASCADING_DROPDOWN_SYSTEM.md](./CASCADING_DROPDOWN_SYSTEM.md) - Asset hierarchy background
- [CASCADING_DROPDOWN_REFERENCE.md](./CASCADING_DROPDOWN_REFERENCE.md) - Implementation details

---

**Document Version:** 1.0  
**Last Updated:** April 7, 2026  
**Author:** AI Assistant
