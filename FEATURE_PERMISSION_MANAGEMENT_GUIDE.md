# FEATURE PERMISSION MANAGEMENT - LENGKAP ✅
**Tanggal**: 6 Februari 2026  
**Status**: READY TO USE

---

## 📋 OVERVIEW

Sekarang Anda bisa **mengatur menu/fitur mana saja yang bisa diakses per departemen** melalui Django Admin dengan interface checkbox yang user-friendly.

### **Konsep**
```
Departemen Teknik
├── ☑ Dashboard (enabled)
├── ☑ Project Management (enabled)
├── ☑ Preventive Jobs (enabled)
└── ☐ Analytics (disabled)

Departemen HR
├── ☑ Dashboard (enabled)
├── ☑ Meetings & Notulen (enabled)
└── ☐ Preventive Jobs (disabled)
```

---

## 🎯 FITUR YANG BISA DIKONTROL

List fitur yang bisa di-enable/disable per departemen:

| Feature Key | Display Name |
|------------|--------------|
| `dashboard` | Dashboard |
| `project` | Project Management |
| `job` | Job Management |
| `preventive_jobs` | Preventive Jobs |
| `maintenance_report` | Maintenance Report |
| `inventory` | Inventory Management |
| `toolkeeper` | Toolkeeper |
| `meetings` | Meetings & Notulen |
| `analytics` | Analytics & Reports |
| `settings` | Settings |

---

## 🚀 CARA SETUP

### **Step 1: Generate Default Features (Optional)**

Jalankan command untuk auto-generate permission records untuk semua departemen:

```bash
python manage.py setup_departemen_features
```

**Output:**
```
✓ Created: Teknik - Dashboard
✓ Created: Teknik - Project Management
...
✅ Setup Complete!
Created: 60 records
Skipped: 0 records (already exist)
```

**Note**: Command ini hanya perlu dijalankan sekali. Setiap departemen akan mendapat akses ke semua fitur secara default.

---

### **Step 2: Manage Features di Django Admin**

#### **Via Departemen Edit Page** (Recommended)

1. **Buka Django Admin**
   ```
   http://192.168.10.239:4321/admin/core/departemen/
   ```

2. **Click Edit Departemen** (misal: "Teknik")

3. **Scroll ke section "Daftar Departemen Feature Permission"**
   ```
   DAFTAR DEPARTEMEN FEATURE PERMISSION
   
   [ ] Dashboard              [✓] Aktif
   [ ] Project Management     [✓] Aktif
   [X] Preventive Jobs        [✓] Aktif
   [ ] Analytics              [ ] Aktif
   ...
   ```

4. **Check/Uncheck checkbox untuk enable/disable fitur**
   - ✓ = Departemen bisa akses fitur ini
   - ☐ = Departemen TIDAK bisa akses fitur ini

5. **Klik "SIMPAN"**

#### **Via Dedicated Feature Permission Page** (Alternative)

1. **Buka Django Admin**
   ```
   http://192.168.10.239:4321/admin/core/departemenfeature/
   ```

2. **List semua permission records**
   ```
   Departemen | Feature | Aktif | Created
   Teknik     | Dashboard | ✓   | 6 Feb
   Teknik     | Project | ✓   | 6 Feb
   HR         | Meetings | ✓   | 6 Feb
   ...
   ```

3. **Click untuk edit individual record jika perlu**

---

## 💻 CARA MENGGUNAKAN DI VIEWS & TEMPLATES

### **A. PROTECT VIEW DENGAN @feature_required DECORATOR**

```python
# core/views.py

from core.departemen_permissions import feature_required

@feature_required('dashboard')
def dashboard_view(request):
    """
    Hanya user yang departemennya enable 'dashboard' feature
    bisa akses halaman ini
    """
    return render(request, 'dashboard.html')

@feature_required('preventive_jobs')
def preventive_dashboard(request):
    """Hanya user dari departemen dengan preventive_jobs enabled"""
    return render(request, 'preventive/dashboard.html')

@feature_required('analytics')
def analytics_report(request):
    """Hanya user dari departemen dengan analytics enabled"""
    return render(request, 'analytics/report.html')
```

