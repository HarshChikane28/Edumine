# Build Prompt: EduSync ERP — Local Web Application

Paste everything below this line into your coding agent (Claude Code, Cursor, etc.) as its operating brief. The agent has shell access and should run real CLI commands, not just print instructions.

---

## 0. Context You Are Given

You are implementing the **web application** for **EduSync ERP**, a school management system. You have been given two source assets in the project folder:

1. **`/stitch_edunexus_school_erp/*/code.html`** — eight Stitch-generated Tailwind/HTML mockups. These are the *visual and functional spec*. Do not redesign them — re-implement them faithfully as real, data-driven React components.
   - `student_dashboard_high_fidelity` — student home: greeting, upcoming events/countdowns, announcement banner, "My Progress" chart placeholder, bottom nav (Home/Schedule/Tasks/Profile).
   - `student_assignments_high_fidelity` — assignments list grouped by subject with status (Pending/Submitted/Graded), due-date urgency, "New Assignment" action.
   - `student_profile_insights_high_fidelity` — profile header (name, class, ID), GPA/Attendance/Assignments stat tiles, an "AI Performance Insight" panel, collapsible "Personal Details" and "Attendance History" sections.
   - `student_result_analysis_high_fidelity` — single exam result: rank, GPA, pass/fail, marksheet table (subject/marks/grade/status), subject-vs-class-average chart, share/download actions.
   - `wireframe_exam_management` — admin exam module: summary tiles (upcoming exams, average score, grading progress), exams table (subject/date/hall/proctor/status).
   - `wireframe_paperwork_manager` — admin document workflow: upload, requests table (document/subject/date/requestor/status: Pending/Processing/Completed), view/download actions.
   - `wireframe_student_activities` — admin activities dashboard: upcoming clubs/events with supervisor + enrollment counts, top-performing clubs, recent activity feed.
   - `wireframe_timetable_builder` — drag-and-drop weekly timetable grid by grade/section, with a palette of draggable subjects and classrooms.
2. **`academic_core/DESIGN.md`** — the design system: color tokens, typography scale, spacing, radii, elevation, and component rules.

   **Important discrepancy to resolve, don't ask the user — just follow this rule:** the prose in `DESIGN.md` describes a conceptual "Admin Navy (#1E293B) vs Student Blue (#3B82F6)" dual-brand scheme, but every mockup that was actually built (both student and admin screens) uses the Material 3 purple palette defined in the YAML frontmatter (`primary: #4f378a`, `surface: #fdf7ff`, etc.). **Treat the YAML frontmatter tokens as the single source of truth** for the Tailwind theme, since that's what's implemented pixel-for-pixel in every `code.html`. Keep the Admin Navy / Student Blue idea only as an optional `role` accent variant (e.g. a thin top-bar accent or badge color) layered on top of the shared purple system — do not replace the core palette with navy/blue.

Your job: stand up the architecture below, then port these eight screens into a real, working, API-backed web app — same layout, spacing, color tokens, and copy, but with live data, auth, and persistence instead of hardcoded HTML.

**This is a local-only build.** No cloud services, no external accounts, no API keys for third-party infra. Everything must run on the developer's machine with `docker compose up` (or equivalent) and nothing else.

---

## 1. Target Architecture (must match exactly)

```
React (Vite, TypeScript)  ──HTTP/JSON──>  FastAPI (Python)  ──asyncpg/SQLAlchemy──>  PostgreSQL (+ pgvector, pg_trgm)
                                               │
                                               └──local filesystem──>  backend/storage/ (files: PDFs, images, documents)
```

- **Frontend:** React + Vite + TypeScript + Tailwind (theme generated from `DESIGN.md`).
- **Backend:** FastAPI (Python 3.11+), single API serving the web client (and, later, an Android client — design endpoints to be client-agnostic, but do not build Android now).
- **Database:** PostgreSQL running locally (via Docker), as system of record for all relational data, including `JSONB` columns for flexible/semi-structured fields (e.g. AI insight payloads, timetable metadata).
- **Search:** `pgvector` for semantic/embedding search (e.g. "find similar assignments/announcements"), `pg_trgm` for fuzzy full-text search (e.g. document/student name search in Paperwork Manager and Student Activities).
- **File storage:** local filesystem only — a `backend/storage/` directory (gitignored), served back to the frontend through a FastAPI static/file route. Postgres stores only metadata + relative file paths, never file bytes. Structure it behind one `services/storage.py` module with `save_file()` / `get_file_url()` / `delete_file()` functions, so swapping in real object storage later (R2, S3, etc.) is a one-file change, not a rewrite — but do not build or configure any cloud provider now.
- **Auth:** Role-based (Student, Teacher/Proctor, Admin) — the "Switch Role" control seen in the admin mockups should map to a real role-permission system, not a fake toggle.

