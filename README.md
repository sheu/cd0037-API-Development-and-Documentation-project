# Trivia API Project

Full-stack trivia application built with Flask, SQLAlchemy, PostgreSQL, and React. The backend exposes a REST API for listing questions, filtering by category, searching, creating and deleting questions, and serving quiz questions. The frontend consumes that API through the browser.

## Tech Stack

- Backend: Flask, SQLAlchemy, Flask-CORS, PostgreSQL
- Frontend: React, jQuery, Create React App
- Testing: `unittest`
- Local database: Docker Compose with Postgres 16

## Project Structure

- [backend](./backend/README.md): Flask API, database models, tests, and Docker Compose
- [frontend](./frontend/README.md): React client application

## Environment Variables

Database credentials are read from environment variables instead of being hard-coded in application code.

Example values:

```bash
export POSTGRES_USER=myuser
export POSTGRES_PASSWORD=mypassword
export POSTGRES_DB=mydb
export POSTGRES_PORT=5432

export TRIVIA_DB_NAME=trivia
export TRIVIA_DB_USER=myuser
export TRIVIA_DB_PASSWORD=mypassword
export TRIVIA_DB_HOST=localhost
export TRIVIA_DB_PORT=5432
export TRIVIA_TEST_DB_NAME=trivia_test
```

You can put these values in a local `.env` file for your shell tooling if you prefer. `.env` is ignored by git.

## Quick Start

1. Start Postgres:

```bash
cd backend
docker compose up -d postgres
```

2. Create and seed the application database:

```bash
docker exec -i postgres psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE trivia;"
docker exec -i postgres psql -U "$POSTGRES_USER" -d trivia < trivia.psql
```

3. Install backend dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

4. Start the Flask API:

```bash
cd backend
PYTHONPATH=$PWD FLASK_APP=flaskr flask run --reload
```

5. Install frontend dependencies and start React:

```bash
cd frontend
npm install
NODE_OPTIONS=--openssl-legacy-provider npm start
```

6. Open the app at `http://127.0.0.1:3000`.

## Tests

Run the backend test suite:

```bash
cd backend
python -m unittest test_flaskr.py
```

## API Documentation

Detailed endpoint documentation is in [backend/README.md](./backend/README.md).
