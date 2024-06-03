import { BASE_POSITIONS, HOME_ENTRANCE, HOME_POSITIONS, PLAYERS, SAFE_POSITIONS, START_POSITIONS, STATE, TURNING_POINTS } from './constants.js';
import { UI } from './UI.js';
import { OUT_OF_GAME } from './constants.js';

export class Ludo {
    currentPositions = {
        P1: [],
        P2: [],
        P3: [],
        P4: [],
    }

    firstExit = {
        P1: false,
        P2: false,
        P3: false,
        P4: false,
    }



    _diceValue;
    get diceValue() {
        return this._diceValue;
    }
    set diceValue(value) {
        this._diceValue = value;

        UI.setDiceValue(value);
    }

    _diceValue2;
    get diceValue2() {
        return this._diceValue2;
    }
    set diceValue2(value) {
        this._diceValue2 = value;

        UI.setDiceValue2(value); 
    }

    _pairCount = 0;
    get pairCount() {
        return this._pairCount;
    }
    set pairCount(value) {
        this._pairCount = value;
        if (value === 3) {
            this.removePieceFromGame(PLAYERS[this.turn], 0);
            this._pairCount = 0;  // Reset pair count
            // Permitir al jugador sacar una ficha del juego
        }
    }

    // _turn;
    // get turn() {
    //     return this._turn;
    // }
    // // set turn(value) {
    // //     this._turn = value;
    // //     UI.setTurn(value);
    // // }

    _state;
    get state() {
        return this._state;
    }
    set state(value) {
        this._state = value;

        // if(value === STATE.DICE_NOT_ROLLED) {
        //     UI.enableDice();
        //     UI.unhighlightPieces();
        // } else {
        //     UI.disableDice();
        // }
    }

    extraTurn = false;

    constructor() {
        console.log('Hello World! Lets play Ludo!');
        this.baseExitAttempts = 0;
        // this.determineFirstTurn();

        this.listenDiceClick();
        // this.listenResetClick();
        // this.listenPieceClick();

        this.resetGame();
        
        
    }

    removePieceFromGame(player, piece) {
        this.setPiecePosition(player, piece, OUT_OF_GAME);
    }

    // determineFirstTurn() {
    //     const firstTurnResults = {};
    //     for (let player of PLAYERS) {
    //         firstTurnResults[player] = 1 + Math.floor(Math.random() * 6);
    //     }
    //     const firstPlayer = Object.keys(firstTurnResults).reduce((a, b) => firstTurnResults[a] > firstTurnResults[b] ? a : b);
    //     this.turn = PLAYERS.indexOf(firstPlayer);
    // }
  
    listenDiceClick() {
        UI.listenDiceClick(this.onDiceClick.bind(this))
    }

    onDiceClick() {
        console.log('dice clicked!');
        document.querySelector('.active-player span').innerText = '';
        // this.diceValue = 1 + Math.floor(Math.random() * 6);
        // this.diceValue2 = 1 + Math.floor(Math.random() * 6); 
        // this.state = STATE.DICE_ROLLED;
        
        
        // this.checkForEligiblePieces();

        // if (this.diceValue === this.diceValue2) {
        //     this.pairCount++;
        //     this.baseExitAttempts++;
        //     this.extraTurn = true; 
        //     if (this.baseExitAttempts === 3) {
        //         this.baseExitAttempts = 0;
        //         this.incrementTurn();
        //     }
        // }
        // else {
        //     this.pairCount = 0;
        // }
    }

    checkForEligiblePieces() {
        const player = PLAYERS[this.turn];
        // eligible pieces of given player
        const eligiblePieces = this.getEligiblePieces(player);
        if(eligiblePieces.length) {
            // highlight the pieces
            UI.highlightPieces(player, eligiblePieces);
        } else {
            this.incrementTurn();
        }
    }

    incrementTurn() {
        this.turn = (this.turn + 1) % PLAYERS.length; 
        this.state = STATE.DICE_NOT_ROLLED;
    }

    getEligiblePieces(player) {
        const hasPieceOutsideHome = this.currentPositions[player].some(
            position => !BASE_POSITIONS[player].includes(position)
        );
        return [0, 1, 2, 3].filter(piece => {
            const currentPosition = this.currentPositions[player][piece];

            if(currentPosition === HOME_POSITIONS[player]) {
                return false;
            }

            // if(
            //     BASE_POSITIONS[player].includes(currentPosition)
            //     && this.diceValue !== 6
            // ){
            //     return false;
            // }
            
            if(
                BASE_POSITIONS[player].includes(currentPosition)
                && this.diceValue !== this.diceValue2
            ){
                return false;
                // return this.firstExit[player] || hasPieceOutsideHome;
            }

            if(
                HOME_ENTRANCE[player].includes(currentPosition)
                && this.diceValue > HOME_POSITIONS[player] - currentPosition
                ) {
                return false;
            }

            return true;
        });
    }

