"""
API routes for conversation and message management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from db import get_db
from services.conversations import (
    create_conversation,
    get_conversation,
    list_conversations,
    delete_conversation,
    create_message,
    get_messages
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


# Pydantic models for request/response validation
class MessageCreate(BaseModel):
    """Request model for creating a message."""
    role: str
    content: str
    metadata: Optional[dict] = None


class ConversationCreate(BaseModel):
    """Request model for creating a conversation."""
    title: Optional[str] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_conversation(
    data: ConversationCreate = None,
    db: Session = Depends(get_db)
):
    """
    Create a new conversation.
    
    The conversation will be assigned a unique ID starting with 'conv_'.
    Title is optional and can be set later based on the first message.
    """
    title = data.title if data else None
    conversation = create_conversation(db, title)
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "messages": []
    }


@router.get("/")
async def list_all_conversations(db: Session = Depends(get_db)):
    """
    List all conversations ordered by most recent.
    
    Returns conversations sorted by updated_at in descending order,
    limited to the most recent 50 conversations.
    """
    conversations = list_conversations(db)
    return {
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": len(conv.messages)
            }
            for conv in conversations
        ],
        "count": len(conversations)
    }


@router.get("/{conversation_id}")
async def get_conversation_by_id(
    conversation_id: str, 
    db: Session = Depends(get_db)
):
    """
    Get conversation by ID with all messages.
    
    Returns the full conversation including all messages in chronological order.
    Raises 404 if conversation is not found.
    """
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "metadata": msg.message_metadata,
                "created_at": msg.created_at.isoformat()
            }
            for msg in sorted(conversation.messages, key=lambda m: m.created_at)
        ]
    }


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_by_id(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete conversation and all its messages.
    
    Cascade delete will automatically remove all messages belonging to this conversation.
    Raises 404 if conversation is not found.
    """
    success = delete_conversation(db, conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return None


@router.post("/{conversation_id}/messages", status_code=status.HTTP_201_CREATED)
async def create_conversation_message(
    conversation_id: str,
    data: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Add a message to a conversation.
    
    Creates a new message with the specified role (user/assistant) and content.
    Raises 404 if conversation is not found.
    """
    message = create_message(
        db,
        conversation_id,
        data.role,
        data.content,
        data.metadata
    )
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "role": message.role,
        "content": message.content,
        "metadata": message.message_metadata,
        "created_at": message.created_at.isoformat()
    }

