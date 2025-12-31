"""
Embedding Manager for KANZ System
Handles text embeddings using sentence-transformers
"""
from typing import List, Union
from sentence_transformers import SentenceTransformer
from loguru import logger
import numpy as np

from config import settings


class EmbeddingManager:
    """Manage text embeddings for RAG system"""
    
    def __init__(self):
        self.model_name = settings.embedding_model
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding model loaded. Dimension: {self.dimension}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embeddings
        """
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error embedding batch: {e}")
            raise
    
    def compute_similarity(
        self,
        embedding1: Union[List[float], np.ndarray],
        embedding2: Union[List[float], np.ndarray]
    ) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score (0-1)
        """
        try:
            e1 = np.array(embedding1)
            e2 = np.array(embedding2)
            
            similarity = np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))
            return float(similarity)
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0


# Global embedding manager instance
embeddings = EmbeddingManager()
