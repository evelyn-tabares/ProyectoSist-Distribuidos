import json

class App:
    def __init__(self):
        self.__rooms = {}

    def create_room(self, data):
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
        return self.__rooms

