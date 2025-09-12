// extrato.js - Versão completa com paginação AJAX e filtros recolhíveis

$(document).ready(function() {
    // 1. Inicialização - Filtros começam fechados
    $('#form-filtros').hide();
    $('#toggle-filtros i').removeClass('fa-chevron-up').addClass('fa-sliders-h');

    // 2. Verifica se há filtros ativos (exceto paginação)
    const urlParams = new URLSearchParams(window.location.search);
    let hasActiveFilters = false;
    
    urlParams.forEach((value, key) => {
        if (key !== 'page' && value) {
            hasActiveFilters = true;
        }
    });

    // 3. Se houver filtros ativos, mostra o formulário
    if (hasActiveFilters) {
        $('#form-filtros').show();
        $('#toggle-filtros i').removeClass('fa-sliders-h').addClass('fa-chevron-up');
    }

    // 4. Toggle dos filtros
    $('#toggle-filtros').click(function() {
        $('#form-filtros').toggle();
        $(this).find('i').toggleClass('fa-sliders-h fa-chevron-up');
    });

    // 5. Ao limpar filtros, fecha o painel
    $('.btn-limpar').click(function() {
        setTimeout(() => {
            $('#form-filtros').hide();
            $('#toggle-filtros i').removeClass('fa-chevron-up').addClass('fa-sliders-h');
        }, 100);
    });

    // 6. Validação de datas
    $('#data_inicio, #vencimento_inicio').change(function() {
        const target = $(this).attr('id').includes('data') ? '#data_fim' : '#vencimento_fim';
        $(target).attr('min', $(this).val());
    });

    $('#data_fim, #vencimento_fim').change(function() {
        const target = $(this).attr('id').includes('data') ? '#data_inicio' : '#vencimento_inicio';
        $(target).attr('max', $(this).val());
    });

    // 7. Paginação via AJAX
    let isLoading = false;

    function loadExtratos(page, filters = {}) {
        if (isLoading) return;
        
        isLoading = true;
        $('.table-responsive').append('<div class="loading-overlay"><div class="loading-spinner"></div></div>');
        
        filters.page = page;
        
        $.ajax({
            url: window.location.pathname,
            data: filters,
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                updateExtratoTable(data);
                updatePagination(data.paginator);
                updateSaldo(data.saldo_total);
                
                // Atualiza a URL sem recarregar
                const params = $.param(filters);
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

    function updateExtratoTable(data) {
        const tbody = $('table tbody');
        tbody.empty();
        
        if (data.extratos.length === 0) {
            tbody.append('<tr><td colspan="7">Nenhuma transação encontrada com os filtros aplicados.</td></tr>');
            return;
        }
        
        data.extratos.forEach(extrato => {
            const contaRelacionada = extrato.conta_relacionada;
            const row = `
                <tr>
                    <td>${extrato.data}</td>
                    <td>${extrato.descricao}</td>
                    <td>
                        ${contaRelacionada.id ? 
                            `<a href="#" class="conta-relacionada" 
                                data-conta-id="${contaRelacionada.id}"
                                data-tipo="${contaRelacionada.tipo}"
                                onclick="mostrarDetalhesConta(this); return false;">
                                ${contaRelacionada.descricao || 'Sem descrição'}
                                <span class="conta-id">(ID: ${contaRelacionada.id})</span>
                            </a>` : 
                            '-'}
                    </td>
                    <td>${extrato.metodo_pagamento}</td>
                    <td class="${extrato.classe_valor}">${extrato.valor_formatado}</td>
                    <td>
                        <span class="badge-${extrato.tipo}">
                            ${extrato.tipo === 'entrada' ? 'Entrada' : 'Saída'}
                        </span>
                    </td>
                    <td>
                        <span class="${extrato.classe_status}">
                            ${extrato.status}
                        </span>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
    }

    function updatePagination(paginator) {
        const paginationHtml = `
            <div class="pagination">
                ${paginator.has_previous ? 
                    `<a href="javascript:void(0)" class="page-link" data-page="1">&laquo; primeira</a>
                     <a href="javascript:void(0)" class="page-link" data-page="${paginator.previous_page_number}">anterior</a>` : 
                    '<span class="disabled">&laquo; primeira</span><span class="disabled">anterior</span>'}

                <span class="current">
                    Página ${paginator.number} de ${paginator.num_pages}
                </span>

                ${paginator.has_next ? 
                    `<a href="javascript:void(0)" class="page-link" data-page="${paginator.next_page_number}">próxima</a>
                     <a href="javascript:void(0)" class="page-link" data-page="${paginator.num_pages}">última &raquo;</a>` : 
                    '<span class="disabled">próxima</span><span class="disabled">última &raquo;</span>'}
            </div>
        `;
        
        $('.paginacao').html(paginationHtml);
    }

    function updateSaldo(saldo) {
        const saldoElement = $('.saldo p');
        saldoElement.text(`R$ ${saldo.toFixed(2)}`);
        saldoElement.removeClass('saldo-positivo saldo-negativo')
                   .addClass(saldo >= 0 ? 'saldo-positivo' : 'saldo-negativo');
    }

    // Event listeners para paginação
    $(document).on('click', '.page-link', function(e) {
        e.preventDefault();
        loadExtratos($(this).data('page'), getCurrentFilters());
    });

    // Submit do formulário de filtros
    $('#form-filtros').submit(function(e) {
        e.preventDefault();
        loadExtratos(1, $(this).serialize());
    });

    function getCurrentFilters() {
        return $('#form-filtros').serialize();
    }

    // Carrega os dados iniciais
    loadExtratos(1, getCurrentFilters());
});

// Função para mostrar detalhes da conta
function mostrarDetalhesConta(element) {
    const contaId = element.getAttribute('data-conta-id');
    const tipoConta = element.getAttribute('data-tipo');
    const modal = document.getElementById('contaModal');
    const modalContent = document.getElementById('modalContent');
    
    // Mostra o modal com um loader animado
    modal.style.display = 'block';
    modalContent.innerHTML = `
        <div class="modal-header">
            <h3>Carregando...</h3>
        </div>
        <div style="text-align: center; padding: 30px;">
            <div class="loader"></div>
        </div>
    `;
    
    // Faz a requisição AJAX
    fetch(`/detalhes-conta/${tipoConta}/${contaId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Preenche o modal com os detalhes formatados
                modalContent.innerHTML = `
                    <div class="modal-header">
                        <h3>Detalhes da Conta</h3>
                    </div>
                    <div class="detalhes-conta">
                        <div class="detalhes-item">
                            <strong>Descrição</strong>
                            <p>${data.descricao}</p>
                        </div>
                        <div class="detalhes-item">
                            <strong>Valor</strong>
                            <p class="valor-destaque">R$ ${data.valor}</p>
                        </div>
                        <div class="detalhes-item">
                            <strong>Método Pagamento</strong>
                            <p>${data.metodo_pagamento}</p>
                        </div>
                        <div class="detalhes-item">
                            <strong>Data Vencimento</strong>
                            <p>${data.data_vencimento}</p>
                        </div>
                        <div class="detalhes-item">
                            <strong>Status</strong>
                            <p class="${data.status === 'Recebido' || data.status === 'Pago' ? 'status-pago' : 'status-pendente'}">
                                ${data.status}
                            </p>
                        </div>
                        ${data.pedido ? `
                        <div class="detalhes-item">
                            <strong>Pedido Relacionado</strong>
                            <p>${data.pedido}</p>
                        </div>` : ''}
                        <div class="detalhes-item">
                            <strong>Data Criação</strong>
                            <p>${data.data_criacao}</p>
                        </div>
                    </div>
                `;
            } else {
                modalContent.innerHTML = `
                    <div class="modal-header">
                        <h3>Erro</h3>
                    </div>
                    <div class="detalhes-conta">
                        <p>Não foi possível carregar os detalhes desta conta.</p>
                        ${data.error ? `<p>${data.error}</p>` : ''}
                    </div>
                `;
            }
        })
        .catch(error => {
            modalContent.innerHTML = `
                <div class="modal-header">
                    <h3>Erro de Conexão</h3>
                </div>
                <div class="detalhes-conta">
                    <p>Ocorreu um erro ao conectar com o servidor.</p>
                </div>
            `;
        });
}

// Fechar o modal quando clicar no X
document.querySelector('.close-modal').addEventListener('click', function() {
    document.getElementById('contaModal').style.display = 'none';
});

// Fechar o modal quando clicar fora dele
window.addEventListener('click', function(event) {
    const modal = document.getElementById('contaModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
});