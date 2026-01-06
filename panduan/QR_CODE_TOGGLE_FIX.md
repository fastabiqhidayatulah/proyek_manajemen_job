# URL Routing Fix - QR Code Toggle Error 🔧

## Problem
When clicking "Aktifkan QR" button, error message: "Error toggling QR code"

## Root Cause
JavaScript URL path tidak match dengan Django URL pattern:

### ❌ Before (Wrong)
```javascript
// JavaScript di meeting_detail.html
fetch(`/meetings/${meetingId}/qr/generate/`)  // qr - SALAH
fetch(`/meetings/${meetingId}/qr/toggle/`)    // qr - SALAH

// URL Pattern di urls.py
path('<uuid:pk>/qr-code/generate/', ...)      // qr-code - BENAR
path('qr-code/<str:token>/toggle/', ...)      // qr-code - BENAR
```

### ✅ After (Fixed)
```javascript
// JavaScript - DIPERBAIKI
fetch(`/meetings/${meetingId}/qr-code/generate/`)  // qr-code - BENAR
fetch(`/meetings/${meetingId}/qr-code/toggle/`)    // qr-code - BENAR

// URL Pattern - DITAMBAH route baru
path('<uuid:pk>/qr-code/generate/', ...)          // Existing
path('<uuid:pk>/qr-code/toggle/', ...)            // NEW - untuk meeting_pk
path('qr-code/<str:token>/display/', ...)         // Existing
path('qr-code/<str:token>/toggle/', ...)          // Existing - untuk token
```

## Changes Made

### 1. `meetings/urls.py`
```python
# Reorder URL patterns untuk clarity dan consistency
path('<uuid:pk>/qr-code/generate/', views.QRCodeGenerateView.as_view(), name='qr-generate'),
path('<uuid:pk>/qr-code/toggle/', views.QRCodeToggleView.as_view(), name='qr-toggle'),  # NEW
path('qr-code/<str:token>/display/', views.QRCodeDisplayView.as_view(), name='qr-display'),
path('qr-code/<str:token>/toggle/', views.QRCodeToggleView.as_view(), name='qr-toggle-token'),
```

### 2. `meetings/views.py` - QRCodeToggleView
```python
def post(self, request, pk=None, token=None):
    # Support BOTH routing approaches
    if pk:
        meeting = get_object_or_404(Meeting, pk=pk)          # Via meeting_pk
    elif token:
        meeting = get_object_or_404(Meeting, qr_code_token=token)  # Via token
    else:
        return JsonResponse({'error': 'Meeting not found'}, status=404)
    
    # ... rest of logic
```

### 3. `templates/meetings/meeting_detail.html` - JavaScript
```javascript
// Before
fetch(`/meetings/${meetingId}/qr/generate/`)  ❌
fetch(`/meetings/${meetingId}/qr/toggle/`)    ❌

// After
fetch(`/meetings/${meetingId}/qr-code/generate/`)  ✅
fetch(`/meetings/${meetingId}/qr-code/toggle/`)    ✅
```

## Complete URL Mapping Reference

| Action | Method | URL Pattern | View |
|--------|--------|-------------|------|
| **Generate QR** | POST | `/meetings/{pk}/qr-code/generate/` | QRCodeGenerateView |
| **Toggle QR** | POST | `/meetings/{pk}/qr-code/toggle/` | QRCodeToggleView |
| **Display QR** | GET | `/meetings/qr-code/{token}/display/` | QRCodeDisplayView |
| **Presensi Form** | GET/POST | `/meetings/presensi/{token}/` | PresensiExternalView |

## Testing

Coba sekarang:
1. ✅ Klik "Generate QR" → QR code should appear
2. ✅ Klik "Aktifkan QR" → button text change, no error
3. ✅ Klik "Nonaktifkan QR" → QR toggle off
4. ✅ Klik "Fullscreen" → QR fullscreen opens

## What Was Fixed

### Before
```
User klik "Aktifkan QR"
    ↓
JavaScript POST ke /meetings/{id}/qr/toggle/  ❌ WRONG PATH
    ↓
404 Not Found
    ↓
Error callback triggered
    ↓
alert("Error toggling QR code")
```

### After
```
User klik "Aktifkan QR"
    ↓
JavaScript POST ke /meetings/{id}/qr-code/toggle/  ✅ CORRECT PATH
    ↓
View receives request, toggles QR
    ↓
Returns JSON { success: true, qr_code_active: true }
    ↓
Page reloads
    ↓
QR status updated ✅
```

---

**Status:** ✅ FIXED

The toggle QR code feature should now work properly!
