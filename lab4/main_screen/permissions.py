from rest_framework import permissions
from .models import CustomUser
from .redis import session_storage

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


# from rest_framework import permissions
# from .redis import session_storage
# from .models import User

class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        session_id = request.COOKIES['session_id']
        print(session_id)
        if session_id is None:
            return False
        try:
            session_storage.get(session_id).decode('utf-8')
        except:
            return False
        return True
    
class IsAuthManager(permissions.BasePermission):
    def has_permission(self, request, view):
        session_id = request.COOKIES['session_id']
        if session_id is None:
            return False
        try:
             email = session_storage.get(session_id).decode('utf-8')
        except:
            return False
        user = CustomUser.objects.filter(email=email).first()
        print(user)
        print(user.is_superuser)
        return user.is_superuser