# Build progress

| Phase | Status | Notes |
|---|---|---|
| Frontend scaffold | Complete | React/Vite/TypeScript screens and responsive shells implemented. |
| Frontend structure | Complete | `web/src` split into app, components, pages, services, data, styles, and types. |
| Backend API boundary | In progress | FastAPI app, versioned routes, upload storage, Docker/PostgreSQL scaffold added. |
| Database models/migrations | Complete | SQLAlchemy 2 models, async session, Alembic initial migration, and seed script added. |
| Auth and permissions | Complete | Real password verification, JWT decoding, admin teacher grants, runtime permission checks, and student/teacher scope checks added. |
| Database-backed screen reads | In progress | Student, assignments, results, exams, documents, activities, and timetable reads now query the database; write workflows remain to be completed. |
