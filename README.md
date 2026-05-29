# ai-helpdesk-agent

Multichannel AI support agent for the Gatum SMS/SMPP platform. Connects to Telegram and
Zendesk (real), mocks WhatsApp/Teams through an in-app simulator, handles 8 support
scenarios, records a structured ticket per conversation, escalates to the right specialist,
and reports analytics. Ships with a React admin panel.

## Prerequisites
- Docker + Docker Compose
- (Optional, for local dev) `uv` and Node.js 20+
- An OpenAI API key (for live AI replies; the app still runs without one — replies fall back
  to deterministic templates)
- (Optional) A Telegram bot token and a Zendesk trial account

## One-command run
```bash
cp .env.example .env        # then fill in OPENAI_API_KEY (and optionally Telegram/Zendesk)
make run                    # docker compose up --build
```
Open http://localhost:8000 — the admin panel, REST API, WebSocket, and (if a token is set)
the in-process Telegram bot all run in the single `app` container. PostgreSQL runs as the
`db` container with a persistent named volume.

- Analytics from the CLI: `make report`
- Load demo tickets: `make seed`
- Run unit tests (host): `make test`

<details>
<summary>Without <code>make</code> (Windows, or any machine without GNU Make)</summary>

The `make` targets are thin wrappers over `docker compose`. Run these directly instead:

```bash
cp .env.example .env                # then fill in OPENAI_API_KEY

docker compose up --build           # = make run    (start app + db)
docker compose down                 # = make down   (stop everything)
docker compose build                # = make build  (rebuild images only)

docker compose exec app uv run python -m app.cli report    # = make report
docker compose exec app uv run python -m app.seed          # = make seed
docker compose exec app uv run python -m app.create_user   # = make create-user

cd backend && uv run pytest -v      # = make test   (runs on host, needs uv)
```

The `exec` commands require the stack to be already running (`docker compose up`).
</details>

