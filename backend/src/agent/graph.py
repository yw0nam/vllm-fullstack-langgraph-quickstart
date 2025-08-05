"""LangGraph implementation for the agent."""

import os

# 로깅 설정 추가
import sys

from dotenv import load_dotenv
from google.genai import Client
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_tavily import TavilySearch
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.types import Send

from agent.configuration import Configuration
from agent.prompts import (
    answer_instructions,
    get_current_date,
    query_writer_instructions,
    reflection_instructions,
    web_searcher_instructions,
)
from agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from agent.tools_and_schemas import Reflection, SearchQueryList
from agent.utils import (
    get_citations,
    get_llm_model,
    get_research_topic,
    get_sources,
    insert_citation,
    insert_citation_markers,
    resolve_urls,
)

sys.path.append(
    "/Users/nam-young-woo/Desktop/codes/work/vllm-fullstack-langgraph-quickstart/backend"
)
from components.logging_config import (
    GRAPH_LOGGER,
    log_api_call,
    log_error_with_context,
    log_graph_transition,
    log_tool_usage,
)

load_dotenv()


# Nodes
def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """LangGraph node that generates a search queries based on the User's question.

    Uses Gemini 2.0 Flash to create an optimized search query for web research based on
    the User's question.

    Args:
        state: Current graph state containing the User's question
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated query
    """
    GRAPH_LOGGER.info("🔄 Starting generate_query node")

    try:
        import streamlit as st

        configurable = Configuration.from_runnable_config(config)
        os.environ["GOOGLE_API_KEY"] = st.session_state.user_google_api_key.strip()
        os.environ["TAVILY_API_KEY"] = st.session_state.user_tavily_api_key.strip()
        # check for custom initial search query count
        if state.get("initial_search_query_count") is None:
            state["initial_search_query_count"] = configurable.number_of_initial_queries

        # 사용자 질문 로깅
        user_question = get_research_topic(state["messages"])
        GRAPH_LOGGER.info(f"📝 User question: {user_question[:100]}...")

        # Get model configuration dynamically

        llm = get_llm_model(
            model_type=configurable.model_type,
            temperature=1.0,
            max_retries=2,
        )

        log_api_call(
            GRAPH_LOGGER,
            "ChatModel",
            "INIT",
            f"Type: {configurable.model_type}",
        )

        structured_llm = llm.with_structured_output(SearchQueryList)

        # 프롬프트 로깅
        formatted_prompt = query_writer_instructions.format(
            current_date=get_current_date(),
            number_queries=state["initial_search_query_count"],
            research_topic=user_question,
        )
        GRAPH_LOGGER.debug(f"📋 Query generation prompt: {formatted_prompt[:200]}...")

        # LLM 호출
        GRAPH_LOGGER.info("🤖 Calling LLM for query generation...")
        response = structured_llm.invoke(formatted_prompt)

        # 생성된 쿼리 로깅
        queries = response.query
        GRAPH_LOGGER.info(f"✅ Generated {len(queries)} queries: {queries}")

        log_graph_transition(
            GRAPH_LOGGER,
            "generate_query",
            "web_research",
            {
                "query_count": len(queries),
                "initial_search_query_count": state["initial_search_query_count"],
            },
        )

        return {"query_list": queries}

    except Exception as e:
        log_error_with_context(
            GRAPH_LOGGER,
            e,
            "generate_query",
            {
                "user_question": (
                    user_question if "user_question" in locals() else "Unknown"
                )
            },
        )
        # 에러 발생 시 기본 쿼리 반환
        fallback_query = (
            user_question if "user_question" in locals() else "research topic"
        )
        GRAPH_LOGGER.warning(f"🔄 Using fallback query: {fallback_query}")
        return {"query_list": [fallback_query]}


