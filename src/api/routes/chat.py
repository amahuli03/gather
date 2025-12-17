"""Chat endpoint for agent interactions."""
from fastapi import APIRouter, HTTPException, Depends
from src.api.models import ChatRequest, ChatResponse, ErrorResponse
from src.api.dependencies import get_tool_context, get_user_tool_context
from src.agent.types import ToolContext
from src.agent.coordinator import run_task
from src.agent.memory import get_memory, save_memory

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    base_context: ToolContext = Depends(get_tool_context)
):
    """
    Send a message to the agent and get a response.
    
    Args:
        request: Chat request with message and user_id
        base_context: Shared tool context (injected dependency)
    
    Returns:
        ChatResponse with agent response and tool calls
    """
    try:
        # Create user-specific tool context
        ctx = get_user_tool_context(request.user_id, base_context)
        
        # Get or create memory for this user
        memory = get_memory(request.user_id, window_size=20)
        
        # Run the agent task
        output, tool_calls = run_task(ctx, request.message, memory=memory)
        
        # Save memory after processing
        save_memory(request.user_id, memory)
        
        return ChatResponse(
            response=output,
            tool_calls=tool_calls,
            user_id=request.user_id
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

