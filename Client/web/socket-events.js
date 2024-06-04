const socket = window.ludoSocket
import { UI } from './ludo/UI.js';
import { BASE_POSITIONS, HOME_ENTRANCE, HOME_POSITIONS, PLAYERS, SAFE_POSITIONS, START_POSITIONS, STATE, TURNING_POINTS } from './ludo/constants.js';

let usernameSet = '';
let local_player_id = '';
let diceTry = 0;
let color_piece_player;



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
    const isSelectedFirtsPlayer = true;
    const data = {
        isSelectedFirtsPlayer: isSelectedFirtsPlayer,
    }
    socket.emit('start_game', data);
});



//Función que permite conectarse al servidor de la aplicación
/*document.getElementById('connect').addEventListener('click', async () => {
    usernameSet = document.getElementById('name').value;
    color_piece_player = document.getElementById('color').value;
    const data = { 
        user_name: usernameSet,
        color_piece: color_piece_player,
        status: 'ready',
    }
    
    socket.emit('create_player', data);
});*/
// Función que permite conectarse al servidor de la aplicación
document.getElementById('connect').addEventListener('click', async () => {
    usernameSet = document.getElementById('user_name').value;
    color_piece_player = document.getElementById('color').value;
    document.getElementById('player-message').innerHTML = 'Jugador: ' + usernameSet + '<br/>Color: ' + color_piece_player;    
    if (usernameSet === '') {
        alert('Ingresa un nombre de usuario');
        return;
    }

    if (color_piece_player === '') {
        alert('Selecciona un color de ficha');  
        return;
    }
    if (usernameSet.length > 15) {
        alert('El nombre de usuario no puede tener más de 15 caracteres.');
        return;
    }

    if (!/^[a-z]+$/.test(usernameSet)) {
        alert('El nombre de usuario solo puede contener letras minúsculas.');
        return;
    }

    const data = { 
        user_name: usernameSet,
        color_piece: color_piece_player,
        status: 'ready',
        type: 'on_lobby'
    }
    
    socket.emit('create_player', data);
    change_btns_lobby('connect');
});

//Función que permite desconectarse del servidor del juego
document.getElementById('disconnect').addEventListener('click', async () => {
    if(usernameSet != '' && color_piece_player != ''){
        usernameSet = '';
        color_piece_player = '';
        document.getElementById('start').style.display = 'none';
        socket.emit('disconnect_player');
        change_btns_lobby('disconnect');
    }

});

/*==================================================================================
=            Funciones para sincronizar el reloj al iniciar una partida            =
====================================================================================*/
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
/*==================================================================================
=            Fin Funciones para sincronizar el reloj al iniciar una partida            =
====================================================================================*/


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
        usernameSet = ''; 
        color_piece_player = '';
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
// en progreso pero no puede ingresar a jugar hasta que la partida actual termine
socket.on('active_wating_room', error => {
    //alert("usernameSet: " + usernameSet + " color_piece_player: " + color_piece_player);
    if (usernameSet === '' && color_piece_player === undefined) {   
        activate_room();
    }
});


