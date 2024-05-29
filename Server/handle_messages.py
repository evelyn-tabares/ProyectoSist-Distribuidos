import json

class App:
    def __init__(self):
        self.__rooms = {}
        self.__players = {}
        self.__game = None
        self.__avaliable_pieces = ['red', 'blue', 'green', 'yellow']

    # Crear un nuevo jugador
    def create_player(self, data):
        print("data", data)
        name = data["user_name"]
        color_piece = data["color_piece"]
        status = data["status"]
        
        if name in self.__players:
            return {"success": False, "message": f"Player '{name}' already exists."}
        
        # Verificar si el color de la pieza seleccionada por el jugador ya fue seleccionado por otro jugador
        for player in self.__players:
            if self.__players[player]["color_piece"] == color_piece:
                return {"success": False, "message": f"Color '{color_piece}' already selected by another player."}

        self.__players[name] = {
            "name": name,
            "color_piece": color_piece,
            "status": status
        }

        # Borrar el color de la lista de colores disponibles
        self.__avaliable_pieces.remove(color_piece)

        return {"success": True, "name": name, "color_piece": color_piece, "status": status, "message": f"Player '{name}' created successfully."}   
    
    # Eliminar un jugador
    def remove_player(self, name):
        if name in self.__players:
            del self.__players[name]
            return {"success": True, "message": f"Player '{name}' removed successfully."}
        else:
            return {"success": False, "message": f"Player '{name}' does not exist."}

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
    
    def set_game(self, game):
        self.__game = game



