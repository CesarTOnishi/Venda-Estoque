document.addEventListener('DOMContentLoaded', function() {
    function filterTable() {
        const query = document.getElementById('search').value.toLowerCase();
        const rows = document.querySelectorAll('.tabela_cliente tbody tr');
        rows.forEach(row => {
            const cells = row.getElementsByTagName('td');
            let match = false;
            for (let i = 0; i < cells.length; i++) {
                if (cells[i].textContent.toLowerCase().includes(query)) {
                    match = true;
                    break;
                }
            }
            row.style.display = match ? '' : 'none';
        });
    }

    document.getElementById('search').addEventListener('input', filterTable);

    function addTableAnimations() {
        const rows = document.querySelectorAll('.tabela_cliente tbody tr');
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
});
