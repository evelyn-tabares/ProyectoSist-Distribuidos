import eventlet
import socketio
import os
from dotenv import dotenv_values
from handle_messages import App
import threading

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
    #print(result))
    if result['success']:
        sio.emit("users_list_update", ludo.get_players())
    else:
        sio.emit("error_crte_player", result)

# Actualizar la lista de jugadores en el lobby cada segundo
@sio.event
def update_players_list(sid, data):
    #print("actualizando lista", sid)
    sio.emit("users_list_update", ludo.get_players())

# Eliminar un jugador cuando se desconecta del lobby
@sio.event
def disconnect_player(sid, data):
    #print('disconnect ', sid)
    ludo.remove_player(data)
    sio.emit("users_list_update", ludo.get_players())

# Función que se ejecuta en segundo plano y verifica si hay minimo 2 jugadores conectados.
def check_connected_players():
    while True:
        #print("Background task")
        if len(ludo.get_players()) >= 2:
            print("Hay 2 o más jugadores conectados. El juego va a comenzar.")
            ludo.set_game(True)
            sio.emit("start_game", ludo.get_game()) 

            break            
        else:
            print("No hay suficientes jugadores conectados")
        
        sio.emit("users_list_update", ludo.get_players())
        sio.sleep(1)        

'''@sio.event
def create_game_room(sid, data):
    print("hey", sid, data)
    result = ludo.create_room(data)
    print(result)
    if result['success']:
        sio.emit("rooms_list_update", ludo.get_rooms())'''

if __name__ == '__main__':
    conected_players = sio.start_background_task(check_connected_players)
    #avaliable_pieces = sio.start_background_task(check_available_pieces)
    #thread = threading.Thread(target=check_connected_players)
    #thread.start()

    eventlet.wsgi.server(eventlet.listen(('', PORT)), app)
    print(f"Server running on {HOST}:{PORT}")