# Alur Kerja Meetings (Notulen Rapat) 📋

## Overview
Aplikasi Meetings membantu Anda mengelola notulen rapat, peserta, dan presensi dengan fitur QR Code untuk check-in eksternal.

---

## Alur Kerja Lengkap

### **1️⃣ BUAT MEETING BARU**
**Status: DRAFT** (kuning)

**Menu**: Meetings → Create

**Yang perlu diisi:**
- ✅ Tanggal Meeting
- ✅ Waktu Mulai & Selesai
- ✅ Tempat
- ✅ Agenda
- ✅ Peserta (minimal 1 orang)

**Hasil**: Meeting dalam status **DRAFT** - masih bisa diubah

---

### **2️⃣ KELOLA PESERTA** (OPSIONAL)
**Status tetap: DRAFT**

**Peserta ada 2 tipe:**

#### a) **Peserta Internal** (User Sistem)
- Klik **+ Tambah Peserta**
- Pilih dari list karyawan yang sudah terdaftar
- Status presensi bisa diubah: Hadir, Izin, Alpa

#### b) **Peserta External** (Via QR Code)
- Nanti scan QR saat rapat berlangsung
- Otomatis tercatat di system

---

### **3️⃣ ATUR NOTULEN ITEMS (ACTION ITEMS)** ⭐ **PENTING**
**Status tetap: DRAFT**

**Klik**: "+ Tambah Item" atau "+ Tambah Item" di bagian Notulen Items

**Untuk setiap action item, isi:**
- 📝 **Pokok Bahasan**: Hasil diskusi/keputusan yang dicapai
- 💬 **Tanggapan** (opsional): Detail/penjelasan lebih lanjut
- 👤 **PIC** (Person In Charge): Siapa yang bertanggung jawab
- 📅 **Target Deadline**: Kapan harus selesai

**Fitur Edit & Hapus:**
- Klik ✏️ untuk edit item (form akan ter-populate dengan data)
- Klik 🗑️ untuk hapus item

---

### **4️⃣ SETUP QR CODE (OPSIONAL)** 📱
**Status tetap: DRAFT**

**Kapan digunakan:**
- Jika ada peserta eksternal yang perlu check-in via QR
- Atau untuk dokumentasi kehadiran otomatis

**Langkah:**
1. Scroll ke bagian **"QR Code Presensi"** (kolom kanan)
2. Klik **"Generate QR"** (jika belum ada)
3. QR Code akan muncul
4. Klik **"Aktifkan QR"** untuk enable presensi external
5. Bagikan link atau tampilkan QR full-screen dengan tombol **"Fullscreen"**

**Status QR Code:**
- 🟢 **Aktif**: Peserta bisa scan dan check-in
- 🟡 **Nonaktif**: QR code ada tapi tidak bisa scan

---

### **5️⃣ FINALIZE MEETING** ✅
**Status berubah: DRAFT → FINAL** (biru)

**Klik**: Tombol hijau **"Finalisir"**

**Validasi:**
- ✅ Minimal ada 1 peserta
- ✅ Semua field meeting sudah diisi
- ✅ Notulen items lengkap (opsional)

**Apa yang berubah:**
- Meeting tidak bisa diedit lagi (tombol Edit hilang)
- Peserta dan notulen items tidak bisa ditambah/dihapus
- Bisa ditampilkan untuk review

---

### **6️⃣ CLOSE MEETING** 🔒
**Status berubah: FINAL → CLOSED** (abu-abu)

**Klik**: Tombol abu-abu **"Tutup Meeting"**

**Prasyarat:**
- Status HARUS **FINAL** (sudah di-finalize)
- Semua notulen items sudah **DONE**

**Apa yang berubah:**
- Meeting completely locked
- Tidak ada akses untuk edit lagi
- Data tersimpan sebagai archive

---

## Status Meeting

| Status | Warna | Keterangan | Bisa Edit? |
|--------|-------|-----------|-----------|
| **DRAFT** | 🟡 Kuning | Sedang diisi, masih bisa diubah | ✅ Ya |
| **FINAL** | 🔵 Biru | Sudah finalize, siap review | ❌ Tidak |
| **CLOSED** | ⚫ Abu-abu | Selesai dan archived | ❌ Tidak |

---

## Status Notulen Items

| Status | Warna | Arti |
|--------|-------|------|
| **Open** | 🟡 Kuning | Baru dibuat, belum dikerjakan |
| **Progress** | 🔵 Biru | Sedang dikerjakan |
| **Done** | 🟢 Hijau | Selesai |
| **Overdue** | 🔴 Merah | Sudah lewat deadline, belum selesai |

---

## Checklist Sebelum Finalize

- [ ] Tanggal, waktu, tempat sudah diisi
- [ ] Agenda sudah lengkap
- [ ] Peserta minimal 1 orang
- [ ] Semua notulen items sudah dicatat
- [ ] PIC untuk tiap item sudah ditentukan
- [ ] Deadline item sudah di-set

---

## FAQ

### **Q: Apakah HARUS finalize?**
**A**: Ya, untuk lock meeting dan prevent perubahan tidak sengaja. Setelah finalize, meeting tidak bisa diedit.

### **Q: Bisa kembali dari FINAL ke DRAFT?**
**A**: Tidak. Alasan: untuk maintain data integrity dan audit trail. Jika perlu ubah, hapus dan buat baru (jika masih DRAFT).

### **Q: QR Code buat apa?**
**A**: Untuk presensi external/vendor/tamu. Mereka scan QR → isi nama/identitas → otomatis masuk daftar kehadiran.

### **Q: Dimana lihat meeting yang sudah closed?**
**A**: Meetings → List → Filter Status = "Closed"

### **Q: Bagaimana flow notulen item menjadi pekerjaan?**
**A**: 
1. Setiap notulen item adalah action item (PIC bertanggung jawab)
2. Sistem bisa auto-create Job dari notulen item (fitur forthcoming)
3. PIC bisa track status via Job Management

---

## Shortcut Tips

- **Meetings**: Main menu → Meetings
- **Create Meeting**: Meetings → Create
- **Detail Meeting**: Meetings → List → Klik nama meeting
- **Edit Peserta**: Detail Meeting → Peserta → + Tambah
- **Edit Notulen**: Detail Meeting → Notulen Items → Edit
- **Generate QR**: Detail Meeting → QR Code Card → Generate QR
- **Finalize**: Detail Meeting → Tombol Finalisir ✅

---

## Troubleshooting

### **QR Code tidak muncul**
- Pastikan sudah klik **"Generate QR"**
- Refresh halaman (F5)
- Cek apakah ada permission error di console browser

### **Tidak bisa edit notulen**
- Pastikan meeting masih status **DRAFT**
- Hanya creator meeting yang bisa edit
- QR Code tidak di-relate dengan permission edit

### **Peserta tidak bisa di-add**
- Peserta sudah ada di list kehadiran
- User harus active di system (not disabled)

### **Tidak bisa finalize**
- Pastikan minimal ada 1 peserta
- Refresh dan coba lagi

---

**Pertanyaan atau saran?** Hubungi tim support atau buat issue di system. 

Good luck with your meetings! 🎉
