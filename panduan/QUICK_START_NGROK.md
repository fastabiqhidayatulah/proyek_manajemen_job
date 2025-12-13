# 🚀 QUICK START - NGROK SETUP (5 MENIT)

## ⚡ SUPER CEPAT (Copy-Paste)

### Terminal 1 - Ngrok
```powershell
# Jalankan di PowerShell/CMD
ngrok http 4321
```

**Lihat output:**
```
Forwarding    https://xxxx-xxxx-xxxx.ngrok.io -> http://localhost:4321
```

**COPY URL INI** → `https://xxxx-xxxx-xxxx.ngrok.io`

---

### Terminal 2 - Set Environment & Django

```powershell
# Set environment variable
$env:DJANGO_PUBLIC_URL="https://xxxx-xxxx-xxxx.ngrok.io"
# (Ganti dengan URL dari Terminal 1)

# Verify
$env:DJANGO_PUBLIC_URL
# Output: https://xxxx-xxxx-xxxx.ngrok.io

# Masuk folder project
cd \\192.168.10.239\proyek_management_job

# Start Django
python manage.py runserver 0.0.0.0:4321
```

---

## ✅ TEST (1 MENIT)

### 1. Akses via Browser
```
Buka: https://xxxx-xxxx-xxxx.ngrok.io
# Harusnya muncul halaman Django atau login page
```

### 2. Test Share Modal
```
Buka: https://xxxx-xxxx-xxxx.ngrok.io/preventive/execution/1/detail/
Klik: "📤 KIRIM CHECKLIST VIA WHATSAPP"
Preview: Harusnya punya URL Ngrok (bukan localhost)
```

### 3. Send Test Message
```
Di modal:
- Pilih 1 penerima (Anda sendiri)
- Klik "KIRIM VIA FONTTE API"
- Cek WhatsApp
- Klik link → form checklist terbuka
- Isi form → Submit
```

---

## 🎯 SELESAI!

Jika semua berhasil → Ngrok setup OK ✅

---

## ⚠️ COMMON ISSUES

| Issue | Solusi |
|-------|--------|
| "Connection refused" | Pastikan Django running (Terminal 2) |
| "URL punya localhost" | DJANGO_PUBLIC_URL tidak set atau Django belum restart |
| "Form tidak muncul" | Token expired atau URL berubah |
| "Pesan tidak terkirim" | Check Fontte token di settings |

---

## 📝 NOTES

- **Ngrok URL berubah setiap restart** (pakai free plan)
- **Setiap update URL** → restart Django
- **Link berlaku 7 hari** dari saat generate
- **Test pakai nomor WA sendiri** dulu

---

**Status: READY TO GO** 🟢

Ada issue? Check NGROK_SETUP_GUIDE.md 📖
