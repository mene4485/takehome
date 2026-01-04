"""
Database models for chat conversations and messages.
"""
from datetime import datetime, UTC
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from db.database import Base


class Conversation(Base):
    """
    Represents a chat conversation.
    
    A conversation contains multiple messages and tracks when it was created
    and last updated. Each conversation has a unique ID and an optional title.
    """
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.now(UTC), 
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )
    
    # Relationship: One conversation has many messages
    # cascade="all, delete-orphan" means deleting a conversation deletes all its messages
    messages = relationship(
        "Message", 
        back_populates="conversation", 
        cascade="all, delete-orphan"
    )


class Message(Base):
    """
    Represents a single message in a conversation.
    
    Each message has a role (user or assistant), text content, optional metadata
    for tool calls/code execution, and belongs to exactly one conversation.
    """
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    conversation_id = Column(
        String, 
        ForeignKey("conversations.id"), 
        nullable=False
    )
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # Stores tool calls, code execution, etc.
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    
    # Relationship: Each message belongs to one conversation
    conversation = relationship("Conversation", back_populates="messages")

