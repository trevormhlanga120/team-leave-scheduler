# Team Leave Scheduler

A small internal HR tool for viewing team leave over the next 30 days, submitting
leave requests, and approving or rejecting pending requests.

## Stack

- Backend: FastAPI, SQLAlchemy, SQLite
- Frontend: React and Vite
- Tests: pytest

## Project Structure

- `backend/` - API, business rules, seed data, and tests
- `frontend/` - React app
- `DECISIONS.md` - business-rule decisions and alternatives
- `AI_USAGE.md` - AI tools and prompts used during development

## Backend Setup

From the repository root:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

On startup, the app creates a SQLite database and seeds it from:

- `backend/data/employees.csv`
- `backend/data/public_holidays.json`

## Frontend Setup

Open a second terminal from the repository root:

```bash
cd frontend
npm install
npm run dev
```

The UI runs at the Vite URL shown in the terminal, usually
`http://localhost:5173`.

## Tests and Checks

Backend tests:

```bash
cd backend
source venv/bin/activate
pytest -q
```

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

## API Endpoints

- `GET /leave/?days=30` - list requests overlapping the next 30 days
- `POST /leave/` - submit a leave request
- `PUT /leave/{request_id}/approve` - approve a pending request
- `PUT /leave/{request_id}/reject` - reject a pending request
- `GET /employees/` - list employees for the request form

## Business Rule Summary

- The 30% team cap rounds down.
- The cap is checked per working day.
- Weekends and public holidays are ignored for cap calculations.
- Overlap is checked against approved requests for the same employee.
- Approval re-checks overlap and team capacity before changing status.
