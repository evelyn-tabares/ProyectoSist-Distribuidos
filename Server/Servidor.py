import eventlet
import socketio
import os
from dotenv import dotenv_values
from handle_messages import App
from handle_messages import Ludo  # Importa la clase Ludo
from threading import Thread
import time

# from handle_messages import handle_messages

ludo = App()
PLAYERS = []  # Lista de jugadores

ludof = None
parent_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(parent_dir, '..', '.env')
env_vars = dotenv_values(env_path)
# HOST = env_vars.get("SERVER_SOCKET_HOST")
HOST = '192.168.0.16'
# PORT = int(env_vars.get("SERVER_SOCKET_PORT"))
PORT = 8002
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

# Configuración del servidor
clients = {}
# Inicializar el primer turno
# Crear un nuevo jugador cuando se conecta al lobby
player_counter = 0  # Global counter for player codes

@sio.event
def create_player(sid, data):
    global ludof
    global player_counter  # Declare player_counter as global

    print("hey", sid, data)
    result = ludo.create_player(data)
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
        # player_thread.start()


def player_loop(sid):
    while True:
        time.sleep(1)  # Esperar un segundo antes de la próxima iteración

def start_game():
    print("Starting game")
    first_player()

# Actualizar la lista de jugadores en el lobby cada segundo
@sio.event
def update_players_list(sid, data):
    print("actualizando lista", sid)
    sio.emit("users_list_update", ludo.get_players())

@sio.event
def first_player(sid, data):
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