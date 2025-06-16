document.addEventListener('DOMContentLoaded', function() {
    let sidebar = document.querySelector(".sidebar");
    let closeBtn = document.querySelector("#btn");
    
    closeBtn.addEventListener("click", ()=>{
        sidebar.classList.toggle("open");
        menuBtnChange();
    });
    
    function menuBtnChange() {
      if(sidebar.classList.contains("open")){
          closeBtn.classList.replace("bx-menu", "bx-menu-alt-right");
      } else {
          closeBtn.classList.replace("bx-menu-alt-right","bx-menu");
          // Fecha todos os dropdowns quando a sidebar fecha
          document.querySelectorAll('.dropdown').forEach(dropdown => {
              dropdown.classList.remove('active');
          });
      }
    }
    
    // Dropdown functionality
    document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
      // Adiciona data-title para o tooltip
      const title = toggle.querySelector('.links_name').textContent;
      toggle.setAttribute('data-title', title);
      
      toggle.addEventListener('click', function(e) {
        e.preventDefault();
        const dropdown = this.parentElement;
        
        // Fecha outros dropdowns antes de abrir este
        if (!dropdown.classList.contains('active')) {
          document.querySelectorAll('.dropdown').forEach(item => {
            if (item !== dropdown) item.classList.remove('active');
          });
        }
        
        // Alterna o dropdown clicado
        dropdown.classList.toggle('active');
        
        // Se a sidebar estiver fechada, fecha o dropdown ao clicar fora
        if (!sidebar.classList.contains('open')) {
          e.stopPropagation();
        }
      });
    });
    
    // Fecha dropdowns ao clicar fora (quando sidebar fechada)
    document.addEventListener('click', function(e) {
      if (!sidebar.classList.contains('open')) {
        const isDropdown = e.target.closest('.dropdown');
        if (!isDropdown) {
          document.querySelectorAll('.dropdown').forEach(dropdown => {
            dropdown.classList.remove('active');
          });
        }
      }
    });
  });