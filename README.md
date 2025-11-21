# 📊 App Fiscal

Sistema Fiscal Multiempresa desenvolvido com **FastAPI + React + PostgreSQL**.  
Este repositório contém o backend (Python/FastAPI) e futuramente o frontend (React).

---

## 🚀 Tecnologias

- **Backend:** FastAPI, SQLAlchemy (async), asyncpg
- **Banco de Dados:** PostgreSQL
- **Autenticação:** JWT (via python-jose + passlib/bcrypt)
- **Frontend:** React (a ser criado)
- **Outros:** Docker (futuramente para deploy), Alembic (migrações)

---

## 📂 Estrutura do projeto
app_fiscal/
├── backend/
│ ├── app/
│ │ ├── main.py # Ponto de entrada (inclui routers)
│ │ ├── database.py # Configuração do banco
│ │ ├── models/ # Modelos SQLAlchemy
│ │ ├── schemas/ # Schemas Pydantic
│ │ └── routers/ # Rotas (users, auth, companies)
│ └── requirements.txt # Dependências do backend
├── venv/ # Ambiente virtual (ignorado no git)
└── .gitignore # Arquivo de exclusão do git


---

## 🛠️ Rodando o backend

### 1. Clonar o repositório
```bash
git clone https://github.com/SEU_USUARIO/app-fiscal.git
cd app-fiscal/backend


2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate

3. Instalar dependências
pip install -r requirements.txt

4. Rodar o servidor FastAPI
uvicorn app.main:app --reload
A API estará disponível em: http://127.0.0.1:8000
Swagger Docs: http://127.0.0.1:8000/docs

✅ Funcionalidades Fase 1 (concluída)
 CRUD de usuários (GET, POST, PUT, DELETE)
 Senha com bcrypt
 Autenticação JWT (login + rota /auth/me)
 Estrutura inicial com routers organizados

 🎯 Próximos Passos (Fase 2)
 Criar módulo de empresas (companies)
 Relacionamento usuário ↔ empresa
 Proteção de escopo multiempresa
 Cadastros fiscais (clientes, fornecedores, produtos, serviços)a