**Behavior**:
- User akses view → Django check apakah departemennya punya permission
- Jika tidak ada permission → **403 Forbidden** error
- Jika ada permission → View execute normally

---

### **B. CONDITIONAL MENU DI TEMPLATE**

#### **Via user_features Context Variable** (Recommended)

```django
<!-- templates/navbar.html -->

<nav class="navbar">
  
  <!-- Always show -->
  <a href="{% url 'core:dashboard' %}">Home</a>
  
  <!-- Show hanya jika user bisa akses dashboard -->
  {% if user_features.dashboard %}
    <a href="{% url 'core:dashboard' %}">
      <i class="bi bi-speedometer2"></i> Dashboard
    </a>
  {% endif %}
  
  <!-- Show hanya jika user bisa akses project -->
  {% if user_features.project %}
    <a href="{% url 'core:project' %}">
      <i class="bi bi-folder"></i> Project Management
    </a>
  {% endif %}
  
  <!-- Show hanya jika user bisa akses preventive jobs -->
  {% if user_features.preventive_jobs %}
    <a href="{% url 'preventive:dashboard' %}">
      <i class="bi bi-tools"></i> Preventive Jobs
    </a>
  {% endif %}
  
  <!-- Show hanya jika user bisa akses inventory -->
  {% if user_features.inventory %}
    <a href="{% url 'inventory:list' %}">
      <i class="bi bi-box"></i> Inventory
    </a>
  {% endif %}
  
  <!-- Show hanya jika user bisa akses analytics -->
  {% if user_features.analytics %}
    <a href="{% url 'core:analytics' %}">
      <i class="bi bi-bar-chart"></i> Analytics
    </a>
  {% endif %}
  
</nav>
```

**Result**:
- User dari Departemen Teknik dengan dashboard, project, preventive_jobs enabled
  → akan lihat 3 menu (Dashboard, Project, Preventive Jobs)
  
- User dari Departemen HR dengan hanya dashboard, meetings enabled
  → akan lihat hanya Dashboard (project & preventive hidden)

---

### **C. CHECK PERMISSION DI VIEW LOGIC**

```python
from core.departemen_permissions import user_has_feature_access

def some_view(request):
    user = request.user
    
    # Check fitur per fitur
    if user_has_feature_access(user, 'dashboard'):
        # User bisa akses dashboard
        dashboard_data = get_dashboard_data()
    
    if user_has_feature_access(user, 'analytics'):
        # User bisa akses analytics
        analytics_data = get_analytics_data()
    
    # Get semua features user bisa akses
    from core.departemen_permissions import get_user_allowed_features
    user_features = get_user_allowed_features(user)
    
    context = {
        'features': user_features,
        'dashboard_visible': user_features['dashboard'],
        'analytics_visible': user_features['analytics'],
    }
    return render(request, 'template.html', context)
```

---

## 📱 CONTOH REAL WORLD USAGE

### **Skenario 1: Departemen Teknik hanya boleh akses Dashboard & Preventive**

1. **Buka Departemen Teknik** di Django Admin

2. **Di section "Daftar Departemen Feature Permission"**:
   ```
   [X] Dashboard                [✓] Aktif
   [ ] Project Management       [ ] Aktif
   [X] Preventive Jobs          [✓] Aktif
   [ ] Analytics                [ ] Aktif
   [ ] Inventory                [ ] Aktif
   ...
   ```

3. **Result**: User dari Teknik hanya bisa:
   - Akses `/dashboard/`
   - Akses `/preventive/`
   - Menu project, inventory, analytics TERSEMBUNYI

---

### **Skenario 2: Departemen HR dapat akses semuanya**

1. **Buka Departemen HR** di Django Admin

