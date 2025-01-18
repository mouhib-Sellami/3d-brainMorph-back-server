"""
WSGI config for brainMorph_back_server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""
import eventlet.wsgi
import eventlet
import os
from .socket_handler import sio
import socketio
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brainMorph_back_server.settings')

django_app = StaticFilesHandler(get_wsgi_application())
application = socketio.WSGIApp(sio, django_app)

eventlet.wsgi.server(eventlet.listen(('', 8000)), application)