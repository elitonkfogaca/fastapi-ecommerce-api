# 🛒 FastAPI E-commerce API

API REST completa para e-commerce desenvolvida com FastAPI, PostgreSQL, SQLAlchemy 2.0 e autenticação JWT. Projeto profissional pronto para produção, ideal para portfólio e freelas.

## ✨ Features

### 🔐 Autenticação & Autorização
- ✅ JWT Authentication
- ✅ OAuth2 compatible (Swagger UI)
- ✅ Dual login endpoints (form-data + JSON)
- ✅ Role-Based Access Control (RBAC)
- ✅ Password hashing com Argon2
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

### Opção 1: Com Docker (Recomendado)

#### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/fastapi-ecommerce-api.git
cd fastapi-ecommerce-api
```

#### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` com suas configurações:

```env
APP_NAME=FastAPI E-commerce API
DEBUG=True

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ecommerce
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

SECRET_KEY=your-super-secret-key-min-32-chars
```

#### 3. Suba os containers

```bash
docker-compose up -d --build
```

#### 4. Execute as migrations

```bash
docker-compose exec api alembic upgrade head
```

#### 5. (Opcional) Popule com dados de exemplo

```bash
docker-compose exec api python -m app.database.seed
```

Isso criará:
- **Admin**: `admin@example.com` / `admin123`
- **Customer**: `customer@example.com` / `customer123`
- **5 categorias de exemplo**

⚠️ **IMPORTANTE: Troque a senha do admin após o primeiro login!**

#### 6. Acesse a aplicação

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

#### Comandos úteis do Docker

```bash
# Ver logs da API
docker-compose logs -f api

# Ver logs do Postgres
docker-compose logs -f postgres

# Parar os containers
docker-compose down

# Parar e remover volumes (limpar banco)
docker-compose down -v

# Rebuild após mudanças
docker-compose up -d --build

# Acessar shell do container
docker-compose exec api bash
```

---

### Opção 2: Ambiente Local (Sem Docker)

#### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/fastapi-ecommerce-api.git
cd fastapi-ecommerce-api
```

#### 2. Configure o PostgreSQL

Instale o PostgreSQL 16 e crie o banco:

```sql
CREATE DATABASE ecommerce;
```

#### 3. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ecommerce
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua-senha
SECRET_KEY=gere-com-openssl-rand-hex-32
```

#### 4. Instale as dependências

```bash
# Com uv (recomendado)
uv sync

# Ou com pip
pip install -e .
```

#### 5. Execute as migrations

```bash
alembic upgrade head
```

#### 6. (Opcional) Popule com dados de exemplo

```bash
python -m app.database.seed
```

#### 7. Rode a API

```bash
uvicorn app.main:app --reload
```

#### 8. Acesse a aplicação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 Documentação da API

### Autenticação

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/v1/auth/register` | Registrar novo usuário | ❌ |
| POST | `/api/v1/auth/login` | Login (OAuth2 form-data para Swagger) | ❌ |
| POST | `/api/v1/auth/login/json` | Login (JSON para clientes REST) | ❌ |
| GET | `/api/v1/auth/me` | Dados do usuário logado | ✅ |

**Nota**: Use `/login` no Swagger UI (botão Authorize) e `/login/json` para requisições via Postman/Frontend.

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

### Docker Compose (Produção)

```bash
# Build e run em produção
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

### Docker Image (Manual)

```bash
# Build da imagem
docker build -t fastapi-ecommerce .

# Run com variáveis de ambiente
docker run -d \
  -p 8000:8000 \
  -e POSTGRES_HOST=seu-host \
  -e POSTGRES_DB=ecommerce \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=senha \
  -e SECRET_KEY=sua-chave-secreta \
  fastapi-ecommerce
```

### Plataformas Recomendadas

- **Railway**: Deploy automático com PostgreSQL incluído
- **Render**: Free tier disponível
- **Fly.io**: Global edge deployment
- **DigitalOcean App Platform**: Fácil configuração
- **AWS ECS/Fargate**: Para produção enterprise

## � Docker

O projeto inclui configuração completa de Docker:

- **Dockerfile multi-stage**: Build otimizado e leve
- **docker-compose.yml**: PostgreSQL + API
- **Health checks**: Monitoramento automático
- **Volumes persistentes**: Dados do PostgreSQL
- **Network isolado**: Segurança entre containers

### Estrutura Docker

```yaml
services:
  postgres:    # PostgreSQL 16
  api:         # FastAPI Application
```

## �📝 Variáveis de Ambiente

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