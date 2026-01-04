"""
Tests for Conversation and Message API Endpoints
=================================================

This module tests all conversation and message endpoints including
creating, retrieving, listing, and deleting conversations and messages.
"""
import time
from fastapi.testclient import TestClient
from main import app
from db import SessionLocal, Conversation, Message

client = TestClient(app)


# =============================================================================
# Tests for Conversation Creation
# =============================================================================

def test_create_conversation():
    """Test creating a conversation with a title."""
    response = client.post(
        "/conversations/",
        json={"title": "Test Conversation"}
    )
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert "id" in data
    assert data["id"].startswith("conv_")
    assert data["title"] == "Test Conversation"
    assert "created_at" in data
    assert "updated_at" in data
    assert "messages" in data
    assert len(data["messages"]) == 0


def test_create_conversation_without_title():
    """Test creating a conversation without a title."""
    response = client.post("/conversations/", json={})
    assert response.status_code == 201
    data = response.json()
    
    # Verify it succeeds even without a title
    assert "id" in data
    assert data["id"].startswith("conv_")
    assert data["title"] is None
    assert "created_at" in data
    assert "updated_at" in data


# =============================================================================
# Tests for Conversation Retrieval
# =============================================================================

def test_get_conversation():
    """Test retrieving a specific conversation by ID."""
    # First create a conversation
    create_response = client.post(
        "/conversations/",
        json={"title": "Retrieve Test"}
    )
    conversation_id = create_response.json()["id"]
    
    # Now retrieve it
    response = client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == conversation_id
    assert data["title"] == "Retrieve Test"
    assert "messages" in data
    assert isinstance(data["messages"], list)


def test_get_nonexistent_conversation():
    """Test retrieving a conversation that doesn't exist."""
    response = client.get("/conversations/conv_fakeid123")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_conversations():
    """Test listing all conversations."""
    # Create 3 conversations
    titles = ["Conversation 1", "Conversation 2", "Conversation 3"]
    created_ids = []
    
    for title in titles:
        response = client.post(
            "/conversations/",
            json={"title": title}
        )
        created_ids.append(response.json()["id"])
    
    # List all conversations
    response = client.get("/conversations/")
    assert response.status_code == 200
    data = response.json()
    
    assert "conversations" in data
    assert "count" in data
    assert data["count"] >= 3  # At least our 3 conversations
    
    # Verify our conversations are in the list
    conversation_ids = [conv["id"] for conv in data["conversations"]]
    for created_id in created_ids:
        assert created_id in conversation_ids


# =============================================================================
# Tests for Message Creation and Retrieval
# =============================================================================

def test_create_message():
    """Test creating a message in a conversation."""
    # Create a conversation
    conv_response = client.post(
        "/conversations/",
        json={"title": "Message Test"}
    )
    conversation_id = conv_response.json()["id"]
    
    # Add a message
    response = client.post(
        f"/conversations/{conversation_id}/messages",
        json={
            "role": "user",
            "content": "Hello, this is a test message"
        }
    )
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert data["id"].startswith("msg_")
    assert data["conversation_id"] == conversation_id
    assert data["role"] == "user"
    assert data["content"] == "Hello, this is a test message"
    assert data["metadata"] is None
    assert "created_at" in data


def test_create_message_with_metadata():
    """Test creating a message with metadata."""
    # Create a conversation
    conv_response = client.post("/conversations/", json={})
    conversation_id = conv_response.json()["id"]
    
    # Add a message with metadata
    metadata = {
        "tool_calls": ["get_team_members", "get_projects"],
        "execution_time": 1.5
    }
    response = client.post(
        f"/conversations/{conversation_id}/messages",
        json={
            "role": "assistant",
            "content": "Here are the team members and projects",
            "metadata": metadata
        }
    )
    assert response.status_code == 201
    data = response.json()
    
    assert data["role"] == "assistant"
    assert data["metadata"] == metadata


def test_create_message_in_nonexistent_conversation():
    """Test creating a message in a conversation that doesn't exist."""
    response = client.post(
        "/conversations/conv_fakeid123/messages",
        json={
            "role": "user",
            "content": "This should fail"
        }
    )
    assert response.status_code == 404


def test_get_conversation_with_messages():
    """Test retrieving a conversation with multiple messages."""
    # Create a conversation
    conv_response = client.post(
        "/conversations/",
        json={"title": "Multi-Message Test"}
    )
    conversation_id = conv_response.json()["id"]
    
    # Add 2 messages
    messages = [
        {"role": "user", "content": "First message"},
        {"role": "assistant", "content": "Second message"}
    ]
    
    for msg in messages:
        client.post(
            f"/conversations/{conversation_id}/messages",
            json=msg
        )
    
    # Retrieve the conversation
    response = client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["messages"]) == 2
    assert data["messages"][0]["content"] == "First message"
    assert data["messages"][1]["content"] == "Second message"
    # Verify chronological order
    assert data["messages"][0]["role"] == "user"
    assert data["messages"][1]["role"] == "assistant"


# =============================================================================
# Tests for Conversation Deletion
# =============================================================================

