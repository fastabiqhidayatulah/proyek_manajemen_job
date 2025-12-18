"""
Cache utilities untuk optimization access control dan hierarchical data.

Functions:
- get_user_accessible_projects: Get accessible projects with caching
- invalidate_user_accessible_projects_cache: Manually invalidate cache
"""

from django.core.cache import cache
from django.db.models import Q


def get_user_accessible_projects(user):
    """
    Get all accessible project IDs for user with caching.
    
    Accessible projects:
    1. Projects created by user (owner)
    2. Projects shared to all users (is_shared=True)
    3. Projects from subordinates (user as supervisor/reviewer)
    4. Projects from supervisors (user as subordinate/collaborator)
    
    Args:
        user: CustomUser instance
    
    Returns:
        List of project IDs accessible by user
    """
    cache_key = f"accessible_projects_{user.id}"
    cached = cache.get(cache_key)
    
    if cached is not None:
        return cached
    
    from .models import Project
    
    # Get subordinate IDs
    subordinate_ids = user.get_all_subordinates()
    
    # Get supervisor IDs (all people above in hierarchy)
    supervisor_ids = []
    current_user = user
    while current_user.atasan:
        supervisor_ids.append(current_user.atasan.id)
        current_user = current_user.atasan
    
    # Query accessible projects
    accessible_projects = Project.objects.filter(
        Q(manager_project=user) |  # Owner
        Q(is_shared=True) |  # Shared to all
        Q(manager_project_id__in=subordinate_ids) |  # Subordinate projects (for review)
        Q(manager_project_id__in=supervisor_ids)  # Supervisor projects (for collaborative work)
    ).values_list('id', flat=True).distinct()
    
    result = list(accessible_projects)
    
    # Cache for 1 hour (3600 seconds)
    cache.set(cache_key, result, 3600)
    
    return result


def invalidate_user_accessible_projects_cache(user):
    """
    Manually invalidate accessible projects cache for user and supervisors.
    Called when project sharing changes.
    
    Args:
        user: CustomUser instance
    """
    cache_key = f"accessible_projects_{user.id}"
    cache.delete(cache_key)
    
    # Also invalidate for all supervisors up the chain
    current = user
    while current.atasan:
        supervisor_key = f"accessible_projects_{current.atasan.id}"
        cache.delete(supervisor_key)
        current = current.atasan


def invalidate_user_subordinates_cache(user):
    """
    Manually invalidate subordinates cache for user and supervisors.
    Called when hierarchy changes.
    
    Args:
        user: CustomUser instance
    """
    cache_key = f"subordinates_{user.id}"
    cache.delete(cache_key)
    
    # Also invalidate for all supervisors up the chain
    current = user
    while current.atasan:
        supervisor_key = f"subordinates_{current.atasan.id}"
        cache.delete(supervisor_key)
        current = current.atasan


def clear_all_access_control_cache():
    """
    Clear all access control caches. Useful for debugging or admin actions.
    WARNING: This is expensive, only use if necessary.
    """
    from .models import CustomUser, Project
    
    # Clear all subordinates caches
    for user in CustomUser.objects.all():
        cache_key = f"subordinates_{user.id}"
        cache.delete(cache_key)
    
    # Clear all accessible projects caches
    for user in CustomUser.objects.all():
        cache_key = f"accessible_projects_{user.id}"
        cache.delete(cache_key)
