"""
FastAPI Backend for NexTrade Multi-Agent Trading System.

This module provides professional REST APIs for the multi-agent system,
including health checks, agent interactions, and portfolio management.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import uuid
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from langchain_core.messages import HumanMessage
from agent.graph import create_financial_advisor_system
from agent.resilience import HealthCheck, retry_with_backoff, RetryConfig
from agent.guardrails_integration import SafetyLayer, ComplianceLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NexTrade Multi-Agent Trading API",
    description="Professional REST API for intelligent stock market operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
safety_layer = SafetyLayer()
compliance_logger = ComplianceLogger()
health_check = HealthCheck()

# Global supervisor instance (cached)
_supervisor = None


# ==================== Request/Response Models ====================

class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    message: str = Field(..., description="User message to the agent")
    user_id: str = Field(..., description="Unique user identifier")
    thread_id: Optional[str] = Field(None, description="Conversation thread ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Research NVIDIA stock and provide analysis",
                "user_id": "user_12345",
                "thread_id": "thread_67890"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    response: str = Field(..., description="Agent response")
    thread_id: str = Field(..., description="Conversation thread ID")
    timestamp: str = Field(..., description="Response timestamp")
    requires_approval: bool = Field(default=False, description="Whether human approval is needed")
    approval_details: Optional[Dict[str, Any]] = Field(None, description="Details for approval")
    approved: Optional[bool] = Field(None, description="Approval status (if applicable)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "I've completed the research on NVIDIA...",
                "thread_id": "thread_67890",
                "timestamp": "2025-11-03T10:30:00Z",
                "requires_approval": False
            }
        }


class ApprovalRequest(BaseModel):
    """Request model for human-in-the-loop approval."""
    thread_id: str = Field(..., description="Conversation thread ID")
    approved: bool = Field(..., description="Whether the action is approved")
    user_id: str = Field(..., description="User ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "thread_id": "thread_67890",
                "approved": True,
                "user_id": "user_12345"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Overall system status")
    timestamp: str = Field(..., description="Health check timestamp")
    components: Dict[str, bool] = Field(..., description="Status of individual components")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-11-03T10:30:00Z",
                "components": {
                    "api": True,
                    "llm": True,
                    "database": True
                }
            }
        }


class OrderRequest(BaseModel):
    """Request model for placing orders."""
    user_id: str = Field(..., description="User ID")
    symbol: str = Field(..., description="Stock symbol")
    quantity: int = Field(..., gt=0, description="Number of shares")
    order_type: str = Field(..., description="Order type (buy/sell)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_12345",
                "symbol": "AAPL",
                "quantity": 10,
                "order_type": "buy"
            }
        }


# ==================== Dependency Injection ====================

def get_supervisor():
    """Get or create supervisor instance."""
    global _supervisor
    if _supervisor is None:
        logger.info("Initializing supervisor instance...")
        _supervisor = create_financial_advisor_system()
    return _supervisor


def get_safety_layer() -> SafetyLayer:
    """Get safety layer instance."""
    return safety_layer


# ==================== Health Check Endpoints ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "NexTrade Multi-Agent Trading API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_endpoint():
    """
    Health check endpoint for monitoring system status.
    
    Returns:
        System health status and component statuses
    """
    try:
        # Register health checks
        health_check.register("api", lambda: True)
        
        def check_llm():
            try:
                supervisor = get_supervisor()
                return supervisor is not None
            except Exception as e:
                logger.error(f"LLM health check failed: {e}")
                return False
        
        health_check.register("llm", check_llm)
        
        def check_database():
            try:
                from agent.database_tools import get_user_orders
                return True
            except Exception as e:
                logger.error(f"Database health check failed: {e}")
                return False
        
        health_check.register("database", check_database)
        
        # Run health checks
        components = health_check.run_all()
        is_healthy = all(components.values())
        
        return HealthResponse(
            status="healthy" if is_healthy else "degraded",
            timestamp=datetime.now().isoformat(),
            components=components
        )
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


# ==================== Chat Endpoints ====================

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    supervisor=Depends(get_supervisor),
    safety=Depends(get_safety_layer)
):
    """
    Chat with the multi-agent system.
    
    Args:
        request: Chat request with message and user info
        
    Returns:
        Agent response or approval requirement
        
    Raises:
        HTTPException: If validation fails or system error occurs
    """
    try:
        # Log user action
        compliance_logger.log_user_action(
            action="chat_request",
            user_id=request.user_id,
            details={"message_preview": request.message[:100]}
        )
        
        # Validate input
        validation_result = safety.validate_user_input(request.message)
        
        if not validation_result["is_valid"]:
            compliance_logger.log_safety_violation(
                violation_type="input_validation_failed",
                details=validation_result,
                user_id=request.user_id
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Input validation failed",
                    "details": validation_result["errors"]
                }
            )
        
        # Generate thread_id if not provided
        thread_id = request.thread_id or str(uuid.uuid4())
        
        # Create configuration with recursion limit
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": request.user_id
            },
            "recursion_limit": 100  # Maximum 100 node executions to prevent infinite loops
        }
        
        # Invoke supervisor
        logger.info(f"Processing chat request for user {request.user_id}")
        response = supervisor.invoke({
            "messages": [HumanMessage(content=validation_result["sanitized_input"])]
        }, config)
        
        # Check for interrupt (HITL approval needed)
        if "__interrupt__" in response:
            interrupts = response["__interrupt__"]
            if interrupts:
                interrupt_data = interrupts[0].value
                
                logger.info(f"HITL approval required for user {request.user_id}")
                
                return ChatResponse(
                    response="Action requires human approval",
                    thread_id=thread_id,
                    timestamp=datetime.now().isoformat(),
                    requires_approval=True,
                    approval_details=interrupt_data["approval_details"]
                )
        
        # Extract final response
        final_message = response['messages'][-1]
        response_content = final_message.content
        
        # Validate output
        output_validation = safety.validate_llm_output(response_content)
        
        if not output_validation["is_valid"]:
            logger.error(f"Output validation failed: {output_validation}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Response validation failed"
            )
        
        return ChatResponse(
            response=output_validation["sanitized_output"],
            thread_id=thread_id,
            timestamp=datetime.now().isoformat(),
            requires_approval=False
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/approve", response_model=ChatResponse, tags=["Chat"])
async def approve_action(
    request: ApprovalRequest,
    supervisor=Depends(get_supervisor)
):
    """
    Approve or reject a pending action.
    
    Args:
        request: Approval request with decision
        
    Returns:
        Result of approved action
    """
    try:
        # Log approval decision
        compliance_logger.log_user_action(
            action="approval_decision",
            user_id=request.user_id,
            details={"approved": request.approved, "thread_id": request.thread_id}
        )
        
        # Create configuration with recursion limit
        config = {
            "configurable": {
                "thread_id": request.thread_id,
                "user_id": request.user_id
            },
            "recursion_limit": 100  # Maximum 100 node executions to prevent infinite loops
        }
        
        # Resume with approval decision  
        from langgraph.types import Command
        if request.approved:
            response = supervisor.invoke(Command(resume={"approved": True}), config)
        else:
            response = supervisor.invoke(Command(resume={"approved": False}), config)
        
        # Extract result
        final_message = response['messages'][-1]
        
        return ChatResponse(
            response=final_message.content,
            thread_id=request.thread_id,
            timestamp=datetime.now().isoformat(),
            requires_approval=False,
            approved=request.approved
        )
    
    except Exception as e:
        logger.error(f"Approval endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== Portfolio Endpoints ====================

@app.get("/portfolio/{user_id}", tags=["Portfolio"])
async def get_portfolio(user_id: str):
    """
    Get user's portfolio positions.
    
    Args:
        user_id: User identifier
        
    Returns:
        Portfolio positions
    """
    try:
        from agent.database_tools import get_portfolio_positions
        
        positions = get_portfolio_positions(user_id)
        
        return {
            "user_id": user_id,
            "positions": positions,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Portfolio endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/orders/{user_id}", tags=["Orders"])
async def get_orders(user_id: str, limit: int = 10):
    """
    Get user's order history.
    
    Args:
        user_id: User identifier
        limit: Maximum number of orders to return
        
    Returns:
        Order history
    """
    try:
        from agent.database_tools import get_user_orders
        
        orders = get_user_orders(user_id, limit)
        
        return {
            "user_id": user_id,
            "orders": orders,
            "count": len(orders),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Orders endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    logger.info("Starting NexTrade API server...")
    logger.info("Initializing multi-agent supervisor...")
    # Warm up the supervisor
    try:
        get_supervisor()
        logger.info("Supervisor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize supervisor: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down NexTrade API server...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
