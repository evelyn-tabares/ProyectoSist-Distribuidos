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

# Ejecutar la aplicación
def start():
    #Se inicia la aplicación en el archivo index.html
    #Se ingresan los datos de los input y se envian al servidor 
    #llamando a la función sumar_y_mostrar
    #para que realice la suma y devuelva el resultado
    #Se muestra el resultado en el div resultado
    eel.start('index.html', mode=None, port=FRONTEND_PORT)
    

# Iniciar el cliente
start()
