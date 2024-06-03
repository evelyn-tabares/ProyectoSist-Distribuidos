const socket = window.ludoSocket
import { UI } from './ludo/UI.js';
import { BASE_POSITIONS, HOME_ENTRANCE, HOME_POSITIONS, PLAYERS, SAFE_POSITIONS, START_POSITIONS, STATE, TURNING_POINTS } from './ludo/constants.js';

let usernameSet;
let local_player_id;
let diceTry = 0;
let color_piece_player;
//Función que permite conectarse al servidor de la aplicación
document.getElementById('connect').addEventListener('click', async () => {
    usernameSet = document.getElementById('name').value;
    color_piece_player = document.getElementById('color').value;
    const data = { 
        user_name: usernameSet,
        color_piece: color_piece_player,
        status: 'ready',
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
            if (players[player].name === usernameSet) {
                local_player_id = players[player].player_id;
            }
        }
    }
});

// //actualizar la lista de jugadores cada segundo
// setInterval(async () => {
//     console.log('update players list');
//     socket.emit('update_players_list', {});
// }, 1000);



document.getElementById('dice-btn').addEventListener('click', () => { 
    const data2 = { 
        color_piece: color_piece_player,
    }
    console.log(local_player_id, "tiró los dados");
    socket.emit('on_dice_click', data2);
});

document.getElementById('iniciar').addEventListener('click', () => {
    const isSelectedFirtsPlayer = true;
    const data = {
        isSelectedFirtsPlayer: isSelectedFirtsPlayer,
    }
    socket.emit('first_player', data);
});

socket.on('first_player', data => {
    const first_player = data.first_player;
    const user_name = data.user_name;
    console.log('first player', first_player);
    document.querySelector('.active-player span').innerText =`${user_name} lanza los dados.`;
    if(local_player_id != first_player) {
        UI.disableDice();
    } else {
        UI.enableDice();
        UI.unhighlightPieces();
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
    }
    else{
        document.querySelector('.active-player span').innerText =
        `Es el turno de ${user_name}`;
    }
    console.log('el user_name actual es ', user_name);
    console.log('el usernameSet actual es ', usernameSet);
    console.log('el local_player_id actual es ', local_player_id);
    console.log('el player actual es ', player);
  

    document.querySelector('.dice-value').textContent = diceValues[0];
    document.querySelector('.dice-value2').textContent = diceValues[1];
   
    highlightActivePlayerBase(player);

    if (eligible_pieces.length > 0) {
        // UI.highlightPieces(player, eligible_pieces);
    }
    else{
        UI.unhighlightPieces();
    }
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
    [0, 1, 2, 3].forEach(piece => {
        UI.setPiecePosition(player, piece, currentPositions[player][piece])
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
