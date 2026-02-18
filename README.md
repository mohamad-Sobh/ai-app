# ai-backend-template

A starter structure for building AI backends with a clean, scalable layout. ✨

## What this template includes
- A minimal app entrypoint powered by `g-agent-ai-core-backend`.
- Clear separation of concerns (agents, routers, services, tools, utils).
- Dockerfile optimized for dependency caching and repeatable builds.

## Folder overview 🗂️
- `app/` — Core application code.
- `app/context/` — Conversation context models and suggestion helpers.
- `app/handlers/` — Event or message handlers.
- `app/knowledge/` — Knowledge sources, loaders, or embeddings.
- `app/models/` — Data models and schemas.
- `app/routers/` — API/WebSocket routes.
- `app/services/` — Service layer logic.
- `app/tools/` — Tooling used by the agent (search, retrieval, etc.).
- `app/utils/` — Shared helpers and utilities.
- `docs/` — Project documentation.
- `tests/` — Automated tests.

## Local setup ⚙️
1) Create and activate a virtual environment.
2) Install dependencies.
3) Run the app.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

Notes:
- Copy `.env.example` to `.env` and adjust values as needed.
- `requirements.txt` includes a minimal baseline; add your dependencies as you build.
- The default server runs on `0.0.0.0:8000` and can be configured via env vars.

## Configuration 🔧
Environment variables used by the app:
- `APP_HOST` — Defaults to `0.0.0.0`
- `APP_PORT` — Defaults to `8000`
- The `.env.example` file contains the minimal required key set; copy it to `.env` and fill in values.

## Running with Docker 🐳
Build the image (replace `pat_token` and `<image_name>`):

```bash
docker buildx build --platform linux/amd64 --build-arg PAT_TOKEN=pat_token -t <image_name> .
```

Run the container (expects a local `.env` file):

```bash
docker run -p 8000:8000 --env-file .env <image_name>:latest
```

## Deployment notes 🚀
- Ensure the container can reach any external services (vector DBs, object storage, etc.).
- Provide required secrets via the environment or a secrets manager.
- If you deploy behind a proxy, forward `APP_HOST`/`APP_PORT` as needed.

## How to extend ✅
- Add routers in `app/routers/` and register them in `app/factory.py`.
- Implement agent logic in `app/agent.py` and supporting services in `app/services/`.
- Keep reusable utilities in `app/utils/`.
- For private dependencies, use a tokenized URL or a secrets manager.

## Testing 🧪
Add tests under `tests/`. When you introduce a test runner, document commands here.
