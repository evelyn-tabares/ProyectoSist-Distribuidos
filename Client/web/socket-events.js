const socket = window.ludoSocket
let username = '';
let color_piece = '';
let game_ready = false;
let time_game = 0;

// Al cargar la página, se debe verificar si el juego ya empezó
document.addEventListener('DOMContentLoaded', async () => {
    activate_room();       
});

 
// Función que permite iniciar el juego
document.getElementById('start').addEventListener('click', async () => {
    socket.emit('start_game');
});


// Función que permite conectarse al servidor de la aplicación
document.getElementById('connect').addEventListener('click', async () => {
    username = document.getElementById('user_name').value;
    color_piece = document.getElementById('color').value;
    
    if (username === '') {
        alert('Ingresa un nombre de usuario');
        return;
    }

    if (color_piece === '') {
        alert('Selecciona un color de ficha');  
        return;
    }
    
    const data = { 
        user_name: username,
        color_piece: color_piece,
        status: 'ready',
        type: 'on_lobby'
    }
    
    socket.emit('create_player', data);
    change_btns_lobby('connect');
});


//Función que permite desconectarse del servidor del juego
document.getElementById('disconnect').addEventListener('click', async () => {
    username = '';
    color_piece = '';
    document.getElementById('start').style.display = 'none';
    socket.emit('disconnect_player');
    change_btns_lobby('disconnect');
});
















// Permite enviar la hora actual del cliente al servidor, para que pueda calcular
// el ajuste que debe realizar en el tiempo del cliente
socket.on('request_time', data => {
    const serverTime = data.server_time;
    const clientTime = Date.now() / 1000; // Convertir a segundos
    socket.emit('provide_time_offset', {
        server_time: serverTime,
        client_time: clientTime
    });
});

// Recibe el ajuste que debe realizar el cliente en su tiempo
socket.on('adjust_time', data => {
    const offset = data.offset;
    adjustClientTime(offset);
});

// Ajusta el tiempo del cliente. El ajuste que envía el servidor esta en UTC 00:00
// por lo que se debe ajustar a la zona horaria del cliente.
function adjustClientTime(offset) {
    // Obtener la hora actual del cliente en segundos
    const adjusted_time = (Date.now() / 1000) + offset;
    const adjusted_date = new Date(adjusted_time * 1000);

    // Obtener el desplazamiento de la zona horaria del usuario en minutos
    // Ajusta la hora usando el desplazamiento de la zona horaria del usuario
    const timezone_offset_in_minutes = adjusted_date.getTimezoneOffset();
    const local_adjusted_date = new Date(adjusted_date.getTime() - (timezone_offset_in_minutes * 60 * 1000));

    // Formatear la hora en formato HH:MM:SS
    const hours = local_adjusted_date.getUTCHours().toString().padStart(2, '0');
    const minutes = local_adjusted_date.getUTCMinutes().toString().padStart(2, '0');
    const seconds = local_adjusted_date.getUTCSeconds().toString().padStart(2, '0');
    
    const formatted_time = `${hours}:${minutes}:${seconds}`;
    time_game = formatted_time;
    //console.log(`Adjusted Time: ${formatted_time}`);
}

//Solicitar la sincronización de los relojes de los clientes que se conectan al juego
socket.on('synchronize_clocks', () => {
    socket.emit('synchronize_clocks');
});




























// Conectarse a un juego que está en curso
/*document.getElementById('connect2').addEventListener('click', async () => {
    const username = document.getElementById('user_name2').value;
    const color_piece = document.getElementById('color2').value;

    if (username === '') {
        alert('Ingresa un nombre de usuario');
        return;
    }

    if (color_piece === '') {
        alert('Selecciona un color');
        return;
    }

    const data = {
        user_name: username,
        color_piece: color_piece,
        status: 'ready',
        type: 'on_game'
    }

    socket.emit('create_player', data);
});*/

// Mostrar la información de espacios disponibles en la sala de espera cuando
// la partida ya está en curso
socket.on('start_game_run', num_players => {
    const num_info = document.getElementById('spaces');
    const listItem = document.createElement('h1');
    num_info.innerHTML = '';
    
    if (game_ready === false) {
        if (num_players === 4) {
            //alert('La sala se llenó. Solo puedes observar el juego en curso');

            document.getElementById('connect2').disabled = true;
            listItem.textContent = `El juego esta completo, pero puede ingresar como espectador`;
            const colorsList = document.getElementById('color2');
            colorsList.innerHTML = '';
        }else{
            listItem.textContent = `Espacios disponibles: ${4 - num_players}`;
        }

        num_info.appendChild(listItem);
    }
});

// Evaluar los errores que pueden ocurrir al crear un jugador
socket.on('error_crte_player', result => {
    if (result['success'] === false) {
        alert(result['message']);
        username = '';
        color_piece = '';
        change_btns_lobby('disconnect');
    }
});

