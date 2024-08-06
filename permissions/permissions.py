from rest_framework.permissions import BasePermission, SAFE_METHODS


class NotAuthenticated(BasePermission):
    message = 'You already authenticated!'

    def has_permission(self, request, view):
        return bool(request.user and not request.user.is_authenticated)


class IsOwnerOrReadOnly(BasePermission):
    message = 'you are not the owner!'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        condition = obj.id
        if hasattr(obj, 'owner'):
            condition = obj.owner.id
        return bool(request.user and request.user.is_authenticated and condition == request.user.id)
