# Deploy no Easy Panel

## Opção 1: Dois serviços (recomendado)

No Easy Panel você pode criar **dois apps** a partir do mesmo repositório:

1. **Backend**
   - Build: Dockerfile em `./backend`
   - Porta: 8000
   - Variável: `DATABASE_URL=sqlite+aiosqlite:///./data/leiloes.db`
   - Volume: montar um volume em `/app/data` para persistir o SQLite

2. **Frontend**
   - Build: Dockerfile em `./frontend`
   - Porta: 3000
   - Variável: `NEXT_PUBLIC_API_URL=https://url-do-seu-backend` (URL pública do backend no Easy Panel)

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
