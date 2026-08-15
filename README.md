# EduSync ERP Web

React + Vite + TypeScript frontend for the EduSync ERP application.

## Run locally

```powershell
cd web
npm install
npm run dev
```

Open the local URL printed by Vite, normally `http://localhost:5173`.

## Build

```powershell
cd web
npm run build
npm run preview
```

## Project structure

```text
web/src/
├── app/                 # Application shell and route resolution
├── components/          # Common UI and layout shells
├── data/                # Temporary demo data
├── pages/               # Admin and student screens
├── services/api/        # FastAPI HTTP client boundary
├── styles/              # Global design system styles
├── types/               # Shared TypeScript domain types
└── main.tsx             # Vite entry point
web/.env.example         # Frontend environment template
docs/mockups/            # Original HTML references, kept unchanged
```

The current pages use local demo data. The API client is ready for the FastAPI service through `VITE_API_BASE_URL`.

## Run the local API

Start PostgreSQL and FastAPI with Docker from the repository root:

```powershell
docker compose up --build
```

The API is available at `http://localhost:8000`, with interactive documentation at `http://localhost:8000/docs`.

The backend currently provides the versioned screen endpoints and local document upload boundary. Database models, Alembic migrations, and enforced JWT role permissions are the next backend phase.
