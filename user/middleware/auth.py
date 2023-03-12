from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path_info == '/login/':
            return
        elif request.path_info == '/register/':
            return
        elif request.path_info == '/resetpassword/':
            return
        elif request.path_info == '/checkusername/':
            return
        elif request.path_info == '/aboutus/':
            return

        info_dict = request.session.get("info")
        if info_dict:
            return
        return redirect('/login/')
