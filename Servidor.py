import socket
import json
import constants  # Importa el módulo de constantes

# Función para sumar dos números
def sumar(num1, num2):
    return int(num1) + int(num2)

# Función para manejar las solicitudes de los clientes
def manejar_solicitud(client_socket, address):
    while True:
        #se recibe el JSON del ciente
        data = client_socket.recv(1024).decode('utf-8')
        print(f"data: {data}")
        if not data:
            break
        data = json.loads(data)
        opcion = data.get("opcion")
        print(f"opcion: {opcion}")


        if opcion == '1':
            num1 = data.get("num1")
            num2 = data.get("num2")
            print(f"num1: {num1}, num2: {num2}")

            resultado = sumar(num1, num2)
            response = str(resultado)
            client_socket.sendall(response.encode('utf-8'))

        if opcion == '3':
            # Enviar la constante PLAYERS al cliente
            print("Enviando constante PLAYERS al cliente...")
            response = json.dumps({'PLAYERS': constants.PLAYERS})
            print("Enviando respuesta:", response)  # Mensaje de depuración

            client_socket.sendall(response.encode('utf-8'))

        else:
            response = "Opción no válida"
            client_socket.sendall(response.encode('utf-8'))

    client_socket.close()

# Configuración del servidor
HOST = 'localhost'  # La dirección IP del servidor
PORT = 8001        # El puerto en el que el servidor escuchará las conexiones
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("Servidor esperando conexiones...")
    while True:
        client_socket, address = server_socket.accept()
        print(f"Conexión establecida desde {address}")
        manejar_solicitud(client_socket, address)
