from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.role == 'admin'


class IsAdminOrLibrarianOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.role in ['admin', 'librarian']


class IsAdminOrLibrarianOrOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or request.user.role == ['admin', 'librarian']


class IsAdminOrLibrarian(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'librarian']
