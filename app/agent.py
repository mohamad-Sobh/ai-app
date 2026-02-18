from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from gagent_core.base_agent import BaseChatAgent
from gagent_core.websocket_manager import ConnectionManager
from gagent_core.settings import settings
from gagent_core.logs import logger


class MyAgent(BaseChatAgent):
    """
    Reusable template for a g-agent Core backend agent.
    - Uses step tracking (update_step)
    - Can store and restore session state
    - Structured to be easy to customize
    """

    def __init__(self, manager: ConnectionManager):
        super().__init__(manager=manager)
        self.agent_type = "custom"
        self.last_message_by = "default"
        self.thought_mapping = {
            "init": "Initializing session",
            "plan": "Planning response",
            "act": "Executing tools",
            "final": "Finalizing response",
        }

    def system_prompt(self) -> str:
        """
        Optional: Add your custom system prompt.
        This composes with BaseChatAgent's system prompt.
        """
        additional = """
        ## CUSTOM GUIDELINES:
        - Be concise and accurate.
        - Ask for clarification when needed.
        """
        return super().system_prompt() + "\n\n" + additional

    async def process_message(
        self,
        thread_id: str,
        query: str,
        user_name: Optional[str],
        user_context: Optional[Dict[str, Any]],
        files: Optional[List[Dict[str, Any]]],
        metadata: Optional[Dict[str, Any]],
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Main processing entry point.
        Return (response_text, metadata_dict).
        """
        # Step 0: Initialize
        await self.update_step(thread_id, 0)

        state = await self.load_state(thread_id) or {}
        state["last_query"] = query

        # Step 1: Plan / gather info
        await self.update_step(thread_id, 1)
        plan = self._plan_response(query, user_context)

        # Step 2: Act / run tools
        await self.update_step(thread_id, 2)
        answer = self._execute_plan(plan)

        # Step 3: Finalize
        await self.update_step(thread_id, 3)
        response = self._format_response(answer)

        await self.save_state(thread_id, state)

        meta = metadata or {}
        meta.update({"plan": plan})
        return response, meta

    # ---------------------------
    # Internal helpers
    # ---------------------------
    def _plan_response(self, query: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "intent": "general_assistance",
            "query": query,
            "context": user_context or {},
        }

    def _execute_plan(self, plan: Dict[str, Any]) -> str:
        # Replace with tool calls or LLM inference
        return f"I understood your request: {plan['query']}"

    def _format_response(self, content: str) -> str:
        return content