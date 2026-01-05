"""
Chat API routes for Claude AI integration.

This module handles the main chat endpoint where users send messages to Claude
and receive AI-generated responses with Programmatic Tool Calling support.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json
import asyncio

from db import get_db
from services.conversations import get_conversation, create_message, get_messages
from services.claude_client import chat_with_claude, chat_with_claude_streaming


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    conversation_id: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    conversation_id: str
    message_id: str



@router.post("/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Stream chat with Claude AI showing real-time tool execution progress via Server-Sent Events.
    
    This endpoint:
    1. Validates the conversation exists
    2. Loads conversation history (last 20 messages for context)
    3. Streams events as Claude processes: thinking, code writing, tool calls, results
    4. Saves assistant's response to database after streaming completes
    5. Returns Server-Sent Events stream
    
    Args:
        request: ChatRequest with message and conversation_id
        db: Database session injected by FastAPI
        
    Returns:
        StreamingResponse with SSE events (text/event-stream)
        
    Raises:
        HTTPException 400: If conversation_id is missing
        HTTPException 404: If conversation doesn't exist
    """
    # Validate conversation exists
    if not request.conversation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="conversation_id is required"
        )
    
    conversation = get_conversation(db, request.conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {request.conversation_id} not found"
        )
    
    # Load conversation history for context (last 20 messages)
    messages = get_messages(db, request.conversation_id)
    
    # Limit to last 20 messages to avoid overwhelming Claude's context
    if len(messages) > 20:
        messages = messages[-20:]
    
    # Format messages for Claude API
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]
    
    # Track final response for database save
    final_response = {"content": "", "tool_calls_count": 0}
    
    async def event_generator():
        """Generate SSE events from Claude streaming."""
        try:
            # Stream events from Claude
            async for event in chat_with_claude_streaming(
                request.message, 
                history
            ):
                # Track final response data
                if event["type"] == "response":
                    final_response["content"] = event["content"]
                    final_response["tool_calls_count"] = event.get("tool_calls_count", 0)
                
                # Format as SSE and yield
                yield f"data: {json.dumps(event)}\n\n"
            
            # Save assistant message to database after streaming completes
            try:
                if final_response["content"]:
                    create_message(
                        db=db,
                        conversation_id=request.conversation_id,
                        role="assistant",
                        content=final_response["content"],
                        metadata={
                            "tool_calls": final_response["tool_calls_count"]
                        }
                    )
                    db.commit()  # Commit the transaction
            except Exception as db_error:
                print(f"Failed to save message to database: {db_error}")
                # Don't fail the stream - user already saw the response
                
        except asyncio.CancelledError:
            # Client disconnected - cleanup gracefully
            print("Client disconnected from stream")
            raise
        except Exception as e:
            # Stream error - yield error event
            print(f"Streaming error: {str(e)}")
            error_event = {
                "type": "error",
                "content": "An error occurred while processing your request.",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )



@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message to Claude AI and get a response.
    
    This endpoint:
    1. Validates the conversation exists
    2. Loads conversation history (last 20 messages for context)
    3. Sends message to Claude with PTC-enabled tools
    4. Saves assistant's response to database
    5. Returns the response to frontend
    
    Args:
        request: ChatRequest with message and conversation_id
        db: Database session injected by FastAPI
        
    Returns:
        ChatResponse with Claude's response and message ID
        
    Raises:
        HTTPException 400: If conversation_id is missing
        HTTPException 404: If conversation doesn't exist
    """
    # Validate conversation exists
    if not request.conversation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="conversation_id is required"
        )
    
    conversation = get_conversation(db, request.conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {request.conversation_id} not found"
        )
    
    # Load conversation history for context (last 20 messages)
    messages = get_messages(db, request.conversation_id)
    
    # Limit to last 20 messages to avoid overwhelming Claude's context
    if len(messages) > 20:
        messages = messages[-20:]
    
    # Format messages for Claude API
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]
    
    try:
        # Call Claude service with conversation history
        claude_response = await chat_with_claude(request.message, history)
        
        # Extract response text
        response_text = claude_response["response"]
        
        # Check for errors but still save to DB (graceful degradation)
        if "error" in claude_response:
            print(f"Claude API error: {claude_response['error']}")
            # Still save the error message so user sees Claude tried to help
        
        # Save assistant message to database
        assistant_message = create_message(
            db=db,
            conversation_id=request.conversation_id,
            role="assistant",
            content=response_text,
            metadata={"tool_calls": claude_response.get("tool_calls", 0)}
        )
        
        if not assistant_message:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save assistant message"
            )
        
        return ChatResponse(
            response=response_text,
            conversation_id=request.conversation_id,
            message_id=assistant_message.id
        )
        
    except Exception as e:
        # Log the error
        print(f"Chat endpoint error: {str(e)}")
        
        # Return user-friendly error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )
