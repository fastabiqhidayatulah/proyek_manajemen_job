# 🚀 SETUP NGROK - PANDUAN LENGKAP

## 📥 STEP 1: Download Ngrok

### Option A: Download dari Website (Recommended)
1. Buka: https://ngrok.com/download
2. Pilih sistem operasi Anda (Windows)
3. Download file ZIP

### Option B: Via Chocolatey (Jika sudah install)
```powershell
choco install ngrok
```

---

## 📦 STEP 2: Extract & Setup

### Windows:

**Cara 1: Extract ke Program Files**
```powershell
# Extract ngrok-stable-windows-amd64.zip ke folder
C:\Program Files\ngrok

# Atau ke folder lain, tapi ingat pathnya
```

**Cara 2: Extract ke Project Folder**
```powershell
# Extract ke project folder
cd \\192.168.10.239\proyek_management_job
# Extract ngrok.exe ke folder ini
```

---

## 🔑 STEP 3: Setup Authentication (Optional tapi Recommended)

Buat akun Ngrok gratis:
1. Buka: https://dashboard.ngrok.com/signup
2. Sign up dengan email
3. Verify email
4. Login ke dashboard
5. Cari "Your Authtoken" di halaman dashboard
6. Copy token

**Add token ke config:**
```powershell
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

---

## 🌐 STEP 4: Start Ngrok

### Buka Terminal Baru:
```powershell
# Arahkan ke folder ngrok
cd C:\Program Files\ngrok
# atau lokasi extract Anda

# Jalankan ngrok
ngrok http 4321
```

### Output yang akan muncul:
```
ngrok                                       (Ctrl+C to quit)

Session Status                online
Account                       [your-email]@gmail.com (Plan: Free)
Version                       3.3.5
Region                        jp (Japan)
Forwarding                    https://xxxx-xxxx-xxxx.ngrok.io -> http://localhost:4321
Forwarding                    http://xxxx-xxxx-xxxx.ngrok.io -> http://localhost:4321

Connections                   ttl     opn     dl      in      out
                              0       0       0       0       0
```

### ⭐ COPY URL INI:
```
https://xxxx-xxxx-xxxx.ngrok.io
```

---

## 🔧 STEP 5: Set Django PUBLIC_URL

Sekarang kita harus set `DJANGO_PUBLIC_URL` ke URL Ngrok yang baru.

### Option A: Via Environment Variable (Recommended)

**PowerShell:**
```powershell
# Set environment variable untuk session saat ini
$env:DJANGO_PUBLIC_URL="https://xxxx-xxxx-xxxx.ngrok.io"

# Verify
$env:DJANGO_PUBLIC_URL
# Output: https://xxxx-xxxx-xxxx.ngrok.io
```

**Permanent (Windows):**
1. Search "Environment Variables" di Windows
2. Klik "Edit the system environment variables"
3. Klik "Environment Variables..."
4. Klik "New..." (di bagian User variables)
5. Variable name: `DJANGO_PUBLIC_URL`
6. Variable value: `https://xxxx-xxxx-xxxx.ngrok.io`
7. Klik OK → OK → OK
8. Restart Terminal/CMD

### Option B: Edit settings.py Langsung

File: `config/settings.py`

```python
# Cari baris ini:
DJANGO_PUBLIC_URL = os.environ.get('DJANGO_PUBLIC_URL', 'http://192.168.10.239:4321')

# Ubah ke:
DJANGO_PUBLIC_URL = 'https://xxxx-xxxx-xxxx.ngrok.io'
```

---

## ▶️ STEP 6: Restart Django Server

```powershell
# Stop server yang running (Ctrl+C)

# Start ulang
cd \\192.168.10.239\proyek_management_job
python manage.py runserver 0.0.0.0:4321
```

---

## ✅ STEP 7: Verify Setup

### Test 1: Akses via Ngrok URL
```
Buka browser: https://xxxx-xxxx-xxxx.ngrok.io/

Harusnya melihat halaman Django atau redirect ke login
```

### Test 2: Share Modal
```
Buka: https://xxxx-xxxx-xxxx.ngrok.io/preventive/execution/1/detail/

Klik "📤 KIRIM CHECKLIST VIA WHATSAPP"
Preview pesan harusnya punya link: https://xxxx-xxxx-xxxx.ngrok.io/preventive/checklist-fill/token/
```

### Test 3: Kirim ke WhatsApp
```
Di modal:
- Pilih penerima
- Klik "KIRIM VIA FONTTE API"
- Terima pesan di WA
- Link di pesan harusnya: https://xxxx-xxxx-xxxx.ngrok.io/...
```

### Test 4: Buka Link dari WA
```
Klik link di pesan WA
Form checklist harusnya terbuka
Isi form → Submit
Success message harusnya muncul
```

---

## 📋 CHECKLIST SETUP NGROK

