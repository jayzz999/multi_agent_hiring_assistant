"""Base agent class for all hiring assistant agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import settings


class BaseAgent(ABC):
    """Abstract base class for all agents in the hiring assistant system."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tools: Optional[List[Any]] = None,
        temperature: float = 0.7,
        model: Optional[str] = None
    ):
        """
        Initialize the base agent.

        Args:
            name: Agent name for identification
            system_prompt: System prompt defining agent behavior
            tools: Optional list of tools the agent can use
            temperature: LLM temperature (0.0-1.0)
            model: Optional model override (default from settings)
        """
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.temperature = temperature
        self.model = model or settings.LLM_MODEL

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=temperature,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # Bind tools if provided
        if self.tools:
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        else:
            self.llm_with_tools = self.llm

        # Metrics tracking
        self.last_execution_time: float = 0
        self.last_token_count: int = 0

    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's primary task.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state
        """
        pass

    def invoke(self, messages: List[BaseMessage]) -> str:
        """
        Invoke the LLM with messages.

        Args:
            messages: List of messages (will prepend system prompt)

        Returns:
            LLM response content
        """
        start_time = time.time()

        # Prepend system message
        full_messages = [SystemMessage(content=self.system_prompt)] + messages

        # Invoke LLM
        response = self.llm.invoke(full_messages)

        # Track execution time
        self.last_execution_time = time.time() - start_time

        # Estimate token count (rough approximation)
        total_chars = sum(len(m.content) for m in full_messages) + len(response.content)
        self.last_token_count = total_chars // 4  # Rough token estimate

        return response.content

    def invoke_with_tools(self, messages: List[BaseMessage]) -> Any:
        """
        Invoke the LLM with tool support.

        Args:
            messages: List of messages

        Returns:
            LLM response (may include tool calls)
        """
        full_messages = [SystemMessage(content=self.system_prompt)] + messages
        return self.llm_with_tools.invoke(full_messages)

    def chat(self, user_message: str) -> str:
        """
        Simple chat interface for single messages.

        Args:
            user_message: User's message

        Returns:
            Agent's response
        """
        return self.invoke([HumanMessage(content=user_message)])

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get agent metrics from last execution.

        Returns:
            Dictionary with execution metrics
        """
        return {
            "agent_name": self.name,
            "execution_time": self.last_execution_time,
            "estimated_tokens": self.last_token_count,
            "model": self.model,
            "temperature": self.temperature
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', model='{self.model}')"

    def __str__(self) -> str:
        return f"{self.name} Agent"
