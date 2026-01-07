"""
Vector Store for Memory
Stores and retrieves conversation context using vector embeddings.
"""
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector store for semantic search over conversation history.
    Uses ChromaDB for storage with local embeddings.
    """
    
    def __init__(self):
        # Use local embeddings instead of OpenAI
        embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model
        )
        self.persist_directory = os.getenv("VECTOR_STORE_PATH", "./chroma_db")
        
        # Initialize ChromaDB
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="conversation_memory"
            )
            logger.info("Loaded existing vector store")
        except Exception as e:
            logger.warning(f"Could not load existing vector store: {e}. Creating new one.")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="conversation_memory"
            )
    
    def add_conversation(
        self,
        session_id: str,
        query: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a conversation turn to the vector store.
        
        Args:
            session_id: Session identifier
            query: User query
            response: Agent response
            metadata: Additional metadata
        """
        try:
            # Combine query and response for context
            text = f"Query: {query}\nResponse: {response}"
            
            doc_metadata = {
                "session_id": session_id,
                "type": "conversation",
                **(metadata or {})
            }
            
            document = Document(
                page_content=text,
                metadata=doc_metadata
            )
            
            self.vectorstore.add_documents([document])
            logger.info(f"Added conversation to vector store for session: {session_id}")
        
        except Exception as e:
            logger.error(f"Error adding conversation to vector store: {e}", exc_info=True)
    
    def search_similar(
        self,
        query: str,
        session_id: Optional[str] = None,
        k: int = 3
    ) -> List[Document]:
        """
        Search for similar conversations.
        
        Args:
            query: Search query
            session_id: Optional session ID to filter by
            k: Number of results to return
            
        Returns:
            List of similar documents
        """
        try:
            # Build search filter if session_id provided
            search_kwargs = {"k": k}
            if session_id:
                search_kwargs["filter"] = {"session_id": session_id}
            
            results = self.vectorstore.similarity_search(
                query,
                k=k,
                **search_kwargs
            )
            
            logger.info(f"Found {len(results)} similar conversations")
            return results
        
        except Exception as e:
            logger.error(f"Error searching vector store: {e}", exc_info=True)
            return []
    
    def get_context(self, query: str, session_id: Optional[str] = None) -> str:
        """
        Get relevant context from past conversations.
        
        Args:
            query: Current query
            session_id: Optional session ID
            
        Returns:
            Context string from similar conversations
        """
        similar_docs = self.search_similar(query, session_id=session_id, k=2)
        
        if not similar_docs:
            return ""
        
        context_parts = []
        for doc in similar_docs:
            context_parts.append(doc.page_content)
        
        return "\n\n---\n\n".join(context_parts)

