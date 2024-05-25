import socket
import eel
import json

# Inicializar eel
eel.init('web')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Función para enviar la suma al servidor
@eel.expose
def sumar_y_mostrar(num1, num2):
    try:
        # Enviar datos al servidor en formato JSON
        data = {'opcion': '1', 'num1': num1, 'num2': num2}
        s.sendall(json.dumps(data).encode('utf-8'))

        # Recibir resultado del servidor
        resultado = s.recv(1024).decode('utf-8')
        print(f"Resultado: {resultado}")
        return resultado

    except Exception as e:
        print("Error:", e)


@eel.expose
def obtener_constants():
    try:
        data = {'opcion': '3'}
        s.sendall(json.dumps(data).encode('utf-8'))

        constants = s.recv(1024).decode('utf-8')
        constants = json.loads(constants)
        # if 'PLAYERS' in constants:
        #     print("Players received from server:", constants)
        #     constants = constants['PLAYERS']  # Assign the 'PLAYERS' array to 'players'
        #     # process_players(players)  # Handle the received data
        return constants
    except json.JSONDecodeError:
        print("Error: The server did not send a valid JSON.")

# def process_players(players):
#     for player in players['PLAYERS']:
#         print("Player:", player)


# Ejecutar la aplicación
def start():
    try:
        # Connect to the serve
        print("Connecting to the server...")
        s.connect(('localhost', 8001))

        obtener_constants()

        # Start the application in the index.html file
        # Input data is sent to the server by calling the sumar_y_mostrar function
        # The function performs the sum and returns the result
        # The result is displayed in the resultado div
        eel.start('index.html')

    except socket.error as e:
        print("Error connecting to the server:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
# Iniciar el cliente
start()