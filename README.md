# Leilões MVP — Dashboard e Scraping

Dashboard que agrega informações de sites de leilões (Calil, Vegas, etc.), armazena e atualiza os dados, com visão para uso de IA na tomada de decisão.

## Stack

- **Backend**: Python, FastAPI, PostgreSQL, scrapers (Playwright/BeautifulSoup)
- **Frontend**: Next.js (dashboard)
- **Deploy**: Docker Compose — local e [Easy Panel](https://easypanel.io)

## Rodar localmente

### Pré-requisitos

- Python 3.11+
- Node 18+
- Docker e Docker Compose (para rodar tudo junto)

### Opção 1 — Docker (recomendado)

```bash
docker compose up -d
```

- API: http://localhost:8000  
- Dashboard: http://localhost:3000  
- Docs API: http://localhost:8000/docs  

### Opção 2 — Manual

**Backend**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

**Scraper (agendado ou manual)**

```bash
cd backend
python -m app.scrapers.run_all
```

## Deploy no Easy Panel

1. **GitHub**: crie um repositório e envie o código:
   ```bash
   git init
   git add .
   git commit -m "MVP Leilões - dashboard e scrapers"
   git remote add origin https://github.com/SEU_USUARIO/leiloes.git
   git branch -M main
   git push -u origin main
   ```

2. **Easy Panel**: no painel do servidor:
   - **Create** → **App** → escolha **Docker Compose** ou **Template**.
   - Conecte o repositório GitHub (ou cole o conteúdo do `docker-compose.yml`).
   - O Easy Panel fará build das imagens e subirá `backend` e `frontend`.

3. **Variáveis de ambiente** (produção):
   - No serviço **frontend**: `NEXT_PUBLIC_API_URL=https://sua-api.easypanel.xxx` (URL pública do backend).
   - No **backend**: configurar `DATABASE_URL` com a URL do PostgreSQL (ex.: serviço no Easy Panel).

4. **PostgreSQL**: no Easy Panel, crie um banco PostgreSQL e defina `DATABASE_URL` no backend e no job de scraper (ex.: `postgresql+asyncpg://user:senha@host:5432/leiloes`).

5. **Scraper agendado**: use o serviço `scraper` com profile ou crie um Cron no Easy Panel para rodar periodicamente:
   ```bash
   docker compose --profile scrape run scraper
   ```

## Estrutura

```
Leilões/
├── backend/          # API + scrapers + DB
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── scrapers/
│   │   └── api/
│   └── requirements.txt
├── frontend/         # Dashboard Next.js
├── docker-compose.yml
└── README.md
```

## Licença

Uso interno / projeto FabriaIA.
