# 🛒 FastAPI E-commerce API

API REST completa para e-commerce desenvolvida com FastAPI, PostgreSQL, SQLAlchemy 2.0 e autenticação JWT. Projeto profissional pronto para produção, ideal para portfólio e freelas.

## ✨ Features

### 🔐 Autenticação & Autorização
- ✅ JWT Authentication
- ✅ Role-Based Access Control (RBAC)
- ✅ Password hashing com Argon2
- ✅ Refresh token support
- ✅ Granular permissions (Admin/Customer)

### 👤 Gestão de Usuários
- ✅ CRUD completo de usuários
- ✅ Busca por nome/email
- ✅ Alteração de senha com validação
- ✅ Ativar/desativar usuários
- ✅ Gestão de roles (admin only)
- ✅ Self-service (usuário edita próprio perfil)

### 📦 Produtos
- ✅ CRUD completo
- ✅ Filtros avançados (nome, categoria, preço)
- ✅ Paginação
- ✅ Gestão de estoque
- ✅ Soft delete
- ✅ Relacionamento com categorias

### 🏷️ Categorias
- ✅ CRUD completo
- ✅ Geração automática de slug
- ✅ Contagem de produtos por categoria
- ✅ Busca por slug
- ✅ Validação de exclusão (previne deletar com produtos)

### 🛒 Pedidos
- ✅ Criação de pedidos com múltiplos items
- ✅ Cálculo automático de total
- ✅ Validação de estoque
- ✅ Atualização automática de estoque
- ✅ Status workflow (PENDING → PAID → SHIPPED → DELIVERED)
- ✅ Cancelamento com devolução de estoque
- ✅ Filtros por status e usuário
- ✅ Access control (user vê apenas seus pedidos)

## 🛠️ Stack Tecnológica

- **Framework**: FastAPI
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: JWT + Argon2
- **Validation**: Pydantic V2
- **Container**: Docker Compose

## 📋 Pré-requisitos

- Python 3.12+
- Docker & Docker Compose
- Git

## 🚀 Como Rodar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/fastapi-ecommerce-api.git
cd fastapi-ecommerce-api
```

### 2. Crie o arquivo .env

```bash
cp .env.example .env
```

Edite o `.env` com suas configurações (principalmente o `SECRET_KEY`):

```bash
# Gerar SECRET_KEY segura
openssl rand -hex 32
```

### 3. Suba o banco de dados

```bash
docker compose up -d
```

### 4. Instale as dependências

```bash
# Com pip
pip install -e .

# Ou com uv (recomendado)
uv sync
```

### 5. Execute as migrations

```bash
alembic upgrade head
```

### 6. Popule o banco com dados iniciais

```bash
python -m app.database.seed
```

Isso criará:
- **Admin**: `admin@example.com` / `admin123`
- **Customer**: `customer@example.com` / `customer123`
- **5 categorias de exemplo**

⚠️ **IMPORTANTE: Troque a senha do admin após o primeiro login!**

### 7. Rode a API

```bash
uvicorn app.main:app --reload
```

### 8. Acesse a documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 Documentação da API

### Autenticação

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/v1/auth/register` | Registrar novo usuário | ❌ |
| POST | `/api/v1/auth/login` | Login | ❌ |
| GET | `/api/v1/auth/me` | Dados do usuário logado | ✅ |

### Usuários

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/v1/users` | Listar usuários | Admin |
| GET | `/api/v1/users/{id}` | Buscar usuário | Self/Admin |
| PUT | `/api/v1/users/{id}` | Atualizar usuário | Self/Admin |
| PATCH | `/api/v1/users/{id}/password` | Alterar senha | Self |
| PATCH | `/api/v1/users/{id}/role` | Alterar role | Admin |
| PATCH | `/api/v1/users/{id}/status` | Ativar/desativar | Admin |
| DELETE | `/api/v1/users/{id}` | Deletar usuário | Admin |

### Produtos

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/v1/products` | Listar produtos | ❌ |
| GET | `/api/v1/products/{id}` | Buscar produto | ❌ |
| POST | `/api/v1/products` | Criar produto | Admin |
| PUT | `/api/v1/products/{id}` | Atualizar produto | Admin |
| PATCH | `/api/v1/products/{id}/stock` | Atualizar estoque | Admin |
| DELETE | `/api/v1/products/{id}` | Desativar produto | Admin |

