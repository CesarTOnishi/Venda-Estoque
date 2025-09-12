$(document).ready(function() {
    // Inicializa filtros como escondidos
    $('#form-filtros').hide();
    
(function($) {
    $(document).ready(function() {
        // Variável para controle do loading
        var isLoading = false;
        
        function loadContas(page, filters = {}) {
            if (isLoading) return;
            
            isLoading = true;
            $('.table-responsive').append('<div class="loading-overlay"><div class="loading-spinner"></div></div>');
            
            filters.page = page;
            
            // Use a sintaxe completa do jQuery.ajax
            jQuery.ajax({
                url: window.location.pathname,
                data: filters,
                headers: {'X-Requested-With': 'XMLHttpRequest'},
                type: 'GET',
                dataType: 'json',
                success: function(data) {
                    updateTable(data);
                    updatePagination(data.paginator);
                    updateSaldo(data.saldo_total);
                    
                    // Atualiza a URL sem recarregar
                    const params = jQuery.param(filters);
                    window.history.pushState({}, '', `${window.location.pathname}?${params}`);
                },
                error: function(xhr, status, error) {
                    console.error("Erro:", error);
                    alert("Erro ao carregar dados. Tente novamente.");
                },
                complete: function() {
                    $('.loading-overlay').remove();
                    isLoading = false;
                    $('html, body').animate({
                        scrollTop: $('.table-responsive').offset().top - 20
                    }, 200);
                }
            });
        }

    function updateTable(data) {
        const tbody = $('table tbody');
        tbody.empty();
        
        if (data.contas.length === 0) {
            tbody.append('<tr><td colspan="7">Nenhuma conta a receber encontrada com os filtros aplicados.</td></tr>');
            return;
        }
        
        data.contas.forEach(conta => {
            const vencida = new Date(conta.vencimento.split('/').reverse().join('-')) < new Date();
            const row = `
                <tr class="${vencida ? 'conta-vencida' : ''}">
                    <td>
                        ${conta.editavel ? 
                            `<button class="editar-btn" data-metodo="${conta.metodo_pagamento}"
                                data-id="${conta.id}" data-descricao="${conta.descricao}"
                                data-valor="${conta.valor}" data-vencimento="${conta.vencimento}">
                                Editar
                            </button>` : 
                            `<span class="nao-editavel">Não editável</span>`}
                    </td>
                    <td>${conta.criado_em}</td>
                    <td>${conta.descricao}</td>
                    <td class="valor-positivo">R$ ${parseFloat(conta.valor).toFixed(2)}</td>
                    <td>${conta.metodo_pagamento}</td>
                    <td class="${vencida ? 'data-vencida' : ''}">
                        ${conta.vencimento}
                        ${vencida ? '<i class="fas fa-exclamation-triangle"></i>' : ''}
                    </td>
                    <td>
                        <select class="acao" data-conta-id="${conta.id}">
                            <option value="pendente" ${!conta.recebido ? 'selected' : ''}>Pendente</option>
                            <option value="pago" ${conta.recebido ? 'selected' : ''}>Pago</option>
                        </select>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
    }

    function updatePagination(paginator) {
        const paginationHtml = `
            <span class="step-links">
                ${paginator.has_previous ? 
                    `<a href="javascript:void(0)" class="page-link" data-page="1">&laquo; primeira</a>
                     <a href="javascript:void(0)" class="page-link" data-page="${paginator.previous_page_number}">anterior</a>` : ''}

                <span class="current">
                    Página ${paginator.number} de ${paginator.num_pages}.
                </span>

                ${paginator.has_next ? 
                    `<a href="javascript:void(0)" class="page-link" data-page="${paginator.next_page_number}">próxima</a>
                     <a href="javascript:void(0)" class="page-link" data-page="${paginator.num_pages}">última &raquo;</a>` : ''}
            </span>
        `;
        
        $('.paginacao').html(paginationHtml);
    }

    function updateSaldo(saldo) {
        const saldoElement = $('.saldo p');
        saldoElement.text(`R$ ${saldo.toFixed(2)}`);
        saldoElement.removeClass('saldo-positivo saldo-negativo')
                   .addClass(saldo >= 0 ? 'saldo-positivo' : 'saldo-negativo');
    }

    // Event listeners
    $(document)
        .on('click', '.page-link', function(e) {
            e.preventDefault();
            loadContas($(this).data('page'), getCurrentFilters());
        })
        .on('submit', '#form-filtros', function(e) {
            e.preventDefault();
            loadContas(1, $(this).serialize());
        })
        .on('click', '#toggle-filtros', function() {
            $('#form-filtros').toggle();
            $(this).find('i').toggleClass('fa-chevron-down fa-chevron-up');
        })
        .on('change', '.acao', function() {
            const select = $(this);
            const valorAnterior = select.data('prev-value') || select.val();
            select.data('prev-value', valorAnterior);
            
            $.ajax({
                url: `/financeiro/atualizarPagamento/${select.data('conta-id')}/`,
                method: 'POST',
                headers: {'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()},
                data: {status: select.val()},
                success: function(data) {
                    if (data.success) {
                        updateSaldo(data.saldo_total);
                    } else {
                        select.val(valorAnterior);
                        alert('Erro ao atualizar status');
                    }
                },
                error: function() {
                    select.val(valorAnterior);
                    alert('Erro na conexão');
                }
            });
        });

    // Modal handling
    $('#open_modal_button').click(function() {
        $('#modal_container').show();
        $('#modal-title').text('Adicionar Conta a Receber');
        $('#pagamento_id, #descricao, #vencimento, #valor').val('');
        $('#tipo_pagamento').val('');
    });

    $('#close_modal_button').click(function() {
        $('#modal_container').hide();
    });

    $(document).on('click', '.editar-btn', function() {
        $('#modal_container').show();
        $('#modal-title').text('Editar Conta a Receber');
        $('#pagamento_id').val($(this).data('id'));
        $('#descricao').val($(this).data('descricao'));
        $('#vencimento').val($(this).data('vencimento'));
        $('#valor').val($(this).data('valor').replace(',', '.'));
        $('#tipo_pagamento').val($(this).data('metodo'));
    });

    // Date validation
    $('#data_inicio, #vencimento_inicio').change(function() {
        const target = $(this).attr('id').includes('data') ? '#data_fim' : '#vencimento_fim';
        $(target).attr('min', $(this).val());
    });

    $('#data_fim, #vencimento_fim').change(function() {
        const target = $(this).attr('id').includes('data') ? '#data_inicio' : '#vencimento_inicio';
        $(target).attr('max', $(this).val());
    });

    // Initial load
    loadContas(1, getCurrentFilters());

    function getCurrentFilters() {
        return $('#form-filtros').serialize();
    }
});

function closeNotification() {
    $('#notification').removeClass('visible').addClass('hidden');
}
loadContas(1, getCurrentFilters());
    });
})(jQuery);