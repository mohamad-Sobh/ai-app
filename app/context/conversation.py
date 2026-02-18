"""
Conversation Context Management for multi-turn awareness.

Tracks user intent history, recent topics, tool usage, and unresolved queries
per thread_id to enable proactive, context-aware responses.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from app.utils import LRUDict


@dataclass
class ConversationTurn:
    """Represents a single conversation turn with metadata."""
    timestamp: datetime
    user_message: str
    detected_language: str
    tools_used: List[str] = field(default_factory=list)
    tool_results_summary: Dict[str, str] = field(default_factory=dict)
    topics_discussed: List[str] = field(default_factory=list)
    intent_detected: Optional[str] = None
    was_clarification_needed: bool = False
    user_sentiment: Optional[str] = None  # positive, neutral, frustrated


@dataclass
class ConversationContext:
    """
    Holds the complete context for a single conversation thread.

    This context is injected into the system prompt to enable:
    - Multi-turn awareness (remembering previous topics)
    - Proactive suggestions based on conversation flow
    - Intent clarification when queries are ambiguous
    - Personalized responses based on user history
    """
    thread_id: str
    created_at: datetime = field(default_factory=datetime.now)
    turns: List[ConversationTurn] = field(default_factory=list)

    # Aggregated context for quick access
    all_topics_discussed: List[str] = field(default_factory=list)
    all_tools_used: List[str] = field(default_factory=list)
    pending_suggestions: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)

    # Conversation state
    is_first_interaction: bool = True
    last_interaction: Optional[datetime] = None
    unresolved_query: Optional[str] = None
    conversation_goal: Optional[str] = None  # e.g., "renew civil id", "get digital signature"

    # User profile hints (inferred from conversation)
    inferred_user_type: Optional[str] = None  # citizen, resident, business
    mentioned_services: List[str] = field(default_factory=list)

    def add_turn(self, turn: ConversationTurn) -> None:
        """Add a new conversation turn and update aggregated context."""
        self.turns.append(turn)
        self.is_first_interaction = False
        self.last_interaction = turn.timestamp

        # Update aggregates
        for topic in turn.topics_discussed:
            if topic not in self.all_topics_discussed:
                self.all_topics_discussed.append(topic)

        for tool in turn.tools_used:
            if tool not in self.all_tools_used:
                self.all_tools_used.append(tool)

    def get_recent_turns(self, count: int = 3) -> List[ConversationTurn]:
        """Get the most recent N turns for context injection."""
        return self.turns[-count:] if self.turns else []

    def get_context_summary(self) -> str:
        """
        Generate a concise context summary for system prompt injection.

        Returns a formatted string that helps the LLM understand:
        - What topics have been discussed
        - What tools were used
        - Any pending/unresolved queries
        - User's apparent goal
        """
        if not self.turns:
            return "This is the start of a new conversation."

        lines = []

        # Conversation history summary
        lines.append(f"**Conversation History:** {len(self.turns)} previous exchanges")

        # Recent topics
        if self.all_topics_discussed:
            recent_topics = self.all_topics_discussed[-5:]  # Last 5 topics
            lines.append(f"**Recent Topics:** {', '.join(recent_topics)}")

        # Services mentioned
        if self.mentioned_services:
            lines.append(f"**Services Discussed:** {', '.join(self.mentioned_services)}")

        # User's goal if detected
        if self.conversation_goal:
            lines.append(f"**User's Goal:** {self.conversation_goal}")

        # Unresolved query
        if self.unresolved_query:
            lines.append(f"**Pending Question:** {self.unresolved_query}")

        # Pending proactive suggestions
        if self.pending_suggestions:
            lines.append(f"**Consider Suggesting:** {', '.join(self.pending_suggestions[:2])}")

        return "\n".join(lines)

    def to_prompt_context(self) -> str:
        """Format context for direct injection into system prompt."""
        if self.is_first_interaction:
            return """
