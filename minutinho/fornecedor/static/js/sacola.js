$('#metodo_pagamento').change(function() {
    const metodo = $(this).val();
    if (metodo === "cartao_credito") {
        $('#parcelamento').show();
    } else {
        $('#parcelamento').hide();
        $('#parcelas').val(1);
        updateParcelas(1); 
    }
});

$('#parcelas').change(function() {
    const parcelas = parseInt($(this).val(), 10);
    updateParcelas(parcelas);
});

function updateParcelas(parcelas) {
    const valorTotal = { valor_geral }; 
    const valorParcela = (valorTotal / parcelas).toFixed(2);
    $('.total-section h2').html(`Parcelas: ${parcelas}x de R$ ${valorParcela}`); 
}
