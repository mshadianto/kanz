"""
Document Processor for KANZ System
Handles document chunking and indexing
"""
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger
import re

from config import settings
from database import db
from embeddings import embeddings


class DocumentProcessor:
    """Process and index documents for RAG"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        logger.info("Document processor initialized")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove excessive whitespace
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove box drawing characters (from formatted documents)
        text = re.sub(r'[─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬]', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        clean_text = self.clean_text(text)
        chunks = self.text_splitter.split_text(clean_text)
        logger.info(f"Text split into {len(chunks)} chunks")
        return chunks
    
    async def process_and_index_document(
        self,
        title: str,
        content: str,
        source: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Process a document: chunk, embed, and index
        
        Args:
            title: Document title
            content: Document content
            source: Source identifier
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        try:
            logger.info(f"Processing document: {title}")
            
            # Create document record
            doc_id = await db.create_document(
                title=title,
                content=content,
                source=source,
                metadata=metadata or {}
            )
            
            # Chunk the content
            chunks = self.chunk_text(content)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Generate embeddings for all chunks
            logger.info("Generating embeddings...")
            chunk_embeddings = embeddings.embed_batch(chunks)
            
            # Prepare chunk data
            chunk_data = [
                {
                    "content": chunk,
                    "index": idx,
                    "embedding": embedding,
                    "metadata": {
                        "title": title,
                        "source": source,
                        "chunk_length": len(chunk)
                    }
                }
                for idx, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings))
            ]
            
            # Store chunks in database
            logger.info("Storing chunks in database...")
            await db.create_chunks(doc_id, chunk_data)
            
            logger.success(f"Document indexed successfully: {title} ({doc_id})")
            return str(doc_id)
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise
    
    async def search_documents(
        self,
        query: str,
        top_k: int = None,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks
        
        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Similarity threshold
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            # Generate query embedding
            query_embedding = embeddings.embed_text(query)
            
            # Search similar chunks
            k = top_k or settings.top_k_results
            results = await db.search_similar_chunks(
                query_embedding=query_embedding,
                top_k=k,
                threshold=threshold
            )
            
            logger.info(f"Found {len(results)} relevant chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def extract_key_sections(self, text: str, keywords: List[str]) -> List[str]:
        """
        Extract sections containing specific keywords
        
        Args:
            text: Full text
            keywords: List of keywords to search for
            
        Returns:
            List of relevant sections
        """
        sections = []
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if any(keyword.lower() in para.lower() for keyword in keywords):
                sections.append(para.strip())
        
        return sections


# Global document processor instance
doc_processor = DocumentProcessor()
