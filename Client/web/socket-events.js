const socket = window.ludoSocket
let game_ready = false;


// Al cargar la página, se debe verificar si el juego ya empezó

document.addEventListener('DOMContentLoaded', async () => {
    socket.emit('check_game_status');
    
    socket.on('game_started', game_status => {
        game_ready = game_status;

        if (game_ready) {
            alert('El juego ya ha empezado');
        }
    });        
});


//Función que permite conectarse al servidor de la aplicación
document.getElementById('connect').addEventListener('click', async () => {
    const username = document.getElementById('user_name').value;
    const color_piece = document.getElementById('color').value;
    
    if (username === '') {
        alert('Please enter a username');
        return;
    }

    if (color_piece === '') {
        alert('Please enter a color');  
        return;
    }
    
    const data = { 
        user_name: username,
        color_piece: color_piece,
        status: 'ready'
    }
    
    socket.emit('create_player', data);
    //cambiar mensaje del botón connect de Conectar a Conectado e inhabilitar el botón
    change_btns_lobby('connect');
});


//Función que permite desconectarse del servidor del juego
document.getElementById('disconnect').addEventListener('click', async () => {
    const user_name = document.getElementById('user_name').value;
    socket.emit('disconnect_player');
    //socket.emit('disconnect_player', user_name);
    //cambiar mensaje del botón connect de Conectado a Conectar e habilitar el botón
    change_btns_lobby('disconnect');
});

// Evaluar los errores que pueden ocurrir al crear un jugador
socket.on('error_crte_player', result => {
    if (result['success'] === false) {
        alert(result['message']);
        change_btns_lobby('disconnect');
    }
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

// Empezar el juego de manera automatica cuando por lo menos hay 2 jugadores conectados
socket.on('start_game', game_status => {
    if (game_status) {
        change_btns_lobby('connect');
        document.getElementById('disconnect').disabled = true;
        game_ready = true;
        const countdownElement = document.getElementById('countdown');
        let time = 5;

        setInterval(() => {
            countdownElement.textContent = time;
            if (time === 0) {
                //Ocultar container y mostrar el tablero con clase ludo-container
                document.getElementById('container').style.display = 'none';
                document.getElementById('ludo-container').style.display = 'block';
                countdownElement.textContent = "¡Tiempo!";
                return;               
            }
            time--;
        }, 1000);
    }
});

// Función para cambiar el boton de conectar y desconectar dependiendo de la acción que se realice o los
// errores que puedan ocurrir
function change_btns_lobby(action){
    if (action === 'connect') {
        document.getElementById('connect').textContent = 'Conectado';
        document.getElementById('connect').disabled = true;
        document.getElementById('user_name').disabled = true;
        document.getElementById('color').disabled = true;
    } else if (action === 'disconnect') {
        document.getElementById('connect').textContent = 'Conectar';
        document.getElementById('connect').disabled = false;
        document.getElementById('user_name').disabled = false;
        document.getElementById('color').disabled = false;
    }
}



//actualizar la lista de jugadores cada segundo


/*setInterval(async () => {
    if (game_ready) {
        return;
    }

    console.log('update players list');
    socket.emit('update_players_list', {});
}, 1000);*/

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