def continue_to_web_research(state: QueryGenerationState):
    """LangGraph node that sends the search queries to the web research node.

    This is used to spawn n number of web research nodes, one for each search query.
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["query_list"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """LangGraph node that performs web research using the native Google Search API tool.

    Executes a web search using the native Google Search API tool in combination with Gemini 2.0 Flash.

    Args:
        state: Current graph state containing the search query and research loop count
        config: Configuration for the runnable, including search API settings

    Returns:
        Dictionary with state update, including sources_gathered, research_loop_count, and web_research_results
    """
    GRAPH_LOGGER.info(
        f"🔍 Starting web_research node for query: '{state['search_query']}'"
    )

    try:
        # Configure
        configurable = Configuration.from_runnable_config(config)
        formatted_prompt = web_searcher_instructions.format(
            current_date=get_current_date(),
            research_topic=state["search_query"],
        )

        GRAPH_LOGGER.debug(f"📋 Web search prompt: {formatted_prompt[:200]}...")

        message = {"role": "user", "content": formatted_prompt}

        # Get search type from session state (safe import)
        if configurable.search_type == "tavily":
            # Get model configuration dynamically
            llm = get_llm_model(
                model_type=configurable.model_type,
                max_retries=2,
                temperature=0.7,
            )

            log_api_call(
                GRAPH_LOGGER,
                "ChatModel",
                "INIT",
                f"Type: {configurable.model_type}",
            )
            tavily_search_tool = TavilySearch(max_results=5)
            agent = create_react_agent(
                llm,
                tools=[tavily_search_tool],
            )

            GRAPH_LOGGER.info("🤖 Invoking web research agent...")

            out = agent.invoke(input={"messages": [message]})
            message = out["messages"]

            # Uses the google genai client as the langchain client doesn't return grounding metadata

            log_tool_usage(
                GRAPH_LOGGER,
                "react_agent",
                state["search_query"],
                f"Messages count: {len(message)}",
                True,
            )

            # sources 추출 시 에러 처리
            try:
                sources = get_sources(message, state["id"])
                GRAPH_LOGGER.info(f"📚 Extracted {len(sources)} sources")
            except Exception as e:
                log_error_with_context(
                    GRAPH_LOGGER, e, "get_sources", {"query": state["search_query"]}
                )
                sources = []  # 빈 소스 목록으로 계속 진행

            # citation 삽입 시 에러 처리
            try:
                summarized_text = insert_citation(message[-1].content, sources)
                GRAPH_LOGGER.info(
                    f"📝 Generated summarized text with citations ({len(summarized_text)} chars)"
                )
            except Exception as e:
                log_error_with_context(
                    GRAPH_LOGGER, e, "insert_citation", {"sources_count": len(sources)}
                )
                # citation 없이 원본 텍스트 사용
                summarized_text = (
                    message[-1].content
                    if message
                    else "검색 결과를 가져올 수 없습니다."
                )
        elif configurable.search_type == "google":
            google_api_key = os.getenv("GOOGLE_API_KEY")
            genai_client = Client(api_key=google_api_key)
            response = genai_client.models.generate_content(
                model=os.getenv("GEMINI_MODEL_NAME"),
                contents=formatted_prompt,
                config={
                    "tools": [{"google_search": {}}],
                    "temperature": 0,
                },
            )
            # resolve the urls to short urls for saving tokens and time
            resolved_urls = resolve_urls(
                response.candidates[0].grounding_metadata.grounding_chunks,
                state["id"],
            )
            # Gets the citations and adds them to the generated text
            citations = get_citations(response, resolved_urls)
            summarized_text = insert_citation_markers(response.text, citations)
            sources = [item for citation in citations for item in citation["segments"]]

        result = {
            "sources_gathered": sources,
            "search_query": [state["search_query"]],
            "web_research_result": [summarized_text],
        }

        log_graph_transition(
            GRAPH_LOGGER,
            "web_research",
            "reflection",
            {"sources_count": len(sources), "query": state["search_query"]},
        )

        GRAPH_LOGGER.info("✅ Web research completed successfully")
        return result

    except Exception as e:
        log_error_with_context(
            GRAPH_LOGGER, e, "web_research", {"query": state["search_query"]}
        )
        # 에러 발생 시 기본값 반환
        error_result = {
            "sources_gathered": [],
            "search_query": [state["search_query"]],
            "web_research_result": [f"검색 중 오류가 발생했습니다: {str(e)}"],
        }
        GRAPH_LOGGER.warning("⚠️ Web research failed, returning error result")
        return error_result


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """LangGraph node that identifies knowledge gaps and generates potential follow-up queries.

    Analyzes the current summary to identify areas for further research and generates
    potential follow-up queries. Uses structured output to extract
    the follow-up query in JSON format.

    Args:
        state: Current graph state containing the running summary and research topic
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated follow-up query
    """
    GRAPH_LOGGER.info("🤔 Starting reflection node")

    try:
        configurable = Configuration.from_runnable_config(config)
        # Increment the research loop count and get the reasoning model
        state["research_loop_count"] = state.get("research_loop_count", 0) + 1

        GRAPH_LOGGER.info(f"🔄 Research loop count: {state['research_loop_count']}")

        # Format the prompt
        current_date = get_current_date()
        research_topic = get_research_topic(state["messages"])
        summaries = "\n\n---\n\n".join(state["web_research_result"])

        GRAPH_LOGGER.info(
            f"📊 Analyzing {len(state['web_research_result'])} research results"
        )
        GRAPH_LOGGER.debug(f"📝 Research topic: {research_topic[:100]}...")

        formatted_prompt = reflection_instructions.format(
            current_date=current_date,
            research_topic=research_topic,
            summaries=summaries,
        )

        # Get model configuration dynamically
        llm = get_llm_model(
            configurable.model_type,
            max_retries=2,
            temperature=0.7,
        )

        log_api_call(
            GRAPH_LOGGER,
            "ChatModel",
            "INIT",
            f"Type: {configurable.model_type}",
        )

        GRAPH_LOGGER.info("🤖 Calling LLM for reflection analysis...")
        result = llm.with_structured_output(Reflection).invoke(formatted_prompt)

        # 결과 로깅
        GRAPH_LOGGER.info(
            f"✅ Reflection completed - Is sufficient: {result.is_sufficient}"
        )
        if not result.is_sufficient:
            GRAPH_LOGGER.info(
                f"🔍 Knowledge gap identified: {result.knowledge_gap[:100]}..."
            )

        # 다음 노드 결정 로깅
        next_node = "finalize_answer" if result.is_sufficient else "web_research"
        log_graph_transition(
            GRAPH_LOGGER,
            "reflection",
            next_node,
            {
                "is_sufficient": result.is_sufficient,
                "research_loop_count": state["research_loop_count"],
            },
        )

        return {
            "is_sufficient": result.is_sufficient,
            "knowledge_gap": result.knowledge_gap,
            "follow_up_queries": result.follow_up_queries,
            "research_loop_count": state["research_loop_count"],
            "number_of_ran_queries": len(state["search_query"]),
        }

    except Exception as e:
        log_error_with_context(
            GRAPH_LOGGER,
            e,
            "reflection",
            {
                "research_loop_count": state.get("research_loop_count", 0),
                "web_research_result_count": len(state.get("web_research_result", [])),
            },
        )
        # 에러 발생 시 충분하다고 간주하여 종료
        GRAPH_LOGGER.warning("⚠️ Reflection failed, assuming sufficient information")
        return {
            "is_sufficient": True,
            "knowledge_gap": result.knowledge_gap,
            "follow_up_queries": result.follow_up_queries,
            "research_loop_count": state["research_loop_count"],
            "number_of_ran_queries": len(state["search_query"]),
        }


def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
) -> OverallState:
    """LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.

    Args:
        state: Current graph state containing the research loop count
        config: Configuration for the runnable, including max_research_loops setting

    Returns:
        String literal indicating the next node to visit ("web_research" or "finalize_summary")
    """
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        return "finalize_answer"
    else:
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]


def finalize_answer(state: OverallState, config: RunnableConfig):
    """LangGraph node that finalizes the research summary.

    Prepares the final output by deduplicating and formatting sources, then
    combining them with the running summary to create a well-structured
    research report with proper citations.

    Args:
        state: Current graph state containing the running summary and sources gathered

    Returns:
        Dictionary with state update, including running_summary key containing the formatted final summary with sources
    """
    GRAPH_LOGGER.info("📝 Starting finalize_answer node")

    try:
        configurable = Configuration.from_runnable_config(config)

        research_topic = get_research_topic(state["messages"])
        summaries_count = len(state.get("web_research_result", []))
        sources_count = len(state.get("sources_gathered", []))

        GRAPH_LOGGER.info(
            f"📊 Finalizing answer with {summaries_count} summaries and {sources_count} sources"
        )
        GRAPH_LOGGER.debug(f"📝 Research topic: {research_topic[:100]}...")

        # Format the prompt
        current_date = get_current_date()
        formatted_prompt = answer_instructions.format(
            current_date=current_date,
            research_topic=research_topic,
            summaries="\n---\n\n".join(state["web_research_result"]),
        )

        llm = get_llm_model(
            configurable.model_type,
            max_retries=2,
            temperature=0.7,
        )

        log_api_call(
            GRAPH_LOGGER,
            "ChatModel",
            "INIT",
            f"Type: {configurable.model_type}",
        )

        GRAPH_LOGGER.info("🤖 Calling LLM for final answer generation...")
        result = llm.invoke(formatted_prompt)

        # 결과 로깅
        answer_length = len(result.content) if hasattr(result, "content") else 0
        GRAPH_LOGGER.info(f"✅ Final answer generated ({answer_length} characters)")

        log_graph_transition(
            GRAPH_LOGGER,
            "finalize_answer",
            "END",
            {
                "answer_length": answer_length,
                "summaries_used": summaries_count,
                "sources_used": sources_count,
            },
        )

        # Replace the short urls with the original urls and add all used urls to the sources_gathered
        # unique_sources = []
        # for source in state["sources_gathered"]:
        #     if source["short_url"] in result.content:
        #         result.content = result.content.replace(        #             source["short_url"], source["value"]
        #         )
        #         unique_sources.append(source)

        return {
            "messages": [AIMessage(content=result.content)],
            "sources_gathered": state["sources_gathered"],
        }

    except Exception as e:
        log_error_with_context(
            GRAPH_LOGGER,
            e,
            "finalize_answer",
            {
                "summaries_count": len(state.get("web_research_result", [])),
                "sources_count": len(state.get("sources_gathered", [])),
            },
        )
        # 에러 발생 시 기본 답변 반환
        error_message = f"최종 답변 생성 중 오류가 발생했습니다: {str(e)}"
        GRAPH_LOGGER.warning(f"⚠️ {error_message}")
        return {
            "messages": [AIMessage(content=error_message)],
            "sources_gathered": state.get("sources_gathered", []),
        }


# Create our Agent Graph
builder = StateGraph(OverallState, config_schema=Configuration)

# Define the nodes we will cycle between
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)

# Set the entrypoint as `generate_query`
# This means that this node is the first one called
builder.add_edge(START, "generate_query")
# Add conditional edge to continue with search queries in a parallel branch
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
# Reflect on the web research
builder.add_edge("web_research", "reflection")
# Evaluate the research
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
# Finalize the answer
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="pro-search-agent")
