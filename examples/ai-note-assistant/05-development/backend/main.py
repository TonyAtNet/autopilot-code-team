from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import openai
import os

app = FastAPI(title="AI Note Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

# In-memory storage for demo (replace with PostgreSQL in production)
notes_db = []

class NoteCreate(BaseModel):
    content: str
    user_id: str

class NoteResponse(BaseModel):
    id: str
    content: str
    summary: str
    tags: List[str]
    created_at: str

class SearchRequest(BaseModel):
    query: str
    user_id: str

@app.post("/api/notes", response_model=NoteResponse)
async def create_note(note: NoteCreate):
    """
    Create a new note with AI-generated summary and tags.
    """
    try:
        # Generate summary and tags using OpenAI
        response = await openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes notes and extracts tags. "
                               "Respond in JSON format: {\"summary\": \"...\", \"tags\": [\"tag1\", \"tag2\"]}"
                },
                {
                    "role": "user",
                    "content": f"Summarize this note and extract 3-5 relevant tags:\n\n{note.content}"
                }
            ],
            response_format={"type": "json_object"}
        )
        
        result = eval(response.choices[0].message.content)
        
        note_id = str(len(notes_db) + 1)
        new_note = {
            "id": note_id,
            "content": note.content,
            "summary": result.get("summary", ""),
            "tags": result.get("tags", []),
            "user_id": note.user_id,
            "created_at": "2026-06-21T10:00:00Z"
        }
        notes_db.append(new_note)
        
        return NoteResponse(
            id=note_id,
            content=new_note["content"],
            summary=new_note["summary"],
            tags=new_note["tags"],
            created_at=new_note["created_at"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")

@app.get("/api/notes", response_model=List[NoteResponse])
async def list_notes(user_id: str):
    """
    List all notes for a user.
    """
    user_notes = [n for n in notes_db if n["user_id"] == user_id]
    return [
        NoteResponse(
            id=n["id"],
            content=n["content"],
            summary=n["summary"],
            tags=n["tags"],
            created_at=n["created_at"]
        )
        for n in sorted(user_notes, key=lambda x: x["created_at"], reverse=True)
    ]

@app.post("/api/notes/search")
async def search_notes(request: SearchRequest):
    """
    Semantic search through notes using OpenAI embeddings.
    """
    try:
        # Generate embedding for query
        query_embedding = await openai.embeddings.create(
            model="text-embedding-3-small",
            input=request.query
        )
        
        # In production, use pgvector for cosine similarity search
        # For demo, return simple keyword matching
        user_notes = [n for n in notes_db if n["user_id"] == request.user_id]
        query_lower = request.query.lower()
        
        results = []
        for note in user_notes:
            score = 0
            if query_lower in note["content"].lower():
                score += 3
            if any(query_lower in tag.lower() for tag in note["tags"]):
                score += 2
            if query_lower in note["summary"].lower():
                score += 1
            
            if score > 0:
                results.append({
                    "note": NoteResponse(
                        id=note["id"],
                        content=note["content"],
                        summary=note["summary"],
                        tags=note["tags"],
                        created_at=note["created_at"]
                    ),
                    "score": score
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return {"results": [r["note"] for r in results[:10]]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ai-note-assistant"}
