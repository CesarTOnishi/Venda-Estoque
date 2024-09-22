document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('.caixa_input input');
    
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focus');
        });

        input.addEventListener('blur', () => {
            if (input.value === '') {
                input.parentElement.classList.remove('focus');
            }
        });
    });
});
