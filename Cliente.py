import socket
import eel
import json

# Inicializar eel
eel.init('web')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Función para enviar los datos del nuevo usuario al servidor
@eel.expose
def new_user(user_name, color_piece):
    #Conectar al servidor
    try:
            #Enviar datos al servidor en formato JSON
            data = {'user_name': user_name, 'color_piece': color_piece}
            s.sendall(json.dumps(data).encode('utf-8'))

            #Recibir resultado del servidor
            resultado = s.recv(1024).decode('utf-8')
            
            print(f"Usuarios conectados: {resultado}")
            
            return resultado
            #El problema está aquí, porque al salir del 
            #with, se cierra la conexión con el servidor y 
            #el socket s no se puede usar más. Entonces, el 
            #hilo del servidor no encuentra el socket que tiene
            #cada objeto player y no puede hacer broadcast.
    except Exception as e:
        print("Error:", e)

# Ejecutar la aplicación
def start():
    try:
        # Connect to the serve
        print("Connecting to the server...")
        s.connect(('localhost', 8001))

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

