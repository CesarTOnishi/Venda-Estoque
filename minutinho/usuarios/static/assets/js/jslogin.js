document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("logar");
    const inputs = document.querySelectorAll(".caixa_input input");

    form.addEventListener("submit", function(event) {
        let valid = true;

        inputs.forEach(input => {
            if (input.value.trim() === "") {
                valid = false;
                input.style.borderColor = "#ac4147"; 
                input.style.backgroundColor = "#555"; 
            } else {
                input.style.borderColor = "#993d3b"; 
                input.style.backgroundColor = "#444";
            }
        });

        if (!valid) {
            event.preventDefault();
            alert("Por favor, preencha todos os campos.");
        }
    });

    inputs.forEach(input => {
        input.addEventListener("focus", function() {
            input.style.borderColor = "#993d3b";
            input.style.backgroundColor = "#444";
        });

        input.addEventListener("blur", function() {
            if (input.value.trim() === "") {
                input.style.borderColor = "#ac4147"; 
                input.style.backgroundColor = "#555"; 
            } else {
                input.style.borderColor = "#993d3b";
                input.style.backgroundColor = "#444";
            }
        });
    });
});
