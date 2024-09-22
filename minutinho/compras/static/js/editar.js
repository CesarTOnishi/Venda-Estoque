function closeNotification() {
    const notification = document.getElementById('notification');
    notification.classList.remove('visible');
    notification.classList.add('hidden');
}

function showNotification(message) {
    const notification = document.getElementById('notification');
    const messageSpan = document.getElementById('notification-message');

    messageSpan.innerHTML = message; // Permite múltiplas linhas
    notification.classList.remove('hidden');
    notification.classList.add('visible');

    setTimeout(() => {
        closeNotification();
    }, 5000); // Fechar após 3 segundos
} 
$('#data_pedido').val(currentDate);
    if ($('.notification').hasClass('visible')) {
        setTimeout(() => {
            closeNotification();
        }, 5000);
    }