'''import eventlet
import socketio
import os
from dotenv import dotenv_values
from handle_messages import App
from handle_messages import Ludo  # Importa la clase Ludo
from threading import Thread
import time'''
import eventlet
import socketio
import os
from dotenv import dotenv_values
from handle_messages import App
from handle_messages import Ludo  # Importa la clase Ludo
from threading import Thread
import time
import requests 
from datetime import datetime

# from handle_messages import handle_messages

ludo = App()
PLAYERS = []  # Lista de jugadores

ludof = None
parent_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(parent_dir, '..', '.env')
env_vars = dotenv_values(env_path)
# HOST = env_vars.get("SERVER_SOCKET_HOST")

HOST = env_vars.get("SERVER_SOCKET_HOST")
#HOST = '192.168.0.16'
# PORT = int(env_vars.get("SERVER_SOCKET_PORT"))
PORT = 8002
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

# Configuración del servidor
clients = {}
# Inicializar el primer turno
# Crear un nuevo jugador cuando se conecta al lobby
player_counter = 0  # Global counter for player codes



#====================================================================
# Funciones para sincronizar el reloj de los clientes con el servidor
# utilizando el algoritmo de Berkeley y un servidor UTC externo (o local)
# con time.time() de Python
#====================================================================
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
    current_time_server = get_current_time()

    if current_time_server is None:
        # Tomar la hora la hora local del servidor si no se puede obtener la hora de un servidor externo
        current_time_local = time.time()
        sio.emit('request_time', {'server_time': current_time_local}, to=sid)
    else:
        sio.emit('request_time', {'server_time': current_time_server.timestamp()}, to=sid)

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
#====================================================================
# Fin de las funciones para sincronizar el reloj de los clientes con el servidor
#====================================================================


# Crear un nuevo jugador cuando se conecta al lobby
@sio.event
def create_player(sid, data):
    global player_counter  # Declare player_counter as global
    
    if len(ludo.get_players()) < 4:
        result = ludo.create_player(data)
        print(result)
        if result['success']:
            player_counter += 1  # Increment the counter
            player_id = data['color_piece']
            # Add player_id to data
            PLAYERS.append(player_id)
            print("jugadores en el lobby: ", PLAYERS)
            clients[sid] = data['user_name']

            if data['type'] == "on_game":
                sio.emit("user_in_game", True, to=sid)
            else:
                sio.emit("users_list_update", ludo.get_players())
        else:
            sio.emit("error_crte_player", result, to=sid)
    else:
        sio.emit("error_crte_player", {"success": False, "message": "La sala está llena."}, to=sid)



    #print("hey", sid, data)
    '''result = ludo.create_player(data)
    if result['success']:
        player_counter += 1  # Increment the counter
        player_id = data['color_piece']
        # Add player_id to data
        PLAYERS.append(player_id)
        clients[player_id] = data['user_name']


        print("Jugadores conectados", ludo.get_players())
        sio.emit("users_list_update", ludo.get_players())
        if player_counter == 2:
            ludof = Ludo(PLAYERS)
            start_game()

             # Create Ludo instance after players have been added
        # Iniciar un nuevo hilo para el jugador
        #player_thread = Thread(target=player_loop, args=(sid,))
        # player_thread.start()'''

# Actualizar la lista de jugadores en el lobby cada segundo
@sio.event
def update_players_list(sid, data):
    #print("actualizando lista", sid)
    sio.emit("users_list_update", ludo.get_players())

# Eliminar un jugador cuando se desconecta del lobby
@sio.event
def disconnect_player(sid):
    #print('disconnect ', sid)
    print("Lista de clientes: ", clients)
    print("Lista de jugadores en LUDO: ", ludo.get_players())
    player_name = clients.pop(sid, None)
    print("Nombre jugador a eliminar: ", player_name)
    #eliminar de PLAYERS el jugador que se va a desconectar
    #mirar cual es el color de player_name
    color = ludo.get_color_player(player_name)
    print("color a eliminar: ", color)
    PLAYERS.remove(color)

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

'''def start_game():
    print("Starting game")
    first_player()'''
# Iniciar el juego cuando hay 2 o más jugadores conectados
@sio.event
def start_game(sid, data):
    global ludof
    #print("start_game")
    if len(ludo.get_players()) >= 2:
        ludo.set_game(True)
        ludof = Ludo(PLAYERS)
        for client in clients:
            sio.emit("start_game", ludo.get_game(), to=client)
            # Pedir la hora a cada jugador
            sio.emit("synchronize_clocks", to=client)
            
        first_player(data)    
    else:
        sio.emit("error_start_game", {"success": False, "message": "No hay suficientes jugadores conectados."}, to=sid)


def player_loop(sid):
    while True:
        time.sleep(1)  # Esperar un segundo antes de la próxima iteración



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



@sio.event
def first_player(data):
    if (data["isSelectedFirtsPlayer"] == True):
        result = ludof.first_player()
        print("first player", result)
        sio.emit("first_player", result)

@sio.event
def on_dice_click(sid, data=None):
    print(f"Client {sid} clicked the dice")
    color_piece = data['color_piece']  # Acceder a 'color_piece' en los datos enviados por el cliente
    print(f"Color piece: {color_piece}")
    result = ludof.on_dice_click(color_piece)  # Aquí puedes pasar 'color_piece' a la función si es necesario
    sio.emit("dice_clicked", result)

@sio.event
def piece_clicked(sid, data):
    player = data['player']
    piece = data['piece']
    result = ludof.handle_piece_click(player, piece)
    sio.emit("piece_clicked", result)
    # Aquí puedes manejar los datos del jugador y la pieza


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
    eventlet.wsgi.server(eventlet.listen(('', PORT)), app)
    print(f"Server running on {HOST}:{PORT}")