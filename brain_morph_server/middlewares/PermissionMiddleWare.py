from brain_morph_server import models
from brainMorph_back_server.auth.BearerTokenAuth import BearerTokenAuth
from django.http import HttpResponse
CONTENT_TYPE = "application/json"

EXCLUDE_VIEW_FUNC = ["AuthViewSet"]


class PermissionMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith('/api') and view_func.__name__ not in EXCLUDE_VIEW_FUNC:
            try:
                user: models.User = BearerTokenAuth(
                ).authenticate(request=request)[0]
                if user:
                    role: models.Role = user.role
                    if role:
                        setattr(request, "permissions", role.permissions.all())
                    else:
                        setattr(request, "permissions", [])
                else:
                    setattr(request, "permissions", [])
            except:
                return HttpResponse(status=401, content_type=CONTENT_TYPE)

    def __call__(self, request):
        return self.get_response(request)
