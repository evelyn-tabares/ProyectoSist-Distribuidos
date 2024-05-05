import eventlet
import socketio
import os
from dotenv import dotenv_values
from handle_messages import App
# from handle_messages import handle_messages

ludo = App()

parent_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(parent_dir, '..', '.env')
env_vars = dotenv_values(env_path)

HOST = env_vars.get("SERVER_SOCKET_HOST")
PORT = int(env_vars.get("SERVER_SOCKET_PORT"))

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

# Configuración del servidor
clients = {}

@sio.event
def create_game_room(sid, data):
    print("hey", sid, data)
    result = ludo.create_room(data)
    print(result)
    if result['success']:
        sio.emit("rooms_list_update", ludo.get_rooms())

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', PORT)), app)