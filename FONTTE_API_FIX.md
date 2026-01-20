# Panduan Fontte API Integration

## Status Perbaikan
- ✅ Fixed API endpoint: `/send` (bukan `/send-file`)
- ✅ Fixed parameter names: `target` (bukan `chat_id`)
- ✅ Added proper multipart form-data handling
- ✅ Added format instructions in template
- ✅ Created test script for debugging

## Format API Fontte yang Benar

### Dokumentasi Resmi
- URL Dasar: `https://api.fontte.com/v1`
- Endpoint untuk kirim file: `POST /send`
- Authentication: `Authorization: Bearer YOUR_TOKEN`

### Contoh Request (cURL)
```bash
curl -X POST https://api.fontte.com/v1/send \
  -H "Authorization: Bearer E6CwLwwzuP8Db6Dud5mn" \
  -F "target=628123456789-1234567890@g.us" \
  -F "file=@stock_report.pdf" \
  -F "caption=Laporan Stok"
```

### Parameter yang Benar
| Parameter | Tipe | Keterangan |
|-----------|------|-----------|
| target | string | ID grup/kontak WA (format: 628xxx-1234567890@g.us) |
| file | file | File yang akan dikirim (PDF, PNG, JPG, dll) |
| caption | string | Caption/keterangan untuk file (opsional) |

### Format Group ID di Fontte
Group ID di Fontte memiliki format:
```
628[NOMOR_WA]-[TIMESTAMP]@g.us
```

Contoh:
- Grup Chat: `628812345678-1234567890@g.us`
- Personal Chat: `628812345678@c.us`
- Broadcast: `12025551234@broadcast`

## Cara Mendapatkan Group ID

### Metode 1: Dari Fontte Dashboard
1. Login ke https://dashboard.fontte.com
2. Pilih menu "Chats" atau "Percakapan"
3. Klik pada grup WA yang ingin dituju
4. Copy "Chat ID" atau "Group ID" yang ditampilkan
5. Format akan terlihat: `628xxx-1234567890@g.us`

### Metode 2: Menggunakan Fontte API
```bash
curl -X GET https://api.fontte.com/v1/chats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "data": [
    {
      "id": "628812345678-1234567890@g.us",
      "name": "Nama Grup",
      "is_group": true
    }
  ]
}
```

## Troubleshooting

### Error: "Tidak bisa terhubung ke server Fontte"
- ❌ Mungkin endpoint salah (`/send-file` bukan `/send`)
- ✅ Gunakan: `https://api.fontte.com/v1/send`

### Error: "401 Unauthorized"
- ❌ Token tidak valid atau expired
- ✅ Check token di Fontte Dashboard
- ✅ Generate token baru jika diperlukan

### Error: "target field required"
- ❌ Parameter `chat_id` salah namanya
- ✅ Gunakan parameter: `target`

### Error: "File tidak ditemukan"
- ❌ Path file tidak benar
- ✅ Pastikan file sudah di-generate di lokasi temp

### Error: "Invalid target format"
- ❌ Format Group ID salah
- ✅ Format yang benar: `628xxx-1234567890@g.us` atau `628xxx@c.us`
- ✅ Jangan gunakan hanya nomor: `62812345678` ❌

## Testing

Gunakan script test yang sudah disediakan:
```bash
python test_fontte_connection.py
```

Script akan test:
1. Koneksi dasar ke API
2. Mengirim pesan teks
3. Mengirim file
4. Mendapatkan info device

## Perubahan Kode yang Dilakukan

### File: `inventory/views.py`
- Function `send_pdf_to_fontte()`:
  - Ubah endpoint: `/send-file` → `/send`
  - Ubah parameter: `chat_id` → `target`
  - Tambah parameter: `caption` untuk deskripsi file
  - Add JSON response parsing

### File: `templates/inventory/stock_export_setting.html`
- Tambah format instructions untuk Group ID
- Tambah info cara mendapatkan Group ID
- Simplify UI untuk manual group entry

## Next Steps

1. ✅ Fix API format - DONE
2. ⏳ Test dengan real Fontte account
3. ⏳ Fix JavaScript untuk display groups (belum di-fix)
4. ⏳ Implement Celery task scheduler untuk auto-send
5. ⏳ Add error handling & retry logic

## Testing Checklist

- [ ] Buka halaman `/inventory/export-setting/`
- [ ] Masukkan Group ID dengan format: `628xxx-1234567890@g.us`
- [ ] Masukkan Nama Grup
- [ ] Klik "Tambah Grup"
- [ ] Grup muncul di "Grup yang dipilih"
- [ ] Klik tombol "Test Kirim PDF"
- [ ] Cek apakah PDF diterima di grup WA
- [ ] Jika berhasil, simpan setting
- [ ] Tunggu jadwal untuk auto-send atau test manual

