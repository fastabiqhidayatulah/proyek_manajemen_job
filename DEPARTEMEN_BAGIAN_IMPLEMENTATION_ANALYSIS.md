# ANALISIS IMPLEMENTASI DEPARTEMEN & BAGIAN
**Tanggal**: 6 Februari 2026  
**Status**: FEASIBLE ✅ - Dapat Diimplementasikan

---

## 📋 RINGKASAN PERMINTAAN
Menambahkan struktur **Departemen** dan **Bagian** untuk mendukung:
1. Hierarki organisasi: **Bagian** (subordinat) → **Departemen** (atasan)
2. Contoh: SPV Pemper Elektrik FC → Kepala Bagian Pemper → Manager Teknik
3. Mengikat user ke departemen/bagian
4. **Access Control Menu**: Menu spesifik hanya bisa diakses departemen tertentu

---

## 🔍 ANALISIS STRUKTUR APLIKASI SAAT INI

### 1. **User & Hierarki yang Sudah Ada**
```
CustomUser (Model Login)
├── jabatan (FK → Jabatan) ✅ Sudah ada
├── atasan (FK → self) ✅ Sudah ada
├── bawahan (M2M via atasan) ✅ Berfungsi dengan cache
└── get_all_subordinates() ✅ Recursive dengan circular ref prevention
```

**Status**: ✅ **Sistem hierarki user sudah SOLID & TERUJI**

---

### 2. **Model Karyawan (Master Data)**
```python
class Karyawan(models.Model):
    nik              → String (unique)
    nama_lengkap     → String
    departemen       → CharField (HARDCODED TEXT) ⚠️
    posisi           → CharField (HARDCODED TEXT) ⚠️
    status           → Choice field (Aktif/Tidak Aktif/Cuti/Keluar)
```

**Status**: ⚠️ **Departemen saat ini hanya TEXT, bukan FK**

---

### 3. **Meeting Peserta (External Participant)**
```python
class MeetingPeserta(models.Model):
    ...
    bagian = models.CharField(max_length=255, blank=True, null=True)
    # Ini hanya untuk external peserta (scan QR), bukan internal system
```

**Status**: ℹ️ **Bagian di meetings hanya untuk eksternal, tidak terikat dengan user**

---

### 4. **Sistem Akses Existing**
```
Project.can_access(user)      → Cek owner + shared + hierarki bidirectional ✅
Project.can_manage(user)      → Full bidirectional access ✅
get_user_accessible_projects() → Cache-aware filtering ✅
```

**Status**: ✅ **Sistem akses sudah sophisticated, bisa diluaskan untuk departemen**

---

## ✨ REKOMENDASI IMPLEMENTASI

### **OPSI A: STRUKTUR BARU (RECOMMENDED)**
Membuat model Departemen & Bagian baru yang terstruktur.

#### **Diagram Hierarki:**
```
Departemen (Parent)
    ├── nama_departemen (Teknik)
    ├── kepala_departemen (FK → CustomUser, Manager Teknik)
    └── daftar_bagian

        Bagian (Child)
            ├── nama_bagian (Pemper)
            ├── kepala_bagian (FK → CustomUser, Kepala Bagian Pemper)
            ├── departemen (FK → Departemen)
            └── daftar_user

                CustomUser
                    ├── jabatan (SPV Pemper Elektrik FC)
                    ├── atasan (FK → Kepala Bagian) ✅ Already linked
                    └── departemen (FK → Departemen, auto from bagian)
                        bagian (FK → Bagian)
```

#### **Model yang Perlu Ditambah:**

```python
# 1. Departemen (Parent Level)
class Departemen(models.Model):
    nama_departemen = models.CharField(max_length=100, unique=True)
    kepala_departemen = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departemen_dipimpin'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Departemen"
        verbose_name_plural = "Daftar Departemen"
    
    def __str__(self):
        return self.nama_departemen

# 2. Bagian (Child Level - Subordinate dari Departemen)
class Bagian(models.Model):
    nama_bagian = models.CharField(max_length=100)
    departemen = models.ForeignKey(
        Departemen,
        on_delete=models.CASCADE,
        related_name='daftar_bagian'
    )
    kepala_bagian = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bagian_dipimpin'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Bagian"
        verbose_name_plural = "Daftar Bagian"
        unique_together = ('departemen', 'nama_bagian')
    
    def __str__(self):
        return f"{self.nama_bagian} ({self.departemen.nama_departemen})"

# 3. Update CustomUser
class CustomUser(AbstractUser):
    # ... existing fields ...
    departemen = models.ForeignKey(
        Departemen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anggota_departemen'
    )
    bagian = models.ForeignKey(
        Bagian,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anggota_bagian'
    )
    
    def save(self, *args, **kwargs):
        # Auto-set departemen dari bagian jika bagian sudah set
        if self.bagian:
            self.departemen = self.bagian.departemen
        super().save(*args, **kwargs)
```

