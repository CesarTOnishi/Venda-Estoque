document.addEventListener('DOMContentLoaded', function () {
    const openModalButton = document.getElementById('open_modal_button');
    const modalContainer = document.getElementById('modal_container');
    const closeModalButton = document.getElementById('close_modal_button');

    openModalButton.addEventListener('click', () => {
        modalContainer.classList.add('show');  // classe que mostra o modal
    });

    closeModalButton.addEventListener('click', () => {
        modalContainer.classList.remove('show');
    });
});

