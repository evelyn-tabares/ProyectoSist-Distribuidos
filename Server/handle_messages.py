import json
import random
import socketio

sio = socketio.Client()
# Constants
BASE_POSITIONS = {
    "P1": [500, 501, 502, 503],
    "P2": [800, 801, 802, 803],
    "P3": [600, 601, 602, 603],
    "P4": [700, 701, 702, 703],
}

START_POSITIONS = {
    "P1": 0,
    "P2": 13,
    "P3": 26,
    "P4": 39,
}

HOME_ENTRANCE = {
    "P1": [100, 101, 102, 103, 104],
    "P2": [400, 401, 402, 403, 404],
    "P3": [200, 201, 202, 203, 204],
    "P4": [300, 301, 302, 303, 304],
}

HOME_POSITIONS = {
    "P1": 105,
    "P2": 405,
    "P3": 205,
    "P4": 305
}

TURNING_POINTS = {
    "P1": 50,
    "P2": 11,
    "P3": 24,
    "P4": 37,
}

SAFE_POSITIONS = [0, 8, 13, 21, 26, 34, 39, 47]

STATE = {
    "DICE_NOT_ROLLED": 'DICE_NOT_ROLLED',
    "DICE_ROLLED": 'DICE_ROLLED',
}

OUT_OF_GAME = -1

# PLAYERS = ['P1', 'P2', 'P3', 'P4']
global_player_names = {} 
global_player_firts_count = {}
first_turn_response = False
dice_attemps_firts_turn = {}
class App:
    def __init__(self):
        self.__rooms = {}
        self.__players = {}
        self.__game = False
        self.__avaliable_pieces = ['P1', 'P2', 'P3', 'P4']
        self.time_offsets = {}

    # ================================================
    # Métodos para la sincronización del reloj de los jugadores
    # ================================================
    # Guardar el offset de tiempo de todos los jugadores conectados para 
    # calcular la corrección de tiempo con el promedio de todos los offsets 
    def update_time_offset(self, sid, offset):
        self.time_offsets[sid] = offset
    
    # Verificar si todos los jugadores conectados han respondido con su offset de tiempo
    def all_clients_responded(self):
        return len(self.time_offsets) == len(self.__players)
    
    # Calcular el promedio de todos los offsets de tiempo de los jugadores conectados
    def calculate_average_offset(self):
        total_offset = sum(self.time_offsets.values())
        return total_offset / len(self.time_offsets)
    
    # Reiniciar la lista de offsets de tiempo
    def reset_time_offset(self):
        self.time_offsets = {}
    # ================================================
    # Fin de los métodos para la sincronización del reloj de los jugadores
    # ================================================



    # Crear un nuevo jugador
    def create_player(self, data):
        print("data", data)
        name = data["user_name"]     
        color_piece = data["color_piece"]
        status = data["status"]
        player_id = data['color_piece']
           # Assign player number based on color
        
        
        # Comprobar si el nombre ya existe
        if name in self.__players:
            return {"success": False, "message": f"Jugador '{name}' ya existe."}
        
        # Verificar si el color de la pieza seleccionada por el jugador ya fue seleccionado por otro jugador
        if self.__avaliable_pieces.count(color_piece) == 0:
            color = ''
            if color_piece == 'P1':
                color = 'Azul'
            elif color_piece == 'P2':
                color = 'Amarillo'
            elif color_piece == 'P3':
                color = 'Verde'
            elif color_piece == 'P4':
                color = 'Rojo'
            return {"success": False, "message": f"Color '{color}' fue seleccionado por otro jugador."}
        
        # Verificar si es el primer jugador en conectarse
        if len(self.__players) == 0:
            primero = True
        else:
            primero = False

        self.__players[name] = {
            "name": name,
            "color_piece": color_piece,
            "status": status,
            "primero": primero,
            "player_id": data['color_piece']
        }

        # Borrar el color de la lista de colores disponibles
        self.__avaliable_pieces.remove(color_piece)
        global_player_names[player_id] = name
        global_player_firts_count[color_piece] = 0

        return {"success": True, "name": name, "player_id": player_id, "color_piece": color_piece, "status": status, "message": f"Jugador '{name}' creado correctamente."}   
    
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

    
    # Obtener la lista de jugadores conectados
    def get_players(self):
        return self.__players
    
    #obtener el color de la pieza de un jugador 
    def get_color_player(self, player_name):
        for player in self.__players.values():
            if player["name"] == player_name:
                return player["color_piece"]
        return None
        

    def get_game(self):
        return self.__game
    
    def get_pieces(self):
        return self.__avaliable_pieces
    
    def get_available_colors(self):
        return self.__avaliable_pieces
    
    def set_game(self, game):
        self.__game = game
    
class Ludo():
    def __init__(self, PLAYERS):
        self.PLAYERS = PLAYERS
        self.current_positions = {player: BASE_POSITIONS[player].copy() for player in self.PLAYERS}
        self.first_exit = {player: False for player in self.PLAYERS}
        self._dice_value = None
        self._dice_value2 = None
        self._pair_count = 0
        self.first_roll = {player: True for player in self.PLAYERS}  # Añadir una variable first_roll para cada jugador

        self._turn = None
        self._state = None
        self.extra_turn = False
        self.base_exit_attempts = 0
        self.first_turn_results = {}
        self.unhighlighted_pieces = False
        self.newpositionplayer = None
        self.first_player1 = None
        self.dice_sums = {}
        self.isJailOut = {player: False for player in self.PLAYERS}
    
        self.turn_count = 0
        self.userAfter = None
        self.userAfterName = None
        self.first_turn_response = False
        self.player_for_elegible_pieces = None

        print(f"PLAYERS: {self.PLAYERS}")

    @property
    def dice_value(self):
        return self._dice_value

    @dice_value.setter
    def dice_value(self, value):
        self._dice_value = value

    @property
    def dice_value2(self):
        return self._dice_value2

    @dice_value2.setter
    def dice_value2(self, value):
        self._dice_value2 = value

    @property
    def pair_count(self):
        return self._pair_count

    @pair_count.setter
    def pair_count(self, value):
        self._pair_count = value
        if value == 3:
            self.remove_piece_from_game(self.PLAYERS[self.turn], 0)
            self._pair_count = 0

    @property
    def turn(self):
        return self._turn

    @turn.setter
    def turn(self, value):
        if isinstance(value, int) and 0 <= value < len(self.PLAYERS):
            self._turn = value
        else:
            raise ValueError("Turn must be an integer between 0 and the number of players.")

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def first_player(self):
        self.first_player1 = self.PLAYERS[0]
        return {"first_player": self.PLAYERS[0], "user_name": global_player_names[self.PLAYERS[0]]} 
   
    def determine_first_turn(self, color_piece):
        self.turn_count += 1
        dice_attemps_firts_turn[color_piece] = 0

        if self.dice_value == 6 and self.dice_value2 == 6:
            self.PLAYERS.remove(color_piece)
            self.PLAYERS.insert(0, color_piece)
            self.turn = 0  # El turno ahora es del primer jugador
            return True
        else:
            self.dice_sums[color_piece] = self.dice_value + self.dice_value2

        if self.turn_count == len(self.PLAYERS):
            # Ordenar self.dice_sums de mayor a menor
            sorted_dice_sums = sorted(self.dice_sums.items(), key=lambda item: item[1], reverse=True)

            # Reordenar self.PLAYERS en función del orden de self.dice_sums
            self.PLAYERS = [item[0] for item in sorted_dice_sums]

            return True

        return False

    def on_dice_click(self, color_piece):
        if self.turn == None:
            self.turn = 0
        self.userAfter = None
        self.userAfterName = None
        self.player_for_elegible_pieces = None
       
        print('dice clicked! por el jugador', color_piece)
        self.dice_value = random.randint(1, 6)
        self.dice_value2 = random.randint(1, 6)
        print(f"Dice values: {self.dice_value}, {self.dice_value2}")

        if global_player_firts_count[color_piece] == 0:
            self.first_turn_response = self.determine_first_turn(color_piece)
            global_player_firts_count[color_piece] += 1

            if self.first_turn_response == True: #The array has been reordered
               self.state = STATE["DICE_NOT_ROLLED"]
               player = self.PLAYERS[0] #The array is 0 indexed 
               dice_attemps_firts_turn[player] = 4
               eligible_pieces = []
               print("player numero 1 al reordenar array", player)
               print("dice_attemps_firts_turn", dice_attemps_firts_turn[player])

               return {"dice_values": (self.dice_value, self.dice_value2), 
                    "eligible_pieces": eligible_pieces,
                    "player": player, "state": self.state, 
                    "user_name": global_player_names[player],
                    "first_turn_response": self.first_turn_response}
            else:
                self.increment_turn()
                eligible_pieces = []
                player = self.PLAYERS[self.turn] #The array is 0 indexed 

                return {"dice_values": (self.dice_value, self.dice_value2), 
                    "eligible_pieces": eligible_pieces,
                    "player": player, "state": self.state, 
                    "user_name": global_player_names[player],
                    "first_turn_response": self.first_turn_response}
            
        if dice_attemps_firts_turn[color_piece] > 1 and self.dice_value != self.dice_value2:
            print("jugador", color_piece)
            print("dice_attemps_firts_turn", dice_attemps_firts_turn[color_piece])
            dice_attemps_firts_turn[color_piece] -= 1
            self.state = STATE["DICE_NOT_ROLLED"]
            eligible_pieces = []
            player = self.PLAYERS[0] #The array is 0 indexed 

          
            if dice_attemps_firts_turn[color_piece] == 1:
                self.first_turn_response = False
                self.state = STATE["DICE_NOT_ROLLED"]
                player = self.PLAYERS[self.turn] #The array is 0 indexed 


            print("dice_attemps_firts_turn", dice_attemps_firts_turn[color_piece])
            return {"dice_values": (self.dice_value, self.dice_value2), 
                    "eligible_pieces": eligible_pieces,
                    "player": player, "state": self.state, 
                    "user_name": global_player_names[player],
                    "first_turn_response": self.first_turn_response}
        
        if dice_attemps_firts_turn[color_piece] > 1 and self.dice_value == self.dice_value2:
            dice_attemps_firts_turn[color_piece]  = 0
            # self.first_turn_response = False
            eligible_pieces = self.get_eligible_pieces(color_piece)
            self.turn = 0
            player = self.PLAYERS[self.turn] 
            return {"dice_values": (self.dice_value, self.dice_value2), 
                "eligible_pieces": eligible_pieces, "userAfter": self.userAfter,
                "userAfterName": self.userAfterName, 
                "player": player, "state": self.state, 
                "user_name": global_player_names[player],
                "first_turn_response": self.first_turn_response}

        self.state = STATE["DICE_ROLLED"]

        eligible_pieces = self.check_for_eligible_pieces()
   
        if self.dice_value == self.dice_value2 :
            player = color_piece #Change the player to the one who rolled the dice
            self.player_for_elegible_pieces = color_piece

            print("jugador fichas iguales", player)
            # self.userAfter = player
            # self.userAfterName = global_player_names[player]
        elif self.dice_value != self.dice_value2 and self.first_exit[color_piece] == True and self.isJailOut == False:
            player = self.PLAYERS[(self.turn + 1) % len(self.PLAYERS)]
            print("jugador fichas distintas isJailOut false pero salio de la carcel " , player)
            
        else:
            player = self.PLAYERS[self.turn]#The player is the one who is in the next turn
            print("entra al else de default", player)
            # self.userAfter =  self.PLAYERS[(self.turn + 1) % len(self.PLAYERS)]
            # self.userAfterName = global_player_names[self.userAfter]

        if self.dice_value != self.dice_value2 and self.isJailOut[player] == True: #The player get out of jail and the dice are not the same
            # self.isJailOut[player] = False
            self.first_turn_response = False

            # player = self.PLAYERS[(self.turn + 1) % len(self.PLAYERS)]
            if (self.first_exit[color_piece] == True):#The player has already exited from jail a long time ago
                eligible_pieces = self.get_eligible_pieces(player)
            else:
                eligible_pieces = []
            
            self.player_for_elegible_pieces = color_piece

            player = self.PLAYERS[self.turn]
            print("jugador fichas distintas isJailOut" , player)
            self.userAfter =  self.PLAYERS[(self.turn + 1) % len(self.PLAYERS)]
            self.userAfterName = global_player_names[self.userAfter]
        
            
        print("jugador fichas  que se envia" , player)

       
        return {"dice_values": (self.dice_value, self.dice_value2), 
                "eligible_pieces": eligible_pieces,
                "playerElegiblePieces": self.player_for_elegible_pieces,
                "userAfter": self.userAfter,
                "userAfterName": self.userAfterName, 
                "player": player, "state": self.state, 
                "user_name": global_player_names[player],
                "first_turn_response": self.first_turn_response}
    
    #
    def check_for_eligible_pieces(self):
        player = self.PLAYERS[self.turn]
        eligible_pieces = self.get_eligible_pieces(player)
        if not eligible_pieces:
            self.increment_turn()
        return eligible_pieces

    def increment_turn(self):
        self.turn = (self.turn + 1) % len(self.PLAYERS)
        self.state = STATE["DICE_NOT_ROLLED"]

    def get_eligible_pieces(self, player):
        eligible_pieces = []
        for piece in range(4):
            current_position = self.current_positions[player][piece]
            if current_position == HOME_POSITIONS[player]:
                continue
            if current_position in BASE_POSITIONS[player] and self.dice_value != self.dice_value2:
                continue
            if current_position in HOME_ENTRANCE[player] and self.dice_value > HOME_POSITIONS[player] - current_position:
                continue
            eligible_pieces.append(piece)
        return eligible_pieces

    def handle_piece_click(self, player, piece):
        # if player != self.PLAYERS[self.turn]:
        #     return
        piece = int(piece)
        print("la pieza elegida es ", player, piece)
        # player = self.PLAYERS[self.turn]
        current_position = self.current_positions[player][piece]
        self.unhighlighted_pieces =  True

        if current_position in BASE_POSITIONS[player] and self.first_exit[player]:
            self.set_piece_position(player, piece, START_POSITIONS[player])
            print("primer exit", self.first_exit[player])
            
            self.state = STATE["DICE_NOT_ROLLED"]
            return {"player": player, "piece": piece,
                     "current_positions": self.current_positions,
                     "state": self.state, "isunhiglighted_pieces": self.unhighlighted_pieces
                    }

        if current_position in BASE_POSITIONS[player]:
            # Move all pieces to the start position
            for piece in range(4):
                self.set_piece_position(player, piece, START_POSITIONS[player])
                print("primer exit", self.first_exit[player])

            self.state = STATE["DICE_NOT_ROLLED"]
            return {"player": player, "piece": piece,
                     "current_positions": self.current_positions,
                     "state": self.state, "isunhiglighted_pieces": self.unhighlighted_pieces
                    }

        # UI.unhighlight_pieces()
        self.unhighlighted_pieces =  True
        self.move_piece(player, piece, self.dice_value + self.dice_value2)
        first_exit = False
        # If the player has an extra turn, allow them to roll the dice again
        if self.extra_turn:
            self.state = STATE["DICE_NOT_ROLLED"]
            self.extra_turn = False
        return {"player": player, "piece": piece, 
                "current_positions": self.current_positions,"state": self.state,
                "isunhiglighted_pieces": self.unhighlighted_pieces, "userAfter": self.userAfter,
                "userAfterName": self.userAfterName
               }

    def set_piece_position(self, player, piece, new_position):
        current_position = self.current_positions[player][piece]
        if new_position == START_POSITIONS[player] and current_position in BASE_POSITIONS[player]:
            self.isJailOut[player] = True #The player is going out of jail

        self.current_positions[player][piece] = new_position
        # UI.set_piece_position(player, piece, new_position)

        if new_position == START_POSITIONS[player]:
            self.first_exit[player] = True
            print("primer exit", self.first_exit[player])
     

    def remove_piece_from_game(self, player, piece):
        self.set_piece_position(player, piece, OUT_OF_GAME)

    def reset_game(self):
        self.current_positions = {player: BASE_POSITIONS[player].copy() for player in self.PLAYERS}
        for player in self.PLAYERS:
            for piece in range(4):
                self.set_piece_position(player, piece, self.current_positions[player][piece])
        self.turn = 0
        self.state = STATE["DICE_NOT_ROLLED"]

    # def set_piece_position(self, player, piece, new_position):
    #     self.current_positions[player][piece] = new_position

    def move_piece(self, player, piece, move_by):
        interval = move_by
        while interval > 0:
            self.increment_piece_position(player, piece)
            interval -= 1

        if self.has_player_won(player):
            print(f"Player {player} has won!")
            self.reset_game()
            return

        is_kill = self.check_for_kill(player, piece)
        if is_kill or self.dice_value == 6:
            self.state = STATE["DICE_NOT_ROLLED"]
        else:
            self.increment_turn()

    def check_for_kill(self, player, piece):
        current_position = self.current_positions[player][piece]
        kill = False
        for opponent in self.PLAYERS:
            if opponent != player:
                for opponent_piece in range(4):
                    opponent_position = self.current_positions[opponent][opponent_piece]
                    if current_position == opponent_position and current_position not in SAFE_POSITIONS:
                        self.set_piece_position(opponent, opponent_piece, BASE_POSITIONS[opponent][opponent_piece])
                        kill = True
        return kill

    def has_player_won(self, player):
        return all(position == HOME_POSITIONS[player] for position in self.current_positions[player])

    def increment_piece_position(self, player, piece):
        self.set_piece_position(player, piece, self.get_incremented_position(player, piece))

    def get_incremented_position(self, player, piece):
        current_position = self.current_positions[player][piece]
        if current_position == TURNING_POINTS[player]:
            return HOME_ENTRANCE[player][0]
        elif current_position == 51:
            return 0
        return current_position + 1

# Example usage
if __name__ == "__main__":
    ludo = Ludo()
    
    # print("First turn:", ludo.turn)

    # eligible_pieces = ludo.on_dice_click(color_piece='blue')
    # print("Eligible pieces:", eligible_pieces)
