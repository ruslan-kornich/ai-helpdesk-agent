<h1 align="center">AI Helpdesk Agent</h1>

<p align="center">
  Multichannel AI support agent for an SMS/SMPP platform — classifies incoming messages,
  answers from a knowledge base, opens structured tickets, escalates to the right specialist
  and reports analytics. Ships with a React admin panel.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/frontend-React%2018-61DAFB?logo=react&logoColor=black" alt="React 18" />
  <img src="https://img.shields.io/badge/database-PostgreSQL-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/LLM-OpenAI-412991?logo=openai&logoColor=white" alt="OpenAI" />
  <img src="https://img.shields.io/badge/deploy-Docker%20Compose-2496ED?logo=docker&logoColor=white" alt="Docker" />
</p>

---

## Features

| Feature | Description |
|---|---|
| **Channels** | Telegram bot and Zendesk (real, long-polling — no public URL needed), WhatsApp/Teams via an in-app simulator. All channels share one agent pipeline. |
| **AI pipeline** | One structured LLM call does classification, entity extraction and sentiment; routing is deterministic pure logic. Without an API key, replies fall back to templates. |
| **Tickets** | One structured ticket per conversation session, with category, priority, extracted entities and escalation target. |
| **Escalation** | 8 support scenarios routed to finance, sales, L2 support or the support lead; urgent outages escalate immediately, even after hours. |
| **Admin panel** | React dashboard with live conversations (WebSocket), ticket browser, analytics charts and editable agent settings (working hours, persona). |
| **Analytics** | Resolution rate, category/priority breakdowns — in the UI and via `make report` in the CLI. |

## Support scenarios

| Trigger | Category | Priority | Escalation |
|---|---|---|---|
| How to use the platform | `how_to` | normal | — (AI-resolved) |
| Top-up balance / wallet | `billing` | normal | finance |
| Undelivered SMS report | `delivery_issue` | high | L2 support |
| Message outside working hours | `after_hours` | normal | morning queue |
| Pricing / commercial request | `commercial` | normal | sales |
| Outage / API error | `outage` | urgent | L2 support (immediate) |
| Unrecognized intent | `unknown` | normal | general support |
| Service complaint | `other` | high | support lead |

## Quick start

```bash
cp .env.example .env    # fill in OPENAI_API_KEY (and optionally Telegram/Zendesk)
make run                # docker compose up --build
```

Open http://localhost:8000 — the admin panel, REST API, WebSocket and the Telegram bot
(if a token is set) run in a single `app` container; PostgreSQL runs as the `db` container.

```bash
make create-user        # create an admin user (email + password)
make seed               # load demo tickets
make report             # analytics from the CLI
make test               # run unit tests (host, needs uv)
```

Without `make`, each target is a thin wrapper over `docker compose` — e.g.
`docker compose up --build` or `docker compose exec app uv run python -m app.cli report`.

## Configuration

Every variable has a default, so the app boots even with an empty `.env`:

| Variable | Notes |
|---|---|
| `OPENAI_API_KEY` | Enables live AI replies; empty → deterministic template fallback. |
| `TELEGRAM_BOT_TOKEN` | From [@BotFather](https://t.me/BotFather); enables the in-process Telegram poller. |
| `ZENDESK_SUBDOMAIN` / `ZENDESK_EMAIL` / `ZENDESK_API_TOKEN` | Enables the Zendesk inbound poller; replies and priority/tags are posted back to the ticket. |
| `DATABASE_URL` | Async SQLAlchemy URL; preset for the compose `db` service. |
| `JWT_SECRET` | Signs admin-panel auth tokens — change for any non-local use. |

The full list (working hours, timezone, confidence threshold, token lifetimes) lives in
[`.env.example`](.env.example).

## Architecture

```
  Telegram ─┐
  Zendesk  ─┼─► conversation_service ─► agent pipeline ─► PostgreSQL
  Simulator┘         │                  (analyzer · router · responder)
                     ▼
              WebSocket broadcast ─► React admin panel
```

Layered (onion) backend: `models → repositories → schemas → services → routers`, with side
modules `agent/` (pure, no DB), `channels/` (infra adapters) and `knowledge/` (FAQ retriever).

- **Single LLM call + pure router** — classification, entities and sentiment in one structured
  OpenAI call; routing is a fully unit-tested pure function.
- **In-process pollers** — Telegram and Zendesk long-polling run inside the FastAPI lifespan;
  no broker or public tunnel needed.
- **Provider abstractions** — a thin `LLMProvider` ABC and a `Retriever` ABC allow swapping
  the model or dropping in a vector store with no agent changes.
- **Sessions** — a new message from the same client within 30 minutes appends to the existing
  ticket; Zendesk tickets map 1:1 to internal tickets instead.

## Repository layout

```
.
├── backend/            # FastAPI app — SQLAlchemy 2.0 async, agent pipeline, channels
│   ├── app/
│   │   ├── agent/      # analyzer · router · responder (pure, no DB)
│   │   ├── channels/   # Telegram bot, Zendesk poller, simulator
│   │   ├── services/   # conversation, ticket, escalation, analytics
│   │   └── ...         # models, repositories, schemas, routers
│   └── tests/
├── frontend/           # React 18 admin panel — TypeScript, Vite, Tailwind CSS v4
├── docker-compose.yml  # app + PostgreSQL
└── Makefile
```

## Local development (no Docker)

```bash
cd backend && uv sync && uv run uvicorn app.main:app --port 8000
cd frontend && npm install && npm run dev    # :5173 with proxy to :8000
```
