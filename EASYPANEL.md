# Deploy no Easy Panel

O Easy Panel usa a **raiz do repositório** como contexto de build. Use os Dockerfiles na raiz:

## Backend

- **Repositório:** mesmo para os dois serviços
- **Dockerfile:** `Dockerfile.backend` (na raiz do repo)
- **Contexto / Root:** raiz do repositório (padrão)
- **Porta:** 8000
- **Variável:** `DATABASE_URL=sqlite+aiosqlite:///./data/leiloes.db`
- **Volume:** montar em `/app/data` para persistir o SQLite

## Frontend

- **Dockerfile:** `Dockerfile.frontend` (na raiz do repo)
- **Contexto / Root:** raiz do repositório (padrão)
- **Porta:** 3000
- **Variável:** `NEXT_PUBLIC_API_URL=https://url-publica-do-backend` (URL do serviço backend no Easy Panel)

## Opção 2: Docker Compose

Se o Easy Panel suportar import de **Docker Compose**:

- Use o `docker-compose.yml` da raiz.
- Ajuste `NEXT_PUBLIC_API_URL` no serviço `frontend` para a URL do backend em produção (ex.: `https://backend.seudominio.com`).

## Scraper (agendado)

Para atualizar os dados periodicamente:

- Crie um **Cron** ou **scheduled job** no Easy Panel que rode:
  - Imagem: mesma do backend
  - Comando: `python -m app.scrapers.run_all`
  - Volume: mesmo volume de dados do backend (`/app/data`)

Ou use o perfil do compose: `docker compose --profile scrape run scraper`.