---

## 2. Repository Layout to Create

```
edusync-erp/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/          # config, security, db session
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── api/v1/        # routers: auth, users, school, attendance,
│   │   │                  #   assignments, exams, timetable, documents,
│   │   │                  #   activities, notifications, search
│   │   ├── services/      # business logic per module (incl. storage.py for local files)
│   │   └── db/            # session, migrations helpers
│   ├── alembic/           # migrations
│   ├── storage/           # gitignored - uploaded/generated files live here
│   ├── tests/
│   ├── pyproject.toml (or requirements.txt)
│   ├── Dockerfile
│   └── .env.example
├── web/
│   ├── src/
│   │   ├── app/           # routing, layout shells (student shell, admin shell)
│   │   ├── pages/          # one folder per mockup screen (see §4 mapping)
│   │   ├── components/     # shared UI (cards, chips, tables, stat tiles)
│   │   ├── theme/           # tailwind tokens generated from DESIGN.md
│   │   ├── lib/api/         # typed API client (fetch/axios + generated types)
│   │   └── stores/          # auth/session state
│   ├── index.html
│   ├── tailwind.config.ts
│   ├── vite.config.ts
│   └── .env.example
├── docs/
│   ├── ARCHITECTURE.md
│   └── mockups/            # copy of the original code.html + screen.png as reference, untouched
├── docker-compose.yml       # postgres(+pgvector), backend, web
└── README.md
```

Copy the original `stitch_edunexus_school_erp/` folder into `docs/mockups/` verbatim before doing anything else, so it remains a stable reference throughout the build.

---

## 3. Build Order (execute phases sequentially; each phase must run and pass its own checks before moving on)

### Phase 0 — Scaffolding
```bash
mkdir -p edusync-erp && cd edusync-erp
git init
mkdir -p docs/mockups && cp -r ../stitch_edunexus_school_erp/* docs/mockups/

# Backend scaffold
mkdir -p backend/app/{core,models,schemas,api/v1,services,db} backend/alembic backend/tests
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" sqlalchemy[asyncio] asyncpg alembic \
            pydantic-settings python-jose[cryptography] passlib[bcrypt] \
            pgvector python-multipart aiofiles pytest httpx
pip freeze > requirements.txt
cd ..

# Frontend scaffold
npm create vite@latest web -- --template react-ts
cd web
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install react-router-dom axios @tanstack/react-query recharts zustand
cd ..
```

