# Konfigurasi NGROK untuk QR Code External Access 🚀

## Problem
Ketika peserta scan QR code dari smartphone eksternal/mobile network, URL `http://localhost:4321` tidak bisa diakses karena localhost hanya valid di device lokal.

## Solution
Gunakan NGROK untuk forward port lokal ke public URL yang bisa diakses dari mana saja.

---

## Setup NGROK

### 1. **Ensure NGROK running**
```powershell
# Check jika ngrok sudah berjalan
netstat -ano | findstr :4040

# Jika belum, start ngrok (pointing to port 4321)
ngrok http 4321
```

Output akan seperti:
```
Forwarding       https://one-chimp-hardly.ngrok-free.app -> http://localhost:4321
```

### 2. **Copy NGROK URL**
Ambil URL yang muncul, contoh:
```
https://one-chimp-hardly.ngrok-free.app
```

---

## Konfigurasi Django

### Option A: Via Environment Variable (RECOMMENDED)
```powershell
# Set environment variable sebelum run Django
$env:DJANGO_PUBLIC_URL="https://one-chimp-hardly.ngrok-free.app"

# Atau Linux/Mac:
export DJANGO_PUBLIC_URL="https://one-chimp-hardly.ngrok-free.app"

# Kemudian run server
python manage.py runserver 0.0.0.0:4321
```

### Option B: Direct Edit settings.py
Edit `config/settings.py`:
```python
DJANGO_PUBLIC_URL = 'https://one-chimp-hardly.ngrok-free.app'
```

**CATATAN:** Option A lebih fleksibel karena NGROK URL bisa berubah setiap kali restart.

---

## Testing

### 1. **Generate QR Code via Detail Meeting**
- Buka Meeting Detail
- Klik "Generate QR" button
- QR code akan muncul

### 2. **Check Embedded URL**
Setiap QR code sekarang contain:
```
https://one-chimp-hardly.ngrok-free.app/meetings/presensi/[token-uuid]
```

Bukan:
```
http://localhost:4321/meetings/presensi/[token-uuid]  ❌ (ini tidak bisa dari eksternal)
```

### 3. **Test dari Smartphone**
- Ambil smartphone (bukan di network yang sama)
- Buka camera/QR scanner app
- Scan QR code
- Seharusnya buka form presensi (dengan NGROK URL)

---

## Troubleshooting

### **Q: QR code masih mengarah ke localhost?**
A: Refresh page browser, clear cache, atau regenerate QR code.

### **Q: NGROK URL berubah setiap kali?**
A: 
- NGROK free plan punya URL yang berubah setiap restart
- Atau upgrade ke NGROK paid untuk custom domain
- **Solusi**: Selalu update `DJANGO_PUBLIC_URL` environment variable saat NGROK restart

### **Q: Bagaimana jika NGROK disconnect?**
A:
- NGROK session expired/timeout
- Restart NGROK dengan command `ngrok http 4321` lagi
- Copy URL baru
- Update environment variable
- Regenerate QR code

### **Q: Peserta masih tidak bisa akses?**
Checklist:
- ✅ NGROK running? (`ngrok http 4321`)
- ✅ Django server running? (`python manage.py runserver 0.0.0.0:4321`)
- ✅ DJANGO_PUBLIC_URL di-set ke URL NGROK?
- ✅ QR Code sudah di-generate SETELAH set DJANGO_PUBLIC_URL?
- ✅ CSRF_TRUSTED_ORIGINS include NGROK domain? (should be auto)
- ✅ Peserta pakai mobile network (bukan WiFi lokal)?

---

## DJANGO Settings yang Relevant

Sudah auto-configure di `config/settings.py`:

```python
# Public URL untuk QR code, external forms, dll
DJANGO_PUBLIC_URL = os.environ.get('DJANGO_PUBLIC_URL', 'https://one-chimp-hardly.ngrok-free.app')

# CSRF trusted origins - allow NGROK domain
CSRF_TRUSTED_ORIGINS = [
    'https://one-chimp-hardly.ngrok-free.app',
    'https://*.ngrok-free.app',
    'http://192.168.10.239:4321',
    'http://localhost:4321',
    'http://127.0.0.1:4321',
]
```

Jadi tidak perlu config manual, NGROK domain sudah trusted.

---

## Workflow Lengkap

```
1. Start NGROK
   └─ ngrok http 4321
   └─ Copy URL: https://one-chimp-hardly.ngrok-free.app

2. Set Environment Variable (PowerShell)
   └─ $env:DJANGO_PUBLIC_URL="https://one-chimp-hardly.ngrok-free.app"

3. Run Django Server
   └─ python manage.py runserver 0.0.0.0:4321

4. Generate QR Code
   └─ Meeting Detail → Generate QR
   └─ QR now contains NGROK URL

5. Test Scan
   └─ Smartphone scan QR
   └─ Form presensi terbuka via NGROK URL

6. Submit Form
   └─ Peserta tercatat di database
   └─ Status: HADIR
```

---

## Notes

- **Security**: NGROK akan show warning tentang public access. Ini normal untuk dev/testing.
- **Production**: Gunakan domain yang proper + SSL certificate, bukan NGROK.
- **Multiple URLs**: Jika perlu change NGROK URL sering, buat script automation.
- **Batch QR Generation**: Setelah setup NGROK, regenerate semua QR codes yang sudah existing.

---

**Happy testing with QR codes! 🎉**
