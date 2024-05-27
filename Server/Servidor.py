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

# Crear un nuevo jugador cuando se conecta al lobby
@sio.event
def create_player(sid, data):
    print("hey", sid, data)
    result = ludo.create_player(data)
    #print(result)
    if result['success']:
        print("Jugadores conectados", ludo.get_players())
        sio.emit("users_list_update", ludo.get_players())

# Actualizar la lista de jugadores en el lobby cada segundo
@sio.event
def update_players_list(sid, data):
    print("actualizando lista", sid)
    sio.emit("users_list_update", ludo.get_players())

'''def my_background_task(my_argument):
    while True:
        sio.emit("users_list_update", ludo.get_players())
        eventlet.sleep(1)'''
        




'''@sio.event
def create_game_room(sid, data):
    print("hey", sid, data)
    result = ludo.create_room(data)
    print(result)
    if result['success']:
        sio.emit("rooms_list_update", ludo.get_rooms())'''

if __name__ == '__main__':
    #task = sio.start_background_task(my_background_task, 123)
    eventlet.wsgi.server(eventlet.listen(('', PORT)), app)
    print(f"Server running on {HOST}:{PORT}")