// Gestionar los errores que pueden ocurrir al iniciar el juego
socket.on('error_start_game', error => {
    if (error['success'] === false) {
        alert(error['message']);
    }
});

// Cerrar el lobby cuando una persona no ingresa nombre de usuario  y color y
// selecciona el botón de conectar. En este caso se carga la pantalla de juego
// en progreso y puede ingresar siempre y cuando haya espacio disponible
socket.on('active_wating_room', error => {
    if (username === '' && color_piece === '') {
        activate_room();
    }
});


//Mostrar la lista de jugadores conectados
socket.on('users_list_update', players => {
    const playersList = document.getElementById('player-list');
    playersList.innerHTML = '';

    if (Object.keys(players).length === 0) {
        const listItem = document.createElement('li');
        listItem.textContent = 'No hay jugadores conectados';
        playersList.appendChild(listItem);
    }else{
        for (let player in players) {
            const listItem = document.createElement('li');
            listItem.textContent = `name: ${players[player].name}, color_piece: ${players[player].color_piece}, Status: ${players[player].status}`;
            playersList.appendChild(listItem);

            if (players[player].primero && players[player].name === username) {
                document.getElementById('start').style.display = 'block';
            }
        }
    }
});

// Empezar un juego desde la pantalla de partida en progreso
socket.on('user_in_game', result => {
    if (result) {
        game_ready = true;
        startCountdown();
    }
});

// Empezar el juego desde el lobby
socket.on('start_game', game_status => {
    if (game_status) {
        change_btns_lobby('connect');
        document.getElementById('disconnect').disabled = true;
        game_ready = true;
        startCountdown();
    }
});

// Función para un conteo regresivo cada vez que se inicia el juego
function startCountdown() {
    const countdownOverlay = document.getElementById('countdown-overlay');
    const countdownElement = document.getElementById('countdown');
    countdownOverlay.style.display = 'flex';
    let time = 5;

    const countdownInterval = setInterval(() => {
        countdownElement.textContent = time;
        if (time === 0) {
            clearInterval(countdownInterval);
            countdownOverlay.style.display = 'none';
            // Ocultar container y mostrar el tablero con clase ludo-container
            document.getElementById('ludo-container').style.display = 'block';
            document.getElementById('container2').style.display = 'none';
            document.getElementById('container').style.display = 'none';
            document.getElementById('time').style.display = 'none';
            updateGameTime();

            return;
        }
        time--;
    }, 1000);
}

function updateGameTime() {
    const countdownElement = document.getElementById('time');
    countdownElement.style.display = 'block';
    const listItem = document.createElement('h1');
    listItem.textContent = `Tiempo de juego: ${time_game}`;
    countdownElement.innerHTML = '';
    countdownElement.appendChild(listItem);
}

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

// Función que activa el lobby o la sala de espera. Cuando el lobby se carga, se 
// verifica si el juego ya está en curso y se muestra la pantalla de juego en progreso
// o se muestra el lobby para que los jugadores se conecten
function activate_room() {
    socket.emit('check_game_status');

    socket.on('game_started', game_status => {
        //game_ready = game_status;
        if (game_status['run'] === true) {
            document.getElementById('container').style.display = 'none';
            document.getElementById('container2').style.display = 'block';
            //document.getElementById('connect2').disabled = true;

            const num_info = document.getElementById('spaces');
            const listItem = document.createElement('h1');
            num_info.innerHTML = '';
            listItem.textContent = `El juego esta completo. Intente más tarde`;
            num_info.appendChild(listItem);
            /*if (game_status['all_players'] === false) {
                
                //ocultar container y mostrar container2
                document.getElementById('container').style.display = 'none';
                document.getElementById('container2').style.display = 'block';

                //consultar colores de las fichas disponibles
                socket.emit('get_available_colors');
                socket.on('available_colors', colors => {
                    const colorsList = document.getElementById('color2');
                    let text_color = '';
                    colorsList.innerHTML = '';

                    for (let color in colors) {
                        const listItem = document.createElement('option');
                        listItem.value = colors[color];
                        
                        if (colors[color] === 'red') {
                            text_color = 'Rojo';
                        } else if (colors[color] === 'blue') {
                            text_color = 'Azul';
                        } else if (colors[color] === 'green') {
                            text_color = 'Verde';
                        } else if (colors[color] === 'yellow') {
                            text_color = 'Amarillo';
                        }

                        listItem.textContent = text_color
                        colorsList.appendChild(listItem);
                    }
                });*/
            /*}else{
                document.getElementById('container').style.display = 'none';
                document.getElementById('container2').style.display = 'block';
                document.getElementById('connect2').disabled = true;

                const num_info = document.getElementById('spaces');
                const listItem = document.createElement('h1');
                num_info.innerHTML = '';
                listItem.textContent = `El juego esta completo, pero puede ingresar como espectador`;
                num_info.appendChild(listItem);
            }*/
        }else{
            //mostrar container y ocultar container2
            document.getElementById('container').style.display = 'block';
        }
    });
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