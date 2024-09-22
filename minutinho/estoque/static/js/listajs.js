document.addEventListener('DOMContentLoaded', function() {
    function filterTable() {
        const query = document.getElementById('search').value.toLowerCase();
        const rows = document.querySelectorAll('.tabela_produto tbody tr');
        
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

    addTableAnimations();
});
