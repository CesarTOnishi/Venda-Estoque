// === CONTROLE DOS FILTROS AVANÇADOS ===
document.addEventListener('DOMContentLoaded', function() {
    const filtrosForm = document.getElementById('form-filtros');
    const toggleFiltros = document.getElementById('toggle-filtros');
    const dataInicio = document.getElementById('data_inicio');
    const dataFim = document.getElementById('data_fim');
    const vencimentoInicio = document.getElementById('vencimento_inicio');
    const vencimentoFim = document.getElementById('vencimento_fim');

    // Esconde os filtros ao carregar
    if (filtrosForm) {
        filtrosForm.style.display = 'none';
    }

    // Botão para abrir/fechar filtros
    if (toggleFiltros) {
        toggleFiltros.addEventListener('click', function() {
            if (filtrosForm.style.display === 'none' || filtrosForm.style.display === '') {
                filtrosForm.style.display = 'grid';
            } else {
                filtrosForm.style.display = 'none';
            }

            // Alterna o ícone (opcional, se usar Font Awesome)
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-chevron-down');
                icon.classList.toggle('fa-chevron-up');
            }
        });
    }

    // Lógica de validação das datas (período e vencimento)
    if (dataInicio && dataFim) {
        dataInicio.addEventListener('change', function() {
            dataFim.min = this.value;
        });

        dataFim.addEventListener('change', function() {
            dataInicio.max = this.value;
        });
    }

    if (vencimentoInicio && vencimentoFim) {
        vencimentoInicio.addEventListener('change', function() {
            vencimentoFim.min = this.value;
        });

        vencimentoFim.addEventListener('change', function() {
            vencimentoInicio.max = this.value;
        });
    }

    // Máscara monetária (se o jQuery estiver disponível)
    if (typeof $ !== 'undefined' && $('.valor-range input').length) {
        $('.valor-range input').mask('#.##0,00', { reverse: true });
    }
});
