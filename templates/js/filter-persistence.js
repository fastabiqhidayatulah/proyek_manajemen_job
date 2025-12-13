/**
 * Filter Persistence for Dashboard
 * Menyimpan filter ke localStorage saat user mengubah filter
 * Memulihkan filter saat halaman dashboard dimuat
 */

/**
 * Simpan filter ke localStorage
 */
function saveFiltersToLocalStorage() {
    const filters = {
        month: document.getElementById('month-filter')?.value || '',
        year: document.getElementById('year-filter')?.value || '',
        pic: document.getElementById('pic-filter')?.value || '',
        line: document.getElementById('line-filter')?.value || '',
        mesin: document.getElementById('mesin-filter')?.value || '',
        sub_mesin: document.getElementById('sub-mesin-filter')?.value || '',
        sort: document.getElementById('sort-filter')?.value || 'updated_at',
        order: document.getElementById('order-filter')?.value || 'desc',
        page_size: document.getElementById('page-size-filter')?.value || '20',
        timestamp: new Date().toISOString()
    };
    
    localStorage.setItem('dashboardFilters', JSON.stringify(filters));
}

/**
 * Ambil filter dari localStorage
 */
function getFiltersFromLocalStorage() {
    const savedFilters = localStorage.getItem('dashboardFilters');
    if (savedFilters) {
        try {
            return JSON.parse(savedFilters);
        } catch (e) {
            console.error('Error parsing saved filters:', e);
            return null;
        }
    }
    return null;
}

/**
 * Restore filter dari localStorage ke form
 */
function restoreFiltersFromLocalStorage() {
    // IMPORTANT: Check URL parameters dulu
    // Jika URL sudah ada parameters (dari form submit), jangan override
    const urlParams = new URLSearchParams(window.location.search);
    const hasUrlFilters = Array.from(urlParams.keys()).some(key => 
        ['month', 'year', 'pic', 'line', 'mesin', 'sub_mesin'].includes(key)
    );
    
    if (hasUrlFilters) {
        return;
    }

    const savedFilters = getFiltersFromLocalStorage();
    
    if (!savedFilters) {
        return;
    }

    // Set nilai ke form
    if (savedFilters.month && document.getElementById('month-filter')) {
        document.getElementById('month-filter').value = savedFilters.month;
    }

    if (savedFilters.year && document.getElementById('year-filter')) {
        document.getElementById('year-filter').value = savedFilters.year;
    }

    if (savedFilters.pic !== undefined && document.getElementById('pic-filter')) {
        document.getElementById('pic-filter').value = savedFilters.pic;
    }

    if (savedFilters.line && document.getElementById('line-filter')) {
        document.getElementById('line-filter').value = savedFilters.line;
    }

    if (savedFilters.mesin && document.getElementById('mesin-filter')) {
        document.getElementById('mesin-filter').value = savedFilters.mesin;
    }

    if (savedFilters.sub_mesin && document.getElementById('sub-mesin-filter')) {
        document.getElementById('sub-mesin-filter').value = savedFilters.sub_mesin;
    }

    if (savedFilters.sort && document.getElementById('sort-filter')) {
        document.getElementById('sort-filter').value = savedFilters.sort;
    }

    if (savedFilters.order && document.getElementById('order-filter')) {
        document.getElementById('order-filter').value = savedFilters.order;
    }

    if (savedFilters.page_size && document.getElementById('page-size-filter')) {
        document.getElementById('page-size-filter').value = savedFilters.page_size;
    }
}

/**
 * Setup auto-save ketika form filter berubah
 * TANPA auto-submit (user masih perlu klik tombol Filter)
 */
function setupFilterAutoSave() {
    const filterForm = document.querySelector('form[action*="dashboard"]');
    if (!filterForm) return;

    // Listen untuk semua select yang berubah
    const filterSelects = filterForm.querySelectorAll('select');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            saveFiltersToLocalStorage();
        });
    });

    // Juga save saat form di-submit
    filterForm.addEventListener('submit', function() {
        saveFiltersToLocalStorage();
    });
}

/**
 * Clear semua saved filters (Optional)
 * Gunakan untuk testing atau tombol "Reset Filter"
 * Juga clear semua form fields
 */
function clearSavedFilters() {
    // Clear dari localStorage
    localStorage.removeItem('dashboardFilters');
    
    // Clear semua form fields ke default value
    const filterForm = document.querySelector('form[action*="dashboard"]');
    
    if (filterForm) {
        // Reset semua select ke nilai default
        const selects = filterForm.querySelectorAll('select');
        selects.forEach(select => {
            select.value = '0'; // Default value untuk semua dropdown
        });
        
        // Reset date inputs
        const dateInputs = filterForm.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => {
            input.value = ''; // Clear date fields
        });
        
        // Submit form untuk reload dengan filter cleared
        filterForm.submit();
    } else {
        // Jika form tidak ditemukan, reload halaman
        window.location.href = window.location.pathname;
    }
}

// Export functions untuk digunakan di HTML jika perlu
// PENTING: Initialize sebelum pre-DOMContentLoaded code menggunakannya
window.dashboardFilters = {
    save: saveFiltersToLocalStorage,
    restore: restoreFiltersFromLocalStorage,
    get: getFiltersFromLocalStorage,
    clear: clearSavedFilters
};

// URGENT: Restore filter SEBELUM DOMContentLoaded untuk menghindari flash
// Ini penting saat user redirect dari form submit
(function() {
    // Check URL path
    const pathname = window.location.pathname.toLowerCase();
    const isDashboard = pathname.includes('/dashboard') || 
                       pathname.includes('/core/') && pathname.endsWith('/');
    
    if (isDashboard) {
        restoreFiltersFromLocalStorage();
    }
})();

document.addEventListener('DOMContentLoaded', function() {
    // ===== 1. RE-RESTORE SAVED FILTERS (Safety check) =====
    const pathname = window.location.pathname.toLowerCase();
    const isDashboard = pathname.includes('/dashboard') || 
                       pathname.includes('/core/') && pathname.endsWith('/');
    
    if (isDashboard) {
        // Delay sedikit untuk ensure DOM fully loaded
        setTimeout(function() {
            restoreFiltersFromLocalStorage();
        }, 100);
    }

    // ===== 2. SETUP AUTO-SAVE KETIKA FILTER BERUBAH =====
    setupFilterAutoSave();

    // NOTE: Cascading filters are handled in dashboard.html (jQuery AJAX)
    // Do not setup cascading filters here to avoid conflicts
});
