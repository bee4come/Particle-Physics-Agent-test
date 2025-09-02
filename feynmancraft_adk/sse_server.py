#!/usr/bin/env python3
"""
FastAPI SSE Server for FeynmanCraft ADK
Provides real-time event streaming with replay and heartbeat
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Optional, Dict, Any
from .sse_bus import stream, publish, get_stats

logger = logging.getLogger(__name__)

# CORS whitelist as per Zhang Gong's B-B-B plan
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000", 
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176"
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifecycle management"""
    logger.info("Starting FeynmanCraft SSE Server")
    publish({
        "type": "server.ready",
        "message": "SSE server started - ready for real-time events",
        "level": 1
    })
    yield
    logger.info("Shutting down SSE Server")

# Create FastAPI app
app = FastAPI(
    title="FeynmanCraft SSE Server",
    description="Real-time event streaming for ADK workflow visualization",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS per B-B-B plan
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Client-Origin", "Last-Event-ID", "X-Trace-Id", "X-Step-Id"],
)

def _parse_last_event_id(request: Request) -> Optional[int]:
    """Parse Last-Event-ID header for event replay"""
    lei = request.headers.get("Last-Event-ID")
    if not lei:
        return None
    try:
        return int(lei)
    except (ValueError, TypeError):
        logger.warning(f"Invalid Last-Event-ID: {lei}")
        return None

@app.get("/events")
async def events_endpoint(request: Request, since: Optional[int] = None):
    """Main SSE endpoint with replay capability"""
    try:
        # Get replay point from header or query param
        replay_since = since or _parse_last_event_id(request)
        
        async def event_stream():
            async for chunk in stream(replay_since):
                yield chunk
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
    
    except Exception as e:
        logger.error(f"Error in SSE endpoint: {e}")
        raise HTTPException(status_code=500, detail="SSE stream error")

@app.post("/emit")
async def emit_test_event(event: Dict[str, Any]):
    """Test endpoint for manual event emission"""
    try:
        publish(event)
        return {"status": "success", "message": "Event published"}
    except Exception as e:
        logger.error(f"Error emitting event: {e}")
        raise HTTPException(status_code=500, detail="Failed to emit event")

@app.get("/health")
async def health_check():
    """Health check with detailed status"""
    stats = get_stats()
    return {
        "status": "healthy",
        "service": "FeynmanCraft SSE Server",
        "version": "1.0.0",
        **stats
    }

@app.get("/stats")
async def statistics():
    """Get detailed server statistics"""
    return get_stats()

# Development utilities
@app.post("/test/agent-event")
async def test_agent_event(
    agent: str = "test_agent",
    event_type: str = "transfer", 
    trace_id: str = "test-trace",
    step_id: str = "test-step"
):
    """Test agent event emission"""
    publish({
        "type": f"step.{event_type}",
        "traceId": trace_id,
        "stepId": step_id,
        "agent": agent,
        "level": 2,
        "payload": {"summary": f"Test {event_type} event from {agent}"}
    })
    return {"status": "emitted", "type": f"step.{event_type}"}

@app.post("/test/mcp-event")
async def test_mcp_event(
    tool: str = "get_property",
    status: str = "ok",
    trace_id: str = "test-trace",
    latency_ms: int = 150
):
    """Test MCP tool call event"""
    publish({
        "type": "tool.end",
        "traceId": trace_id,
        "stepId": f"step-{tool}",
        "tool": tool,
        "status": status,
        "latency_ms": latency_ms,
        "level": 2,
        "payload": {"summary": f"Test {tool} call completed"}
    })
    return {"status": "emitted", "tool": tool}

if __name__ == "__main__":
    import uvicorn
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger.info("Starting FeynmanCraft SSE Server on port 8001")
    
    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        access_log=True
    )