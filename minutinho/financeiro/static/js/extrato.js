document.addEventListener('DOMContentLoaded', function() {
    // Captura todos os botões de navegação
    const buttons = document.querySelectorAll('.nav-button');

    // Adiciona evento de clique em cada botão
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const sectionToShow = this.getAttribute('data-section');

            // Oculta todas as seções
            document.querySelectorAll('.section').forEach(section => {
                section.classList.remove('active');
                section.style.display = 'none'; // Garante que elas fiquem ocultas
            });

            // Mostra a seção correspondente ao botão clicado
            const activeSection = document.getElementById(sectionToShow);
            if (activeSection) {
                activeSection.classList.add('active');
                activeSection.style.display = 'block'; // Torna visível
            }
        });
    });

    // Garante que apenas a seção ativa seja visível ao carregar a página
    document.querySelectorAll('.section').forEach(section => {
        if (!section.classList.contains('active')) {
            section.style.display = 'none';
        }
    });
});