//Mostrar la lista de jugadores conectados
/*socket.on('users_list_update', players => {
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
            if (players[player].name === usernameSet) {
                local_player_id = players[player].player_id;
            }
        }
    }
});*/
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

            if (players[player].name === usernameSet){
                local_player_id = players[player].player_id;

                if(players[player].primero){                    
                    document.getElementById('start').style.display = 'block';
                }
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
    const countdownElement2 = document.getElementById('countdown2');
    countdownOverlay.style.display = 'flex';
    let time = 3;

    const countdownInterval = setInterval(() => {
        countdownElement.textContent = time;
        countdownElement2.textContent = 'Hora Sincronizada con servidor: ' + time_game;
        if (time === 0) {
            //updateGameTime(countdownElement);
            clearInterval(countdownInterval);
            countdownOverlay.style.display = 'none';
            // Ocultar container y mostrar el tablero con clase ludo-container
            document.getElementById('ludo-container').style.display = 'block';
            document.getElementById('container2').style.display = 'none';
            document.getElementById('container').style.display = 'none';
            document.getElementById('player-message').style.display = 'block';
            //document.getElementById('time').style.display = 'none';

            return;
        }
        time--;
    }, 1000);
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


/*==================================================================================
=            Funciones que hacen parte de la lógica para un juego en desarrollo            =
====================================================================================*/
document.getElementById('dice-btn').addEventListener('click', () => { 
    const data2 = { 
        color_piece: color_piece_player,
    }
    /*alert('color de la ficha: ' + color_piece_player);*/
    console.log(local_player_id, "tiró los dados");
    socket.emit('on_dice_click', data2);
});

/*document.getElementById('iniciar').addEventListener('click', () => {
    const isSelectedFirtsPlayer = true;
    const data = {
        isSelectedFirtsPlayer: isSelectedFirtsPlayer,
    }
    socket.emit('first_player', data);
});*/

socket.on('first_player', data => {
    const first_player = data.first_player;
    const user_name = data.user_name;
    console.log('first player', first_player);
    document.querySelector('.active-player span').innerText =`${user_name} lanza los dados.`;
    /*alert("local_player_id: " + local_player_id + " first_player: " + first_player);*/
    if(local_player_id != first_player) {
        UI.disableDice();
        highlightActivePlayerBase(first_player);
    } else {
        UI.enableDice();
        UI.unhighlightPieces();
        highlightActivePlayerBase(local_player_id);
    }
});

socket.on('dice_clicked', data => {
    const diceValues = data.dice_values;
    const eligible_pieces = data.eligible_pieces;
    const player = data.player;
    const state = data.state;
    const user_name = data.user_name;
    const first_turn_response = data.first_turn_response;
    const userAfterName = data.userAfterName;
    const userAfter = data.userAfter;
    const playerElegiblePieces = data.playerElegiblePieces;
   
    console.log('data es ', data);
    console.log('dice clicked jugador', player); 
    console.log('dice clicked dados', diceValues);
    if(first_turn_response === false){//por probar, puede que no funcione bien
        document.querySelector('.active-player span').innerText =
        `Es el turno de ${user_name}`;
    }
    if (eligible_pieces != undefined){
        console.log('dice clicked piezas elegibles', eligible_pieces);
       
        if(playerElegiblePieces === local_player_id){
            UI.highlightPieces(local_player_id, eligible_pieces);
            document.querySelector('.active-player span').innerText =
            `${usernameSet} puedes mover tus fichas.`;
        }
        else if (eligible_pieces.length > 0) {
            UI.highlightPieces(player, eligible_pieces);
            document.querySelector('.active-player span').innerText =
            `${user_name} puedes mover tus fichas.`;
        }
        if (playerElegiblePieces != local_player_id){
            UI.unhighlightPieces();
            document.querySelector('.active-player span').innerText =
            `Es el turno de ${user_name}`;
        }
    }
    if (first_turn_response === true) {
        document.querySelector('.active-player span').innerText =
        `El primer turno es para ${user_name}.\n
        Tienes 3 intentos para sacar tus fichas de la cárcel.`;
        if (eligible_pieces.length > 0) {
            UI.highlightPieces(player, eligible_pieces);
            document.querySelector('.active-player span').innerText =
            `${user_name} puedes mover tus fichas.`;
        }
    }
    // else{
    //     document.querySelector('.active-player span').innerText =
    //     `Es el turno de ${user_name}`;
    // }
  
    console.log('el user_name actual es ', user_name);
    console.log('el usernameSet actual es ', usernameSet);
    console.log('el local_player_id actual es ', local_player_id);
    console.log('el player actual es ', player);
  

    document.querySelector('.dice-value').textContent = diceValues[0];
    document.querySelector('.dice-value2').textContent = diceValues[1];
   
    highlightActivePlayerBase(player);

    // if (eligible_pieces.length > 0) {
    //     // UI.highlightPieces(player, eligible_pieces);
    // }
    // else{
    //     UI.unhighlightPieces();
    // }
    // if (userAfter === local_player_id) {
    //     UI.enableDice();
    //     document.querySelector('.active-player span').innerText =
    //     `Es el turno de ${userAfterName}`;
    //     return;
    // }

    // if (userAfter != undefined && userAfter != local_player_id){
    //     UI.disableDice();
    //     return;
    // }
    if(user_name === usernameSet)
    {
        UI.enableDice();
    }
    else{
        UI.disableDice();
    }
    
    if (local_player_id != player )//Si el jugador que lanza los dados no es el jugador local
    {
        UI.disableDice();
        return;
    }

    if(state === STATE.DICE_NOT_ROLLED ) {
        UI.enableDice();
    } else {
        UI.disableDice();
    }
    // UI.listenResetClick(this.resetGame.bind(this))
});

listenPieceClick();

function listenPieceClick() {
    UI.listenPieceClick(onPieceClick);
}

function onPieceClick(event) {
    const target = event.target;

    if(!target.classList.contains('player-piece') || !target.classList.contains('highlight')) {
        return;
    }
    const player = target.getAttribute('player-id');
    if ( local_player_id != player) {//si el jugador que quiere mover la ficha no es el jugador local
        return;
    }
    console.log('piece clicked in highlightPieces')
    const piece = target.getAttribute('piece');
    const data = { player: player, piece: piece }
    socket.emit('piece_clicked', data);
}

socket.on('piece_clicked', data => {
    const player = data.player;
    const piece_player = data.piece;
    const isunhiglighted_pieces = data.isunhiglighted_pieces;
    const currentPositions = data.current_positions;
    const state = data.state;
    const userAfter = data.userAfter;
    const userAfterName = data.userAfterName;
    console.log(data);
  
    // Move all pieces to the start position
    ['P1', 'P2', 'P3', 'P4'].forEach(player => {
        if (currentPositions[player] !== undefined) { // Verifica que currentPositions[player] exista
            [0, 1, 2, 3].forEach(piece => {
                if (currentPositions[player][piece] !== undefined) {
                    UI.setPiecePosition(player, piece, currentPositions[player][piece]);
                }
            });
        }
    });

    if (isunhiglighted_pieces){
        UI.unhighlightPieces();
        if( userAfter != undefined && userAfter === local_player_id){
            document.querySelector('.active-player span').innerText =
            `Es el turno de ${userAfterName}`;
            UI.enableDice();
            UI.unhighlightPieces();
            highlightActivePlayerBase(userAfter);
            return;
        }
        if (userAfter != undefined && userAfter != local_player_id){
            document.querySelector('.active-player span').innerText =
            `Es el turno de ${userAfterName}`;
            UI.disableDice();
            highlightActivePlayerBase(userAfter);
            return;
        }

        if (local_player_id != player  )//Si el jugador que lanza los dados no es el jugador local
        {
            UI.disableDice();
            return;
        }
        if(state === STATE.DICE_NOT_ROLLED ) {
            UI.enableDice();
            UI.unhighlightPieces();
        } else {
            UI.disableDice();
        }
    }

});


//Highlight the active player base in the UI
function highlightActivePlayerBase(player) {
    const activePlayerBase = document.querySelector('.player-base.highlight');
    if(activePlayerBase) {
        activePlayerBase.classList.remove('highlight');
    }
    // highlight
    document.querySelector(`[player-id="${player}"].player-base`).classList.add('highlight')
}
/*==================================================================================
=            Fin Funciones que hacen parte de la lógica para un juego en desarrollo            =
====================================================================================*/
