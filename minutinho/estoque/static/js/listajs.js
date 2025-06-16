function aplicarFiltro() {
    const searchValue = document.getElementById('pesquisa').value.toLowerCase();
    const selectedCategory = document.getElementById('categoria').value.toLowerCase();
    const rows = document.querySelectorAll('#productTable tbody tr');

    rows.forEach(row => {
        const productName = row.querySelector('.product-name').textContent.toLowerCase();
        const productCategory = row.querySelector('.product-category').textContent.toLowerCase();

        const matchesSearch = productName.includes(searchValue);
        const matchesCategory = selectedCategory === '' || productCategory === selectedCategory;

        if (matchesSearch && matchesCategory) {
            row.style.display = ''; 
        } else {
            row.style.display = 'none'; 
        }
    });
}

document.getElementById('pesquisa').addEventListener('input', aplicarFiltro);
