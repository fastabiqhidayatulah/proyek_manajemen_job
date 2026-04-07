"""
Module untuk permission check & access control berdasarkan Departemen & Bagian.
Gunakan untuk routing UI/fitur yang hanya bisa diakses departemen tertentu.
"""

from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


# ==============================================================================
# PERMISSION CHECK FUNCTIONS
# ==============================================================================

def can_access_departemen(user, required_departemen_names):
    """
    Check apakah user bisa akses fitur departemen tertentu.
    
    Args:
        user: CustomUser instance
        required_departemen_names: str atau list dari nama departemen yang diizinkan
                                  Misal: 'Teknik' atau ['Teknik', 'Produksi']
    
    Returns:
        bool: True jika user punya akses, False jika tidak
    
    Example:
        if can_access_departemen(user, 'Teknik'):
            # Bisa akses fitur Teknik
    """
    if not user.is_authenticated:
        return False
    
    if not user.departemen:
        return False
    
    # Convert single string to list
    if isinstance(required_departemen_names, str):
        required_departemen_names = [required_departemen_names]
    
    return user.departemen.nama_departemen in required_departemen_names


def can_access_bagian(user, required_bagian_names):
    """
    Check apakah user bisa akses fitur bagian tertentu.
    
    Args:
        user: CustomUser instance
        required_bagian_names: str atau list dari nama bagian yang diizinkan
                               Misal: 'Pemper' atau ['Pemper', 'Elektrik']
    
    Returns:
        bool: True jika user punya akses, False jika tidak
    
    Example:
        if can_access_bagian(user, 'Pemper'):
            # Bisa akses fitur Bagian Pemper
    """
    if not user.is_authenticated:
        return False
    
    if not user.bagian:
        return False
    
    # Convert single string to list
    if isinstance(required_bagian_names, str):
        required_bagian_names = [required_bagian_names]
    
    return user.bagian.nama_bagian in required_bagian_names


def get_user_departemen(user):
    """
    Get departemen user.
    
    Returns:
        Departemen instance atau None
    """
    if not user.is_authenticated:
        return None
    return user.departemen


def get_user_bagian(user):
    """
    Get bagian user.
    
    Returns:
        Bagian instance atau None
    """
    if not user.is_authenticated:
        return None
    return user.bagian


def get_accessible_bagians(user):
    """
    Get semua bagian yang bisa diakses user (bagian di departemennya).
    
    Returns:
        QuerySet of Bagian atau empty QuerySet
    """
    if not user.is_authenticated or not user.departemen:
        from core.models import Bagian
        return Bagian.objects.none()
    
    return user.departemen.daftar_bagian.all()


def get_departemen_members(departemen):
    """
    Get semua user yang tergabung di departemen.
    
    Args:
        departemen: Departemen instance
    
    Returns:
        QuerySet of CustomUser
    """
    if not departemen:
        from core.models import CustomUser
        return CustomUser.objects.none()
    
    return departemen.anggota_departemen.all()


def get_bagian_members(bagian):
    """
    Get semua user yang tergabung di bagian.
    
    Args:
        bagian: Bagian instance
    
    Returns:
        QuerySet of CustomUser
    """
    if not bagian:
        from core.models import CustomUser
        return CustomUser.objects.none()
    
    return bagian.anggota_bagian.all()


# ==============================================================================
# DECORATORS
# ==============================================================================

