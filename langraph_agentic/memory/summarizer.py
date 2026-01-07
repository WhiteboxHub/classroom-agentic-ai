"""
Conversation Summarizer
Summarizes long conversation histories to maintain context.
"""
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
import logging

logger = logging.getLogger(__name__)


class ConversationSummarizer:
    """
    Summarizes conversation history to maintain context window.
    """
    
    def __init__(self):
        self.llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
            temperature=0.1,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a conversation summarizer.
Summarize the conversation history, preserving:
- Key customer information (account numbers, claim numbers, etc.)
- Important decisions made
- Outstanding issues or follow-ups
- Customer preferences or context

Keep the summary concise but informative."""),
            ("user", "Summarize this conversation:\n\n{conversation}")
        ])
    
    def summarize(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Summarize conversation history.
        
        Args:
            conversation_history: List of dicts with 'user' and 'assistant' keys
            
        Returns:
            Summary string
        """
        if not conversation_history:
            return ""
        
        if len(conversation_history) < 3:
            # No need to summarize short conversations
            return self._format_history(conversation_history)
        
        try:
            # Format conversation for summarization
            formatted = self._format_history(conversation_history)
            
            # Generate summary
            chain = self.prompt | self.llm
            summary = chain.invoke({"conversation": formatted})
            
            logger.info("Generated conversation summary")
            return summary.content
        
        except Exception as e:
            logger.error(f"Error summarizing conversation: {e}", exc_info=True)
            # Fallback to formatted history
            return self._format_history(conversation_history[-5:])  # Last 5 turns
    
    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history as string"""
        formatted_parts = []
        for i, turn in enumerate(history, 1):
            user_msg = turn.get("user", "")
            assistant_msg = turn.get("assistant", "")
            
            formatted_parts.append(f"Turn {i}:")
            formatted_parts.append(f"User: {user_msg}")
            if assistant_msg:
                formatted_parts.append(f"Assistant: {assistant_msg}")
            formatted_parts.append("")
        
        return "\n".join(formatted_parts)
    
    def summarize_recent(self, conversation_history: List[Dict[str, str]], keep_last_n: int = 3) -> str:
        """
        Summarize older history but keep recent turns.
        
        Args:
            conversation_history: Full conversation history
            keep_last_n: Number of recent turns to keep
            
        Returns:
            Summary + recent turns
        """
        if len(conversation_history) <= keep_last_n:
            return self._format_history(conversation_history)
        
        # Summarize older history
        older_history = conversation_history[:-keep_last_n]
        recent_history = conversation_history[-keep_last_n:]
        
        summary = self.summarize(older_history)
        recent = self._format_history(recent_history)
        
        return f"Previous conversation summary:\n{summary}\n\nRecent conversation:\n{recent}"