- [ ] Download ngrok
- [ ] Extract ngrok.exe
- [ ] (Optional) Setup auth token
- [ ] Run: `ngrok http 4321`
- [ ] Copy URL dari output
- [ ] Set DJANGO_PUBLIC_URL ke URL Ngrok
- [ ] Restart Django server
- [ ] Verifikasi akses via Ngrok URL
- [ ] Test send checklist via WA

---

## ⚠️ PENTING: Setiap Restart Ngrok

Setiap kali Anda restart Ngrok atau server berhenti, URL akan berubah!

### Ngrok URL Berubah Kapan:
- ✓ Setiap kali run `ngrok http 4321` (jika pakai free plan)
- ✓ Setelah session timeout

### Solusi:

**Option 1: Set Auth Token (Recommended)**
- Daftar akun Ngrok gratis
- Set auth token
- URL akan lebih stabil (tapi tetap bisa berubah)

**Option 2: Pakai Reserved Domain (Premium)**
- Upgrade ke paid plan
- Dapatkan URL permanen
- Tidak perlu update setiap kali

**Option 3: Update Manual (Free & Simple)**
- Setiap restart Ngrok, update DJANGO_PUBLIC_URL
- Set environment variable baru
- Restart Django

---

## 🔄 WORKFLOW SEHARI-HARI

```
Pagi (Start Development):
1. Buka Terminal 1 - Ngrok
   ngrok http 4321
   (Lihat URL: https://xxxx.ngrok.io)

2. Set env variable
   $env:DJANGO_PUBLIC_URL="https://xxxx.ngrok.io"

3. Buka Terminal 2 - Django
   python manage.py runserver 0.0.0.0:4321

4. Test akses:
   Buka: https://xxxx.ngrok.io

Siang (Kirim Checklist):
1. Buka execution detail
2. Klik share button
3. Verify preview punya URL Ngrok
4. Send ke WA
5. Penerima akses via Ngrok URL

Sore (Restart):
- Jika perlu restart Ngrok → update URL di Django
- Jika perlu restart Django → tidak perlu update URL
```

---

## 🆘 TROUBLESHOOTING

### Problem: "Connection refused"
```
Error: Failed to complete tunnel connection
Solution:
- Django server harus running
- Port 4321 harus listening
- Check: netstat -ano | findstr :4321
```

### Problem: "URL Ngrok tidak valid"
```
Error: SSL certificate problem
Solution:
- Verify URL format: https://xxxx-xxxx-xxxx.ngrok.io (HTTPS!)
- Check DJANGO_PUBLIC_URL di settings
- Ngrok output harus show "https://"
```

### Problem: "Pesan WA punya URL localhost"
```
Issue: Share link punya "http://localhost:4321" bukan Ngrok URL
Solution:
- DJANGO_PUBLIC_URL belum di-set
- Verify: $env:DJANGO_PUBLIC_URL
- Set ulang jika kosong
- Restart Django server
```

### Problem: "Form tidak muncul saat klik link WA"
```
Kemungkinan:
1. Token sudah expired (7 hari)
2. URL Ngrok berubah tapi DB masih punya URL lama
3. Network issue

Solution:
- Generate share link baru
- Verifikasi link di database:
  SELECT share_link FROM preventive_jobs_checklistresult;
```

### Problem: Ngrok running tapi Django tidak akses
```
Error: Connection timeout
Solution:
- Check firewalls
- Verify Django running on 0.0.0.0:4321 (bukan 127.0.0.1)
- Check: python manage.py runserver 0.0.0.0:4321
```

---

## 📊 NGROK DASHBOARD

Setelah login, bisa lihat:
- https://dashboard.ngrok.com

Fitur:
- ✅ View active sessions
- ✅ See traffic/requests
- ✅ Monitor connections
- ✅ Check auth token

---

## 🎯 FINAL CHECKLIST

```
✅ Ngrok installed & running
✅ DJANGO_PUBLIC_URL set ke Ngrok URL
✅ Django server restarted
✅ Can access via Ngrok URL
✅ Share modal shows Ngrok URL in preview
✅ Tested send to WhatsApp
✅ Received pesan WA dengan link
✅ Clicked link → form opened
✅ Filled form → submitted
✅ Success message → PIC got notification
```

---

## 💡 TIPS

1. **Auto-set URL**: Buat script PowerShell untuk auto-extract URL Ngrok
2. **Monitor Traffic**: Gunakan Ngrok dashboard untuk lihat request
3. **Debug**: Check Ngrok logs untuk connection issues
4. **Security**: Jangan share Ngrok URL publik, hanya ke tim
5. **HTTPS**: Selalu gunakan HTTPS (Ngrok default)

---

**Status: READY TO USE** 🟢

Setelah setup selesai, test kirim checklist ke nomor WA Anda sendiri! 📱

Ada issue? Check troubleshooting di atas atau message! 💬
