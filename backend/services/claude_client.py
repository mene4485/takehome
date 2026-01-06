"""
Claude AI API client with Programmatic Tool Calling (PTC) support.

This module orchestrates conversations with Claude, handling the PTC loop:
1. Send user message with tool definitions (including custom tools with allowed_callers)
2. Claude writes Python code and executes it in ITS secure environment
3. When Claude's code calls our custom tools, we respond with tool results
4. Repeat until Claude returns final text response

With PTC, Claude can write and execute Python code that calls our tools,
enabling complex multi-step reasoning and data processing.
"""

from anthropic import Anthropic
import os
import json
from datetime import datetime
from typing import AsyncGenerator
from services.tools import TOOL_DEFINITIONS, TOOL_HANDLERS

# Claude model to use (Sonnet 4.5 supports PTC with code_execution_20250825)
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
SYSTEM_PROMPT = """You are Mission Control, an AI operations assistant for Structured AI. 

                    Your role: Help analyze operational data efficiently and provide actionable insights.

                    Guidelines:
                    - Be concise and direct in responses
                    - For data analysis questions, use code_execution to write Python code that processes data
                    - When greeting users, briefly mention you can help with ops data (don't list all tools)
                    - Focus on insights, not just raw data
                    - Use formatting (bold, bullets) to make responses scannable

                    Remember: You have access to tools for team data, projects, incidents, budgets, feedback, and deployments."""


