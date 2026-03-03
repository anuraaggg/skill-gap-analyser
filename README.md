# Job–Resume Matching

Minimal setup to run the project locally.

## Backend (FastAPI)

1. `cd backend`
2. Create and activate a virtualenv (or use your own).
3. `pip install -r requirements.txt`
4. `uvicorn main:app --host 0.0.0.0 --port 8000`

## Frontend (Next.js)

1. `cd frontend`
2. Copy `.env.example` to `.env.local` and set `NEXT_PUBLIC_API_BASE_URL` to your backend URL.
3. `npm install`
4. `npm run dev`