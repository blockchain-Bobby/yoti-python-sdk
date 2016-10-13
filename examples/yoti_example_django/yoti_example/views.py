from django.views.generic import TemplateView

from yoti.client import Client

from .app_settings import (
    YOTI_APPLICATION_ID,
    YOTI_VERIFICATION_KEY,
    YOTI_CLIENT_SDK_ID,
    YOTI_FULL_KEY_FILE_PATH
)


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        context = {
            'app_id': YOTI_APPLICATION_ID,
            'verification_key': YOTI_VERIFICATION_KEY,
        }
        return self.render_to_response(context)


class AuthView(TemplateView):
    template_name = 'profile.html'

    def get(self, request, *args, **kwargs):
        client = Client(YOTI_CLIENT_SDK_ID, YOTI_FULL_KEY_FILE_PATH)
        activity_details = client.get_activity_details(request.GET['token'])
        context = activity_details.user_profile
        return self.render_to_response(context)
