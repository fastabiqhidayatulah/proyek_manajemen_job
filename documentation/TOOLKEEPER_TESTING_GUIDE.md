# Toolkeeper Modal Return Testing Guide

## Quick Start
1. Navigate to: `http://192.168.10.239:4321/toolkeeper/`
2. You should see list of peminjaman with expandable rows

## Test Cases

### Test 1: Expand/Collapse Row
**Steps**:
1. Click on any peminjaman row (on the expand arrow or row text)
2. Observe: Chevron icon rotates 90°, detail section appears

**Expected Results**:
- ✓ Detail row expands smoothly
- ✓ Shows "Alat yang Dipinjam" table
- ✓ Shows history if returns exist
- ✓ Chevron points right (expanded state)

---

### Test 2: Per-Alat Return Modal
**Steps**:
1. Expand a peminjaman row
2. Find an item with "Belum" qty > 0
3. Click the green "Return" button for that item
4. Modal should appear with:
   - Tool name pre-filled
   - "Jumlah Belum Kembali" showing pending qty
   - "Jumlah Dikembalikan" pre-filled with full pending qty
   - Kondisi dropdown empty
   - Catatan field empty

**Expected Results**:
- ✓ Modal appears with correct data
- ✓ Cannot change tool name/qty_belum (display only)
- ✓ Can modify qty_kembali if needed
- ✓ Can select kondisi (Baik/Rusak Ringan/Rusak Berat/Hilang)
- ✓ Can add optional catatan

---

### Test 3: Submit Per-Alat Return (Full Return)
**Steps**:
1. Open modal for item with qty_belum = 5
2. qty_kembali should be auto-filled as 5
3. Select "Baik" from Kondisi dropdown
4. Click "Simpan Return" button
5. Wait for page to reload

**Expected Results**:
- ✓ Modal closes
- ✓ Page reloads
- ✓ Item's "Belum" shows 0 or "Selesai" badge
- ✓ Item's "Kembali" increases by 5
- ✓ New entry appears in History section with:
  - Today's date/time
  - Your username
  - Tool name
  - Qty 5
  - Kondisi "Baik"
- ✓ If all items returned, peminjaman status shows "✓ Lengkap"

---

### Test 4: Partial Return
**Steps**:
1. Open peminjaman with item: qty_pinjam=10, qty_kembali=0, qty_belum=10
2. Click Return button
3. Modal shows:
   - qty_belum = 10
   - qty_kembali = 10 (pre-filled)
4. Change qty_kembali to 3 (return only 3 units)
5. Select kondisi
6. Click "Simpan Return"
7. Wait for reload

**Expected Results**:
- ✓ Item shows: qty_belum=7, qty_kembali=3
- ✓ Return button still visible (qty_belum > 0)
- ✓ History shows entry with qty_kembali=3
- ✓ Can click Return again for remaining 7 units

---

### Test 5: Multiple Returns Same Day
**Steps**:
1. Do partial return of 3 units (qty_belum now 7)
2. Click Return again for same item
3. Modal shows qty_belum=7, qty_kembali=7 (pre-filled)
4. Change to 4 units
5. Submit

**Expected Results**:
- ✓ Two history entries:
  - First: qty_kembali=3, kondisi=Baik
  - Second: qty_kembali=4, kondisi=...
- ✓ Item shows: qty_belum=3, qty_kembali=7
- ✓ Both under same Pengembalian record (same date)

---

### Test 6: Return Semua Alat Button
**Steps**:
1. Expand peminjaman with multiple items
2. Find "Return Semua Alat" button (if status = aktif/overdue)
3. Click it

**Expected Results**:
- ✓ Navigates to pengembalian form page
- ✓ All items pre-filled with qty_belum values
- ✓ User can adjust individual quantities
- ✓ Returns to list after submit

---

### Test 7: Completed Peminjaman
**Steps**:
1. Expand peminjaman that's already "Selesai"
2. Check all items show qty_belum=0
3. Check "Return Semua" button is NOT visible
4. Check History section shows all returns

**Expected Results**:
- ✓ All items show "Selesai" badge
- ✓ Peminjaman shows "✓ Lengkap"
- ✓ Status badge shows "Selesai"
- ✓ No return buttons visible
- ✓ Full history visible

---

### Test 8: Filter & Search
**Steps**:
1. Type employee name in search box
2. Select status filter (Aktif/Overdue/Selesai)
3. Click Filter button

**Expected Results**:
- ✓ List filters to matching records
- ✓ Pagination updates
- ✓ "Hapus Filter" button appears
- ✓ Clicking "Hapus Filter" shows all records

---

### Test 9: Permission Check
**Steps**:
1. Logout
2. Login as user NOT in Workshop/Warehouse group
3. Try to access `/toolkeeper/`

**Expected Results**:
- ✓ Either redirected or permission error
- ✓ Cannot see peminjaman list
- ✓ Cannot click Return buttons

---

### Test 10: Error Handling
**Steps**:
1. Open modal for item
2. Try to change qty_kembali to MORE than qty_belum
3. Check Network tab shows error

**Expected Results**:
- ✓ Server rejects qty > pending
- ✓ Alert shows error message
- ✓ Modal doesn't close
- ✓ Can correct and resubmit

---

## Performance Indicators
- List page should load in < 2s (with 50 items)
- Modal should appear instantly (< 100ms)
- AJAX return should complete in < 1s
- Page reload should complete in < 2s

## Browser Compatibility
Test on:
- ✓ Chrome/Edge 90+
- ✓ Firefox 88+
- ✓ Safari 14+
- ✓ Mobile (iOS Safari/Chrome)

## Troubleshooting

### Modal Not Appearing
- Check browser console for JavaScript errors
- Verify Bootstrap 5 is loaded
- Check if return button data attributes are set

### AJAX Returns 404
- Check URL in modal JavaScript points to `api-return-tool`
- Verify route exists in `toolkeeper/urls.py`
- Check view function `api_return_tool` in `views.py`

### Changes Not Saving
- Check Network tab for response
- Look for 403 Permission error (user not in Workshop/Warehouse group)
- Check database connection

### Page Doesn't Reload
- Check browser console for JavaScript errors
- Verify `location.reload()` is being called
- Check if modal close event is firing
