"""
Main FastAPI Application for KANZ System
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from loguru import logger
import sys
from datetime import datetime

from config import settings
from database import db
from document_processor import doc_processor
from agents import coordinator, AgentType

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO" if not settings.debug else "DEBUG")
logger.add("logs/app_{time}.log", rotation="1 day", retention="7 days")

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Uncover Hidden Opportunities in the Heart of the Desert"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Pydantic Models ====================

class QueryRequest(BaseModel):
    """Request model for chat queries"""
    query: str = Field(..., description="User query")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    agent_type: Optional[str] = Field(None, description="Specific agent to use")


class QueryResponse(BaseModel):
    """Response model for chat queries"""
    response: str
    agent_type: str
    sources: List[Dict[str, Any]]
    session_id: str
    response_time_ms: int


class SessionCreate(BaseModel):
    """Request model for creating a session"""
    session_name: Optional[str] = None


class SessionResponse(BaseModel):
    """Response model for session info"""
    id: str
    session_name: str
    created_at: str
    message_count: int = 0


class DocumentUpload(BaseModel):
    """Request model for document upload"""
    title: str
    content: str
    source: str = "user_upload"
    metadata: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str


# ==================== Startup & Shutdown ====================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Model: {settings.llm_model}")
    logger.info(f"Embedding Model: {settings.embedding_model}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")


# ==================== Health & Info Endpoints ====================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/agents")
async def list_agents():
    """List available specialized agents"""
    return {
        "agents": [
            {
                "type": "strategic",
                "name": "Strategic Analyst",
                "description": "Market entry strategy, Vision 2030 analysis, competitive positioning",
                "icon": "🎯"
            },
            {
                "type": "financial",
                "name": "Financial Advisor",
                "description": "Tax optimization, ROI analysis, incentive calculations",
                "icon": "💰"
            },
            {
                "type": "risk",
                "name": "Risk Assessor",
                "description": "Regulatory compliance, geopolitical risk, mitigation strategies",
                "icon": "⚠️"
            },
            {
                "type": "general",
                "name": "General Advisor",
                "description": "General questions and comprehensive overviews",
                "icon": "💡"
            }
        ]
    }


# ==================== Chat Endpoints ====================

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Process a user query through the RAG system
    """
    try:
        logger.info(f"Processing query: {request.query[:100]}...")
        
        # Get or create session
        if request.session_id:
            session_id = UUID(request.session_id)
            session = await db.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session_id = await db.create_session()
        
        # Get chat history
        history = await db.get_session_messages(session_id)
        
        # Determine agent type
        agent_type = None
        if request.agent_type:
            try:
                agent_type = AgentType(request.agent_type)
            except ValueError:
                logger.warning(f"Invalid agent type: {request.agent_type}")
        
        # Process query
        response = await coordinator.process_query(
            query=request.query,
            agent_type=agent_type,
            chat_history=history
        )
        
        # Save messages to database
        await db.add_message(
            session_id=session_id,
            role="user",
            content=request.query
        )
        
        await db.add_message(
            session_id=session_id,
            role="assistant",
            content=response["content"],
            agent_type=response["agent_type"],
            sources=response["sources"]
        )
        
        # Log analytics
        await db.log_query(
            session_id=session_id,
            query=request.query,
            agent_type=response["agent_type"],
            response_time_ms=response["response_time_ms"],
            sources_retrieved=len(response["sources"])
        )
        
        return QueryResponse(
            response=response["content"],
            agent_type=response["agent_type"],
            sources=response["sources"],
            session_id=str(session_id),
            response_time_ms=response["response_time_ms"]
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Session Management ====================

@app.post("/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreate):
    """Create a new chat session"""
    try:
        session_id = await db.create_session(session_name=request.session_name)
        session = await db.get_session(session_id)
        
        return SessionResponse(
            id=str(session["id"]),
            session_name=session["session_name"],
            created_at=session["created_at"],
            message_count=0
        )
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions")
async def list_sessions(limit: int = 20):
    """List recent chat sessions"""
    try:
        sessions = await db.list_sessions(limit=limit)
        
        # Get message counts for each session
        session_list = []
        for session in sessions:
            messages = await db.get_session_messages(UUID(session["id"]))
            session_list.append({
                "id": session["id"],
                "session_name": session["session_name"],
                "created_at": session["created_at"],
                "updated_at": session["updated_at"],
                "message_count": len(messages)
            })
        
        return {"sessions": session_list}
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details with messages"""
    try:
        session_uuid = UUID(session_id)
        session = await db.get_session(session_uuid)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = await db.get_session_messages(session_uuid)
        
        return {
            "session": session,
            "messages": messages
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session"""
    try:
        # Note: Deletion cascades to messages automatically
        session_uuid = UUID(session_id)
        
        # Verify session exists
        session = await db.get_session(session_uuid)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete from database
        db.client.table("chat_sessions").delete().eq("id", session_id).execute()
        
        return {"message": "Session deleted successfully"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Document Management ====================

@app.post("/documents")
async def upload_document(doc: DocumentUpload):
    """Upload and index a new document"""
    try:
        doc_id = await doc_processor.process_and_index_document(
            title=doc.title,
            content=doc.content,
            source=doc.source,
            metadata=doc.metadata
        )
        
        return {
            "message": "Document indexed successfully",
            "document_id": doc_id
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_documents():
    """List all indexed documents"""
    try:
        result = db.client.table("documents")\
            .select("id, title, source, created_at")\
            .order("created_at", desc=True)\
            .execute()
        
        return {"documents": result.data}
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/search")
async def search_documents(query: str, top_k: int = 5):
    """Search for relevant document chunks"""
    try:
        results = await doc_processor.search_documents(
            query=query,
            top_k=top_k
        )
        
        return {"results": results}
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Analytics ====================

@app.get("/analytics")
async def get_analytics():
    """Get system analytics"""
    try:
        analytics = await db.get_analytics_summary()
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
