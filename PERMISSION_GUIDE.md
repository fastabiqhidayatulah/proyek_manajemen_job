# FEATURE PERMISSION - QUICK START 🚀
**Implementasi Checkbox Menu per Departemen**

---

## ⚡ LANGKAH CEPAT (5 MENIT)

### **1. Setup Default Features**

Buka CMD dan jalankan:

```bash
(venv) D:\proyek_management_job>python manage.py setup_departemen_features
```

Selesai! Semua departemen sekarang punya default permission ke semua fitur.

---

### **2. Configure Departemen Permission**

**Buka Django Admin:**
```
http://192.168.10.239:4321/admin/core/departemen/
```

**Click Edit Departemen (misal "Teknik")**

**Scroll ke bawah, cari section:**
```
DAFTAR DEPARTEMEN FEATURE PERMISSION
```

**Checkbox mana fitur yang ingin di-AKTIFKAN:**
```
☑ Dashboard
☑ Project Management
☑ Preventive Jobs
☐ Analytics (disable dengan uncheck)
☐ Settings
```

**SIMPAN**

---

### **3. Update Navbar (Opsional tapi Recommended)**

Di `templates/base.html` atau navbar template Anda:

```django
<!-- DASHBOARD -->
{% if user_features.dashboard %}
  <li><a href="{% url 'core:dashboard' %}">Dashboard</a></li>
{% endif %}

<!-- PROJECT -->
{% if user_features.project %}
  <li><a href="{% url 'core:project' %}">Project</a></li>
{% endif %}

<!-- PREVENTIVE JOBS -->
{% if user_features.preventive_jobs %}
  <li><a href="{% url 'preventive:dashboard' %}">Preventive Jobs</a></li>
{% endif %}

<!-- ANALYTICS -->
{% if user_features.analytics %}
  <li><a href="{% url 'core:analytics' %}">Analytics</a></li>
{% endif %}
```

---

### **4. Test**

1. **Login sebagai user dari Departemen Teknik**
   - Hanya melihat: Dashboard, Project, Preventive Jobs
   - Analytics menu TERSEMBUNYI

2. **Login sebagai user dari Departemen HR**
   - Lihat semua menu (jika semua di-enable)

✅ **Selesai!**

---

## 📊 ADMIN INTERFACE

### **Departemen Edit Page**

```
┌─────────────────────────────────────────────────┐
│ Edit Departemen: Teknik                         │
├─────────────────────────────────────────────────┤
│ Informasi Departemen                            │
│ Nama Departemen: Teknik                         │
│ Deskripsi: [................]                   │
│                                                 │
│ Kepemimpinan                                    │
│ Kepala Departemen: [nando v]                    │
│                                                 │
│ DAFTAR BAGIAN                                   │
│ + Nama Bagian  | Kepala Bagian  | Deskripsi    │
│ [Pemper      ] | [asmawi   v  ] | [.......]    │
│ [Elektrik    ] | [...      v  ] | [.......]    │
│                                                 │
│ DAFTAR DEPARTEMEN FEATURE PERMISSION            │ ← NEW!
│ + Feature                | Aktif                │
│ ☑ Dashboard              | ☑ Aktif              │
│ ☑ Project Management     | ☑ Aktif              │
│ ☑ Preventive Jobs        | ☑ Aktif              │
│ ☐ Analytics & Reports    | ☐ Aktif              │
│ ☐ Inventory Management   | ☐ Aktif              │
│ ☑ Meetings & Notulen     | ☑ Aktif              │
│ ...                      | ...                 │
│                                                 │
│ [SIMPAN] [BATAL]                               │
└─────────────────────────────────────────────────┘
```

---

## 🎯 CONTOH IMPLEMENTASI

### **Navbar dengan Feature Permission**

```django
<!-- templates/base.html -->

<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container">
    <a class="navbar-brand" href="/">KERJA</a>
    
    <ul class="navbar-nav ms-auto">
      
      {# Dashboard - Always visible jika enabled #}
      {% if user_features.dashboard %}
        <li class="nav-item">
          <a class="nav-link" href="{% url 'core:dashboard' %}">
            <i class="bi bi-speedometer2"></i> Dashboard
          </a>
        </li>
      {% endif %}
      
      {# Project Menu - Only visible jika enabled #}
      {% if user_features.project %}
        <li class="nav-item">
          <a class="nav-link" href="{% url 'core:project' %}">
            <i class="bi bi-folder"></i> Project
          </a>
        </li>
      {% endif %}
      
      {# Preventive Jobs - Only visible jika enabled #}
      {% if user_features.preventive_jobs %}
        <li class="nav-item">
          <a class="nav-link" href="{% url 'preventive:dashboard' %}">
            <i class="bi bi-tools"></i> Preventive
          </a>
        </li>
      {% endif %}
      
      {# Analytics - Only visible jika enabled #}
      {% if user_features.analytics %}
        <li class="nav-item">
          <a class="nav-link" href="{% url 'core:analytics' %}">
            <i class="bi bi-bar-chart"></i> Analytics
          </a>
        </li>
      {% endif %}
      
    </ul>
  </div>
</nav>
```

### **Protect View dengan Decorator**

```python
# core/views.py

from core.departemen_permissions import feature_required

@feature_required('dashboard')
def dashboard_view(request):
    """Hanya departemen dengan dashboard feature enabled"""
    return render(request, 'dashboard.html')

@feature_required('preventive_jobs')
def preventive_dashboard(request):
    """Hanya departemen dengan preventive_jobs feature enabled"""
    jobs = PreventiveJob.objects.filter(pic=request.user)
    return render(request, 'preventive/dashboard.html', {'jobs': jobs})
```

---

## 📋 CHECKLIST

- [ ] Jalankan: `python manage.py setup_departemen_features`
- [ ] Buka Django Admin → Daftar Departemen
- [ ] Edit departemen → Setup checkbox feature permission
- [ ] Update navbar template dengan `{% if user_features.xxx %}`
- [ ] (Optional) Tambah `@feature_required()` ke critical views
- [ ] Test dengan login berbagai user

---

## 🔧 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Menu tidak hilang padahal disabled | Clear browser cache & check `{% if user_features.xxx %}` |
| @feature_required decorator error | Ensure user login & punya departemen assignment |
| Feature tidak muncul di admin | Run migrate & refresh page |
| Permission cache lama update | Clear: `python manage.py shell` → `cache.clear()` |

---

## 📞 REFERENCE

### **Context Variables Available in All Templates**

```django
{{ user_features }}              {# Dict of all features #}
{{ user_features.dashboard }}    {# True/False #}
{{ user_features.project }}      {# True/False #}
{{ user_features.preventive_jobs }} {# True/False #}
{{ user_features.analytics }}    {# True/False #}
{{ user_features.inventory }}    {# True/False #}
{{ user_features.meetings }}     {# True/False #}
{{ user_features.toolkeeper }}   {# True/False #}
{{ user_features.job }}          {# True/False #}
{{ user_features.maintenance_report }} {# True/False #}
{{ user_features.settings }}     {# True/False #}
```

---

**Status**: ✅ **READY TO USE**

Selamat! Fitur permission management sudah siap! 🎉
