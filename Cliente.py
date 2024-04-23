import socket
import eel
import json

# Inicializar eel
eel.init('web')

@eel.expose
#Función para enviar los datos del nuevo usuario al servidor
def new_user(user_name, color_piece):
    #Conectar al servidor
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 8001))

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
    #Se inicia la aplicación en el archivo index.html
    #Se ingresan los datos de los input y se envian al servidor 
    #llamando a la función sumar_y_mostrar
    #para que realice la suma y devuelva el resultado
    #Se muestra el resultado en el div resultado
    eel.start('index.html')
    

# Iniciar el cliente
start()
