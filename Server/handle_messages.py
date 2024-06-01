import json

class App:
    def __init__(self):
        #self.__rooms = {}
        self.__players = {}
        self.__game = False
        self.__avaliable_pieces = ['red', 'blue', 'green', 'yellow']

    # Crear un nuevo jugador
    def create_player(self, data):
        #print("data", data)
        name = data["user_name"]
        color_piece = data["color_piece"]
        status = data["status"]
        
        #print("avaliable_pieces", self.__avaliable_pieces)

        if name in self.__players:
            return {"success": False, "message": f"Jugador '{name}' ya existe."}
        
        # Verificar si el color de la pieza seleccionada por el jugador ya fue seleccionado por otro jugador
        if self.__avaliable_pieces.count(color_piece) == 0:
            return {"success": False, "message": f"Color '{color_piece}' fue seleccionado por otro jugador."}

        # Verificar si es el primer jugador en conectarse
        if len(self.__players) == 0:
            primero = True
        else:
            primero = False

        self.__players[name] = {
            "name": name,
            "color_piece": color_piece,
            "status": status, 
            "primero": primero
        }

        # Borrar el color de la lista de colores disponibles
        self.__avaliable_pieces.remove(color_piece)

        return {"success": True, "name": name, "color_piece": color_piece, "status": status, "message": f"Jugador '{name}' creado correctamente."}   
    
    # Eliminar un jugador
    def remove_player(self, name):
        if name in self.__players:
            self.__avaliable_pieces.append(self.__players[name]["color_piece"])
            del self.__players[name]
            
            if len(self.__players) > 0:
                self.__players[list(self.__players.keys())[0]]["primero"] = True
                
            return {"success": True, "message": f"Player '{name}' eliminado correctamente."}
        else:
            return {"success": False, "message": f"Player '{name}' no existe."}

    '''def create_room(self, data):
        name = data["name"]
        num_of_players = data["playersQuantity"]
        password = data["password"]
        room_data = data["room_data"]
        if name in self.__rooms:
            return {"success": False, "message": f"Room '{name}' already exists."}
        else:
            print("dadaname")
            self.__rooms[name] = {
                "name": name,
                "password": password,
                "room_data": room_data,
                "num_of_players": num_of_players
            }
            return {"success": True, "message": f"Room '{name}' created successfully."}
        
    def get_rooms(self):
        return self.__rooms'''
    
    # Obtener la lista de jugadores conectados
    def get_players(self):
        return self.__players

    def get_game(self):
        return self.__game
    
    def get_pieces(self):
        return self.__avaliable_pieces
    
    def get_available_colors(self):
        return self.__avaliable_pieces
    
    def set_game(self, game):
        self.__game = game



