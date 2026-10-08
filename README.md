# Reading Lizard

Reading Lizard is an AI-powered learning and research app. Learners can ask questions in a conversational interface, get beginner-friendly explanations, and explore a website by URL. Website content is scraped and indexed so follow-up answers can use relevant source material. Signed-in users can return to saved conversations and continue asking questions with recent conversation context.

## How It Works

The project runs as three services:

- **Frontend:** React and Vite provide the home page, account screens, and protected research workspace.
- **Backend:** Express handles authentication, saved conversations, MongoDB persistence, and requests to the AI service.
- **AI service:** FastAPI routes questions to the appropriate learning workflow. Groq generates explanations, Firecrawl extracts website content, and ChromaDB stores/retrieves indexed content. Redis is used for caching.

A typical request travels from the React app to the Express API, which stores the user's message and sends the query and recent history to FastAPI. FastAPI returns the answer and any website-learning state; the backend saves the answer and returns it to the frontend.

## Features

- User registration and login with JWT authentication
- General, conversational learning answers
- Website scraping and indexing for source-informed answers
- Topic selection for website-based learning
- Saved conversations and recent message history
- Redis caching for supported AI and scraping workflows

## Project Structure

```text
learnloom/
|-- frontend/       React + Vite application
|-- backend/        Express API, authentication, and MongoDB models
|-- ai_services/    FastAPI application and AI/retrieval workflows
`-- README.md
```

## Requirements

- Node.js and npm
- Python 3.10 or later
- A MongoDB database
- API credentials for the AI features you use: Groq and Firecrawl
- Upstash Redis credentials for the Redis cache

## Configuration

Create local environment files; do not commit secrets. The repository ignores `.env` files.

Create `backend/src/.env`:

```dotenv
PORT=3000
MONGODB_URI=your-mongodb-connection-string
JWT_SECRET=use-a-long-random-secret
AI_SERVICE_URL=http://127.0.0.1:8000
```

`AI_SERVICE_URL` must be configured. The backend has no implicit localhost fallback. It accepts the AI service base URL or the full `/analyze-query` URL. In production, use the deployed AI service's public URL; a loopback URL such as `127.0.0.1` is rejected.

Create `ai_services/.env`:

```dotenv
GROQ_API_KEY=your-groq-api-key
FIRECRAWL_API_KEY=your-firecrawl-api-key
UPSTASH_REDIS_REST_URL=your-upstash-redis-url
UPSTASH_REDIS_REST_TOKEN=your-upstash-redis-token
```

Create `frontend/.env`:

```dotenv
VITE_API_URL=http://localhost:3000
```

For a deployed frontend, set `VITE_API_URL` to the public backend URL when building the frontend. Vite embeds `VITE_` variables in the client build, so they are not server-side secrets.

## Run Locally

Start MongoDB and make sure the environment files above are configured. Run each service in a separate terminal from the repository root.

**1. AI service**

```powershell
cd ai_services
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The AI service exposes `GET /health` and `POST /analyze-query`.

**2. Backend API**

```powershell
cd backend
npm install
npm run dev
```

The backend exposes `GET /api/health` and `GET /api/health/ready`. The ready check reports whether MongoDB is connected.

**3. Frontend**

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite in the terminal.

## Deployment

Deploy the frontend, backend, and AI service as separate services, and configure service URLs and secrets in the hosting providers' environment settings.

- Set backend `AI_SERVICE_URL` to the public AI service URL. The AI service must be reachable from the backend over the network.
- Run the AI service with a command such as `uvicorn main:app --host 0.0.0.0 --port $PORT`, with the service root directory set to `ai_services`.
- Set frontend `VITE_API_URL` to the public backend URL before building the frontend.
- Set backend `MONGODB_URI` and `JWT_SECRET`; set the AI service's provider and Redis credentials as listed above.
- Check `GET /health` on the AI service, `GET /api/health` on the backend, and `GET /api/health/ready` for backend/database readiness.

The host must provide the `PORT` environment variable expected by its platform, or the start command should use that platform's documented port syntax.

## Keep Deployed Services Awake

The GitHub Actions workflow at `.github/workflows/keep-services-awake.yml` pings both services every 10 minutes and retries temporarily unavailable health endpoints. To enable it, add these repository **Variables** under **Settings > Secrets and variables > Actions > Variables**:

- `AI_SERVICE_HEALTH_URL`: the public AI service health URL, ending in `/health`.
- `BACKEND_HEALTH_URL`: the public backend health URL, ending in `/api/health`.

The workflow also supports a manual run from the repository's Actions tab. Scheduled workflows run from the repository's default branch. This external ping can prevent idle suspension only when the hosting provider treats incoming health requests as activity and allows this kind of monitoring. It cannot override a provider's sleep policy or replace an always-on instance; check the provider's plan if the service still suspends.

## Tests

Run the backend tests from the repository root:

```powershell
npm --prefix backend test
```

Run the AI service tests from its directory with the service dependencies installed:

```powershell
cd ai_services
python -m unittest discover -s tests
```

## Notes

- User accounts, conversations, and messages are stored in MongoDB.
- ChromaDB data is persisted under `ai_services/chroma_data/`; configure durable storage for this directory if website indexes must survive AI service restarts or redeployments.
- Keep API keys and database credentials out of source control and frontend environment variables.
