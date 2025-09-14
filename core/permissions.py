from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps


def role_required(*allowed_roles):
    """
    Decorator to check if user has one of the allowed roles.
    Usage: @role_required('editor', 'journalist')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("You must be logged in to access this page.")
            
            if request.user.role not in allowed_roles:
                raise PermissionDenied(f"You must be a {' or '.join(allowed_roles)} to access this page.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def is_editor(user):
    """Check if user is an editor."""
    return user.is_authenticated and user.role == 'editor'


def is_journalist(user):
    """Check if user is a journalist."""
    return user.is_authenticated and user.role == 'journalist'


def is_reader(user):
    """Check if user is a reader."""
    return user.is_authenticated and user.role == 'reader'


def is_journalist_or_editor(user):
    """Check if user is a journalist or editor."""
    return user.is_authenticated and user.role in ['journalist', 'editor']


def can_create_article(user):
    """Check if user can create articles."""
    return user.is_authenticated and user.role in ['journalist', 'editor']


def can_approve_article(user):
    """Check if user can approve articles."""
    return user.is_authenticated and (
        user.role == 'editor' or 
        user.has_perm('core.can_approve_article')
    )


def can_create_newsletter(user):
    """Check if user can create newsletters."""
    return user.is_authenticated and (
        user.role == 'editor' or 
        user.has_perm('core.can_create_newsletter')
    )


def can_send_newsletter(user):
    """Check if user can send newsletters."""
    return user.is_authenticated and (
        user.role == 'editor' or 
        user.has_perm('core.can_send_newsletter')
    )


# Decorators for views
editor_required = user_passes_test(is_editor)
journalist_required = user_passes_test(is_journalist)
journalist_or_editor_required = user_passes_test(is_journalist_or_editor)
article_creator_required = user_passes_test(can_create_article)
article_approver_required = user_passes_test(can_approve_article)
newsletter_creator_required = user_passes_test(can_create_newsletter)
newsletter_sender_required = user_passes_test(can_send_newsletter)

