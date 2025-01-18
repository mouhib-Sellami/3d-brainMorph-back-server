
import socketio
import logging
logger = logging.getLogger('Local_Server')
sio = socketio.Server(cors_allowed_origins='*', async_mode="eventlet")


@sio.on('connection-bind')
def connection_bind(sid, data):
    logger.info("connection bind {}".format(sid))


@sio.on('disconnect')
def disconnect(sid):
    """"""
    logger.error("{} disconnected")


@sio.on('connect')
def connect(sid, _):
    logger.info("new connection {}".format(sid))
