# 📦 Sistema ERP (Venda e Estoque)

![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange)
![Python](https://img.shields.io/badge/Python-3.11.5-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2.5-darkgreen?logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?logo=sqlite&logoColor=white)
![xhtml2pdf](https://img.shields.io/badge/xhtml2pdf-A80200?logo=adobeacrobatreader&logoColor=white)
![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-blue)

Este projeto é um Sistema ERP (Enterprise Resource Planning) desenvolvido para auxiliar empresas no controle de cadastros, movimentações financeiras, vendas, compras e geração de relatórios gerenciais.

A proposta do ERP é centralizar operações, garantir organização dos dados e facilitar a tomada de decisões com informações confiáveis.

---

## ✨ Features Principais

O sistema ERP foi estruturado para atender às principais necessidades de gestão empresarial, oferecendo recursos organizados em módulos independentes e integrados.

### 🔹 Gestão Administrativa
* Registro e controle de cadastros essenciais (clientes, fornecedores, colaboradores e produtos)
* Gestão de usuários e permissões de acesso
* Parametrização de condições de pagamento e contas bancárias

### 🔹 Gestão Operacional e Financeira
* Controle de compras e recebimento de mercadorias
* Controle de vendas e faturamento
* Contas a pagar e contas a receber
* Controle de fluxo de caixa e movimentação bancária

### 🔹 Relatórios Gerenciais (PDF)
* Relatórios detalhados de vendas, compras, clientes, fornecedores e produtos
* Extrato financeiro consolidado
* Histórico financeiro por período

---

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando as seguintes tecnologias:

| Componente | Descrição |
| :--- | :--- |
| **Python 3.11.5** | Linguagem principal do projeto |
| **Django 4.2.5** | Framework utilizado no desenvolvimento da aplicação |
| **SQLite** | Banco de dados relacional leve e integrado |
| **xhtml2pdf** | Geração de relatórios PDF a partir de templates HTML/CSS |
| **Visual Studio Code** | IDE utilizada no desenvolvimento |
| **Astah UML** | Criação de diagramas UML (caso de uso, classe, sequência) |
| **DBeaver** | Ferramenta para gerenciamento do banco de dados |

---

## 📚 Documentação Completa

Este projeto foi desenvolvido como parte de um Trabalho de Conclusão de Curso (TCC). A documentação completa inclui:

* Planejamento do sistema
* Especificação de requisitos
* Modelagem UML (caso de uso, classe e sequência)
* Estrutura do banco de dados
* Descrição técnica da implementação

**A documentação formal (PDF) está disponível [clicando aqui](https://github.com/CesarTOnishi/Venda-Estoque/blob/main/Documento.pdf).**
*Os diagramas UML (caso de uso, sequência e classe) foram desenvolvidos utilizando o Astah UML.*
---

## ⚙️ Instalação e Execução (Setup)

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/CesarTOnishi/Venda-Estoque.git
    ```

2.  **Acesse a pasta do projeto:**
    ```bash
    cd Venda-Estoque
    ```

3.  **Crie e ative um ambiente virtual (venv):**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    
    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Aplique as migrações do banco de dados:**
    ```bash
    python manage.py migrate
    ```

6.  **Crie um superusuário (para acessar o /admin):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```

8.  Acesse o sistema em `http://127.0.0.1:8000/` no seu navegador.

---

## 📄 Licença

Este projeto é distribuído sob a licença MIT. 
