# Simple Task Management REST API

A simple REST API for task management built with Flask. This API uses an in-memory cache as a database for demonstration purposes.

## Features

- Create, read, update, and delete tasks
- Search tasks by status
- Get task statistics

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/tasks | Get all tasks |
| GET | /api/tasks/:id | Get a specific task |
| POST | /api/tasks | Create a new task |
| PUT | /api/tasks/:id | Update a task |
| DELETE | /api/tasks/:id | Delete a task |
| GET | /api/tasks/search?status=:status | Search tasks by status |
| GET | /api/stats | Get task statistics |

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`

## Task Structure

```json
{
  "id": "uuid-string",
  "title": "Task title",
  "description": "Task description",
  "status": "pending|in_progress|completed",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp"
}
```

## Sample Usage

### Create a task
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "New task", "description": "Task description", "status": "pending"}'
```

### Get all tasks
```bash
curl http://localhost:5000/api/tasks
```

### Search tasks by status
```bash
curl http://localhost:5000/api/tasks/search?status=completed
```
