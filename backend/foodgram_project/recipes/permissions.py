from rest_framework.permissions import SAFE_METHODS, BasePermission


class Superuser(BasePermission):
    def has_permission(self, request, view):
        return (request.user
                and request.user.is_authenticated
                and request.user.is_superuser)


class Author(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method not in ['PUT', 'DELETE']:
            return True
        return obj.author == request.user


class ReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS
