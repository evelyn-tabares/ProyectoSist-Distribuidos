const socket = window.ludoSocket

//Función que permite conectarse al servidor de la aplicación
document.getElementById('connect').addEventListener('click', async () => {
    const username = document.getElementById('name').value;
    const color_piece = document.getElementById('color').value;
    const data = { 
        user_name: username,
        color_piece: color_piece,
        status: 'ready'
    }
    
    socket.emit('create_player', data);
});

//Mostrar la lista de jugadores conectados
socket.on('users_list_update', players => {
    const playersList = document.getElementById('player-list');
    playersList.innerHTML = '';

    if (Object.keys(players).length === 0) {
        const listItem = document.createElement('li');
        listItem.textContent = 'No players connected';
        playersList.appendChild(listItem);
    }else{

        for (let player in players) {
            const listItem = document.createElement('li');
            listItem.textContent = `name: ${players[player].name}, color_piece: ${players[player].color_piece}, Status: ${players[player].status}`;
            playersList.appendChild(listItem);
        }
    }
});

//actualizar la lista de jugadores cada segundo
setInterval(async () => {
    console.log('update players list');
    socket.emit('update_players_list', {});
}, 1000);

//actualizar la lista de jugadores cada segundo



/*document.querySelector("#createRoomFormButton").addEventListener("click", submitForm)
function submitForm() {
    const formData = new FormData(document.getElementById("createRoomForm"));
    const data = {
        name: formData.get("name"),
        password: formData.get("password"),
        playersQuantity: formData.get("numPlayers"),
        room_data: {}
    }
    socket.emit('create_game_room', data)
}

function updateRoomsList(rooms) {
    const tableBody = document.getElementById('roomsTable').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';
    
    const insertRow = (name, password, num_of_players) => {
        const row = tableBody.insertRow();

        const cellName = row.insertCell();
        cellName.innerText = name;

        const cellPassword = row.insertCell();
        cellPassword.innerText = password;

        const cellPlayers = row.insertCell();
        cellPlayers.innerText = num_of_players;
    }

    insertRow("Room Name", "Password", "Number of Players")

    for (const roomId in rooms) {
        if (rooms.hasOwnProperty(roomId)) {
            const room = rooms[roomId];
            insertRow(room.name, room.password, room.num_of_players)
        }
    }
}

socket.on('rooms_list_update', rooms => {
    console.log("rooms list update", rooms);
    updateRoomsList(rooms);
});*/