# PANDUAN IMPLEMENTASI DEPARTEMEN & BAGIAN
**Tanggal**: 6 Februari 2026  
**Status**: ✅ SELESAI & READY TO USE

---

## 📋 SUMMARY

Aplikasi sudah dilengkapi dengan sistem **Departemen & Bagian** untuk:
- **Hierarki organisasi**: Departemen (parent) → Bagian (child)
- **Access Control**: Membatasi akses fitur per departemen/bagian
- **UI Routing**: Tampilkan menu berbeda berdasarkan departemen user
- **Master Data**: Karyawan tetap terpisah, user yang dapat departemen/bagian

---

## 🎯 IMPLEMENTASI YANG SUDAH SELESAI

### ✅ 1. Models
- ✅ `Departemen` - Parent level
- ✅ `Bagian` - Child level (subordinat dari Departemen)
- ✅ `CustomUser` - Field `departemen` & `bagian` ForeignKey
- ✅ Auto-set departemen dari bagian di `save()` method

### ✅ 2. Database
- ✅ Migration dibuat: `0016_add_departemen_bagian`
- ✅ Migration sudah dijalankan (status OK)
- ✅ Indexes untuk performa optimal

### ✅ 3. Django Admin
- ✅ `DepartemenAdmin` - Full CRUD + inline bagian
- ✅ `BagianAdmin` - Full CRUD + filter departemen
- ✅ `CustomUserAdmin` - Update dengan field departemen & bagian
- ✅ Display bagus dengan color badges & jumlah anggota

### ✅ 4. Permission & Access Control
- ✅ File: `core/departemen_permissions.py`
- ✅ Helper functions (6 buah)
- ✅ Decorators (3 buah)
- ✅ Context processor helper functions

### ✅ 5. Template Context
- ✅ File: `core/context_processors.py`
- ✅ Function: `departemen_context()`
- ✅ Settings.py sudah terupdate

---

## 🚀 CARA MENGGUNAKAN

### **FASE 1: Setup Master Data (Django Admin)**

#### 1. Buka Django Admin
```
http://192.168.10.239:8000/admin/
```

#### 2. Tambah Departemen
1. Klik **"Daftar Departemen"** → **"+ Tambah"**
2. Isi:
   - Nama Departemen: `Teknik`
   - Kepala Departemen: (pilih user, misal Manager Nando)
   - Deskripsi: (opsional)
3. **Simpan**

Repeat untuk departemen lain: `Produksi`, `HR`, dll.

#### 3. Tambah Bagian
1. Klik **"Daftar Bagian"** → **"+ Tambah"**
2. Isi:
   - Nama Bagian: `Pemper`
   - Departemen: `Teknik` (pilih dari dropdown)
   - Kepala Bagian: (pilih user, misal Kepala Bagian Pemper)
   - Deskripsi: (opsional)
3. **Simpan**

Repeat untuk bagian lain: `Elektrik`, `Mekanik`, dll.

#### 4. Assign User ke Departemen & Bagian
1. Klik **"Daftar Pengguna"**
2. Click user yang ingin di-assign (misal: "asmawi")
3. Scroll ke section **"Informasi Organisasi"**
4. Isi:
   - Departemen: `Teknik` (pilih)
   - Bagian: `Pemper` (pilih dari bagian yang ada di Teknik)
   - **Otomatis**: departemen akan di-set ke `Teknik` (dari bagian)
5. **Simpan**

Contoh struktur:
```
Departemen: Teknik
├── Bagian: Pemper
│   ├── User: Nando (Manager Teknik)
│   ├── User: asmawi (Kepala Bagian Pemper)
│   └── User: you (SPV Pemper Elektrik FC)
├── Bagian: Elektrik
│   └── ...
```

---

### **FASE 2: Implementasi di Views (Django Code)**

#### A. PROTECT VIEW DENGAN DEPARTEMEN

```python
# core/views.py

from core.departemen_permissions import departemen_required

@departemen_required('Teknik')
def dashboard_teknik(request):
    """Hanya user dari Departemen Teknik bisa akses"""
    return render(request, 'dashboard_teknik.html')

@departemen_required(['Teknik', 'Produksi'])
def dashboard_teknologi(request):
    """User dari Departemen Teknik ATAU Produksi bisa akses"""
    return render(request, 'dashboard_teknologi.html')
```

#### B. PROTECT VIEW DENGAN BAGIAN

```python
from core.departemen_permissions import bagian_required

@bagian_required('Pemper')
def dashboard_pemper(request):
    """Hanya user dari Bagian Pemper bisa akses"""
    return render(request, 'dashboard_pemper.html')

@bagian_required(['Pemper', 'Elektrik'])
def dashboard_pemeliharaan(request):
    """User dari Bagian Pemper ATAU Elektrik bisa akses"""
    return render(request, 'dashboard_pemeliharaan.html')
```

#### C. CHECK PERMISSION DI LOGIC