2. **Di section "Daftar Departemen Feature Permission"**, check semua:
   ```
   [X] Dashboard                [✓] Aktif
   [X] Project Management       [✓] Aktif
   [X] Meetings & Notulen       [✓] Aktif
   [X] Analytics                [✓] Aktif
   ...
   ```

3. **Result**: User dari HR bisa akses semua menu & fitur

---

## 🔐 IMPLEMENTATION CHECKLIST

- [ ] Jalankan `python manage.py setup_departemen_features`
- [ ] Buka Django Admin → Daftar Departemen
- [ ] Edit setiap departemen → Atur feature permission dengan checkbox
- [ ] Add `@feature_required()` decorator ke critical views
- [ ] Update navbar/menu template untuk conditional rendering
- [ ] Test dengan user dari berbagai departemen

---

## 📊 TEMPLATE CONTEXT VARIABLES

```django
{{ user_features }}           <!-- Dict: {'dashboard': True, 'project': False, ...} -->
{{ user_features.dashboard }}  <!-- True/False -->
{{ user_features.project }}    <!-- True/False -->
{{ user_features.preventive_jobs }} <!-- True/False -->
{{ user_features.analytics }}  <!-- True/False -->
...
```

---

## 🎓 API REFERENCE

### **Functions**

```python
# Check single feature
user_has_feature_access(user, 'dashboard')  # True/False

# Get all allowed features
get_user_allowed_features(user)  # Dict: {'dashboard': True, ...}

# Invalidate cache after permission change
invalidate_feature_cache(departemen)  # Call setelah update permission
```

### **Decorators**

```python
@feature_required('dashboard')
def my_view(request):
    ...

@feature_required('preventive_jobs')
def another_view(request):
    ...
```

---

## 🔄 CACHING

- Feature permission di-cache selama **5 menit** untuk performa
- Setiap update permission di admin → cache otomatis di-invalidate
- Cache key: `feature_access_{departemen_id}_{feature_key}`

---

## 🐛 TROUBLESHOOTING

### Q: Feature permission tidak muncul di Django Admin?
**A**: 
1. Pastikan sudah jalankan migration: `python manage.py migrate`
2. Pastikan DepartemenFeature di-register di admin
3. Refresh page

### Q: Decorator tidak berfungsi?
**A**:
1. Pastikan user sudah login (`@login_required` built-in)
2. Pastikan user punya departemen assignment
3. Cek Django Admin bahwa feature di-enable untuk departemen user
4. Clear browser cache

### Q: Menu masih muncul padahal feature disabled?
**A**:
1. Check template logic: `{% if user_features.dashboard %}`
2. Pastikan context processor `departemen_context` di-load
3. Clear browser cache

### Q: Feature permission cache tidak update?
**A**:
1. Manual clear cache: `python manage.py shell`
   ```python
   from django.core.cache import cache
   cache.clear()  # Clear all cache
   ```
2. Atau restart Django server

---

## 📌 IMPORTANT NOTES

1. **Default State**: Ketika departemen baru dibuat, semua fitur akan DISABLED sampai diaktifkan secara manual atau menjalankan setup command

2. **Multiple Features**: Jika view memerlukan multiple permissions:
   ```python
   @feature_required('dashboard')
   @feature_required('project')
   def combined_view(request):
       # User harus punya BOTH permissions
       ...
   ```

3. **Performance**: Feature permission di-cache, jadi check permission sangat cepat

4. **Admin Flexibility**: Admin bisa enable/disable fitur per departemen real-time tanpa coding

---

## 🎯 NEXT STEPS

1. **Setup default features** → Jalankan management command
2. **Configure departemen permissions** → Edit di Django Admin
3. **Update views** → Tambah `@feature_required()` decorator
4. **Update templates** → Add conditional `{% if user_features.xxx %}`
5. **Test** → Verify dengan user dari berbagai departemen

---

**Status**: ✅ **FULLY IMPLEMENTED & READY TO USE**

Sistem feature permission management siap digunakan di production! 🚀
