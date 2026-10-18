# Adaptive Survey Engine

## Run the backend

1. Create and activate a Python virtual environment.
2. Install the dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and add a Gemini API key only if you use the LLM endpoints.
4. Start the API from this directory with `uvicorn app.main:app --reload --reload-dir app`.
5. Open `http://127.0.0.1:8000/docs` to inspect the API.

The Hot Chocolate frontend uses the deterministic research and adaptive-session
endpoints, so a Gemini API key is not required for its survey flow.

## Connect the Hot Chocolate frontend

The frontend is in the sibling `Hot chocolate` directory. Copy its `.env.example`
to `.env`, keep `VITE_API_BASE_URL=http://localhost:8000` for a local backend,
then run `npm install` and `npm run dev` from that directory. The backend allows
the default Vite origins on port 5173. For another frontend origin, set
`CORS_ORIGINS` in this project's `.env` to a comma-separated list of trusted
origins, then restart the API.

The frontend creates a research project, starts a session with a saved survey
blueprint, requests each adaptive question, and submits answers to that session.
