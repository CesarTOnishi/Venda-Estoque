document.addEventListener('DOMContentLoaded', function() {
    function filterTable() {
        const query = document.getElementById('search').value.toLowerCase();
        const tipoSelecionado = document.querySelector('input[name="tipo_pessoa"]:checked')?.value || 'Pessoa Física';
        const rows = document.querySelectorAll('.tabela_fornecedor tbody tr');

        rows.forEach(row => {
            const tipoPessoa = row.getAttribute('data-tipo-pessoa');
            let match = false;

            // Verifica se a linha corresponde ao tipo selecionado
            const tipoMatch = tipoSelecionado === 'Todos' || tipoSelecionado === tipoPessoa;

            if (tipoMatch) {
                // Verifica se a célula de CPF ou CNPJ correspondente está visível
                const visibleCell = tipoSelecionado === 'Pessoa Física'
                    ? row.querySelector('td:not(.hidden)[data-field="cpf"]')
                    : row.querySelector('td:not(.hidden)[data-field="cnpj"]');

                if (visibleCell) {
                    match = visibleCell.textContent.toLowerCase().includes(query);
                }
            }

            // Exibe ou oculta a linha com base na pesquisa e no tipo de pessoa
            row.style.display = (tipoMatch && match) ? '' : 'none';
        });
    }

    document.getElementById('search').addEventListener('input', filterTable);

    function addTableAnimations() {
        const rows = document.querySelectorAll('.tabela_fornecedor tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseover', () => {
                row.style.backgroundColor = '#666';
            });
            row.addEventListener('mouseout', () => {
                row.style.backgroundColor = row.rowIndex % 2 === 0 ? '#555' : '#444'; 
            });
        });
    }

    addTableAnimations();
    
    // Inicializa o filtro com base na seleção atual
    filterTable();
});
