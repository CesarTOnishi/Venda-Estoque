document.addEventListener('DOMContentLoaded', function() {
    const addButtons = document.querySelectorAll('.btn-adicionar');

    addButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const produtoNome = this.closest('.menu').querySelector('.nome-produto').textContent;
            window.location.href = this.href; 
        });
    });
});

