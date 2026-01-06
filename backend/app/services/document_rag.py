"""
Document RAG (Retrieval-Augmented Generation) Service
Handles document chunking, embedding, and semantic search
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import hashlib
import os


class DocumentRAGService:
    """Document RAG for semantic search over tool documentation"""
    
    def __init__(self, use_llm_summary: bool = False, preload_model: bool = False):
        self.use_llm_summary = use_llm_summary
        self.summarizer = None
        self._model_loading = False
        
        # Initialize ChromaDB with persistent storage
        db_path = os.path.join(os.path.dirname(__file__), "../../data/chroma_db")
        os.makedirs(db_path, exist_ok=True)
        
        self.chroma_client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="tool_documents",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        # Optionally preload model in background
        if use_llm_summary and preload_model:
            import threading
            threading.Thread(target=self._background_load_model, daemon=True).start()
        
        # Use multilingual model (supports English and Chinese)
        print("Loading embedding model...")
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        print("Embedding model loaded successfully")
        
        # Optional: LLM summarization
        self.use_llm_summary = use_llm_summary
        self.summarizer = None
        if use_llm_summary:
            self._load_summarizer()
    
    def chunk_document(self, content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split document into overlapping chunks
        
        Args:
            content: Document text
            chunk_size: Target size of each chunk (characters)
            overlap: Overlap between chunks (characters)
            
        Returns:
            List of text chunks
        """
        if not content or not content.strip():
            return []
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_length = len(para)
            
            # If paragraph itself is too long, split it
            if para_length > chunk_size:
                words = para.split()
                temp_chunk = []
                temp_length = 0
                
                for word in words:
                    temp_chunk.append(word)
                    temp_length += len(word) + 1
                    
                    if temp_length >= chunk_size:
                        if current_chunk:
                            chunks.append(' '.join(current_chunk))
                            current_chunk = []
                            current_length = 0
                        
                        chunks.append(' '.join(temp_chunk))
                        temp_chunk = []
                        temp_length = 0
                
                if temp_chunk:
                    current_chunk.extend(temp_chunk)
                    current_length += temp_length
            else:
                # Add paragraph to current chunk
                if current_length + para_length > chunk_size and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    # Keep some overlap
                    if overlap > 0 and current_chunk:
                        overlap_words = ' '.join(current_chunk).split()[-10:]
                        current_chunk = overlap_words
                        current_length = sum(len(w) + 1 for w in overlap_words)
                    else:
                        current_chunk = []
                        current_length = 0
                
                current_chunk.append(para)
                current_length += para_length + 1
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _extract_key_sentences(self, content: str, query: str, max_sentences: int = 1) -> str:
        """
        Extract the sentence(s) containing the most query keywords
        
        Args:
            content: Document chunk content
            query: User's search query
            max_sentences: Maximum number of sentences to return (default: 1)
            
        Returns:
            The sentence(s) containing search keywords
        """
        import re
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not sentences:
            return content[:200] + "..." if len(content) > 200 else content
        
        # Extract query keywords
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        query_keywords = query_words - common_words
        
        if not query_keywords:
            return sentences[0][:250] + "..." if len(sentences[0]) > 250 else sentences[0]
        
        # Find sentence with most keyword matches
        best_sentence = ""
        max_matches = 0
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Count keyword matches
            matches = sum(1 for kw in query_keywords if kw in sentence_lower)
            if matches > max_matches:
                max_matches = matches
                best_sentence = sentence
        
        # If no keywords found, return first substantial sentence
        if max_matches == 0:
            best_sentence = sentences[0]
        
        # Truncate if too long
        if len(best_sentence) > 300:
            best_sentence = best_sentence[:297] + "..."
        
        return best_sentence
    
    def _background_load_model(self):
        """Load model in background thread"""
        print("🚀 Starting background model loading (this may take 5-15 minutes)...")
        self._model_loading = True
        self._load_summarizer()
        self._model_loading = False
        if self.summarizer:
            print("✅ LLM model loaded and ready!")
    
    def _load_summarizer(self):
        """Lazy load the summarization model"""
        try:
            from transformers import pipeline
            import torch
            
            print("Loading summarization model (this may take a minute)...")
            
            # Use CPU if no GPU available
            device = 0 if torch.cuda.is_available() else -1
            
            # Load a lightweight summarization model
            # facebook/bart-large-cnn is good but large (~1.6GB)
            # sshleifer/distilbart-cnn-12-6 is smaller (~600MB) and faster
            self.summarizer = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-12-6",
                device=device
            )
            
            print(f"Summarization model loaded on {'GPU' if device == 0 else 'CPU'}")
        except Exception as e:
            print(f"Failed to load summarization model: {e}")
            print("Falling back to extractive summarization")
            self.summarizer = None
            self.use_llm_summary = False
    
    def _generate_llm_summary(self, content: str, query: str = "", max_length: int = 130) -> str:
        """
        Generate query-focused summary using LLM
        
        Args:
            content: Text to summarize
            query: Search query to focus the summary on
            max_length: Maximum length of summary
            
        Returns:
            Query-focused summary
        """
        # Wait if model is loading in background
        if self._model_loading:
            print("⏳ Model still loading in background, falling back to extraction...")
            return self._extract_key_sentences(content, query)
        
        # Lazy load if not loaded yet and not currently loading
        if not self.summarizer and self.use_llm_summary and not self._model_loading:
            print("Loading LLM summarization model (first time only, ~600MB)...")
            self._load_summarizer()
        
        if not self.summarizer or not content.strip():
            return self._extract_key_sentences(content, query)
        
        try:
            # Truncate content if too long (model has input limit)
            if len(content) > 1024:
                content = content[:1024]
            
            # Prefix content with query context for focused summarization
            if query:
                focused_content = f"Regarding '{query}': {content}"
            else:
                focused_content = content
            
            # Calculate appropriate max_length based on input
            # For summarization, output should be shorter than input
            input_tokens = len(content.split())
            adaptive_max_length = min(max_length, max(30, input_tokens // 2))
            
            # Generate summary
            result = self.summarizer(
                focused_content,
                max_length=adaptive_max_length,
                min_length=min(20, adaptive_max_length - 10),
                do_sample=False,
                truncation=True
            )
            
            summary = result[0]['summary_text']
            # Remove the query prefix if it appears in the output
            if query and summary.startswith("Regarding"):
                summary = summary.split(": ", 1)[-1]
            return summary
            
        except Exception as e:
            print(f"LLM summarization failed: {e}, falling back to extraction")
            return self._extract_key_sentences(content, query)
    
    def index_document(
        self, 
        tool_id: str, 
        tool_name: str,
        doc_url: str, 
        content: str,
        doc_type: str = "confluence"
    ) -> int:
        """
        Index document content into vector database
        
        Args:
            tool_id: Unique tool identifier
            tool_name: Tool name for display
            doc_url: URL of the document
            content: Document text content
            doc_type: Type of document (confluence, readme, etc.)
            
        Returns:
            Number of chunks indexed
        """
        if not content or not content.strip():
            print(f"Warning: Empty content for {tool_name}")
            return 0
        
        # Split into chunks
        chunks = self.chunk_document(content)
        
        if not chunks:
            print(f"Warning: No chunks generated for {tool_name}")
            return 0
        
        print(f"Indexing {len(chunks)} chunks for {tool_name}...")
        
        # Generate unique IDs for each chunk
        chunk_ids = [
            hashlib.md5(f"{tool_id}_{doc_url}_{i}".encode()).hexdigest()
            for i in range(len(chunks))
        ]
        
        # Generate embeddings
        embeddings = self.model.encode(chunks, show_progress_bar=True).tolist()
        
        # Prepare metadata
        metadatas = [
            {
                "tool_id": tool_id,
                "tool_name": tool_name,
                "doc_url": doc_url,
                "doc_type": doc_type,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            for i in range(len(chunks))
        ]
        
        # Store in vector database
        try:
            self.collection.upsert(
                ids=chunk_ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas
            )
            print(f"Successfully indexed {len(chunks)} chunks for {tool_name}")
            return len(chunks)
        except Exception as e:
            print(f"Error indexing {tool_name}: {e}")
            return 0
    
    def delete_tool_documents(self, tool_id: str) -> bool:
        """
        Delete all document chunks for a tool
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            True if successful
        """
        try:
            # Query all chunks for this tool
            results = self.collection.get(
                where={"tool_id": tool_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"Deleted {len(results['ids'])} chunks for tool {tool_id}")
            
            return True
        except Exception as e:
            print(f"Error deleting documents for tool {tool_id}: {e}")
            return False
    
    def search(
        self, 
        query: str, 
        top_k: int = 10,
        min_score: float = 0.3,
        tool_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Semantic search over indexed documents
        
        Args:
            query: Search query in natural language
            top_k: Maximum number of results
            min_score: Minimum similarity score (0-1)
            tool_ids: Optional filter by specific tool IDs
            
        Returns:
            List of search results with content, metadata, and scores
        """
        if not query or not query.strip():
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode([query], show_progress_bar=False)[0].tolist()
        
        # Prepare filter
        where_filter = {"tool_id": {"$in": tool_ids}} if tool_ids else None
        
        # Search in vector database
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            print(f"Search error: {e}")
            return []
        
        if not results['documents'] or not results['documents'][0]:
            return []
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            # Convert distance to similarity score (0-1)
            # ChromaDB returns squared euclidean distance
            distance = results['distances'][0][i]
            similarity = 1 / (1 + distance)  # Convert to 0-1 range
            
            if similarity >= min_score:
                content = results['documents'][0][i]
                
                # Generate query-focused summary based on configuration
                if self.use_llm_summary and self.summarizer:
                    # Use LLM to generate query-focused summary
                    summary = self._generate_llm_summary(content, query)
                else:
                    # Use fast extractive summarization (already query-focused)
                    summary = self._extract_key_sentences(content, query)
                
                formatted_results.append({
                    "content": content,
                    "summary": summary,  # Smart extracted summary
                    "tool_id": results['metadatas'][0][i]['tool_id'],
                    "tool_name": results['metadatas'][0][i]['tool_name'],
                    "doc_url": results['metadatas'][0][i]['doc_url'],
                    "doc_type": results['metadatas'][0][i]['doc_type'],
                    "chunk_index": results['metadatas'][0][i]['chunk_index'],
                    "relevance_score": round(similarity, 3)
                })
        
        return formatted_results
    
    def get_stats(self) -> Dict:
        """Get statistics about indexed documents"""
        try:
            collection_data = self.collection.get()
            total_chunks = len(collection_data['ids']) if collection_data['ids'] else 0
            
            # Count unique tools
            unique_tools = set()
            if collection_data['metadatas']:
                for metadata in collection_data['metadatas']:
                    unique_tools.add(metadata['tool_id'])
            
            return {
                "total_chunks": total_chunks,
                "total_tools": len(unique_tools),
                "model": self.model.get_sentence_embedding_dimension()
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"total_chunks": 0, "total_tools": 0, "error": str(e)}


# Global instance - Fast extractive summarization only
rag_service = DocumentRAGService(use_llm_summary=False)
