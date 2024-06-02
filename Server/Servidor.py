import eventlet
import socketio
import os
from dotenv import dotenv_values
from handle_messages import App
import time
import requests 
from datetime import datetime

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








# Permite obtener la hora UTC de un servidor externo que se encuentra en la red
def get_current_time():
    try:
        response = requests.get('http://worldtimeapi.org/api/timezone/Etc/UTC')
        response.raise_for_status()
        data = response.json()
        utc_datetime_str = data['utc_datetime']
        utc_datetime = datetime.fromisoformat(utc_datetime_str.replace('Z', '+00:00'))
        
        return utc_datetime
    except requests.RequestException as e:
        print(f"Error fetching time from server: {e}")
        return None

# Obtener la hora actual del servidor de sincronización y enviarla a cada uno de los clientes que
# estaban conectados cuando empezó el juego
@sio.event
def synchronize_clocks(sid):
    #current_time = time.time()
    current_time = get_current_time()
    sio.emit('request_time', {'server_time': current_time.timestamp()}, to=sid)

# Recibe la hora del cliente y del servidor y calcula el ajuste que debe realizar 
@sio.event
def provide_time_offset(sid, data):
    server_time = data['server_time']
    client_time = data['client_time']
    offset = client_time - server_time
    
    # Almacena la diferencia de tiempo para el cliente actual
    ludo.update_time_offset(sid, offset)
    
    # Si todos los clientes han respondido, calcula la corrección de tiempo
    if ludo.all_clients_responded():
        average_offset = ludo.calculate_average_offset()
        
        for client_sid in clients:
            sio.emit('adjust_time', {'offset': average_offset}, to=client_sid)
        
        ludo.reset_time_offset()










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

# Verifica el estado del juego (si ya inicio) cuando un jugador se conecta al lobby.
# Si el juego ya inicio, redirige al jugador a la sala de espera evitando que se una a una partida que ya inicio.
@sio.event
def check_game_status(sid):    
    if ludo.get_game() == True:
        sio.emit("game_started", {"run": ludo.get_game(), "all_players": True}, to=sid)
        '''if len(ludo.get_players()) < 4:
            count_players = sio.start_background_task(check_num_players)
            sio.emit("game_started", {"run": ludo.get_game(), "all_players": False}, to=sid)
        elif len(ludo.get_players()) == 4:
            sio.emit("game_started", {"run": ludo.get_game(), "all_players": True}, to=sid)'''
    else:
        sio.emit("game_started", {"run": ludo.get_game(), "all_players": False}, to=sid)
        conected_players = sio.start_background_task(check_connected_players)

# Iniciar el juego cuando hay 2 o más jugadores conectados
@sio.event
def start_game(sid):
    #print("start_game")
    if len(ludo.get_players()) >= 2:
        ludo.set_game(True)
        for client in clients:
            sio.emit("start_game", ludo.get_game(), to=client)
            # Pedir la hora a cada jugador
            sio.emit("synchronize_clocks", to=client)
    else:
        sio.emit("error_start_game", {"success": False, "message": "No hay suficientes jugadores conectados."}, to=sid)

'''def check_num_players():
    while True:
        if len(ludo.get_players()) == 4:
            print("La sala está llena.")
            sio.emit("start_game_run", len(ludo.get_players())) 
            break
        else:
            sio.emit("start_game_run", len(ludo.get_players())) 
            sio.sleep(1)'''

# Obtiene los colores disponibles para seleccionar cuando un jugador se conecta a una partida que ya inicio
'''@sio.event
def get_available_colors(sid):
    #print("get_available_colors", ludo.get_available_colors())
    sio.emit("available_colors", ludo.get_available_colors(), to=sid)'''

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
            sio.emit("active_wating_room", ludo.get_game())
            break

# Función que se ejecuta en segundo plano y verifica si el juego ya empezo, para que 
# las personas que se conecten al lobby sean redirigidas a la sala de espera, donde pueden 
# ingresar a la partida que ya inicio. siempre y cuando haya espacio disponible.
'''def lobby_to_waiting_room():
    while True:
        if ludo.get_game() == True:
            sio.emit("active_wating_room", ludo.get_game())
            break
        else:
            #print("Verficando estado.")
            sio.sleep(1)  '''

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
    #connected_players = sio.start_background_task(check_connected_players)
    #lobby_to_wr = sio.start_background_task(lobby_to_waiting_room)
    eventlet.wsgi.server(eventlet.listen(('', PORT)), app)
    
    print(f"Server running on {HOST}:{PORT}")