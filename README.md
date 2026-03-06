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

Envie o código para o GitHub. No Easy Panel, conecte o repositório ao projeto: o painel faz o build e a implantação automaticamente.

No painel, configure só as variáveis de ambiente de cada serviço:

- **Backend:** `DATABASE_URL` com a URL do PostgreSQL (ex.: `postgresql://usuario:senha@host:5432/banco` — a URL normal que o painel ou o provedor do banco fornece).
- **Frontend:** `NEXT_PUBLIC_API_URL` com a URL pública do backend.

Não é preciso rodar nada em shell; tudo ocorre na implantação.

## Tabelas (PostgreSQL)

O backend cria automaticamente duas tabelas ao subir:

| Tabela    | Descrição |
|-----------|-----------|
| **auctions** | Leilões (fonte: calil, vegas). Campos: id, external_id, source, title, url, description, starts_at, ends_at, created_at, updated_at. |
| **lots**     | Lotes de cada leilão. Campos: id, auction_id, external_id, title, description, category, minimum_bid, current_bid, reference_value, url, raw_data, created_at, updated_at. |

A API expõe: `GET /api/auctions`, `GET /api/auctions/{id}`, `GET /api/lots`, `GET /api/stats`, `GET /docs` (Swagger).

## Primeiro scrape (validar dados)

No **dashboard** (frontend), use o botão **Rodar scrape agora**. Ele chama a API, busca leilões (Calil e Vegas), persiste no banco e atualiza a lista na tela. Não é preciso abrir outra URL nem rodar nada em shell.

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