def get_client():
    """Create Anthropic client with API key from environment."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in environment. "
            "Please add it to backend/.env file: ANTHROPIC_API_KEY=your_key_here"
        )
    return Anthropic(api_key=api_key)



async def chat_with_claude_streaming(
    user_message: str, 
    conversation_history: list = None
) -> AsyncGenerator[dict, None]:
    """
    Stream events during Claude conversation with PTC support.
    
    Yields events as they occur:
    - thinking: Initial processing started
    - code: Claude is writing Python code in container
    - tool_call: Tool execution started (with running status)
    - tool_result: Tool execution completed
    - response: Final text answer
    - error: Any error that occurred
    
    Args:
        user_message: The user's message/question
        conversation_history: Optional list of previous messages for context
        
    Yields:
        Dict events with type, content, timestamp, and other metadata
    """
    try:
        # Yield initial thinking event
        yield {
            "type": "thinking",
            "content": "Analyzing your question...",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Initialize messages list with conversation history
        messages = []
        if conversation_history:
            messages = list(conversation_history)  # Copy the already-formatted history
        
        # Add the new user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        tool_calls_count = 0
        max_iterations = 20
        iteration = 0
        current_container_id = None  # Container maintained only within this conversation loop
        
        # Conversation loop: continue until Claude returns text (no tool_use)
        while iteration < max_iterations:
            iteration += 1
            
            # Call Claude API with PTC enabled
            client = get_client()
            
            # Prepare tools: add code_execution tool + custom tools with allowed_callers
            tools = [
                {
                    "type": "code_execution_20250825",
                    "name": "code_execution"
                }
            ] + TOOL_DEFINITIONS
            
            # Build API call parameters
            api_params = {
                "model": CLAUDE_MODEL,
                "max_tokens": 4096,
                "betas": ["advanced-tool-use-2025-11-20"],
                "tools": tools,
                "messages": messages,
                "system": SYSTEM_PROMPT
            }
            
            # Add container_id if we have one
            if current_container_id:
                api_params["container"] = current_container_id
            
            response = client.beta.messages.create(**api_params)
            
            # Extract container_id from response
            if hasattr(response, 'container') and response.container:
                if hasattr(response.container, 'id') and response.container.id:
                    current_container_id = response.container.id
            
            # Check for server_tool_use blocks (contains Python code execution)
            server_tool_uses = [block for block in response.content if hasattr(block, 'type') and block.type == 'server_tool_use']
            if server_tool_uses:
                # Yield code execution events
                for block in server_tool_uses:
                    if hasattr(block, 'input') and 'code' in block.input:
                        yield {
                            "type": "code_execution",
                            "code": block.input['code'],
                            "timestamp": datetime.utcnow().isoformat()
                        }
            
            # Get tool_use blocks (tool calls from Claude or its code)
            tool_use_blocks = [block for block in response.content if block.type == "tool_use"]
            
            if not tool_use_blocks:
                # No tool use - Claude returned final text response
                break
            
            # Append Claude's response to conversation
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Execute each tool call and yield events
            tool_results = []
            for block in tool_use_blocks:
                tool_calls_count += 1
                
                # Yield tool call start event
                yield {
                    "type": "tool_call",
                    "tool_name": block.name,
                    "status": "running",
                    "parameters": block.input,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                try:
                    # Call the tool function
                    tool_func = TOOL_HANDLERS.get(block.name)
                    
                    if not tool_func:
                        result_content = f"Error: Unknown tool '{block.name}'"
                    else:
                        # Call the tool with provided parameters
                        result = await tool_func(**block.input)
                        # Convert result to JSON string for Claude
                        result_content = json.dumps(result)
                    
                    # Yield tool completion event
                    yield {
                        "type": "tool_result",
                        "tool_name": block.name,
                        "status": "completed",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Add successful result
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_content
                    })
                    
                except Exception as e:
                    # Tool execution failed
                    error_msg = f"Error executing {block.name}: {str(e)}"
                    
                    # Yield error status
                    yield {
                        "type": "tool_result",
                        "tool_name": block.name,
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": error_msg,
                        "is_error": True
                    })
            
            # Send tool results back to Claude
            messages.append({
                "role": "user",
                "content": tool_results
            })
        
        # Extract final text response from Claude
        text_blocks = [block for block in response.content if block.type == "text"]
        final_text = "".join([block.text for block in text_blocks])
        
        if not final_text:
            final_text = "I processed your request but didn't generate a text response."
        
        # Yield final response event
        yield {
            "type": "response",
            "content": final_text,
            "tool_calls_count": tool_calls_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Yield error event
        yield {
            "type": "error",
            "content": "I encountered an error processing your request.",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }



async def chat_with_claude(user_message: str, conversation_history: list = None) -> dict:
    """
    Send a message to Claude and handle the full PTC conversation loop.
    
    Args:
        user_message: The user's message/question
        conversation_history: Optional list of previous messages for context
        
    Returns:
        Dict with:
            - response: Claude's final text response
            - tool_calls: Number of tool/code executions performed
            - conversation: Full message history including tool calls
    """
    try:
        print("\n" + "="*80)
        print("🚀 STARTING CLAUDE CONVERSATION")
        print("="*80)
        print(f"📝 User message: {user_message}")
        
        # Initialize messages list with conversation history
        messages = []
        if conversation_history:
            messages = list(conversation_history)  # Copy the already-formatted history
            print(f"📚 Loaded {len(conversation_history)} previous messages for context")
        
        # Add the new user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        tool_calls_count = 0
        max_iterations = 20  # Prevent infinite loops
        iteration = 0
        container_id = None  # Track container_id for PTC execution state
        
        print(f"🔄 Starting conversation loop (max {max_iterations} iterations)")
        print("-"*80)
        
        # Conversation loop: continue until Claude returns text (no tool_use)
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔁 Iteration {iteration}/{max_iterations}")
            
            # Call Claude API with PTC enabled
            client = get_client()
            
            # Prepare tools: add code_execution tool + custom tools with allowed_callers
            tools = [
                {
                    "type": "code_execution_20250825",
                    "name": "code_execution"
                }
            ] + TOOL_DEFINITIONS
            
            print(f"📡 Calling Claude API (model: {CLAUDE_MODEL})...")
            print(f"   Tools available: code_execution + {len(TOOL_DEFINITIONS)} custom tools")
            if container_id:
                print(f"   📦 Using container_id: {container_id}")
            
            # Build API call parameters
            api_params = {
                "model": CLAUDE_MODEL,
                "max_tokens": 4096,
                "betas": ["advanced-tool-use-2025-11-20"],
                "tools": tools,
                "messages": messages,
                "system": """You are Mission Control, an AI operations assistant for Structured AI. 

                    Your role: Help analyze operational data efficiently and provide actionable insights.

                    Guidelines:
                    - Be concise and direct in responses
                    - For data analysis questions, use code_execution to write Python code that processes data
                    - When greeting users, briefly mention you can help with ops data (don't list all tools)
                    - Focus on insights, not just raw data
                    - Use formatting (bold, bullets) to make responses scannable

                    Remember: You have access to tools for team data, projects, incidents, budgets, feedback, and deployments."""
            }
            
            # Add container_id if we have one (required for PTC state tracking)
            if container_id:
                api_params["container"] = container_id
            
            response = client.beta.messages.create(**api_params)
            
            print(f"✅ Received response from Claude (stop_reason: {response.stop_reason})")
            
            # Extract container_id from response.container.id
            # This is critical for PTC - we need the container_id to maintain execution state
            if hasattr(response, 'container') and response.container:
                if hasattr(response.container, 'id') and response.container.id:
                    if container_id != response.container.id:
                        container_id = response.container.id
                        print(f"   📦 Received container_id: {container_id}")
            
            # Check if there are server_tool_use blocks (PTC-specific)
            server_tool_uses = [block for block in response.content if hasattr(block, 'type') and block.type == 'server_tool_use']
            code_results = [block for block in response.content if hasattr(block, 'type') and block.type == 'code_execution_tool_result']
            
            if server_tool_uses:
                print(f"   🔧 Detected {len(server_tool_uses)} server_tool_use block(s) (PTC active)")
                # Log the code Claude is executing (for debugging)
                for idx, block in enumerate(server_tool_uses, 1):
                    if hasattr(block, 'input') and 'code' in block.input:
                        code_preview = block.input['code'][:200] + "..." if len(block.input['code']) > 200 else block.input['code']
                        print(f"   📝 Code block {idx}: {code_preview}")
            
            if code_results:
                print(f"   ✅ Detected {len(code_results)} code_execution_tool_result block(s)")
                for idx, block in enumerate(code_results, 1):
                    if hasattr(block, 'content'):
                        print(f"   📊 Code result {idx}: {str(block.content)[:200]}")
            
            # Determine which blocks to process:
            # - With PTC (server_tool_use present): Claude executes code in ITS environment
            #   We ONLY respond to the tool_use blocks (tool calls FROM Claude's code)
            # - Without PTC: We process regular tool_use blocks
            tool_use_blocks = [block for block in response.content if block.type == "tool_use"]
            
            if server_tool_uses:
                print(f"   📝 PTC MODE: Claude is executing {len(server_tool_uses)} code block(s)")
                print(f"   📞 Responding to {len(tool_use_blocks)} tool call(s) from Claude's code")
            
            if not tool_use_blocks:
                # No tool use - Claude returned final text response
                print("💬 Claude returned FINAL TEXT (no tool use) - exiting loop")
                text_blocks = [block for block in response.content if block.type == "text"]
                if text_blocks:
                    preview = text_blocks[0].text[:100] + ("..." if len(text_blocks[0].text) > 100 else "")
                    print(f"   Preview: {preview}")
                break
            
            # Claude wants to use tools or execute code
            print(f"\n🔧 Claude wants to use {len(tool_use_blocks)} tool(s)")
            
            # Append Claude's response to conversation
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Execute each tool call (these are tool calls FROM Claude's code in PTC mode)
            tool_results = []
            for idx, block in enumerate(tool_use_blocks, 1):
                tool_calls_count += 1
                
                print(f"\n   Tool {idx}/{len(tool_use_blocks)}: {block.name}({block.input})")
                
                try:
                    # Call the tool function
                    tool_func = TOOL_HANDLERS.get(block.name)
                    
                    if not tool_func:
                        result_content = f"Error: Unknown tool '{block.name}'"
                        print(f"   ❌ Error: Tool not found")
                    else:
                        # Call the tool with provided parameters
                        result = await tool_func(**block.input)
                        # Convert result to JSON string for Claude to parse in code execution
                        result_content = json.dumps(result)
                        print(f"   ✅ Tool result: {result_content[:100]}...")
                    
                    # Add successful result
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_content
                    })
                    
                except Exception as e:
                    # Tool execution failed - send error to Claude
                    error_msg = f"Error executing {block.name}: {str(e)}"
                    print(f"   ❌ EXECUTION ERROR: {error_msg}")
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": error_msg,
                        "is_error": True
                    })
            
            # Send tool results back to Claude
            print(f"\n📤 Sending {len(tool_results)} tool result(s) back to Claude...")
            messages.append({
                "role": "user",
                "content": tool_results
            })
            print("   ↻ Looping back to get Claude's next response...")
        
        # Extract final text response from Claude
        text_blocks = [block for block in response.content if block.type == "text"]
        final_text = "".join([block.text for block in text_blocks])
        
        if not final_text:
            final_text = "I processed your request but didn't generate a text response."
        
        print("\n" + "="*80)
        print("✅ CONVERSATION COMPLETE")
        print("="*80)
        print(f"📊 Statistics:")
        print(f"   - Total iterations: {iteration}")
        print(f"   - Tool/code executions: {tool_calls_count}")
        print(f"   - Final response length: {len(final_text)} characters")
        print(f"   - Response preview: {final_text[:150]}...")
        print("="*80 + "\n")
        
        return {
            "response": final_text,
            "tool_calls": tool_calls_count,
            "conversation": messages
        }
        
    except Exception as e:
        # Handle API errors gracefully
        print("\n" + "="*80)
        print("❌ ERROR IN CONVERSATION")
        print("="*80)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("="*80 + "\n")
        
        return {
            "response": "I encountered an error processing your request. Please try again.",
            "error": str(e),
            "tool_calls": tool_calls_count if 'tool_calls_count' in locals() else 0
        }
