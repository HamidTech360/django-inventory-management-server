from rest_framework.permissions import BasePermission


class isAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return bool(request.user and request.user.is_staff)

class ViewCustomerHistoryPermission (BasePermission):
    def has_permission (self, request, view):
        return request.user.has_perm('store.view_history')