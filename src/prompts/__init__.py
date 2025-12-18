"""Agent prompts for the hiring assistant."""

from .planner_prompts import PLANNER_SYSTEM_PROMPT
from .screener_prompts import SCREENER_SYSTEM_PROMPT
from .matcher_prompts import MATCHER_SYSTEM_PROMPT
from .ranker_prompts import RANKER_SYSTEM_PROMPT
from .critic_prompts import CRITIC_SYSTEM_PROMPT

__all__ = [
    "PLANNER_SYSTEM_PROMPT",
    "SCREENER_SYSTEM_PROMPT",
    "MATCHER_SYSTEM_PROMPT",
    "RANKER_SYSTEM_PROMPT",
    "CRITIC_SYSTEM_PROMPT"
]