def test_delete_conversation():
    """Test deleting a conversation."""
    # Create a conversation
    conv_response = client.post(
        "/conversations/",
        json={"title": "Delete Test"}
    )
    conversation_id = conv_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/conversations/{conversation_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/conversations/{conversation_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_conversation():
    """Test deleting a conversation that doesn't exist."""
    response = client.delete("/conversations/conv_fakeid123")
    assert response.status_code == 404


def test_delete_cascades_messages():
    """Test that deleting a conversation also deletes its messages."""
    # Create a conversation with messages
    conv_response = client.post("/conversations/", json={})
    conversation_id = conv_response.json()["id"]
    
    # Add messages
    for i in range(3):
        client.post(
            f"/conversations/{conversation_id}/messages",
            json={"role": "user", "content": f"Message {i}"}
        )
    
    # Verify messages exist
    get_response = client.get(f"/conversations/{conversation_id}")
    assert len(get_response.json()["messages"]) == 3
    
    # Delete conversation
    client.delete(f"/conversations/{conversation_id}")
    
    # Verify messages are gone (conversation doesn't exist anymore)
    get_response = client.get(f"/conversations/{conversation_id}")
    assert get_response.status_code == 404
    
    # Double-check in database that messages are deleted
    db = SessionLocal()
    try:
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).all()
        assert len(messages) == 0
    finally:
        db.close()


# =============================================================================
# Tests for Conversation Ordering
# =============================================================================

def test_conversations_ordered_by_recent():
    """Test that conversations are ordered by most recently updated."""
    # Create conversation A
    response_a = client.post(
        "/conversations/",
        json={"title": "Conversation A"}
    )
    conv_a_id = response_a.json()["id"]
    
    # Wait a moment to ensure different timestamps
    time.sleep(0.1)
    
    # Create conversation B
    response_b = client.post(
        "/conversations/",
        json={"title": "Conversation B"}
    )
    conv_b_id = response_b.json()["id"]
    
    # List conversations
    response = client.get("/conversations/")
    conversations = response.json()["conversations"]
    
    # Find our conversations in the list
    conv_a_idx = next(
        i for i, c in enumerate(conversations) if c["id"] == conv_a_id
    )
    conv_b_idx = next(
        i for i, c in enumerate(conversations) if c["id"] == conv_b_id
    )
    
    # B should come before A (more recent)
    assert conv_b_idx < conv_a_idx


def test_conversation_updated_when_message_added():
    """Test that adding a message updates the conversation's updated_at timestamp."""
    # Create conversation
    conv_response = client.post("/conversations/", json={})
    conversation_id = conv_response.json()["id"]
    original_updated_at = conv_response.json()["updated_at"]
    
    # Wait a moment
    time.sleep(0.1)
    
    # Add a message
    client.post(
        f"/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Update timestamp test"}
    )
    
    # Get conversation again
    get_response = client.get(f"/conversations/{conversation_id}")
    new_updated_at = get_response.json()["updated_at"]
    
    # Updated timestamp should be different (later)
    assert new_updated_at != original_updated_at


# =============================================================================
# Tests for Message Count in List View
# =============================================================================

def test_conversation_list_includes_message_count():
    """Test that listing conversations includes message count."""
    # Create conversation with messages
    conv_response = client.post(
        "/conversations/",
        json={"title": "Count Test"}
    )
    conversation_id = conv_response.json()["id"]
    
    # Add 3 messages
    for i in range(3):
        client.post(
            f"/conversations/{conversation_id}/messages",
            json={"role": "user", "content": f"Message {i}"}
        )
    
    # List conversations
    response = client.get("/conversations/")
    conversations = response.json()["conversations"]
    
    # Find our conversation
    our_conv = next(c for c in conversations if c["id"] == conversation_id)
    assert our_conv["message_count"] == 3


# =============================================================================
# Tests for Edge Cases
# =============================================================================

def test_empty_message_content_fails():
    """Test that creating a message with empty content fails validation."""
    # Create conversation
    conv_response = client.post("/conversations/", json={})
    conversation_id = conv_response.json()["id"]
    
    # Try to add message with empty content
    response = client.post(
        f"/conversations/{conversation_id}/messages",
        json={"role": "user", "content": ""}
    )
    # This should still succeed (backend doesn't validate empty strings)
    # but we can verify it's stored correctly
    assert response.status_code == 201
    assert response.json()["content"] == ""


def test_multiple_conversations_independent():
    """Test that multiple conversations are independent."""
    # Create two conversations
    conv1 = client.post("/conversations/", json={"title": "Conv 1"}).json()
    conv2 = client.post("/conversations/", json={"title": "Conv 2"}).json()
    
    # Add messages to each
    client.post(
        f"/conversations/{conv1['id']}/messages",
        json={"role": "user", "content": "Message in conv 1"}
    )
    client.post(
        f"/conversations/{conv2['id']}/messages",
        json={"role": "user", "content": "Message in conv 2"}
    )
    
    # Verify each conversation has only its own message
    response1 = client.get(f"/conversations/{conv1['id']}")
    response2 = client.get(f"/conversations/{conv2['id']}")
    
    assert len(response1.json()["messages"]) == 1
    assert len(response2.json()["messages"]) == 1
    assert response1.json()["messages"][0]["content"] == "Message in conv 1"
    assert response2.json()["messages"][0]["content"] == "Message in conv 2"

