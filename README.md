📦 Sistema ERP (Enterprise Resource Planning)

Este projeto é um Sistema ERP (Enterprise Resource Planning) desenvolvido para auxiliar empresas no controle de cadastros, movimentações financeiras, vendas, compras e geração de relatórios gerenciais.

✨ Features Principais

O sistema ERP foi estruturado para atender às principais necessidades de gestão empresarial, oferecendo recursos organizados em módulos independentes e integrados.

🔹 Gestão Administrativa

Registro e controle de cadastros essenciais (clientes, fornecedores, colaboradores e produtos)
Gestão de usuários e permissões de acesso
Parametrização de condições de pagamento e contas bancárias

🔹 Gestão Operacional e Financeira

Controle de compras e recebimento de mercadorias
Controle de vendas e faturamento
Contas a pagar e contas a receber
Controle de fluxo de caixa e movimentação bancária

🔹 Relatórios Gerenciais (PDF)

Relatórios detalhados de vendas, compras, clientes, fornecedores e produtos
Extrato financeiro consolidado
Histórico financeiro por período

A proposta do ERP é centralizar operações, garantir organização dos dados e facilitar a tomada de decisões com informações confiáveis.

🛠️ Tecnologias Utilizadas
Componente	Descrição
Python 3.11.5	Linguagem principal do projeto
Django 4.2.5	Framework utilizado no desenvolvimento da aplicação
SQLite	Banco de dados relacional leve e integrado
xhtml2pdf	Geração de relatórios PDF a partir de templates HTML/CSS
Visual Studio Code	IDE utilizada no desenvolvimento
Astah UML	Criação de diagramas UML (caso de uso, classe, sequência)
DBeaver	Ferramenta para gerenciamento do banco de dados

📚 Documentação Completa

Este projeto foi desenvolvido como parte de um Trabalho de Conclusão de Curso (TCC). A documentação completa inclui:

Planejamento do sistema
Especificação de requisitos
Modelagem UML (caso de uso, classe e sequência)
Estrutura do banco de dados
Descrição técnica da implementação
A documentação formal está disponível no diretório do projeto ou mediante solicitação. Os diagramas UML (caso de uso, sequência e classe) foram desenvolvidos utilizando o Astah UML.

⚙️ Instalação e Execução (Setup)
Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

Clone o repositório:
Bash
git clone https://github.com/CesarTOnishi/Venda-Estoque.git
cd minutinho

Crie e ative um ambiente virtual (venv):
Bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

Instale as dependências: 
Bash
pip install -r requirements.txt

Aplique as migrações do banco de dados:
Bash
python manage.py migrate
Crie um superusuário (para acessar o /admin):
Bash
python manage.py createsuperuser

Inicie o servidor de desenvolvimento:
Bash
python manage.py runserver
Acesse o sistema em http://127.0.0.1:8000/ no seu navegador.
