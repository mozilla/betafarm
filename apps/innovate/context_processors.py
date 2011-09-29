from django.conf import settings

def app_name(request):
    return {
        'app_name': settings.APP_NAME
    }
