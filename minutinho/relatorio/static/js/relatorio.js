document.addEventListener("DOMContentLoaded", function () {
    const reportLinks = document.querySelectorAll('.report-links ul li a');
    
    reportLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            console.log(`Você clicou no relatório: ${this.textContent}`);
        });
    });
});
