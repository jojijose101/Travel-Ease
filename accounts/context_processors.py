from .utils import get_role

def user_role(request):
    role = ''
    if getattr(request, 'user', None) and request.user.is_authenticated:
        role = get_role(request.user)
    return {'user_role': role}
