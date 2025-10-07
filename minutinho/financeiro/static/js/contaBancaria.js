tabelaBody.addEventListener("click", function(e) {
    const editBtn = e.target.closest(".edit-button");
    if (editBtn) {
        document.getElementById("modal-title").textContent = "Editar Conta";
        document.getElementById("conta_id").value = editBtn.dataset.id;
        document.getElementById("banco").value = editBtn.dataset.banco;
        document.getElementById("tipo_conta").value = editBtn.dataset.tipo;
        document.getElementById("numero_conta").value = editBtn.dataset.numero;
        document.getElementById("agencia").value = editBtn.dataset.agencia;
        document.getElementById("saldo_inicial").value = editBtn.dataset.saldo;
        document.getElementById("ativo").checked = (editBtn.dataset.ativo === "True");
        modal.classList.add("show");
    }
});
