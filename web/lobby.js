//Función que permite conectarse al servidor de la aplicación
document.getElementById('connect').addEventListener('click', async () => {
    alert('Connecting...');
    const username = document.getElementById('name').value;
    const color_piece = document.getElementById('color').value;
    const response = await eel.new_user(username, color_piece)();
    
    if(response) {
        alert('Connected');
    } else {
        alert('Unable to connect!');
    }
});

//Función que permite actualizar la lista de jugadores en el lobby
setInterval(async () => {
    const players = await eel.update_users()();
}, 1000);   