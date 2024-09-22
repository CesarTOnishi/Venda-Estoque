$(document).ready(function() {
    // Aplica a máscara ao CPF e telefone
    $('#cpf').mask('000.000.000-00');
    $('#telefone').mask('(00) 00000-0000');
    
    // Adiciona um efeito de foco para os inputs
    $('input').focus(function() {
        $(this).css({
            'border-color': '#ac4147',
            'box-shadow': '0 0 8px rgba(172, 65, 71, 0.5)'
        });
    }).blur(function() {
        $(this).css({
            'border-color': '#666',
            'box-shadow': 'none'
        });
    });
});
