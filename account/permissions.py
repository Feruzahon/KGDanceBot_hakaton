from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == "admin")
       # if request.user.role == 'admin':
          #  return True

class IsParentOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role in ['parent','admin'])
        #if request.user.role in ['parent', 'admin']:
         #   return True
        

#Родитель может видеть только Своих детей
class IsParentOfChild(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.parent == request.user or request.user.role == 'admin'
    

