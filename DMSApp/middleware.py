from django.middleware.clickjacking import XFrameOptionsMiddleware

class CustomXFrameOptionsMiddleware(XFrameOptionsMiddleware):
    def get_xframe_options_value(self, request, response):
        return 'SAMEORIGIN'