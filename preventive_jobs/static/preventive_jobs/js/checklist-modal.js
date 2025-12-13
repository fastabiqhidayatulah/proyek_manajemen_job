/**
 * Checklist Modal Script - Support Numeric dan Text Items
 * Menangani loading checklist items (numeric & text), validasi, dan AJAX POST hasil
 */

let currentChecklistResult = null;
let currentExecutionId = null;

document.addEventListener('DOMContentLoaded', function() {
    const checklistModal = document.getElementById('checklistModal');
    
    if (!checklistModal) {
        console.log('Checklist modal not found');
        return;
    }
    
    // Load checklist items saat modal dibuka
    checklistModal.addEventListener('show.bs.modal', function(event) {
        loadChecklistModal(currentExecutionId);
    });
    
    // Setup save button
    const saveBtn = document.getElementById('saveChecklistBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveChecklistResult);
    }
});

/**
 * Load checklist modal dengan support numeric dan text items
 */
function loadChecklistModal(executionId) {
    if (!executionId) {
        executionId = document.getElementById('executionId')?.value;
    }
    
    if (!executionId) {
        console.error('Missing execution ID');
        return;
    }
    
    currentExecutionId = executionId;
    
    const itemsBody = document.getElementById('checklistItemsBody');
    if (!itemsBody) return;
    
    // Clear previous items
    itemsBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted"><i class="fas fa-spinner fa-spin"></i> Loading...</td></tr>';
    
    // Fetch checklist items dari backend
    fetch(`/preventive/execution/${executionId}/checklist-modal/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            renderChecklistItems(data.items || [], data.checklist_result);
        } else {
            showError('Gagal memuat checklist items: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error memuat checklist items: ' + error.message);
    });
}

/**
 * Render checklist items ke dalam tabel (support numeric, text dropdown, dan free text)
 */
function renderChecklistItems(items, existingResult) {
    const itemsBody = document.getElementById('checklistItemsBody');
    itemsBody.innerHTML = '';
    
    if (!items || items.length === 0) {
        itemsBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Tidak ada item checklist</td></tr>';
        return;
    }
    
    currentChecklistResult = existingResult;
    
    items.forEach((item, index) => {
        const itemType = item.item_type;
        const isNumeric = itemType === 'numeric';
        const isFreeText = itemType === 'free_text';
        const existingData = existingResult && existingResult.hasil_pengukuran ? 
                            existingResult.hasil_pengukuran[item.id.toString()] : null;
        const existingStatus = existingResult && existingResult.status_item ?
                            existingResult.status_item[item.id.toString()] : null;
        
        const row = document.createElement('tr');
        let inputHTML = '';
        
        if (isNumeric) {
            // ===== NUMERIC ITEM =====
            inputHTML = `
                <input type="number" 
                       class="form-control form-control-sm checklist-nilai" 
                       data-item-id="${item.id}"
                       data-item-type="numeric"
                       data-min="${item.nilai_min || ''}"
                       data-max="${item.nilai_max || ''}"
                       placeholder="Masukkan nilai"
                       value="${existingData || ''}"
                       step="0.01">
                <small class="text-muted d-block mt-1">Range: ${item.nilai_min} - ${item.nilai_max} ${item.unit}</small>
            `;
        } else if (isFreeText) {
            // ===== FREE TEXT ITEM =====
            inputHTML = `
                <textarea class="form-control form-control-sm checklist-nilai" 
                          data-item-id="${item.id}"
                          data-item-type="free_text"
                          placeholder="Masukkan teks atau observasi..."
                          rows="2">${existingData || ''}</textarea>
                <small class="text-muted d-block mt-1">Input teks bebas - tidak ada validasi format</small>
            `;
        } else {
            // ===== TEXT DROPDOWN ITEM =====
            const options = item.text_options ? item.text_options.split(';').map(o => o.trim()) : [];
            inputHTML = `
                <select class="form-select form-select-sm checklist-nilai" 
                        data-item-id="${item.id}"
                        data-item-type="text">
                    <option value="">-- Pilih --</option>
            `;
            options.forEach(opt => {
                const isSelected = existingData === opt ? 'selected' : '';
                inputHTML += `<option value="${opt}" ${isSelected}>${opt}</option>`;
            });
            inputHTML += `
                </select>
                <small class="text-muted d-block mt-1">Opsi: ${options.join(', ')}</small>
            `;
        }
        
        row.innerHTML = `
            <td class="text-center"><strong>${index + 1}</strong></td>
            <td>
                <span class="badge ${isNumeric ? 'bg-primary' : isFreeText ? 'bg-warning' : 'bg-info'}">
                    ${isNumeric ? 'NUM' : isFreeText ? 'FTX' : 'TXT'}
                </span>
            </td>
            <td>
                <strong>${item.item_pemeriksaan}</strong>
                ${item.tindakan_remark ? `<br><small class="text-muted">Tindakan: ${item.tindakan_remark}</small>` : ''}
            </td>
            <td><small>${item.standar_normal || '-'}</small></td>
            <td>
                ${inputHTML}
            </td>
            <td>
                <select class="form-select form-select-sm checklist-status" data-item-id="${item.id}">
                    <option value="">--</option>
                    <option value="OK" ${existingStatus === 'OK' ? 'selected' : ''}>OK</option>
                    <option value="NG" ${existingStatus === 'NG' ? 'selected' : ''}>NG</option>
                </select>
            </td>
        `;
        
        itemsBody.appendChild(row);
    });
    
    // Restore catatan umum dari existing result
    const catatanInput = document.getElementById('catatanUmum');
    if (existingResult && existingResult.catatan) {
        catatanInput.value = existingResult.catatan;
    }
    
    // Attach validation listeners
    attachValidationListeners();
}


/**
 * Attach listeners untuk auto-validate range
 */
function attachValidationListeners() {
    const nilaiInputs = document.querySelectorAll('.checklist-nilai');
    
    nilaiInputs.forEach(input => {
        input.addEventListener('change', function() {
            validateItemRange(this);
        });
        
        input.addEventListener('input', function() {
            validateItemRange(this);
        });
    });
}

/**
 * Validate nilai terhadap min/max range (hanya untuk numeric items)
 */
function validateItemRange(input) {
    const itemId = input.dataset.itemId;
    const itemType = input.dataset.itemType;
    
    if (itemType === 'text' || itemType === 'free_text') {
        // Text dan Free Text items tidak perlu validasi range
        const statusSelect = document.querySelector(`.checklist-status[data-item-id="${itemId}"]`);
        if (itemType === 'free_text') {
            // Free text items otomatis OK jika ada nilai
            statusSelect.value = input.value.trim() ? 'OK' : '';
        } else {
            // Text items (dropdown)
            statusSelect.value = input.value ? 'OK' : '';
        }
        return;
    }
    
    // NUMERIC VALIDATION
    const nilai = parseFloat(input.value);
    const minVal = input.dataset.min ? parseFloat(input.dataset.min) : null;
    const maxVal = input.dataset.max ? parseFloat(input.dataset.max) : null;
    
    const statusSelect = document.querySelector(`.checklist-status[data-item-id="${itemId}"]`);
    const row = input.closest('tr');
    
    // Clear previous validation
    row.classList.remove('table-danger', 'table-success');
    
    if (!input.value) {
        // Clear status jika nilai kosong
        statusSelect.value = '';
        return;
    }
    
    // Validate range
    if (minVal !== null && maxVal !== null) {
        if (nilai >= minVal && nilai <= maxVal) {
            statusSelect.value = 'OK';
            row.classList.add('table-success');
        } else {
            statusSelect.value = 'NG';
            row.classList.add('table-danger');
        }
    } else if (minVal !== null && nilai >= minVal) {
        statusSelect.value = 'OK';
        row.classList.add('table-success');
    } else if (maxVal !== null && nilai <= maxVal) {
        statusSelect.value = 'OK';
        row.classList.add('table-success');
    }
}

/**
 * Save checklist result via AJAX (support numeric dan text items)
 */
function saveChecklistResult() {
    const executionId = currentExecutionId;
    const hasilPengukuran = {};
    const statusItem = {};
    const catatanUmum = document.getElementById('catatanUmum').value;
    
    // Collect hasil pengukuran
    const nilaiInputs = document.querySelectorAll('.checklist-nilai');
    
    let hasError = false;
    
    nilaiInputs.forEach(input => {
        const itemId = input.dataset.itemId;
        const nilai = input.value.trim();
        
        if (!nilai) {
            input.classList.add('is-invalid');
            hasError = true;
            return;
        }
        
        input.classList.remove('is-invalid');
        hasilPengukuran[itemId] = nilai;
        
        const statusSelect = document.querySelector(`.checklist-status[data-item-id="${itemId}"]`);
        statusItem[itemId] = statusSelect.value || 'OK';
    });
    
    if (hasError) {
        showAlert('Mohon isi semua item checklist terlebih dahulu', 'warning');
        return;
    }
    
    // Show loading
    const saveBtn = document.getElementById('saveChecklistBtn');
    const originalText = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Menyimpan...';
    
    // POST ke backend
    fetch(`/preventive/execution/${executionId}/save-checklist/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            hasil_pengukuran: hasilPengukuran,
            status_item: statusItem,
            catatan: catatanUmum
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;
        
        if (data.success) {
            showAlert('✓ Checklist berhasil disimpan!', 'success');
            
            // Close modal after 1 second
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('checklistModal'));
                if (modal) modal.hide();
                // Reload page untuk update status
                setTimeout(() => {
                    location.reload();
                }, 500);
            }, 1000);
        } else {
            showError('Gagal menyimpan checklist: ' + (data.message || 'Unknown error'));
            saveBtn.disabled = false;
            saveBtn.innerHTML = originalText;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error menyimpan checklist: ' + error.message);
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;
    });
}

/**
 * Get CSRF token dari cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Append to modal body
    const modalBody = document.querySelector('#checklistModal .modal-body');
    if (modalBody) {
        modalBody.insertBefore(alertDiv, modalBody.firstChild);
        
        // Auto-dismiss after 5 seconds if success
        if (type === 'success') {
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    }
}

/**
 * Show error message
 */
function showError(message) {
    showAlert(message, 'danger');
}