### Phase 1 — Database & Backend Core
1. `docker-compose.yml`: use `pgvector/pgvector:pg16` image (not plain `postgres`) so the `vector` extension is available. Only two services needed: `db` and `backend` (plus `web` if you containerize the frontend — running it with `npm run dev` locally is also fine).
2. In `backend/app/core/config.py`, load env vars via `pydantic-settings` (DB URL, JWT secret, `STORAGE_DIR` path, defaulting to `./storage`).
3. On first migration, enable extensions:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   CREATE EXTENSION IF NOT EXISTS pg_trgm;
   ```
4. Set up Alembic (`alembic init alembic`), configure `env.py` to import your models' metadata for autogenerate.
5. Implement JWT auth (access + refresh tokens), password hashing with passlib, and a `role` enum (`student`, `teacher`, `admin`) plus a permissions dependency (`require_role(...)`) used to guard admin-only routers (Exam Management, Paperwork Manager, Student Activities, Timetable Builder).

### Phase 2 — Domain Models (map 1:1 to mockup screens)
Create SQLAlchemy models + Alembic migration per module. Suggested core tables:

- `users`, `roles`, `schools`, `classes` (grade/section) — backs "Users & Roles" + "School Management".
- `students` (profile fields, GPA, attendance %, class link) — backs Student Profile screen.
- `attendance_records` (student_id, date, status) — backs Attendance stat tile + "Attendance History".
- `assignments` (subject, title, due_at, status enum: pending/submitted/graded), `assignment_submissions` (file_path, grade) — backs Assignments screen + New Assignment action.
- `exams`, `exam_schedules` (subject, date, hall, proctor, status) — backs Exam Management table.
- `results`, `result_subject_scores` (marks, grade, status, class_rank, gpa) — backs Result Analysis screen (marksheet + chart).
- `timetable_slots` (grade, section, day, period_start, subject, classroom, teacher) — backs Timetable Builder grid; support bulk upsert for drag-and-drop saves.
- `documents` (name, subject/category, requestor_id, status enum: pending/processing/completed, file_path) — backs Paperwork Manager.
- `activities` / `clubs` (name, supervisor, next_date, capacity, enrolled_count), `activity_enrollments`, `activity_feed_events` — backs Student Activities dashboard.
- `notifications` / `announcements` (title, body, audience, published_at) — backs the "Important Update" banner and bell icon.
- `ai_insights` (student_id, insight_text, kind, JSONB payload) — backs the "AI Performance Insight" panel; keep this table generic (JSONB) so insight-generation logic can evolve independently of schema.

Every table with a name/description field the UI needs to search or filter (documents, students, activities) should have a `pg_trgm` GIN index; every table intended for "similar item" recommendations (assignments, announcements) should have a `pgvector` embedding column.

### Phase 3 — API Endpoints
Build one FastAPI router per module under `api/v1/`, each with standard REST verbs plus the specific reads the mockups need, e.g.:
- `GET /students/{id}/dashboard` → aggregated payload for the Student Dashboard screen (events, announcement, progress summary) in one call — avoid making the frontend stitch together 5 requests for one screen.
- `GET /students/{id}/assignments?status=pending|submitted|graded`
- `GET /results/{id}?exam_id=` → marksheet + chart data
- `GET /exams` (admin), `POST /exams`, `PATCH /exams/{id}`
- `GET /documents`, `POST /documents/upload` (multipart → save to `backend/storage/`, persist metadata), `PATCH /documents/{id}/status`
- `GET /activities/dashboard` (admin) → upcoming + top-performing + feed in one call
- `GET /timetable?grade=&section=`, `PUT /timetable` (bulk save of the whole grid)
- `GET /search?q=&scope=documents|students|assignments` → uses `pg_trgm` for text, `pgvector` for "similar to this item" if `mode=similar`
- `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`

Every file-producing/consuming endpoint (assignment submissions, document uploads, result/marksheet download, activity photos) must go through the `services/storage.py` module, which writes into `backend/storage/<module>/<uuid>-<filename>` and serves reads back via a FastAPI static file route (e.g. `/files/{path}`), returning that URL in API responses rather than raw bytes inline.

### Phase 4 — Frontend
1. Generate `web/src/theme/tokens.ts` and `tailwind.config.ts` directly from the `DESIGN.md` YAML frontmatter (colors, typography, spacing, radii) — don't hand-retype values, parse the frontmatter once and keep it as the single source of truth so the palette can't drift from the mockups.
2. Build two layout shells matching the mockups: a **student shell** (top bar + bottom nav: Home/Schedule/Tasks/Profile) and an **admin shell** (left sidebar: Academic/Admin/Exams/Info/Archives + "Switch Role" + "Quick Upload").
3. Recreate each of the 8 screens as a route + page component, wired to the corresponding API endpoint(s) from Phase 3, preserving structure (cards, chips/status tags, stat tiles, tables) and copy from the mockup. Use `@tanstack/react-query` for data fetching/caching, `recharts` for the progress/marksheet/subject-vs-average charts, and native HTML5 drag-and-drop (or `dnd-kit`) for the Timetable Builder grid.
4. Status chips (Pending/Submitted/Graded, Scheduled, Completed/Processing/Pending) must reuse one shared `<StatusChip>` component with a status→color map, not per-page hardcoded classes.
5. Auth-gate routes by role: student routes require `role=student`; admin/exam/paperwork/activities/timetable routes require `role in (teacher, admin)`.

### Phase 5 — Search & AI Insight Wiring
- Implement the `pg_trgm` search endpoint and hook it into the search icon present in every top bar.
- Implement the `pgvector` similarity path (even a simple version: store embeddings for assignments/announcements, expose a "related items" query) — this can call any embedding model you have access to; keep the embedding call isolated behind one service function so the model can be swapped later.
- `ai_insights` rows should be generated by a service function (`services/insights.py`) callable on a schedule or on-demand; the endpoint backing the Profile screen just reads the latest stored insight — don't compute insights synchronously in the request path.

### Phase 6 — Ops
- `docker-compose.yml` should bring up `db` (pgvector image), `backend`, `web` with one command and healthchecks.
- Write `backend/tests/` covering auth, one CRUD module, and the search endpoint at minimum.
- `.env.example` in both `backend/` and `web/` listing every required variable (DB URL, JWT secret, `STORAGE_DIR`, API base URL). No cloud credentials of any kind.
- `README.md` at repo root: setup steps, `docker compose up`, how to run migrations (`alembic upgrade head`), how to seed demo data (write a `backend/scripts/seed.py` that creates one school, one admin, a few students/classes, and enough rows in every table to make all 8 screens render non-empty).

---

## 4. Screen → Route → Primary Endpoint Map

| Mockup | Route | Role | Primary endpoint |
|---|---|---|---|
| student_dashboard_high_fidelity | `/` | student | `GET /students/{id}/dashboard` |
| student_assignments_high_fidelity | `/assignments` | student | `GET /students/{id}/assignments` |
| student_profile_insights_high_fidelity | `/profile` | student | `GET /students/{id}/profile`, `GET /students/{id}/insights` |
| student_result_analysis_high_fidelity | `/results/:examId` | student | `GET /results/{studentId}?exam_id=` |
| wireframe_exam_management | `/admin/exams` | teacher/admin | `GET/POST /exams` |
| wireframe_paperwork_manager | `/admin/documents` | teacher/admin | `GET /documents`, `POST /documents/upload` |
| wireframe_student_activities | `/admin/activities` | teacher/admin | `GET /activities/dashboard` |
| wireframe_timetable_builder | `/admin/timetable` | teacher/admin | `GET/PUT /timetable` |

---

## 5. Acceptance Criteria

For each of the 8 screens, the ported version must:
- [ ] Match the mockup's layout, spacing, and color tokens (use `docs/mockups/.../screen.png` as the visual reference, `code.html` as the structural reference).
- [ ] Load real data from Postgres via the FastAPI endpoint — no hardcoded arrays in the component.
- [ ] Handle loading and empty states (the mockups show static demo data; your version must degrade gracefully to a real "no assignments yet" state).
- [ ] Respect role-based access (student pages 404/redirect for non-students, admin pages for non-staff).
- [ ] File actions (submit assignment, upload/download document) actually round-trip through `backend/storage/` on the local filesystem, with metadata persisted in Postgres.

Overall system:
- [ ] Runs fully offline/locally — `docker compose up` (db + backend, and web if containerized) with no manual steps beyond `.env` creation and `alembic upgrade head` + seed script. No signup, API key, or external network call required to use the app.
- [ ] `vector` and `pg_trgm` extensions are enabled via migration, not manually.
- [ ] Search bar in the top nav returns real fuzzy results from at least one module (documents or students).
- [ ] No screen makes more than 2 network calls to render (aggregate endpoints, not N+1 chatty calls).

---

## 6. Explicit Constraints

- Do not introduce a second frontend framework or a different backend language — React/Vite/TS and FastAPI/Python only, per the architecture.
- Do not use any cloud service, SaaS, or third-party hosted infra (no S3/R2/GCS, no hosted Postgres, no hosted auth/email providers). Everything runs in Docker/locally on the developer's machine.
- Do not store files in Postgres as BLOBs — local filesystem under `backend/storage/` only; Postgres holds paths/metadata.
- Do not fabricate an Admin Navy/Student Blue two-tone theme that contradicts the actual mockup colors — follow the resolution in §0.
- Do not skip Alembic migrations and hand-edit the DB schema.
- Do not build the Android app in this pass — design the API to be client-agnostic (versioned `/api/v1/...`, JSON, token auth) so it's ready for Kotlin/Compose later, but scope this task to backend + web only.
- Keep the storage layer isolated behind `services/storage.py` so that if cloud storage is wanted later, it's a contained swap — but do not build, configure, or stub any cloud provider now.

---

## 7. Working Process

Work phase by phase per §3. After each phase, run and show: the relevant `pytest`/`npm run build` output, and a short note on what was implemented and what's deferred. Keep a running `docs/PROGRESS.md` log (phase, date, status, open issues) so the work is auditable.
