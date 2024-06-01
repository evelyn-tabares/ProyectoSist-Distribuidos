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
    #print("hey", sid, data)

    if len(ludo.get_players()) < 4:
        result = ludo.create_player(data)
        #print(result))
        if result['success']:
            clients[sid] = data['user_name']

            if data['type'] == "on_game":
                sio.emit("user_in_game", True, to=sid)
            else:
                sio.emit("users_list_update", ludo.get_players())
        else:
            sio.emit("error_crte_player", result, to=sid)
    else:
        sio.emit("error_crte_player", {"success": False, "message": "La sala está llena."}, to=sid)

# Actualizar la lista de jugadores en el lobby cada segundo
@sio.event
def update_players_list(sid, data):
    #print("actualizando lista", sid)
    sio.emit("users_list_update", ludo.get_players())

# Eliminar un jugador cuando se desconecta del lobby
@sio.event
def disconnect_player(sid):
    #print('disconnect ', sid)
    player_name = clients.pop(sid, None)

    if player_name:
        ludo.remove_player(player_name)

    sio.emit("users_list_update", ludo.get_players())

# Verifica el estado del juego (si ya inicio) cuando un jugador se conecta al lobby
@sio.event
def check_game_status(sid):
    #print("=====GAME======::: ", sid)
    #print("check_game_status")
    
    if ludo.get_game() == True:
        if len(ludo.get_players()) < 4:
            count_players = sio.start_background_task(check_num_players)
            sio.emit("game_started", {"run": ludo.get_game(), "all_players": False}, to=sid)
        elif len(ludo.get_players()) == 4:
            sio.emit("game_started", {"run": ludo.get_game(), "all_players": True}, to=sid)
    else:
        sio.emit("game_started", {"run": ludo.get_game(), "all_players": False}, to=sid)
        conected_players = sio.start_background_task(check_connected_players)

@sio.event
def start_game(sid):
    #print("start_game")
    if len(ludo.get_players()) >= 2:
        ludo.set_game(True)
        for client in clients:
            sio.emit("start_game", ludo.get_game(), to=client)
        #sio.emit("start_game", ludo.get_game(), to=)
    else:
        sio.emit("error_start_game", {"success": False, "message": "No hay suficientes jugadores conectados."}, to=sid)

def check_num_players():
    while True:
        if len(ludo.get_players()) == 4:
            print("La sala está llena.")
            sio.emit("start_game_run", len(ludo.get_players())) 
            break
        else:
            sio.emit("start_game_run", len(ludo.get_players())) 
            sio.sleep(1)

# Obtiene los colores disponibles para seleccionar cuando un jugador se conecta a una partida que ya inicio
@sio.event
def get_available_colors(sid):
    #print("get_available_colors", ludo.get_available_colors())
    sio.emit("available_colors", ludo.get_available_colors(), to=sid)

# Función que se ejecuta en segundo plano y verifica si hay minimo 2 jugadores conectados para iniciar la partida.
def check_connected_players():
    while True:
        '''if len(ludo.get_players()) >= 2:
            print("Hay 2 o más jugadores conectados. El juego va a comenzar.")
            ludo.set_game(True)
            sio.emit("start_game", ludo.get_game()) 

            break            
        else:
            print("No hay suficientes jugadores conectados")'''
        
        if ludo.get_game() == False:
            sio.emit("users_list_update", ludo.get_players())
            sio.sleep(1)
        else:
            break

# Función que se ejecuta en segundo plano y verifica si el juego ya empezo, para que 
# las personas que se conecten al lobby sean redirigidas a la sala de espera, donde pueden 
# ingresar a la partida que ya inicio. siempre y cuando haya espacio disponible.
def lobby_to_waiting_room():
    while True:
        if ludo.get_game() == True:
            
            sio.emit("active_wating_room", ludo.get_game())
            break
        else:
            #print("Verficando estado.")
            sio.sleep(1)  

'''@sio.event
def create_game_room(sid, data):
    print("hey", sid, data)
    result = ludo.create_room(data)
    print(result)
    if result['success']:
        sio.emit("rooms_list_update", ludo.get_rooms())'''

if __name__ == '__main__':
    #avaliable_pieces = sio.start_background_task(check_available_pieces)
    #thread = threading.Thread(target=check_connected_players)
    #thread.start()
    lobby_to_wr = sio.start_background_task(lobby_to_waiting_room)
    eventlet.wsgi.server(eventlet.listen(('', PORT)), app)
    
    print(f"Server running on {HOST}:{PORT}")