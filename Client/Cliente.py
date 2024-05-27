import socket
import eel
import json
import os
from dotenv import dotenv_values

parent_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(parent_dir, '..', '.env')
env_vars = dotenv_values(env_path)

BACKEND_SOCKET_HOST = env_vars.get("SERVER_SOCKET_HOST")
BACKEND_SOCKET_PORT = int(env_vars.get("SERVER_SOCKET_PORT"))
FRONTEND_PORT = int(env_vars.get("FRONTEND_PORT"))


# Inicializar eel
eel.init('web')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Función para enviar los datos del nuevo usuario al servidor
@eel.expose
def new_user(user_name, color_piece):
    #Conectar al servidor
    try:
            #Enviar datos al servidor en formato JSON
            print("Enviando datos al servidor...")
            data = {'action': 'new_user', 'user_name': user_name, 'color_piece': color_piece}
            s.sendall(json.dumps(data).encode('utf-8'))

            #Recibir resultado del servidor
            resultado = s.recv(1024).decode('utf-8')
            
            print(f"Usuarios conectados: {resultado}")
            
            return resultado
    except Exception as e:
        print("Error:", e)

# Función para actualizar la lista de usuarios conectados en el lobby
@eel.expose
def update_users():
    try:
        #Enviar petición al servidor
        s.sendall(json.dumps({'action': 'update'}).encode('utf-8'))
        
        #Recibir la lista de usuarios conectados
        resultado = s.recv(1024).decode('utf-8')
        
        #print(f"Usuarios conectados: {resultado}")
        
        return resultado
    except Exception as e:
        print("Error:", e) 

# Ejecutar la aplicación
def start():
    #Se inicia la aplicación en el archivo index.html
    #Se ingresan los datos de los input y se envian al servidor 
    #llamando a la función sumar_y_mostrar
    #para que realice la suma y devuelva el resultado
    #Se muestra el resultado en el div resultado
    eel.start('index.html', mode='chrome', port=FRONTEND_PORT)
    

# Iniciar el cliente
start()
