   // Captura todos os links de deletar
   const deleteButtons = document.querySelectorAll('.delete-btn');

   deleteButtons.forEach(button => {
       button.addEventListener('click', function(e) {
           e.preventDefault(); // Evita o comportamento padrão do link

           const categoriaId = this.getAttribute('data-id'); // Pega o ID da categoria
           openModal(categoriaId); // Abre o modal
       });
   });

   function openModal(id) {
       document.getElementById("modal").style.display = "block";
       // Define a URL para a ação do formulário de deleção
       document.getElementById("delete-form").action = "{% url 'deletarCategoria' 0 %}".replace('0', id);
   }

   function closeModal() {
       document.getElementById("modal").style.display = "none";
   }