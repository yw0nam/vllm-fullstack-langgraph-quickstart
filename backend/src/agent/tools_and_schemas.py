"""Tools and schemas for the agent operations."""

from typing import Annotated, List

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field

load_dotenv()


class SearchQueryList(BaseModel):
    """A list of search queries for web research."""

    query: List[str] = Field(
        description="A list of search queries to be used for web research."
    )
    rationale: str = Field(
        description="A brief explanation of why these queries are relevant to the research topic."
    )


class Reflection(BaseModel):
    """Reflection on the sufficiency of research results."""

    is_sufficient: bool = Field(
        description="Whether the provided summaries are sufficient to answer the user's question."
    )
    knowledge_gap: str = Field(
        description="A description of what information is missing or needs clarification."
    )
    follow_up_queries: List[str] = Field(
        description="A list of follow-up queries to address the knowledge gap."
    )


def is_garbled(text):
    """Check if text contains garbled characters.

    Args:
        text: The text to check for garbled content.

    Returns:
        bool: True if text appears garbled, False otherwise.
    """
    # A simple heuristic to detect garbled text: high proportion of non-ASCII characters
    non_ascii_count = sum(1 for char in text if ord(char) > 127)
    return non_ascii_count > len(text) * 0.3


@tool
def fetch_url(url: Annotated[str, "Target Web site"]) -> str:
    """Fetch and extract clean text content from a given URL.

    This function sends an HTTP GET request to the specified URL. If the
    request is successful, it parses the HTML content to extract all

    Args:
        url: The complete and valid URL of the target website to scrape.

    Returns:
        A string containing the extracted and cleaned text content from the
        website, truncated to 4000 characters. In case of an error, it
        returns a descriptive error message detailing the issue (e.g.,
        403 Forbidden, other HTTP errors, or garbled text detection).
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract text content
        texts = soup.stripped_strings
        content = " ".join(texts)

        # Check for garbled text
        if is_garbled(content):
            content = "error in scraping website, garbled text returned"
        else:
            # Limit the content to 4000 characters
            content = content[:4000]

        return content
    except requests.HTTPError as e:
        if e.response.status_code == 403:
            content = f"error in scraping website, 403 Forbidden for url: {url}"
        else:
            content = f"error in scraping website, {str(e)}"


@tool
def tavily_search(
    query: Annotated[str, "search query"],
    max_result: Annotated[int, "max return result"] = 5,
    topic: Annotated[
        str, "search topic, you can choose 'general', 'news', 'finance'"
    ] = "general",
    time_range: Annotated[
        str,
        "Time range for search. you can choose 'day', 'week', 'month', 'year' or None",
    ] = None,
):
    """Perform a web search using the Tavily Search API and index the results.

    This function initializes the `TavilySearch` tool with specified parameters to
    conduct a web search. After fetching the results, it iterates through them to
    add a 1-based 'index' key to each result dictionary, making them easier to
    reference.

    Args:
        query (str): The search query to be sent to Tavily.
        max_result (int, optional): The maximum number of results to fetch.
            Defaults to 5.
        topic (str, optional): The topic of the search. Can be 'general',
            'news', or 'finance'. Defaults to "general".
        time_range (str, optional): The time range for the search. Can be 'day',
            'week', 'month', 'year', or None. Defaults to None.

    Returns:
        web_search_result(dict) : The web search result from the Tavily search tool.
    """
    tavily_search_tool = TavilySearch(
        max_result=max_result, topic=topic, time_range=time_range
    )
    web_search_result = tavily_search_tool.invoke(query)
    for idx, result in enumerate(web_search_result["results"]):
        result.update({"citation_number": f"[{idx + 1}]"})
    return web_search_result
