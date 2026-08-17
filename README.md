# Edumin

Edumin is a school ERP web application for administrators, teachers, and students. It centralizes daily academic workflows such as student account management, timetable planning, attendance, documents, activities, exams, and results in one local, containerized application.

## Implemented features

- Role-based sign-in for administrator, teacher, and student accounts.
- Admin teacher management with explicit, revocable permissions.
- Teacher student management: teachers granted `manage_students` can create student credentials, choose a class, and assign a roll number and student code.
- Five seeded grade/section classes and ten seeded students created under the demo teacher account.
- Student profile, contact details, document upload, timetable, attendance, assignments, results, and dashboard views.
- Teacher/admin workspaces for exams, paperwork, activities, timetable setup, timetable editing, attendance, and student management.
- Drag-and-drop timetable builder with slot highlighting, manual placement, clear/save actions, class configuration, subject workloads, and teacher assignment.
- Server-generated timetable recommendations with clash detection and warnings.
- NFC attendance APIs for linking a card UID to a student, recording scans, updating same-day attendance, and calculating attendance percentages.
- Document upload for PDF, PNG, JPG, and JPEG files; OCR extraction; sanitized HTML output; and digitized PDF export.
- Student timetable-change notifications in the navigation bell.
- PostgreSQL persistence, Alembic schema migrations, demo data seeding, Docker-based local setup, and FastAPI interactive API documentation.

## Future scope

### RFID/NFC attendance rollout

The RFID/NFC data model and backend attendance flow are already implemented. Each card UID is mapped to a student, and a scan creates or updates that student’s attendance record for the current day. The next practical step is connecting a physical NFC/RFID reader or a school-controlled scanning device to the `/api/v1/attendance/scan` endpoint.

### Mobile application

A mobile application is the planned next client. It will make attendance and class-related actions accessible when teachers are away from their laptops. A teacher could scan a student card, review a class list, create a student credential, check timetable changes, or record essential class activity directly from a phone. The current FastAPI API, PostgreSQL schema, role model, and token-based access design provide a reusable backend foundation for that mobile client.

### Additional improvements

- Re-enable mandatory JWT authentication for deployed environments by setting `AUTH_DISABLED` to `false`.
- Add live device registration, offline scan queueing, and audit trails for physical attendance devices.
- Add automated tests for OCR, timetable constraints, teacher permission changes, and student data scope rules.
- Add cloud storage, production secrets management, monitoring, backups, and deployment automation.

## Core models and algorithms

### Timetable recommendation engine

The timetable feature uses a deterministic constraint-based scheduling heuristic rather than a machine-learning model. It works from each class's subjects, assigned teachers, and requested weekly periods.

For every subject, the algorithm:

1. Prioritizes subjects with the most unplaced periods.
2. Evaluates every weekday and period slot.
3. Rejects an occupied class slot or a slot where the assigned teacher is already teaching another class.
4. Scores valid candidates to spread a subject across days, avoid adjacent repeats where possible, balance teacher daily load, and favor earlier periods when tied.
5. Saves warnings when requested workload exceeds capacity or a period cannot be placed without a clash.

The result is a transparent and repeatable starting timetable. Teachers can then refine it through the drag-and-drop interface and save the final schedule.

### OCR and document digitization

The OCR pipeline accepts PDFs and image files. PDFs are converted to page images with Poppler/pdf2image; image files are sent directly. Each page is submitted to the configured Gemini vision model with a strict transcription prompt and a JSON response schema. The prompt requests faithful text and visible structure, including headings, lists, and tables, rather than summary or correction.

OCR output is stored as structured JSON in PostgreSQL, sanitized before it is shown as HTML, and can be exported as a digitized PDF. The upload route runs OCR in a worker thread with a 45-second timeout, records a failed status and error message if processing cannot complete, and keeps the original document metadata for review.

### Access and school data models

The backend models users, roles, permissions, teacher profiles, student profiles, classes, subjects, timetable slots, RFID cards, attendance records, documents, activities, exams, results, assignments, and notifications.

Administrators have full access. Teachers receive only explicitly granted permissions, and a teacher with `manage_students` can create student accounts. Student and teacher access checks are designed around the student identity, teacher subjects, and assigned classes to avoid exposing school-wide data by default.

## Technology stack

| Layer | Technology | Usage |
| --- | --- | --- |
| Frontend | React, TypeScript, Vite | Responsive web application, routes, screens, local state, drag-and-drop interactions |
| Styling | CSS, Material Symbols, Inter | Shared design system and accessible UI elements |
| Backend | Python, FastAPI, Uvicorn | REST API, validation, role checks, OCR and attendance endpoints |
| Database | PostgreSQL 16 with pgvector image | Persistent ERP data and future-ready vector extension |
| ORM and migrations | SQLAlchemy async, AsyncPG, Alembic | Async persistence, relational models, schema versioning |
| Authentication | JWT, python-jose, Passlib/bcrypt | Login tokens, role-aware access, teacher permission enforcement |
| OCR | Gemini vision API, pdf2image, Poppler, Bleach, ReportLab | Document transcription, safe HTML display, digitized PDF export |
| Attendance | RFID/NFC UID mapping | Card-to-student mapping and scan-based attendance records |
| Local platform | Docker Compose | Reproducible API and PostgreSQL environment |

## How the project is implemented

The React application in `web/` calls the versioned FastAPI API under `/api/v1`. The Vite development server proxies API requests to the backend. FastAPI uses async SQLAlchemy sessions to read and write PostgreSQL, while Alembic keeps the database schema aligned with the application models.

Role and permission checks are implemented at the API dependency layer. Administrators can manage teachers and permissions; teachers work only with their assigned capabilities; students use self-service endpoints for their own profile and documents. The seed script creates the demo accounts, classes, subjects, timetable data, NFC cards, and attendance history needed to explore the application.

For local feature testing, `docker-compose.yml` currently sets `AUTH_DISABLED=true`, which lets protected API routes use the seeded admin account when no bearer token is supplied. This must be disabled outside local development.

## Run locally

### 1. Start the backend and database

From the repository root:

```powershell
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m scripts.seed
```

The API runs at `http://localhost:8000` and its interactive documentation is available at `http://localhost:8000/docs`.

### 2. Start the frontend

```powershell
cd web
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

### Demo credentials

```text
Administrator
admin@edusync.local
Admin@123

Teacher
teacher@edusync.local
Teacher@123

Student
student@edusync.local
Student@123
```

All seeded student accounts use `Student@123` as their password.

## Project structure

```text
backend/
├── alembic/                 # Schema migrations
├── app/
│   ├── api/v1/routes/       # FastAPI feature endpoints
│   ├── core/                # Configuration, security, access dependencies
│   ├── models/              # SQLAlchemy models
│   └── services/            # OCR, timetable, notifications, storage
└── scripts/seed.py          # Demo school data

web/
└── src/
    ├── app/                 # Client routing and application shell
    ├── components/          # Shared UI, layouts, notification bell
    ├── pages/               # Student, admin, and teacher-facing pages
    ├── services/api/        # Typed API client modules
    ├── stores/              # Timetable state management
    └── styles/              # Global and feature styles
```
