# AI Complaint Management System -- Frontend

React + TypeScript + Vite frontend for the pharmaceutical complaint
management system (Phase 6). Talks to the FastAPI backend in `../backend`.

## Stack

React 18, TypeScript, Vite, React Router 6, Tailwind CSS, Axios.

## Setup

```bash
cd frontend
npm install
cp .env.example .env    # point VITE_API_BASE_URL at your running backend
npm run dev
```

Visit `http://localhost:5173`. Make sure the backend is running at the URL
in `.env` (`http://localhost:8000/api/v1` by default) and that
`CORS_ORIGINS` in the backend's `.env` includes `http://localhost:5173`
(it does, out of the box).

The backend defaults to `AI_MOCK_MODE=true`, so every AI feature (extract,
chat, summarize, root cause, CAPA, risk, duplicate check, completeness)
works end-to-end against mock responses with no Groq key required -- this
frontend was built and designed against that mode.

## Project Structure

```
src/
├── main.tsx                 # entrypoint (Router + AuthProvider)
├── App.tsx                  # route table
├── api/                      # one file per backend router (auth/complaints/ai) + axios client
├── types/                     # TS types mirroring backend/app/schemas & models exactly
├── context/AuthContext.tsx      # session state, login/register/logout
├── routes/ProtectedRoute.tsx      # redirects to /login when unauthenticated
├── components/
│   ├── layout/                      # Sidebar + AppShell
│   ├── ui/                            # Stamp, Button, Card, FormField, Spinner
│   └── complaints/                      # IntakeSourcePanel, ComplaintForm, AIActionsPanel, ChatPanel
├── pages/                                 # Login, Register, ComplaintList, NewComplaint, ComplaintDetail, NotFound
└── lib/formatters.ts                        # enum/date label helpers
```

## Design notes

The four intake form sections (Origin & Customer, Product & Batch,
Complaint Details, Initial Assessment & Priority) match
`backend/app/models/complaint.py` field groupings exactly, including the
numbering used there. Status/priority/severity/risk values render through
a shared `Stamp` component styled like a QC release stamp (bordered
rectangle, corner ticks, uppercase monospace) -- the app's one recurring
visual signature. Typography is IBM Plex Sans (UI) / IBM Plex Mono (data,
IDs, timestamps, stamps).

## Known limitation

This was built without network access to the npm registry, so `npm install`
/ `npm run build` have not been run or verified in this environment. Every
file was written and manually reviewed for consistency, but please run
`npm install && npm run build` yourself as a first step and let me know if
anything surfaces -- happy to fix immediately.
