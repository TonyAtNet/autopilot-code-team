import pytest
from fastapi.testclient import TestClient
from main import app, notes_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_notes():
    """Clear notes database before each test."""
    notes_db.clear()

class TestNoteCreation:
    def test_create_note_success(self, monkeypatch):
        """Test successful note creation with AI-generated summary and tags."""
        
        class MockResponse:
            class Choice:
                class Message:
                    content = '{"summary": "Test summary", "tags": ["test", "demo"]}'
                message = Message()
            choices = [Choice()]
        
        monkeypatch.setattr(
            "openai.resources.chat.completions.Completions.create",
            lambda *args, **kwargs: MockResponse()
        )
        
        response = client.post("/api/notes", json={
            "content": "This is a test note about AI and machine learning.",
            "user_id": "user-123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "Test summary"
        assert "test" in data["tags"]
        assert data["content"] == "This is a test note about AI and machine learning."
    
    def test_create_note_empty_content(self):
        """Test note creation with empty content fails."""
        response = client.post("/api/notes", json={
            "content": "",
            "user_id": "user-123"
        })
        assert response.status_code == 422
    
    def test_create_note_missing_user_id(self):
        """Test note creation without user_id fails."""
        response = client.post("/api/notes", json={
            "content": "Test content"
        })
        assert response.status_code == 422

class TestNoteListing:
    def test_list_notes_empty(self):
        """Test listing notes when no notes exist."""
        response = client.get("/api/notes?user_id=user-123")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_notes_returns_user_notes(self, monkeypatch):
        """Test that only user's notes are returned."""
        
        class MockResponse:
            class Choice:
                class Message:
                    content = '{"summary": "Summary", "tags": ["tag"]}'
                message = Message()
            choices = [Choice()]
        
        monkeypatch.setattr(
            "openai.resources.chat.completions.Completions.create",
            lambda *args, **kwargs: MockResponse()
        )
        
        # Create note for user-123
        client.post("/api/notes", json={"content": "User 123 note", "user_id": "user-123"})
        
        response = client.get("/api/notes?user_id=user-123")
        assert response.status_code == 200
        assert len(response.json()) == 1

class TestNoteSearch:
    def test_search_by_keyword(self, monkeypatch):
        """Test keyword-based note search."""
        
        class MockResponse:
            class Choice:
                class Message:
                    content = '{"summary": "AI summary", "tags": ["ai", "tech"]}'
                message = Message()
            choices = [Choice()]
        
        monkeypatch.setattr(
            "openai.resources.chat.completions.Completions.create",
            lambda *args, **kwargs: MockResponse()
        )
        
        client.post("/api/notes", json={
            "content": "Artificial intelligence is transforming the world.",
            "user_id": "user-123"
        })
        
        response = client.post("/api/notes/search", json={
            "query": "artificial intelligence",
            "user_id": "user-123"
        })
        
        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) > 0

class TestHealth:
    def test_health_check(self):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