def departemen_required(required_departemen_names):
    """
    Decorator untuk protect view berdasarkan departemen.
    User hanya bisa akses jika punya departemen yang sesuai.
    
    Args:
        required_departemen_names: str atau list dari nama departemen yang diizinkan
    
    Example:
        @departemen_required('Teknik')
        def dashboard_teknik(request):
            # Hanya user dari Departemen Teknik bisa akses
            ...
        
        @departemen_required(['Teknik', 'Produksi'])
        def dashboard_teknologi(request):
            # User dari Departemen Teknik atau Produksi bisa akses
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if not can_access_departemen(request.user, required_departemen_names):
                return HttpResponseForbidden(
                    '<h1>403 Forbidden</h1>'
                    '<p>Anda tidak memiliki akses ke fitur ini. '
                    'Departemen Anda tidak memenuhi syarat.</p>'
                )
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def bagian_required(required_bagian_names):
    """
    Decorator untuk protect view berdasarkan bagian.
    User hanya bisa akses jika punya bagian yang sesuai.
    
    Args:
        required_bagian_names: str atau list dari nama bagian yang diizinkan
    
    Example:
        @bagian_required('Pemper')
        def dashboard_pemper(request):
            # Hanya user dari Bagian Pemper bisa akses
            ...
        
        @bagian_required(['Pemper', 'Elektrik'])
        def dashboard_pemeliharaan(request):
            # User dari Bagian Pemper atau Elektrik bisa akses
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if not can_access_bagian(request.user, required_bagian_names):
                return HttpResponseForbidden(
                    '<h1>403 Forbidden</h1>'
                    '<p>Anda tidak memiliki akses ke fitur ini. '
                    'Bagian Anda tidak memenuhi syarat.</p>'
                )
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def departemen_and_bagian_required(required_departemen_names, required_bagian_names):
    """
    Decorator untuk protect view berdasarkan BOTH departemen AND bagian.
    User harus punya KEDUANYA untuk akses.
    
    Args:
        required_departemen_names: str atau list dari nama departemen
        required_bagian_names: str atau list dari nama bagian
    
    Example:
        @departemen_and_bagian_required('Teknik', 'Pemper')
        def dashboard_teknik_pemper(request):
            # Hanya user dari Departemen Teknik AND Bagian Pemper bisa akses
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            has_departemen = can_access_departemen(request.user, required_departemen_names)
            has_bagian = can_access_bagian(request.user, required_bagian_names)
            
            if not (has_departemen and has_bagian):
                return HttpResponseForbidden(
                    '<h1>403 Forbidden</h1>'
                    '<p>Anda tidak memiliki akses ke fitur ini. '
                    'Departemen dan/atau Bagian Anda tidak memenuhi syarat.</p>'
                )
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


# ==============================================================================
# TEMPLATE FILTER / CONTEXT PROCESSOR HELPER
# ==============================================================================

def get_departemen_menu_visibility(user):
    """
    Get dictionary berisi visibility menu berdasarkan departemen user.
    Gunakan di context processor atau template untuk conditional menu rendering.
    
    Returns:
        dict dengan keys departemen names dan values True/False
    
    Example:
        menu_visibility = get_departemen_menu_visibility(request.user)
        # {'Teknik': True, 'Produksi': False, 'HR': False, ...}
    """
    from core.models import Departemen
    
    visibility = {}
    for dept in Departemen.objects.all():
        visibility[dept.nama_departemen] = can_access_departemen(user, dept.nama_departemen)
    
    return visibility


def get_bagian_menu_visibility(user):
    """
    Get dictionary berisi visibility menu berdasarkan bagian user.
    Gunakan di context processor atau template untuk conditional menu rendering.
    
    Returns:
        dict dengan keys bagian names dan values True/False
    
    Example:
        menu_visibility = get_bagian_menu_visibility(request.user)
        # {'Pemper': True, 'Elektrik': False, 'Mekanik': False, ...}
    """
    from core.models import Bagian
    
    visibility = {}
    for bagian in Bagian.objects.all():
        visibility[bagian.nama_bagian] = can_access_bagian(user, bagian.nama_bagian)
    
    return visibility


# ==============================================================================
# FEATURE PERMISSION FUNCTIONS (DATABASE-DRIVEN)
# ==============================================================================

def user_has_feature_access(user, feature_key):
    """
    Check apakah user bisa akses fitur tertentu berdasarkan departemen permission.
    Feature permission disimpan di database (DepartemenFeature).
    
    Args:
        user: CustomUser instance
        feature_key: str - key fitur yang ingin dicek (misal: 'dashboard', 'preventive_jobs')
    
    Returns:
        bool: True jika user's departemen punya akses ke fitur, False jika tidak
    
    Example:
        if user_has_feature_access(request.user, 'dashboard'):
            # User bisa akses dashboard
    """
    if not user.is_authenticated:
        return False
    
    if not user.departemen:
        return False
    
    from core.models import DepartemenFeature
    from django.core.cache import cache
    
    # Try cache first (5 minute TTL)
    cache_key = f'feature_access_{user.departemen.id}_{feature_key}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Check database
    has_access = DepartemenFeature.objects.filter(
        departemen=user.departemen,
        feature_key=feature_key,
        is_enabled=True
    ).exists()
    
    # Cache hasil
    cache.set(cache_key, has_access, 300)  # 5 minutes
    
    return has_access


def get_user_allowed_features(user):
    """
    Get semua fitur yang bisa diakses user berdasarkan departemennya.
    
    Args:
        user: CustomUser instance
    
    Returns:
        dict: {
            'dashboard': True,
            'project': True,
            'preventive_jobs': False,
            ...
        }
    
    Example:
        features = get_user_allowed_features(request.user)
        # {'dashboard': True, 'project': True, ...}
    """
    from core.models import DepartemenFeature
    from django.core.cache import cache
    
    if not user.is_authenticated or not user.departemen:
        # Return empty dict jika user tidak punya departemen
        return {choice[0]: False for choice in DepartemenFeature.FEATURE_CHOICES}
    
    # Try cache first
    cache_key = f'user_features_{user.departemen.id}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    # Get semua features dari database
    allowed_features = DepartemenFeature.objects.filter(
        departemen=user.departemen,
        is_enabled=True
    ).values_list('feature_key', flat=True)
    
    # Build dict
    feature_dict = {}
    for feature_key, feature_name in DepartemenFeature.FEATURE_CHOICES:
        feature_dict[feature_key] = feature_key in allowed_features
    
    # Cache
    cache.set(cache_key, feature_dict, 300)  # 5 minutes
    
    return feature_dict


def invalidate_feature_cache(departemen):
    """
    Invalidate feature cache ketika permission berubah.
    Panggil function ini setelah update DepartemenFeature.
    """
    from django.core.cache import cache
    
    cache_key = f'user_features_{departemen.id}'
    cache.delete(cache_key)
    
    # Also invalidate semua users' feature cache di departemen ini
    for user in departemen.anggota_departemen.all():
        # Invalidate individual feature keys
        for feature_key, _ in DepartemenFeature.FEATURE_CHOICES:
            feature_cache_key = f'feature_access_{departemen.id}_{feature_key}'
            cache.delete(feature_cache_key)


# ==============================================================================
# DECORATOR UNTUK FEATURE-BASED ACCESS
# ==============================================================================

def feature_required(feature_key):
    """
    Decorator untuk protect view berdasarkan feature permission di database.
    User hanya bisa akses jika departemennya punya permission untuk fitur ini.
    
    Args:
        feature_key: str - Key fitur (dashboard, preventive_jobs, etc)
    
    Example:
        @feature_required('dashboard')
        def my_dashboard(request):
            # Hanya user yang departemennya enable 'dashboard' bisa akses
            ...
        
        @feature_required('preventive_jobs')
        def preventive_dashboard(request):
            # Hanya user yang departemennya enable 'preventive_jobs' bisa akses
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if not user_has_feature_access(request.user, feature_key):
                return HttpResponseForbidden(
                    '<h1>403 Forbidden</h1>'
                    '<p>Departemen Anda tidak memiliki akses ke fitur ini.</p>'
                    '<p><a href="/">Kembali ke Dashboard</a></p>'
                )
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

