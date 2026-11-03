from django.conf import settings
from datetime import datetime

def global_context(request):
    """Provides common variables across all templates."""
    return {
        'APP_NAME': 'CreatorSpark',
        'APP_VERSION': '1.0.0',
        'DEBUG': settings.DEBUG,
        'CURRENT_YEAR': datetime.now().year,
        'USER_AUTHENTICATED': request.user.is_authenticated,
        'MONGODB_ENABLED': bool(settings.MONGODB_URI),
        'PEXELS_ENABLED': bool(settings.PEXELS_API_KEY),
    }