    listenResetClick() {
        UI.listenResetClick(this.resetGame.bind(this))
    }

    resetGame() {
        console.log('reset game');
        this.currentPositions = structuredClone(BASE_POSITIONS);

        PLAYERS.forEach(player => {
            [0, 1, 2, 3].forEach(piece => {
                this.setPiecePosition(player, piece, this.currentPositions[player][piece])
            })
        });

        this.turn = 0;
        this.state = STATE.DICE_NOT_ROLLED;
    }

    listenPieceClick() {
        UI.listenPieceClick(this.onPieceClick.bind(this));
    }

    onPieceClick(event) {
        const target = event.target;

        if(!target.classList.contains('player-piece') || !target.classList.contains('highlight')) {
            return;
        }
        console.log('piece clicked')

        const player = target.getAttribute('player-id');
        const piece = target.getAttribute('piece');
        // this.handlePieceClick(player, piece);

        // if (player !== PLAYERS[this.turn]) {
        //     return;
        // }
        socket.emit('piece_clicked', { player: player, piece: piece });

    }

    handlePieceClick(player, piece) {
        console.log(player, piece);
        const currentPosition = this.currentPositions[player][piece];

        if(BASE_POSITIONS[player].includes(currentPosition) && this.firstExit[player] == true) {
            this.setPiecePosition(player, piece, START_POSITIONS[player]);
            this.state = STATE.DICE_NOT_ROLLED;
            return;
        }
        
        if(BASE_POSITIONS[player].includes(currentPosition)) {
            // Move all pieces to the start position
            [0, 1, 2, 3].forEach(piece => {
                this.setPiecePosition(player, piece, START_POSITIONS[player]);
            });
            this.state = STATE.DICE_NOT_ROLLED;
            return;
        }


        UI.unhighlightPieces();
        this.movePiece(player, piece, this.diceValue + this.diceValue2);
          // Si el jugador tiene un turno extra, permitirle tirar los dados de nuevo
        if (this.extraTurn) {
            this.state = STATE.DICE_NOT_ROLLED;
            this.extraTurn = false;
        }
    }

    setPiecePosition(player, piece, newPosition) {
        this.currentPositions[player][piece] = newPosition;
        UI.setPiecePosition(player, piece, newPosition)

        if (newPosition === START_POSITIONS[player]) {
            this.firstExit[player] = true;
        }
    }

    movePiece(player, piece, moveBy) {
        // this.setPiecePosition(player, piece, this.currentPositions[player][piece] + moveBy)
        const interval = setInterval(() => {
            this.incrementPiecePosition(player, piece);
            moveBy--;

            if(moveBy === 0) {
                clearInterval(interval);

                // check if player won
                if(this.hasPlayerWon(player)) {
                    alert(`Player: ${player} has won!`);
                    this.resetGame();
                    return;
                }

                const isKill = this.checkForKill(player, piece);

                if(isKill || this.diceValue === 6) {
                    this.state = STATE.DICE_NOT_ROLLED;
                    return;
                }

                this.incrementTurn();
            }
        }, 200);
    }

    checkForKill(player, piece) {
        const currentPosition = this.currentPositions[player][piece];
        let kill = false;

        PLAYERS.forEach(opponent => {
            if(opponent !== player) {
                [0, 1, 2, 3].forEach(piece => {
                    const opponentPosition = this.currentPositions[opponent][piece];

                    if(currentPosition === opponentPosition && !SAFE_POSITIONS.includes(currentPosition)) {
                        this.setPiecePosition(opponent, piece, BASE_POSITIONS[opponent][piece]);
                        kill = true
                    }
                });
            }
        });

        return kill
    }

    hasPlayerWon(player) {
        return [0, 1, 2, 3].every(piece => this.currentPositions[player][piece] === HOME_POSITIONS[player])
    }

    incrementPiecePosition(player, piece) {
        this.setPiecePosition(player, piece, this.getIncrementedPosition(player, piece));
    }
    
    getIncrementedPosition(player, piece) {
        const currentPosition = this.currentPositions[player][piece];

        if(currentPosition === TURNING_POINTS[player]) {
            return HOME_ENTRANCE[player][0];
        }
        else if(currentPosition === 51) {
            return 0;
        }
        return currentPosition + 1;
    }
}