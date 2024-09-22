document.addEventListener('DOMContentLoaded', function() {
    const removeButtons = document.querySelectorAll('.table_nome img');

    removeButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            if (confirm('Tem certeza de que deseja remover este item?')) {
                window.location.href = button.parentElement.href;
            }
        });

        button.addEventListener('mousedown', function() {
            button.style.transform = 'scale(0.9)';
        });

        button.addEventListener('mouseup', function() {
            button.style.transform = 'scale(1)';
        });
    });

    const submitButton = document.querySelector('.realizar');
    submitButton.addEventListener('click', function() {
        submitButton.disabled = true;
        submitButton.innerText = 'Enviando...';
    });
});