```python
from core.departemen_permissions import (
    can_access_departemen,
    can_access_bagian,
    get_user_departemen,
    get_user_bagian,
    get_departemen_members,
    get_bagian_members
)

def some_view(request):
    user = request.user
    
    # Check access
    if can_access_departemen(user, 'Teknik'):
        # Lakukan sesuatu
        pass
    
    if can_access_bagian(user, 'Pemper'):
        # Lakukan sesuatu
        pass
    
    # Get info
    departemen = get_user_departemen(user)  # Departemen instance
    bagian = get_user_bagian(user)          # Bagian instance
    
    # Get members
    dept_members = get_departemen_members(departemen)
    bagian_members = get_bagian_members(bagian)
    
    return render(request, 'template.html', {
        'departemen': departemen,
        'bagian': bagian,
        'dept_members': dept_members,
    })
```

---

### **FASE 3: Implementasi di Template (HTML)**

#### A. CONDITIONAL MENU (Tampilkan menu sesuai departemen)

```django
<!-- templates/navbar.html -->

<nav>
  {% if user.is_authenticated %}
    
    <!-- Menu Umum -->
    <a href="{% url 'core:dashboard' %}">Dashboard</a>
    <a href="{% url 'core:project' %}">Project</a>
    
    <!-- Menu Departemen Teknik -->
    {% if departemen_menu_visibility.Teknik %}
      <a href="{% url 'core:dashboard_teknik' %}">📊 Dashboard Teknik</a>
      <a href="{% url 'core:maintenance_report' %}">🔧 Maintenance Report</a>
    {% endif %}
    
    <!-- Menu Departemen Produksi -->
    {% if departemen_menu_visibility.Produksi %}
      <a href="{% url 'core:dashboard_produksi' %}">📊 Dashboard Produksi</a>
    {% endif %}
    
    <!-- Menu Bagian Pemper (sub-menu) -->
    {% if bagian_menu_visibility.Pemper %}
      <a href="{% url 'core:dashboard_pemper' %}">🔧 Dashboard Pemper</a>
      <a href="{% url 'core:preventive_pemper' %}">Preventive Jobs</a>
    {% endif %}
    
    <!-- Menu Bagian Elektrik (sub-menu) -->
    {% if bagian_menu_visibility.Elektrik %}
      <a href="{% url 'core:dashboard_elektrik' %}">💡 Dashboard Elektrik</a>
    {% endif %}
    
  {% endif %}
</nav>
```

#### B. DISPLAY USER DEPARTEMEN & BAGIAN

```django
<!-- templates/user_info.html -->

{% if user.is_authenticated %}
  <div class="user-card">
    <h3>{{ user.get_full_name }}</h3>
    <p>Jabatan: <strong>{{ user.jabatan }}</strong></p>
    
    {% if user.bagian %}
      <p>Bagian: <strong>{{ user.bagian.nama_bagian }}</strong></p>
    {% endif %}
    
    {% if user.departemen %}
      <p>Departemen: <strong>{{ user.departemen.nama_departemen }}</strong></p>
    {% endif %}
    
    <p>Atasan: <strong>{{ user.atasan }}</strong></p>
  </div>
{% endif %}
```

#### C. SHOW DATA DEPARTEMEN/BAGIAN

```django
<!-- templates/departemen_info.html -->

{% if user_departemen %}
  <div class="departemen-card">
    <h2>{{ user_departemen.nama_departemen }}</h2>
    <p>Kepala: <strong>{{ user_departemen.kepala_departemen }}</strong></p>
    
    <h3>Bagian dalam Departemen:</h3>
    <ul>
    {% for bagian in user_departemen.daftar_bagian.all %}
      <li>
        {{ bagian.nama_bagian }}
        - Kepala: {{ bagian.kepala_bagian }}
        - {{ bagian.anggota_bagian.count }} anggota
      </li>
    {% endfor %}
    </ul>
    
    <h3>Total Anggota Departemen: {{ user_departemen.anggota_departemen.count }}</h3>
  </div>
{% endif %}
```

---

## 📚 API REFERENCE

### **Permission Check Functions**

```python
can_access_departemen(user, required_departemen_names)
# Args: user (CustomUser), required_departemen_names (str atau list)
# Return: bool

can_access_bagian(user, required_bagian_names)
# Args: user (CustomUser), required_bagian_names (str atau list)
# Return: bool

get_user_departemen(user)
# Return: Departemen instance atau None

get_user_bagian(user)
# Return: Bagian instance atau None

get_accessible_bagians(user)
# Return: QuerySet of Bagian di departemen user

get_departemen_members(departemen)
# Return: QuerySet of CustomUser di departemen

get_bagian_members(bagian)
# Return: QuerySet of CustomUser di bagian
```

### **Decorators**

```python
@departemen_required('Teknik')
@departemen_required(['Teknik', 'Produksi'])

@bagian_required('Pemper')
@bagian_required(['Pemper', 'Elektrik'])

@departemen_and_bagian_required('Teknik', 'Pemper')
```

### **Template Context Variables**