## CONVERSATION CONTEXT
This is a **new conversation**. The user is reaching out for the first time in this session.
- Greet them warmly and establish rapport
- Be ready to help with any PACI-related inquiry
"""

        summary = self.get_context_summary()
        return f"""
## CONVERSATION CONTEXT
{summary}

**Guidelines based on context:**
- Reference previous topics naturally when relevant
- If the user seems to be continuing a previous thread, acknowledge it
- Proactively offer related services based on what they've discussed
- Remember their language preference and communication style
"""


class ConversationMemory:
    """
    Thread-safe conversation memory store using LRU eviction.

    Manages ConversationContext instances across multiple threads,
    automatically evicting old conversations when memory limit is reached.
    """

    def __init__(self, max_threads: int = 500, max_turns_per_thread: int = 50):
        """
        Initialize the conversation memory store.

        Args:
            max_threads: Maximum number of conversation threads to keep in memory
            max_turns_per_thread: Maximum turns to keep per conversation (older turns evicted)
        """
        self._contexts: LRUDict = LRUDict(max_size=max_threads)
        self._max_turns = max_turns_per_thread

    def get_context(self, thread_id: str) -> ConversationContext:
        """
        Get or create a conversation context for the given thread.

        Args:
            thread_id: Unique identifier for the conversation thread

        Returns:
            ConversationContext instance (existing or newly created)
        """
        context = self._contexts.get(thread_id)
        if context is None:
            context = ConversationContext(thread_id=thread_id)
            self._contexts[thread_id] = context
        return context

    def update_context(
        self,
        thread_id: str,
        user_message: str,
        detected_language: str,
        tools_used: Optional[List[str]] = None,
        tool_results_summary: Optional[Dict[str, str]] = None,
        topics_discussed: Optional[List[str]] = None,
        intent_detected: Optional[str] = None,
    ) -> ConversationContext:
        """
        Record a new conversation turn and update the context.

        Args:
            thread_id: Conversation thread identifier
            user_message: The user's message text
            detected_language: Language detected in the message
            tools_used: List of tool names that were executed
            tool_results_summary: Brief summary of tool results
            topics_discussed: Topics identified in this turn
            intent_detected: Primary intent of the user's message

        Returns:
            Updated ConversationContext
        """
        context = self.get_context(thread_id)

        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_message=user_message,
            detected_language=detected_language,
            tools_used=tools_used or [],
            tool_results_summary=tool_results_summary or {},
            topics_discussed=topics_discussed or [],
            intent_detected=intent_detected,
        )

        context.add_turn(turn)

        # Evict old turns if over limit
        if len(context.turns) > self._max_turns:
            context.turns = context.turns[-self._max_turns:]

        # Update the context in LRU (marks as recently used)
        self._contexts[thread_id] = context

        return context

    def add_pending_suggestion(self, thread_id: str, suggestion: str) -> None:
        """Add a proactive suggestion to be offered to the user."""
        context = self.get_context(thread_id)
        if suggestion not in context.pending_suggestions:
            context.pending_suggestions.append(suggestion)
            # Keep only last 5 suggestions
            context.pending_suggestions = context.pending_suggestions[-5:]

    def clear_pending_suggestions(self, thread_id: str) -> None:
        """Clear pending suggestions after they've been offered."""
        context = self.get_context(thread_id)
        context.pending_suggestions = []

    def set_conversation_goal(self, thread_id: str, goal: str) -> None:
        """Set the detected user goal for this conversation."""
        context = self.get_context(thread_id)
        context.conversation_goal = goal

    def add_mentioned_service(self, thread_id: str, service: str) -> None:
        """Track a PACI service that was discussed."""
        context = self.get_context(thread_id)
        if service not in context.mentioned_services:
            context.mentioned_services.append(service)

    def get_thread_count(self) -> int:
        """Get the current number of active conversation threads."""
        return len(self._contexts)