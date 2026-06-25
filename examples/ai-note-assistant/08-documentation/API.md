# AI Note Assistant API Documentation

Base URL: `http://localhost:8000`

---

## Authentication

All endpoints require a `user_id` parameter. In production, this will be replaced with JWT authentication.

---

## Endpoints

### Create Note

Create a new note with AI-generated summary and tags.

```http
POST /api/notes
Content-Type: application/json

{
  "content": "Your note content here...",
  "user_id": "user-123"
}
```

**Response:**

```json
{
  "id": "1",
  "content": "Your note content here...",
  "summary": "AI-generated summary",
  "tags": ["tag1", "tag2", "tag3"],
  "created_at": "2026-06-21T10:00:00Z"
}
```

### List Notes

Get all notes for a user.

```http
GET /api/notes?user_id=user-123
```

**Response:**

```json
[
  {
    "id": "1",
    "content": "Note content",
    "summary": "Summary",
    "tags": ["tag1"],
    "created_at": "2026-06-21T10:00:00Z"
  }
]
```

### Search Notes

Semantic search through notes.

```http
POST /api/notes/search
Content-Type: application/json

{
  "query": "about artificial intelligence",
  "user_id": "user-123"
}
```

**Response:**

```json
{
  "results": [
    {
      "id": "1",
      "content": "AI is transforming...",
      "summary": "AI transformation",
      "tags": ["ai", "tech"],
      "created_at": "2026-06-21T10:00:00Z"
    }
  ]
}
```

---

## Error Codes

| Status | Code | Description |
|--------|------|-------------|
| 400 | INVALID_REQUEST | Missing required fields |
| 500 | AI_PROCESSING_ERROR | OpenAI API failure |
| 500 | SEARCH_ERROR | Embedding generation failed |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-21 | Initial release with create, list, search |