### Getting a Telegram token
Message [@BotFather](https://t.me/BotFather), `/newbot`, copy the token into
`TELEGRAM_BOT_TOKEN`. Long-polling is used, so no public URL/tunnel is needed.

### Zendesk trial setup
Create a free Zendesk trial. In Admin Center → Apps and integrations → APIs → Zendesk API,
enable token access and create an API token. Set `ZENDESK_SUBDOMAIN` (the `xxx` in
`xxx.zendesk.com`), `ZENDESK_EMAIL`, and `ZENDESK_API_TOKEN`. If unset, Zendesk is treated as
unavailable (logged warning, no crash). `ZENDESK_POLL_INTERVAL_SECONDS` controls how often the
poller checks for new comments (default: 15 seconds).

At runtime, an in-process poller (started in the FastAPI lifespan alongside the Telegram poller)
polls Zendesk for new requester comments, runs each through the agent pipeline, and posts the reply
plus updated priority/tags/status back onto the same ticket. No public tunnel is needed — the same
approach as Telegram long-polling.

To open a ticket for the demo, the message must be authored by the ticket requester (the bot skips
agent and bot comments). Supported inputs: the Help Center **"submit a request"** form, email-to-
ticket, or an API-created ticket on the requester's behalf. The messaging Web Widget is not
compatible — it creates conversations, not classic ticket comments.

### Local dev (no Docker)
```bash
cd backend && uv sync && uv run uvicorn app.main:app --port 8000
cd frontend && npm install && npm run dev    # :5173 with proxy to :8000
```

## Configuration (environment variables)

Copy `.env.example` → `.env`. Every variable has a default, so the app **boots even with an
empty `.env`** — but without `OPENAI_API_KEY` replies fall back to deterministic templates.
Set these for a real demo:

| Variable | Default | Notes |
|----------|---------|-------|
| `OPENAI_API_KEY` | _(empty)_ | Needed for live AI replies; empty → deterministic template fallback. |
| `OPENAI_MODEL` | `gpt-4.1` | Model used by the analyzer/responder. |
| `TELEGRAM_BOT_TOKEN` | _(empty)_ | From [@BotFather](https://t.me/BotFather); enables the in-process Telegram poller. Leave empty to disable. |
| `ZENDESK_SUBDOMAIN` / `ZENDESK_EMAIL` / `ZENDESK_API_TOKEN` | _(empty)_ | Optional — enables the Zendesk inbound poller. Leave empty to disable (no crash). |
| `DATABASE_URL` | `postgresql+asyncpg://…@db:5432/gatum` | Async SQLAlchemy URL; preset for the compose `db` service. |
| `JWT_SECRET` | `CHANGE_ME` | **Change for any non-local use** — signs admin-panel auth tokens. |

The full list — Postgres credentials, working hours, timezone, confidence threshold, token
lifetimes — lives in [`.env.example`](.env.example) with sensible defaults.

## Architecture

```mermaid
flowchart TD
  subgraph Channels["Channels (infra adapters)"]
    TG[Telegram bot] --> CS
    SIM[Simulator / mock WhatsApp+Teams] --> CS
    ZD[Zendesk inbound poller] --> CS
  end

  subgraph Services["Services (orchestration)"]
    CS[conversation_service]
    TS[ticket_service]
    ES[escalation_service]
  end

  subgraph Agent["agent/ (pure, no DB)"]
    AP[agent.pipeline]
    AN[analyzer · 1 GPT-4o call]
    RT[router · pure logic]
    RS[responder + retriever]
  end

  subgraph Persistence["Persistence"]
    TR[(ticket_repository)]
    MR[(message_repository)]
    DB[(PostgreSQL)]
  end

  CS --> TS
  CS --> ES
  CS --> ZD
  CS --> AP
  AP --> AN
  AP --> RT
  AP --> RS
  CS --> TR
  CS --> MR
  TR --> DB
  MR --> DB
  CS --> WS[[WebSocket broadcast]]
  WS --> UI[React admin]

  classDef external fill:#e7f0ff,stroke:#4577c9,color:#1c2e4a;
  classDef store fill:#eafaf0,stroke:#3a9d6a,color:#143527;
  class TG,SIM,ZD,UI external;
  class TR,MR,DB store;
```

Layered (onion) dependency flow: `models → repositories → schemas → services → routers`, with
side modules `agent/` (pure, no DB), `channels/` (infra adapters), `knowledge/` (retriever),
and `utils/` (generic repository, exceptions, WebSocket manager, timestamp mixin). The
`agent.router` is a pure function and is the most heavily unit-tested unit.

## Architecture Decision Records (ADR)

- **FastAPI** — async-first, matches the WebSocket + Telegram polling workload and gives typed
  request/response models for free.
- **uv** — fast, reproducible installs via `uv.lock`; one tool for venv + deps; used locally
  and in the Dockerfile (`uv sync --frozen`).
- **PostgreSQL (asyncpg) + SQLAlchemy async as primary store** — closest to a real production
  deployment, native `jsonb` for the ticket `metadata`, proper concurrency for live WS/Telegram
  traffic, runs as a compose service with a persistent volume. The engine is built from a single
  `DATABASE_URL`, so unit tests fall back to in-memory SQLite (aiosqlite) for fast, dependency-free
  CI. The only dialect-sensitive surfaces — the JSON column and string UUIDs — are portable across
  both.
- **Async SQLAlchemy** — consistent with async FastAPI + Telegram polling; no sync/async bridging.
- **Single merged analyzer + pure router** (over multi-agent) — one structured GPT-4o call does
  classification + entity extraction + sentiment, cutting latency and cost; routing is deterministic
  pure logic, fully unit-testable and free.
- **OpenAI structured outputs behind our own `LLMProvider`** (over an agent framework like pydantic-ai)
  — the analyzer parses straight into a validated pydantic `AnalysisResult` via the native
  structured-outputs API (`beta.chat.completions.parse`), eliminating manual JSON/enum coercion. We keep
  our own thin `LLMProvider` ABC rather than adopting an agent framework: it satisfies the spec's
  provider-abstraction requirement, keeps the dependency surface small, and leaves the routing logic in
  our own testable pure function instead of a framework's control flow. Domain carriers that are built by
  our own code (`RouterDecision`, `AgentResult`, `AppContext`) stay dataclasses — pydantic adds value only
  at the LLM boundary where untrusted data enters.
- **Layered (onion) architecture** — strict one-directional dependencies keep services unit-testable
  (inject a mock repository) and routes trivial.
- **Keyword retriever** — sufficient for the prototype FAQ; the `Retriever` ABC allows a drop-in
  vector store (Chroma/FAISS) with no agent changes.
- **Mock WhatsApp/Teams** — Business/Teams approval takes time; the simulator exercises every
  scenario through the same pipeline. Telegram + Zendesk satisfy the two-real-channel requirement.
- **After-hours modeling** — `after_hours` is its own category for non-urgent messages outside
  09:00–18:00 (Mon–Fri); urgent outage (C-6) still escalates immediately at night. A `was_after_hours`
  flag is stored in metadata for analytics regardless of final category.
- **Telegram in-process (not a separate worker)** — the polling loop runs in the FastAPI lifespan,
  sharing the pipeline and WebSocket broadcaster in-memory; no broker needed. Extracting it into its
  own container is the documented scaling path, not needed now.
- **Zendesk inbound polling (not webhook/trigger push)** — no public tunnel needed locally,
  consistent with the Telegram long-polling decision; the poller runs in-process in the FastAPI
  lifespan exactly like the Telegram poller.
- **Zendesk Approach A (in-memory `updated_at` watermark + persisted per-ticket
  `last_seen_comment_id` cursor)** over Approach B (Incremental Export cursor API) — simpler to
  implement for a prototype; the persisted cursor de-duplicates already-answered comments across
  restarts. Approach B (Incremental Export) is the documented scaling path.
- **One Zendesk ticket maps to one internal ticket** via `zendesk_ticket_id` in metadata —
  bypasses the 30-minute session window used by other channels because a Zendesk ticket is a
  long-lived thread, not a 30-minute session.
- **Loop prevention via `author_id == requester_id`** — the bot processes only comments authored
  by the ticket requester, skipping its own replies and human agents' comments without requiring a
  `users/me.json` lookup.
- **Accepted prototype limitation** — a comment arriving strictly during a restart (its
  `updated_at` falls before the new in-memory watermark) may be missed until the ticket is next
  updated; day-granularity search re-fetches are harmless because the persisted comment cursor
  de-duplicates already-answered comments.
- **`general_support` escalation target** — extends the assignment's enum so C-7 routes to a non-null
  target, keeping the `resolved_by_ai` invariant clean (C-7 reads as escalated, not AI-resolved).
- **C-6 priority = `urgent`** (not the literal "high") — the scenario demands "escalate immediately"
  and "confirm urgency"; `high` is reserved for C-8.
- **fastapi-pagination** — ready-made `Page[T]` + SQLAlchemy integration keeps list/history endpoints
  uniform; the repository owns `paginate` with a transformer mapping ORM rows → Read schemas.
- **loguru** — zero-boilerplate structured logging over stdlib `logging`; one configured sink.
- **Error model** — expected business failures raise `BusinessError` (mapped to JSON by a registered
  handler); unexpected ones are caught/logged with full context by the `catch_errors` decorator.
- **Backend layout** — `config/` package, `routers/api.py` aggregator, `utils/` generic repository +
  WebSocket manager, `create_app()` factory — follows the team's established conventions.
- **Testing strategy** — the deterministic core is unit-tested (`test_router.py`,
  `test_analytics_service.py`, `test_ticket_repository.py`, plus `test_conversation_service.py`,
  `test_ticket_service.py`, `test_retriever.py`); the non-deterministic LLM pipeline is exercised
  manually via the Simulator rather than asserted, to keep CI fast and stable.
- **Conversation lifecycle** — one ticket per session; a new message from the same client within 30
  minutes appends to the existing ticket, otherwise a new ticket opens.
- **Admin panel + editable settings** — the React admin and the Settings page are our own additions
  (the assignment requires neither a UI nor editable settings); they make the demo and scenario
  walkthrough far easier. Working hours/timezone/agent-persona are held in-memory on `AppContext` and
  applied live: working hours mutate the shared `router_config`; the persona is read per message and
  passed into the responder, so editing it changes the agent's tone immediately. The persona deliberately
  affects only the how_to LLM replies — the classifier prompt stays fixed (a bad edit must not break
  routing) and canned escalation replies stay fixed (guardrails: never quote prices, never hallucinate).
  Cross-restart persistence is out of scope for the prototype.

## Scenario handling

| # | Trigger | Handling | Category | Priority | Escalation |
|---|---------|----------|----------|----------|------------|
| C-1 | How to use the platform | Answer grounded in FAQ | how_to | normal | — (AI-resolved) |
| C-2 | Top-up balance / wallet | Top-up steps + ask for confirmation | billing | normal | finance |
| C-3 | Undelivered SMS report | Collect phone/time/sender ID; confirm; pass to L2 | delivery_issue | high | l2_support |
| C-4 | Outside working hours | Immediate ack + ticket; morning queue | after_hours | normal | — (human queue) |
| C-5 | Pricing / commercial | Acknowledge; sales will contact; never states prices | commercial | normal | sales |
| C-6 | Outage / API error | Ask error/time/IP; escalate immediately | outage | urgent | l2_support |
| C-7 | Unrecognized intent | Pass to specialist; never hallucinate | unknown | normal | general_support |
| C-8 | Service complaint | Detect negative sentiment; flag + notify lead | other | high | support_lead |

## Demo video
3–5 min video (mandatory): _add link here_. Shows app launch, ≥4 scenarios end-to-end via the
Simulator, the created ticket record, and `make report` analytics.
