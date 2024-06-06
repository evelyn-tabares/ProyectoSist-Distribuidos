// script.js

/*function addName() {
    const nameInput = document.getElementById('nombre');
    const nameList = document.getElementById('name-list');
    const colorSelect = document.getElementById("color");
    const selectedOption = colorSelect.options[colorSelect.selectedIndex];
    
    if (nameInput.value.trim() !== "") {
        const listItem = document.createElement('li');
        listItem.textContent = nameInput.value;
        nameList.appendChild(listItem);
        nameInput.value = "";
        colorSelect.removeChild(selectedOption);  
    } else {
        alert("Por favor ingrese un nombre.");
    }
}

function removeLastName() {
    const nameList = document.getElementById('name-list');
    
    if (nameList.lastChild) {
        nameList.removeChild(nameList.lastChild);
    } else {
        alert("No hay nombres en la lista para desconectar.");
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const colorSelect = document.getElementById("color");

    colorSelect.addEventListener("change", function() {
        const selectedOption = colorSelect.options[colorSelect.selectedIndex];
        colorSelect.removeChild(selectedOption);
    });
});*/

function redirectToInstructions() {
    window.location.href = "instrucciones.html";
}

function redirectToCredits() {
    window.location.href = "creditos.html";
}


function Back_menu() {
    window.location.href = "index.html";
}