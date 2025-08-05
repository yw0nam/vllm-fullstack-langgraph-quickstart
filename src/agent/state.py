"""State definitions for the agent graph."""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import TypedDict

from langgraph.graph import add_messages
from typing_extensions import Annotated


class OverallState(TypedDict):
    """Overall state for the agent graph."""

    messages: Annotated[list, add_messages]
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    reasoning_model: str


class ReflectionState(TypedDict):
    """State for reflection on research adequacy."""

    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: Annotated[list, operator.add]
    research_loop_count: int
    number_of_ran_queries: int


class Query(TypedDict):
    """A search query with rationale."""

    query: str
    rationale: str


class QueryGenerationState(TypedDict):
    """State for query generation."""

    query_list: list[Query]


class WebSearchState(TypedDict):
    """State for web search operations."""

    search_query: str
    id: str


@dataclass(kw_only=True)
class SearchStateOutput:
    """Output state for search operations."""

    running_summary: str = field(default=None)  # Final report
