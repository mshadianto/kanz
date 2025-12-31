"""
Document Ingestion Script
Loads initial Saudi Investment documents into the RAG system
"""
import asyncio
from pathlib import Path
from loguru import logger
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from document_processor import doc_processor
from database import db


async def ingest_documents():
    """Ingest initial documents into the system"""
    
    logger.info("Starting document ingestion...")
    
    # Define documents to ingest
    documents = [
        {
            "title": "Saudi Arabia Market Entry Strategy - Full Report",
            "file_path": "/mnt/user-data/outputs/Saudi_Arabia_Market_Entry_Strategy_McKinsey_Report.txt",
            "source": "mckinsey_strategic_analysis",
            "metadata": {
                "type": "strategic_report",
                "date": "2025-08",
                "author": "McKinsey & Company",
                "sections": [
                    "executive_summary",
                    "strategic_pillars",
                    "financial_analysis",
                    "risk_assessment",
                    "implementation_roadmap"
                ]
            }
        },
        {
            "title": "Executive One-Pager - Board Decision Brief",
            "file_path": "/mnt/user-data/outputs/Executive_One_Pager_Saudi_Investment.txt",
            "source": "executive_summary",
            "metadata": {
                "type": "executive_brief",
                "audience": "c_suite",
                "date": "2025-08"
            }
        }
    ]
    
    # Read and ingest each document
    for doc_info in documents:
        try:
            logger.info(f"Processing: {doc_info['title']}")
            
            # Read file content
            file_path = Path(doc_info['file_path'])
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue
            
            content = file_path.read_text(encoding='utf-8')
            
            # Ingest document
            doc_id = await doc_processor.process_and_index_document(
                title=doc_info['title'],
                content=content,
                source=doc_info['source'],
                metadata=doc_info['metadata']
            )
            
            logger.success(f"✓ Ingested: {doc_info['title']} (ID: {doc_id})")
            
        except Exception as e:
            logger.error(f"✗ Error ingesting {doc_info['title']}: {e}")
            continue
    
    logger.success("Document ingestion complete!")
    
    # Show summary
    result = db.client.table("documents").select("*", count="exact").execute()
    chunk_result = db.client.table("document_chunks").select("*", count="exact").execute()
    
    logger.info(f"Total documents: {result.count if hasattr(result, 'count') else 'N/A'}")
    logger.info(f"Total chunks: {chunk_result.count if hasattr(chunk_result, 'count') else 'N/A'}")


if __name__ == "__main__":
    asyncio.run(ingest_documents())
