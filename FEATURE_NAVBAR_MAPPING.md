# Feature & Navbar Mapping Document

## Overview
Setiap fitur di `DepartemenFeature` mewakili menu/link tertentu di navbar. Mapping ini menunjukkan relasi antara feature key, nama menu, dan URL.

---

## Feature ke Menu Mapping

| # | Feature Key | Navbar Label | URL/Route | Type | Catatan |
|----|------------|------------|-----------|------|---------|
| 1 | **dashboard** | Dashboard | `core:dashboard` | Link | Icon: `bi-grid-fill` |
| 2 | **job** | Export Jobs | `core:job_per_day` | Link | Icon: `bi-file-pdf` (PDF icon) |
| 3 | **job** | Export Jobs Trial | `preventive_jobs:job_per_day_trial` | Link | Icon: `bi-file-pdf` + TRIAL badge |
| 4 | **preventive_jobs** | Preventive | `preventive_jobs:index` | Link | Icon: `bi-lightning-charge-fill` |
| 5 | **meetings** | Meetings | `meetings:meeting-list` | Link | Icon: `bi-chat-left-text` |
| 6 | **inventory** | Inventory (Dropdown) | - | Dropdown Parent | Icon: `bi-box-seam` |
| 6a | **inventory** | → Daftar Barang | `inventory:barang-list` | Link (dalam dropdown) | Icon: `bi-list-check` |
| 6b | **toolkeeper** | → Tool Keeper | `toolkeeper:peminjaman-list` | Link (dalam dropdown) | Icon: `bi-tools` |
| 6c | **inventory** | → Import Barang | `inventory:barang-import` | Link (dalam dropdown, staff only) | Icon: `bi-upload` |
| 7 | **project** | Daftar Project | `core:manajemen_project` | Link | Icon: `bi-diagram-3-fill` |
| 8 | **maintenance_report** | *BELUM DIMAP* | *TBD* | *TBD* | Tidak ada di navbar saat ini |
| 9 | **analytics** | *BELUM DIMAP* | *TBD* | *TBD* | Tidak ada di navbar saat ini |
| 10 | **settings** | *BELUM DIMAP* | *TBD* | *TBD* | Tidak ada di navbar saat ini |
| X | **ijin_cuti** | Ijin/Cuti | `core:leave_event` | Link | **BELUM DIKONDISIONALKAN** - tampil untuk semua |

---

## Menu yang SUDAH dikondisionalkan (dengan {% if %})

✅ **Dashboard** - `{% if user_features.dashboard %}`
✅ **Preventive** - `{% if user_features.preventive_jobs %}`
✅ **Meetings** - `{% if user_features.meetings %}`
✅ **Inventory (dropdown + submenu)** - `{% if user_features.inventory %}`
✅ **Daftar Project** - `{% if user_features.project %}`
✅ **Export Jobs (both)** - `{% if user_features.job %}`

---

## Menu yang BELUM dikondisionalkan ⚠️

❌ **Ijin/Cuti** - Line 279-283 - **Perlu ditambah `{% if user_features.??? %}`**
  - Saat ini tampil untuk semua user tanpa conditional
  - Feature key yang sesuai: bisa pakai fitur existing atau buat baru?

❌ **Admin Panel** - Line 275-279 - **Conditional berbeda**
  - Hanya untuk `is_staff` or `is_superuser` (bukan berdasarkan feature)
  - Ini mungkin perlu tetap begini atau diganti?

❌ **Mode toggle (staff only)** - Line 272-274 - **Conditional berbeda**
  - Hanya untuk `is_staff` or `is_superuser` (bukan berdasarkan feature)

❌ **Notification Bell (Overdue Jobs)** - Line 290+ - **Conditional berbeda**
  - Selalu tampil (tidak feature-gated)
  - Ini penting untuk semua user

---

## Features yang BELUM punya Menu Item

| Feature Key | Status | URL | Plan |
|-------------|--------|-----|------|
| **maintenance_report** | ❌ Tidak ada | TBD | Perlu buat? |
| **analytics** | ❌ Tidak ada | TBD | Perlu buat? |
| **settings** | ❌ Tidak ada | TBD | Perlu buat? |

---

## Module Selector (pojok kiri atas)

```html
<!-- DROPDOWN MODULE SELECTOR -->
Manajemen Pekerjaan (main module)
├── Manajemen Pekerjaan (core:dashboard)
└── Meetings & Notulen (meetings:meeting-list)
```

**Status:** 🟡 PARTIAL - dropdown module selector **tidak dikondisionalkan**
- Kedua item selalu tampil
- Mungkin perlu conditional juga?

---

## Pertanyaan untuk Anda

1. **Ijin/Cuti menu** - Feature mana yang seharusnya gate menu ini?
   - Pakai existing feature atau buat baru?

2. **Features tanpa menu**:
   - `maintenance_report` - apakah ada halaman untuk ini?
   - `analytics` - apakah ada halaman untuk ini?
   - `settings` - apakah ada halaman untuk ini?
   - Jika ada, perlu tambah menu item di navbar?

3. **Module selector** - apakah perlu dikondisionalkan juga?
   - Atau selalu tampil?

4. **Admin Panel & Mode toggle** - apakah tetap pakai `is_staff` check?
   - Atau diganti dengan feature permission?

---

## Next Steps (Setelah Anda Jawab)

1. Tambah conditional ke Ijin/Cuti (setelah tahu feature key-nya)
2. Tambah menu items untuk features yang belum punya (maintenance_report, analytics, settings)
3. Decide tentang Module Selector - perlu conditional?
4. Test lagi setelah semua update
