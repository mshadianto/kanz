"""
Database Manager for KANZ System
Handles all database operations with Supabase
"""
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from supabase import create_client, Client
from loguru import logger
import numpy as np

from config import settings


class DatabaseManager:
    """Manage database operations for RAG system"""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        logger.info("Database manager initialized")
    
    # ==================== Document Operations ====================
    
    async def create_document(
        self, 
        title: str, 
        content: str, 
        source: str,
        metadata: Dict[str, Any] = None
    ) -> UUID:
        """Create a new document"""
        try:
            data = {
                "title": title,
                "content": content,
                "source": source,
                "metadata": metadata or {}
            }
            
            result = self.client.table("documents").insert(data).execute()
            doc_id = UUID(result.data[0]["id"])
            logger.info(f"Created document: {title} ({doc_id})")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise
    
    async def get_document(self, document_id: UUID) -> Optional[Dict]:
        """Get document by ID"""
        try:
            result = self.client.table("documents")\
                .select("*")\
                .eq("id", str(document_id))\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
    
    # ==================== Chunk Operations ====================
    
    async def create_chunks(
        self,
        document_id: UUID,
        chunks: List[Dict[str, Any]]
    ) -> List[UUID]:
        """Create multiple chunks for a document"""
        try:
            chunk_data = [
                {
                    "document_id": str(document_id),
                    "content": chunk["content"],
                    "chunk_index": chunk["index"],
                    "embedding": chunk["embedding"],
                    "metadata": chunk.get("metadata", {})
                }
                for chunk in chunks
            ]
            
            result = self.client.table("document_chunks").insert(chunk_data).execute()
            chunk_ids = [UUID(item["id"]) for item in result.data]
            logger.info(f"Created {len(chunk_ids)} chunks for document {document_id}")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"Error creating chunks: {e}")
            raise
    
    async def search_similar_chunks(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks using vector similarity"""
        try:
            # Convert embedding to proper format
            embedding_str = f"[{','.join(map(str, query_embedding))}]"
            
            result = self.client.rpc(
                "match_document_chunks",
                {
                    "query_embedding": embedding_str,
                    "match_threshold": threshold,
                    "match_count": top_k
                }
            ).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            return []
    
    # ==================== Chat Session Operations ====================
    
    async def create_session(
        self,
        session_name: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> UUID:
        """Create a new chat session"""
        try:
            data = {
                "session_name": session_name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "metadata": metadata or {}
            }
            
            result = self.client.table("chat_sessions").insert(data).execute()
            session_id = UUID(result.data[0]["id"])
            logger.info(f"Created session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    async def get_session(self, session_id: UUID) -> Optional[Dict]:
        """Get session by ID"""
        try:
            result = self.client.table("chat_sessions")\
                .select("*")\
                .eq("id", str(session_id))\
                .execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    async def list_sessions(self, limit: int = 20) -> List[Dict]:
        """List recent chat sessions"""
        try:
            result = self.client.table("chat_sessions")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []
    
    # ==================== Message Operations ====================
    
    async def add_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        agent_type: Optional[str] = None,
        sources: List[Dict] = None
    ) -> UUID:
        """Add a message to a chat session"""
        try:
            data = {
                "session_id": str(session_id),
                "role": role,
                "content": content,
                "agent_type": agent_type,
                "sources": sources or []
            }
            
            result = self.client.table("chat_messages").insert(data).execute()
            message_id = UUID(result.data[0]["id"])
            return message_id
            
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise
    
    async def get_session_messages(
        self,
        session_id: UUID,
        limit: int = 50
    ) -> List[Dict]:
        """Get messages for a session"""
        try:
            result = self.client.table("chat_messages")\
                .select("*")\
                .eq("session_id", str(session_id))\
                .order("created_at", desc=False)\
                .limit(limit)\
                .execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    # ==================== Analytics Operations ====================
    
    async def log_query(
        self,
        session_id: UUID,
        query: str,
        agent_type: str,
        response_time_ms: int,
        tokens_used: int = 0,
        sources_retrieved: int = 0
    ):
        """Log query analytics"""
        try:
            data = {
                "session_id": str(session_id),
                "query": query,
                "agent_type": agent_type,
                "response_time_ms": response_time_ms,
                "tokens_used": tokens_used,
                "sources_retrieved": sources_retrieved
            }
            
            self.client.table("query_analytics").insert(data).execute()
            
        except Exception as e:
            logger.error(f"Error logging query: {e}")
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        try:
            # Total queries
            total_result = self.client.table("query_analytics")\
                .select("*", count="exact")\
                .execute()
            
            # Average response time
            avg_result = self.client.rpc(
                "get_avg_response_time"
            ).execute() if hasattr(self.client, "rpc") else None
            
            return {
                "total_queries": total_result.count if hasattr(total_result, "count") else 0,
                "avg_response_time": avg_result.data[0] if avg_result else None
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {}


# Global database manager instance
db = DatabaseManager()
