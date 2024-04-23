import socket
import json
from _thread import *

# Clase para representar a un jugador. 
class Player:
    def __init__(self, user_name, color_piece, socket):
        self.user_name = user_name
        self.color_piece = color_piece
        self.client_socket = socket
        self.status = "Ready"
    
    # Método para convertir el objeto a un diccionario
    def to_dict(self):
        return {"user_name": self.user_name, 
                "color_piece": self.color_piece,
                "status": self.status}
    
    # Método para enviar un mensaje al cliente. Aquí aparece el problema
    # La copia del socket del cliente que está en el hilo
    # ya no existe en el lado del cliente, porque el socket 
    # real en el cliente ya no existe.
    def sendall(self, message):
        self.client_socket.sendall(message)

    def __str__(self):
        return f"Usuario: {self.user_name}, Color: {self.color_piece}"


# Función para manejar las solicitudes de los clientes
def manejar_solicitud(client_socket, address):
    while True:
        #se recibe el JSON del ciente
        data = client_socket.recv(1024).decode('utf-8')

        if not data:
            break

        data = json.loads(data)
        new_player = Player(data["user_name"], data["color_piece"], client_socket)
        #Se agrega el nuevo jugador a la lista de jugadores
        players.append(new_player)
        
        #Se envía la lista de jugadores a todos los clientes
        broadcast(json.dumps({"players": [player.to_dict() for player in players]}).encode('utf-8'))

    client_socket.close()

# Función para enviar un mensaje a todos los clientes
def broadcast(message):
    for player in players:
        print(f"Enviando mensaje a {player.user_name}")
        player.sendall(message)

# Configuración del servidor
players = []
HOST = 'localhost'  # La dirección IP del servidor
PORT = 8001        # El puerto en el que el servidor escuchará las conexiones
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("Servidor esperando conexiones...")
    
    while True:
        client_socket, address = server_socket.accept()
        print(f"Conexión establecida desde {address}")
        
        #Crear el hilo para manejar la solicitud del cliente
        start_new_thread(manejar_solicitud, (client_socket, address))
        
