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

### Prerequisites
- **Python 3.12+** (required by `gagent-core` dependencies; the Dockerfile uses 3.12)
- A GitHub **Personal Access Token (PAT)** with access to the private `g-agent-ai-core-backend` repo

### Steps
1) Create and activate a virtual environment **with Python 3.12**:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

2) Upgrade build tools and install pre-requisites (matches the Dockerfile):

```bash
pip install --upgrade pip setuptools wheel
pip install Cython av==12.3.0
```

3) Install the private `gagent-core` package (replace `<PAT_TOKEN>` with your GitHub PAT):

```bash
pip install "git+https://<PAT_TOKEN>@github.com/Ghaia-ai/g-agent-ai-core-backend.git@v2.3.18"
```

4) Install project dependencies:

```bash
pip install -r requirements.txt
```

5) Configure environment variables:

```bash
cp .env.example .env
# Edit .env and fill in values — ensure all values are properly quoted
```

6) Export environment variables and run the app:

```bash
export $(grep -v '^#' .env | grep -v '^\s*$' | xargs)
python -m app.main
```

The server starts at `http://0.0.0.0:8000` by default.

### Common issues
- **Python version**: `gagent-core` requires Python ≥ 3.10. Using 3.9 or lower will fail with dependency resolution errors.
- **`.env` parsing**: Make sure all values with special characters (URLs, connection strings) are wrapped in double quotes. Avoid URL-encoded characters like `%22` inside values.
- **Env vars not loaded**: Some `gagent-core` settings classes don't read `.env` directly — you must export the variables to the shell environment before running.

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
