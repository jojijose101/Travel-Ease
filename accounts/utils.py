from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def get_role(user):
    try:
        return user.profile.role
    except Exception:
        return 'customer'

def role_required(allowed_roles):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            role = get_role(request.user)
            if role not in allowed_roles and not request.user.is_staff and not request.user.is_superuser:
                messages.error(request, "You don't have permission to access that page.")
                return redirect('booking:hotel_list')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
