"""
Service layer for conversation and message CRUD operations.

This module handles all database operations for conversations and messages,
keeping business logic separate from API routes.
"""
import uuid
from datetime import datetime, UTC
from sqlalchemy.orm import Session

from db import Conversation, Message


def create_conversation(db: Session, title: str = None) -> Conversation:
    """
    Create a new conversation.
    
    Args:
        db: Database session
        title: Optional conversation title (can be set later based on first message)
    
    Returns:
        The created Conversation object with auto-generated ID and timestamps
    """
    conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
    conversation = Conversation(id=conversation_id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation(db: Session, conversation_id: str) -> Conversation | None:
    """
    Get a conversation by ID.
    
    Args:
        db: Database session
        conversation_id: The conversation ID to retrieve
    
    Returns:
        Conversation object if found, None otherwise.
        SQLAlchemy automatically loads related messages via the relationship.
    """
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def list_conversations(db: Session, limit: int = 50) -> list[Conversation]:
    """
    List all conversations ordered by most recently updated.
    
    Args:
        db: Database session
        limit: Maximum number of conversations to return (default: 50)
    
    Returns:
        List of Conversation objects ordered by updated_at descending
    """
    return db.query(Conversation).order_by(Conversation.updated_at.desc()).limit(limit).all()


def delete_conversation(db: Session, conversation_id: str) -> bool:
    """
    Delete a conversation and all its messages.
    
    Args:
        db: Database session
        conversation_id: The conversation ID to delete
    
    Returns:
        True if conversation was deleted, False if not found
    """
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        return False
    
    db.delete(conversation)
    db.commit()
    return True


def create_message(
    db: Session, 
    conversation_id: str, 
    role: str, 
    content: str, 
    metadata: dict = None
) -> Message | None:
    """
    Create a new message in a conversation.
    
    Args:
        db: Database session
        conversation_id: ID of the conversation this message belongs to
        role: Message role ("user" or "assistant")
        content: The message text content
        metadata: Optional dictionary with tool calls, code execution, etc.
    
    Returns:
        The created Message object, or None if conversation doesn't exist
    """
    # Verify conversation exists
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        return None
    
    message_id = f"msg_{uuid.uuid4().hex[:8]}"
    message = Message(
        id=message_id,
        conversation_id=conversation_id,
        role=role,
        content=content,
        message_metadata=metadata
    )
    db.add(message)
    
    # Update conversation's updated_at timestamp
    conversation.updated_at = datetime.now(UTC)
    
    db.commit()
    db.refresh(message)
    return message


def get_messages(db: Session, conversation_id: str) -> list[Message]:
    """
    Get all messages for a conversation in chronological order.
    
    Args:
        db: Database session
        conversation_id: The conversation ID to get messages for
    
    Returns:
        List of Message objects ordered by created_at ascending (oldest first)
    """
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