```django
{{ user_departemen }}           <!-- Departemen instance -->
{{ user_bagian }}               <!-- Bagian instance -->
{{ user_bagians }}              <!-- QuerySet of Bagian di departemen user -->
{{ departemen_menu_visibility }} <!-- Dict: {'Teknik': True, 'Produksi': False, ...} -->
{{ bagian_menu_visibility }}     <!-- Dict: {'Pemper': True, 'Elektrik': False, ...} -->
```

---

## 🔒 SECURITY

### ✅ Implementasi
- Decorator `@login_required` otomatis ditambahkan
- User tanpa departemen/bagian otomatis forbidden
- QuerySet filtering otomatis per departemen/bagian
- Cache-aware untuk performa

### ⚠️ Notes
- User HARUS punya bagian atau departemen untuk akses fitur restricted
- Jika user dipindah departemen, cache akan otomatis invalidate
- Supervisor bisa akses fitur subordinate (via atasan hierarchy yang sudah ada)

---

## 📊 CONTOH REAL WORLD USAGE

### Skenario: Dashboard Teknik untuk Departemen Teknik

```python
# core/views.py

from django.shortcuts import render
from core.departemen_permissions import departemen_required
from core.models import CustomUser

@departemen_required('Teknik')
def dashboard_teknik(request):
    """
    Dashboard khusus untuk Departemen Teknik.
    Menampilkan data team, jobs, projects dari departemen Teknik.
    """
    user = request.user
    dept_members = user.departemen.anggota_departemen.all()
    
    context = {
        'dept_members': dept_members,
        'total_members': dept_members.count(),
        'bagian_list': user.departemen.daftar_bagian.all(),
    }
    return render(request, 'dashboard_teknik.html', context)
```

### Template untuk Dashboard Teknik

```django
<!-- templates/dashboard_teknik.html -->

<h1>Dashboard Departemen {{ user_departemen.nama_departemen }}</h1>

<div class="stats">
  <p>Total Anggota: {{ total_members }}</p>
</div>

<h2>Bagian dalam Departemen</h2>
<table>
  <tr>
    <th>Bagian</th>
    <th>Kepala Bagian</th>
    <th>Jumlah Anggota</th>
    <th>Actions</th>
  </tr>
  {% for bagian in bagian_list %}
  <tr>
    <td>{{ bagian.nama_bagian }}</td>
    <td>{{ bagian.kepala_bagian }}</td>
    <td>{{ bagian.anggota_bagian.count }}</td>
    <td>
      <a href="{% url 'core:bagian_detail' bagian.id %}">View</a>
    </td>
  </tr>
  {% endfor %}
</table>

<h2>Anggota Departemen</h2>
<ul>
{% for member in dept_members %}
  <li>
    {{ member.get_full_name }}
    - {{ member.jabatan }}
    {% if member.bagian %}
      ({{ member.bagian.nama_bagian }})
    {% endif %}
  </li>
{% endfor %}
</ul>
```

---

## 🎓 QUICK START CHECKLIST

- [ ] Django admin sudah buka di browser
- [ ] Tambah 2-3 Departemen (Teknik, Produksi, HR)
- [ ] Tambah 4-5 Bagian (Pemper, Elektrik di Teknik; etc)
- [ ] Assign user ke departemen & bagian
- [ ] Test decorator `@departemen_required` di view
- [ ] Test conditional menu di template
- [ ] Test context variables di template
- [ ] Verifikasi permission dengan user yang berbeda departemen

---

## 🐛 TROUBLESHOOTING

### Q: Bagian tidak muncul di dropdown saat assign user?
**A**: Pastikan Bagian sudah dibuat dan assigned ke Departemen yang benar.

### Q: User tidak bisa akses view meski departemennya benar?
**A**: Cek error log, pastikan decorator ditambahkan dengan benar. User harus login dulu.

### Q: Departemen tidak muncul di "Departemen Menu Visibility"?
**A**: Template context sudah di-setup. Cek browser cache, clear cookies jika perlu.

### Q: Mau menghapus departemen tapi ada user?
**A**: Hapus assignment user dari departemen/bagian terlebih dahulu, atau set ke null.

---

## 📞 NEXT STEPS

1. **Test via Django Admin** - Setup master data departemen & bagian
2. **Test Views dengan @departemen_required** - Pastikan access control berfungsi
3. **Update Navbar** - Tambah conditional menu sesuai departemen user
4. **Update Dashboard** - Tampilkan data per departemen/bagian
5. **Testing Comprehensive** - Test dengan user dari berbagai departemen

---

**Status**: ✅ **READY TO USE**

File-file yang sudah diupdate:
- ✅ `core/models.py` - Departemen, Bagian models
- ✅ `core/admin.py` - Admin registration
- ✅ `core/departemen_permissions.py` - NEW! Permission helpers & decorators
- ✅ `core/context_processors.py` - NEW! Context processor
- ✅ `config/settings.py` - Context processor registration

Semua siap di-integrate dengan views & templates Anda!
