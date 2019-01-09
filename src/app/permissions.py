from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAdminUser, IsAuthenticated

__all__ = [
    'AllowAny',
    'DjangoModelStrictPermissions',
    'IsAuthenticated',
    'IsAdminUser',
]


class DjangoModelStrictPermissions(DjangoModelPermissions):
    """
    Like DjangoModelPermission, but requires change permission for the list view.
    By default DjangoModelPermssions allowes any authenticated user to view all stuff
    http://www.django-rest-framework.org/api-guide/permissions/#djangomodelpermissions
    """
    perms_map = {
        'GET': ['%(app_label)s.change_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.change_%(model_name)s'],
        'HEAD': ['%(app_label)s.change_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class DjangoModelStrictReadPermissions(DjangoModelPermissions):
    """
    Like above, but requires special custom permission view, e.g. comments.view_comment
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }
