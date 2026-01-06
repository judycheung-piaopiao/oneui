import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from app.models.tool import Tool

# Use lightweight model (only 80MB)
# Supports 100+ languages including English and Chinese
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'


class AISearchService:
    """Semantic search using vector embeddings"""
    
    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.embeddings: Optional[np.ndarray] = None
        self.tools: List[Tool] = []
        
    def initialize(self):
        """Load the model (called on first search)"""
        if self.model is None:
            print("Loading AI search model (first time only)...")
            self.model = SentenceTransformer(MODEL_NAME)
            print("AI search model loaded successfully")
    
    def update_embeddings(self, tools: List[Tool]):
        """Generate embeddings for all tools"""
        self.initialize()
        self.tools = tools
        
        if not tools:
            self.embeddings = np.array([])
            return
        
        # Combine tool information into searchable text
        texts = []
        for tool in tools:
            # Use name, description, and keywords for AI search
            text = f"{tool.name} {tool.description}"
            if tool.keywords:
                text += " " + tool.keywords
            texts.append(text)
        
        # Generate embeddings
        self.embeddings = self.model.encode(texts, show_progress_bar=False)
    
    def search(
        self, 
        query: str, 
        tools: List[Tool], 
        top_k: int = 6,
        min_score: float = 0.1
    ) -> List[tuple[Tool, float]]:
        """
        Semantic search for tools
        
        Args:
            query: Search query in natural language
            tools: List of tools to search from
            top_k: Number of results to return
            min_score: Minimum similarity score (0-1)
            
        Returns:
            List of (tool, score) tuples sorted by relevance
        """
        self.initialize()
        
        # Update embeddings if tools changed
        if len(tools) != len(self.tools) or tools != self.tools:
            self.update_embeddings(tools)
        
        if not tools or self.embeddings.size == 0:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query], show_progress_bar=False)[0]
        
        # Calculate cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top results above threshold
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= min_score:
                results.append((tools[idx], score))
        
        return results

ai_search_service = AISearchService()
