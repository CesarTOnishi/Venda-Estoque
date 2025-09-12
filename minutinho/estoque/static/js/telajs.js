document.addEventListener('DOMContentLoaded', function() {
  // Elementos principais
  const sidebar = document.querySelector('.sidebar-tech');
  const toggleBtn = document.getElementById('sidebarToggle');
  
  // Verifica se os elementos existem
  if (!sidebar || !toggleBtn) return;

  // 1. Funcionalidade de abrir/fechar a sidebar
  toggleBtn.addEventListener('click', function(e) {
    e.preventDefault();
    sidebar.classList.toggle('collapsed');
    
    // Fecha todos os dropdowns ao minimizar
    if (sidebar.classList.contains('collapsed')) {
      document.querySelectorAll('.nav-group').forEach(group => {
        group.classList.remove('active');
      });
    }
  });
  
  // 2. Funcionalidade dos dropdowns
  document.querySelectorAll('.group-header').forEach(header => {
    header.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      const group = this.parentElement;
      const wasActive = group.classList.contains('active');
      
      // Se sidebar estiver minimizada, fecha outros dropdowns
      if (sidebar.classList.contains('collapsed')) {
        document.querySelectorAll('.nav-group').forEach(g => {
          if (g !== group) g.classList.remove('active');
        });
      }
      
      // Alterna o estado do dropdown clicado
      group.classList.toggle('active', !wasActive);
    });
  });
  
  // 3. Fechar dropdowns ao clicar fora
  document.addEventListener('click', function(e) {
    // Fecha dropdowns se clicar fora (exceto quando sidebar está minimizada)
    if (!sidebar.classList.contains('collapsed')) {
      const isDropdown = e.target.closest('.nav-group');
      if (!isDropdown) {
        document.querySelectorAll('.nav-group').forEach(group => {
          group.classList.remove('active');
        });
      }
    }
  });
  
  // 4. Fechar dropdowns ao minimizar a sidebar
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.attributeName === 'class') {
        if (sidebar.classList.contains('collapsed')) {
          document.querySelectorAll('.nav-group').forEach(group => {
            group.classList.remove('active');
          });
        }
      }
    });
  });
  
  observer.observe(sidebar, {
    attributes: true
  });
  
  // 5. Fechar dropdowns ao redimensionar para mobile
  function handleResize() {
    if (window.innerWidth <= 768) {
      document.querySelectorAll('.nav-group').forEach(group => {
        group.classList.remove('active');
      });
    }
  }
  
  window.addEventListener('resize', handleResize);
});