---

### **ALUR IMPLEMENTASI:**

#### **Fase 1: Create Models (1 hari)**
1. Buat `Departemen` model
2. Buat `Bagian` model
3. Update `CustomUser` dengan FK departemen & bagian
4. Buat migration
5. Jalankan migration

#### **Fase 2: Django Admin (0.5 hari)**
1. Register Departemen & Bagian di admin.py
2. Atur admin display & filtering
3. Tambah inline untuk Bagian dalam Departemen

#### **Fase 3: Update Views & Forms (2 hari)**
1. Update CustomUser form untuk select departemen/bagian
2. Update dashboard filter untuk filter by departemen/bagian
3. Tambah helper methods untuk departemen access

#### **Fase 4: Access Control / Permission Menu (2 hari)**
Implementasi 2 strategi:

**A. Decorator-based (Recommended):**
```python
@departemen_required(['Teknik', 'Produksi'])
def restricted_view(request):
    # Hanya user dari Teknik atau Produksi bisa akses
    ...

@bagian_required(['Pemper', 'Elektrik'])
def bagian_restricted_view(request):
    # Hanya user dari Bagian Pemper atau Elektrik bisa akses
    ...
```

**B. Template-based (Untuk Menu):**
```django
{% if user.departemen.nama_departemen == 'Teknik' %}
    <li><a href="{% url 'maintenance:dashboard' %}">Dashboard Teknik</a></li>
{% endif %}

{% if user.bagian.nama_bagian == 'Pemper' %}
    <li><a href="{% url 'preventive:dashboard' %}">Dashboard Preventive</a></li>
{% endif %}
```

#### **Fase 5: Update Karyawan Model (0.5 hari)**
Update Karyawan untuk FK departemen:
```python
class Karyawan(models.Model):
    # ...
    departemen = models.ForeignKey(
        Departemen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='karyawan'
    )
    bagian = models.ForeignKey(
        Bagian,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='karyawan'
    )
```

#### **Fase 6: Testing & Data Population (1 hari)**
1. Buat departemen & bagian master data
2. Assign user ke departemen/bagian
3. Test permission logic
4. Test menu visibility

---

## 📊 INTEGRASI DENGAN MODULE YANG ADA

### 1. **Core Module** ✅
- Dashboard: Tambahin filter departemen/bagian
- Project management: Access control departemen
- Job management: Filter by departemen

### 2. **Meetings Module** ✅
- Update MeetingPeserta untuk link ke Bagian model
- Auto-populate bagian dari CustomUser

### 3. **Preventive Jobs** ✅
- Dashboard bisa filter by departemen
- Access control untuk departemen tertentu

### 4. **Toolkeeper** ✅
- Pembatasan tool lending per departemen (future)

### 5. **Inventory** ✅
- Inventory bisa di-segregate per departemen
- Workshop vs Warehouse per departemen (future)

---

## 🔐 SECURITY CONSIDERATIONS

### ✅ Permission Checks
```python
def get_accessible_bagians(user):
    """User hanya bisa lihat bagian di departemennya"""
    if not user.departemen:
        return Bagian.objects.none()
    return user.departemen.daftar_bagian.all()

def can_access_departemen_feature(user, required_departemen):
    """Check departemen access"""
    if not user.departemen:
        return False
    return user.departemen.nama_departemen == required_departemen
```

### ⚠️ Edge Cases
- User tanpa departemen/bagian → tidak bisa akses restricted feature
- Supervisor + bawahan → inheritance dari atasan?
- Bagian dipindahkan departemen → kaskaiding update?

---

## ✅ KELEBIHAN OPSI A (RECOMMENDED)

1. **Terstruktur**: Hierarki jelas Departemen → Bagian → User
2. **Scalable**: Mudah menambah departemen/bagian baru
3. **Access Control**: Granular permission per departemen/bagian
4. **Backward Compatible**: Data Karyawan existing tetap bisa di-migrate
5. **Future-proof**: Support multi-departemen per user di masa depan (M2M)
6. **Master Data**: Referensi tunggal untuk departemen/bagian

---

## 🚀 NEXT STEPS

Apakah Anda ingin saya:

1. **Mulai implementasi langsung** dengan semua model & migration?
2. **Buat contoh data terlebih dahulu** untuk testing?
3. **Fokus ke bagian tertentu** (misal: hanya models + admin)?
4. **Tanyakan detail lebih lanjut** untuk permission logic?

---

**Kesimpulan**: ✅ **100% IMPLEMENTABLE dan RECOMMENDED**
Aplikasi Anda sudah memiliki fondasi yang solid untuk expand dengan departemen & bagian!
