   // Quando o método de pagamento for alterado
   $('#metodo_pagamento').change(function() {
    var metodoPagamento = $(this).val();
    var valorTotal = parseFloat("{{ valor_geral|default:0 }}");

    if (metodoPagamento && valorTotal > 0) {
        $.ajax({
            url: "{% url 'api_condicoes_pagamento' %}",
            data: { 'metodo': metodoPagamento },
            method: "GET",
            success: function(response) {
                var selectCondicao = $('#condicao_pagamento_id');
                selectCondicao.empty();
                selectCondicao.append('<option value="" disabled selected>Selecione uma condição</option>');

                response.forEach(function(condicao) {
                    // Calcula os valores para cada condição
                    var valorComDesconto = valorTotal * (1 - condicao.desconto/100);
                    var valorFinal = valorComDesconto * (1 + condicao.juros/100);
                    var valorParcela = condicao.parcelas > 0 ? valorFinal / condicao.parcelas : valorFinal;
                    
                    selectCondicao.append(
                        '<option value="' + condicao.id + '" ' +
                        'data-parcelas="' + condicao.parcelas + '" ' +
                        'data-juros="' + condicao.juros + '" ' +
                        'data-desconto="' + condicao.desconto + '" ' +
                        'data-valor-parcela="' + valorParcela.toFixed(2) + '" ' +
                        'data-valor-final="' + valorFinal.toFixed(2) + '">' +
                        condicao.nome + ' (' + condicao.tipo_display + ' - ' + condicao.parcelas + 'x)' +
                        '</option>'
                    );
                });

                $('#condicao-pagamento-section').removeClass('hidden');
            },
            error: function() {
                alert("Erro ao carregar condições de pagamento.");
            }
        });
    } else {
        $('#condicao-pagamento-section').addClass('hidden');
    }
});

// Quando a condição de pagamento for alterada
$('#condicao_pagamento_id').change(function() {
    var selectedOption = $(this).find('option:selected');
    var parcelas = selectedOption.data('parcelas');
    var juros = selectedOption.data('juros');
    var desconto = selectedOption.data('desconto');
    var valorParcela = selectedOption.data('valor-parcela');
    var valorFinal = selectedOption.data('valor-final');
    
    // Atualiza os detalhes na página
    $('.condicao-detalhes').html(`
        <h4>Detalhes da Condição</h4>
        <p><strong>Forma de Pagamento:</strong> ${selectedOption.text().match(/\((.*?)\s*-/)[1]}</p>
        <p><strong>Parcelas:</strong> ${parcelas}x de R$ ${valorParcela}</p>
        <p><strong>Valor Total:</strong> R$ ${valorFinal}</p>
        ${desconto > 0 ? '<p><strong>Desconto:</strong> ' + desconto + '%</p>' : ''}
        ${juros > 0 ? '<p><strong>Juros:</strong> ' + juros + '%</p>' : ''}
    `).show();
});