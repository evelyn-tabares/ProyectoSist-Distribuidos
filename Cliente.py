import socket
import eel
import json

# Inicializar eel
eel.init('web')

# Función para conectar con el servidor y enviar la suma
@eel.expose
def sumar_y_mostrar(num1, num2):
    try:
        # Conectar al servidor
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 8001))

            #Ejemplo de uso libreria eel para sumar y mostrar------------
            # Enviar datos al servidor en formato JSON
            data = {'opcion': '1', 'num1': num1, 'num2': num2}
            s.sendall(json.dumps(data).encode('utf-8'))

            # Recibir resultado del servidor
            resultado = s.recv(1024).decode('utf-8')
            print(f"Resultado: {resultado}")
            return resultado
            #Fin de ejemplo de uso libreria eel para sumar y mostrar------------

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
