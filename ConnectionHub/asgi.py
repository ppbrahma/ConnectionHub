import os

from channels.auth import AuthMiddlewareStack
from channels.layers import get_channel_layer
from channels.routing import ProtocolTypeRouter, URLRouter
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from django.core.asgi import get_asgi_application

import Communications.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ConnectionHub.settings')

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'websocket': AuthMiddlewareStack(
            URLRouter(
                Communications.routing.websocket_urlpatterns
            )
        ),
    }
)

application = ASGIStaticFilesHandler(application)

channel_layer = get_channel_layer()

