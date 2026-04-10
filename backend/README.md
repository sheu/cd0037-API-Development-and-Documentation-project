# Backend - Trivia API

## Setup

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- PostgreSQL client tools are optional if you use the Docker commands below

### Install Python Dependencies

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Configure Environment Variables

The backend reads database configuration from environment variables.

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

### Start PostgreSQL

From the `backend` directory:

```bash
docker compose up -d postgres
```

### Create and Seed the Database

Create the application database and load the provided SQL dump:

```bash
docker exec -i postgres psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE trivia;"
docker exec -i postgres psql -U "$POSTGRES_USER" -d trivia < trivia.psql
```

If the dump references the `student` role, create it once before importing:

```bash
docker exec -i postgres psql -U "$POSTGRES_USER" -d postgres -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'student') THEN CREATE ROLE student; END IF; END \$\$;"
```

### Run the Development Server

From the `backend` directory:

```bash
PYTHONPATH=$PWD FLASK_APP=flaskr flask run --reload
```

The API will be available at `http://127.0.0.1:5000`.

## API Endpoints

### GET `/categories`

- Request parameters: None
- Response body:

```json
{
  "success": true,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

### GET `/questions?page=<page-number>`

- Request parameters:
  - `page`: integer, optional, defaults to `1`
- Response body:

```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "What is the heaviest organ in the human body?",
      "answer": "The Liver",
      "category": "1",
      "difficulty": 4
    }
  ],
  "total_questions": 19,
  "current_category": null,
  "categories": {
    "1": "Science",
    "2": "Art"
  }
}
```

### DELETE `/questions/<question_id>`

- Request parameters:
  - `question_id`: integer path parameter
- Response body:

```json
{
  "success": true,
  "deleted": 10
}
```

### PUT `/questions/<question_id>`

- Request parameters:
  - `question_id`: integer path parameter
- Request body: any combination of `question`, `answer`, `category`, and `difficulty`
- Response body:

```json
{
  "success": true,
  "updated": 10,
  "question": {
    "id": 10,
    "question": "Updated prompt?",
    "answer": "Updated answer",
    "category": "1",
    "difficulty": 5
  }
}
```

### POST `/questions`

Creates a question when the request body includes `question`, `answer`, `category`, and `difficulty`.

- Request body:

```json
{
  "question": "What is 2 + 2?",
  "answer": "4",
  "category": "1",
  "difficulty": 1
}
```

- Response body:

```json
{
  "success": true,
  "created": 25
}
```

Searches questions when the request body includes `searchTerm`.

- Request body:

```json
{
  "searchTerm": "title"
}
```

- Response body:

```json
{
  "success": true,
  "questions": [
    {
      "id": 5,
      "question": "Whose autobiography is titled 'I Know Why the Caged Bird Sings'?",
      "answer": "Maya Angelou",
      "category": "4",
      "difficulty": 2
    }
  ],
  "total_questions": 1,
  "current_category": null
}
```

### GET `/categories/<category_id>/questions`

- Request parameters:
  - `category_id`: integer path parameter
- Response body:

```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "What is the heaviest organ in the human body?",
      "answer": "The Liver",
      "category": "1",
      "difficulty": 4
    }
  ],
  "total_questions": 4,
  "current_category": "Science"
}
```

### POST `/quizzes`

- Request body:

```json
{
  "previous_questions": [1, 4, 20],
  "quiz_category": {
    "id": 1,
    "type": "Science"
  }
}
```

- Response body:

```json
{
  "success": true,
  "question": {
    "id": 7,
    "question": "What is the largest lake in Africa?",
    "answer": "Victoria Lake",
    "category": "1",
    "difficulty": 2
  }
}
```

When no questions remain for the chosen quiz scope, `question` is returned as `null`.

## Error Responses

Errors are returned in a consistent JSON format.

```json
{
  "success": false,
  "error": 404,
  "message": "resource not found"
}
```

Implemented handlers:

- `400 bad request`
- `404 resource not found`
- `405 method not allowed`
- `422 unprocessable`
- `500 internal server error`

## Tests

The test suite uses `unittest` and covers success and error behavior for each implemented endpoint.

Create the test database once:

```bash
docker exec -i postgres psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE trivia_test;"
```

Run the tests:

```bash
cd backend
python -m unittest test_flaskr.py
```