### Categorias

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/v1/categories` | Listar categorias | ❌ |
| GET | `/api/v1/categories/{id}` | Buscar categoria | ❌ |
| GET | `/api/v1/categories/slug/{slug}` | Buscar por slug | ❌ |
| POST | `/api/v1/categories` | Criar categoria | Admin |
| PUT | `/api/v1/categories/{id}` | Atualizar categoria | Admin |
| DELETE | `/api/v1/categories/{id}` | Deletar categoria | Admin |

### Pedidos

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/v1/orders` | Listar pedidos | ✅ |
| GET | `/api/v1/orders/{id}` | Buscar pedido | ✅ |
| POST | `/api/v1/orders` | Criar pedido | ✅ |
| PATCH | `/api/v1/orders/{id}/status` | Atualizar status | Admin |
| DELETE | `/api/v1/orders/{id}` | Cancelar pedido | ✅ |

## 🏗️ Arquitetura

```
📦 app/
├── 🔐 auth/              # Autenticação JWT
├── 👤 users/             # Gestão de usuários
├── 📦 products/          # Gestão de produtos
├── 🏷️ categories/        # Gestão de categorias
├── 🛒 orders/            # Gestão de pedidos
├── ⚙️ core/              # Configurações
├── 🗄️ database/          # Database & Seed
├── 📋 enums/             # Enums (Roles, Status)
├── 🗂️ models/            # SQLAlchemy Models
├── 📝 schemas/           # Pydantic Schemas
└── 🚀 main.py           # FastAPI App
```

### Padrões Implementados

- ✅ **Service Layer**: Lógica de negócio separada dos controllers
- ✅ **Repository Pattern**: Acesso a dados centralizado
- ✅ **DTO Pattern**: Pydantic schemas para request/response
- ✅ **Dependency Injection**: FastAPI Depends
- ✅ **SOLID Principles**: Código limpo e manutenível

## 🧪 CLI de Gerenciamento (Opcional)

Se instalou `typer` e `rich`:

```bash
# Ver informações do projeto
python -m app.cli info

# Seed completo
python -m app.cli seed

# Seed apenas admin
python -m app.cli seed --admin-only
```

## 🔒 Segurança

- ✅ Password hashing com Argon2
- ✅ JWT com expiração
- ✅ RBAC granular
- ✅ Input validation (Pydantic)
- ✅ SQL Injection protection (SQLAlchemy)
- ✅ CORS configurável

## 🚢 Deploy

### Docker

```bash
# Build
docker build -t fastapi-ecommerce .

# Run
docker run -p 8000:8000 fastapi-ecommerce
```

### Plataformas Recomendadas

- Railway
- Render
- Fly.io
- DigitalOcean App Platform

## 📝 Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `POSTGRES_HOST` | Host do PostgreSQL | `localhost` |
| `POSTGRES_PORT` | Porta do PostgreSQL | `5432` |
| `POSTGRES_DB` | Nome do banco | `ecommerce_db` |
| `POSTGRES_USER` | Usuário do banco | `postgres` |
| `POSTGRES_PASSWORD` | Senha do banco | `postgres` |
| `SECRET_KEY` | Chave secreta JWT | (gerar com openssl) |
| `DEBUG` | Modo debug | `True` ou `False` |

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 👨‍💻 Autor

Eliton Fogaca - [GitHub](https://github.com/elitonkfogaca)

---

⭐ Se este projeto te ajudou, considere dar uma estrela!