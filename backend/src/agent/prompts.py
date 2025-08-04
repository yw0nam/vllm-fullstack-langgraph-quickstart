from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


query_writer_instructions = """Your goal is to generate sophisticated and diverse web search queries. These queries are intended for an advanced automated web research tool capable of analyzing complex results, following links, and synthesizing information.

Instructions:
- Always prefer a single search query, only add another query if the original question requests multiple aspects or elements and one query is not enough.
- Each query should focus on one specific aspect of the original question.
- Don't produce more than {number_queries} queries.
- Queries should be diverse, if the topic is broad, generate more than 1 query.
- Don't generate multiple similar queries, 1 is enough.
- Query should ensure that the most current information is gathered. The current date is {current_date}.

Format: 
- Format your response as a JSON object with ALL three of these exact keys:
   - "rationale": Brief explanation of why these queries are relevant
   - "query": A list of search queries

Context: {research_topic}"""
# Example:

# Topic: What revenue grew more last year apple stock or the number of people buying an iphone
# ```json
# {{
#     "rationale": "To answer this comparative growth question accurately, we need specific data points on Apple's stock performance and iPhone sales metrics. These queries target the precise financial information needed: company revenue trends, product-specific unit sales figures, and stock price movement over the same fiscal period for direct comparison.",
#     "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth fiscal year 2024", "Apple stock price growth fiscal year 2024"],
# }}
# ```

web_searcher_instructions = """Conduct targeted searches to gather the most recent, credible information on "{research_topic}" and synthesize it into a verifiable text artifact.

Instructions:
- Query should ensure that the most current information is gathered. The current date is {current_date}.
- Conduct multiple, diverse searches to gather comprehensive information.
- Consolidate key findings while meticulously tracking the source(s) for each specific piece of information.
- The output should be a well-written summary or report based on your search findings. 
- Only include the information found in the search results. don't make up any information.
- Only include information that is relevant to the research topic.
- If the content is not sufficient for writing summary, get into raw content for getting more detail using fetch.
- Cite content retrieved from search results by appending a source number, such as [1] or [2], which corresponds to the source URL.
- Note you should start from citation number [0].

Research Topic:
{research_topic}
/no_think
"""

reflection_instructions = """You are an expert research assistant analyzing summaries about "{research_topic}".


Instructions:
- The current date is {current_date}.
- Identify knowledge gaps or areas that need deeper exploration and generate a follow-up query. (1 or multiple).
- If provided summaries are sufficient to answer the user's question, don't generate a follow-up query.
- If there is a knowledge gap, generate a follow-up query that would help expand your understanding.
- Note, Don't generate a follow-up query that is too broad or vague, and avoid queries that are too specific or narrow focus on trends of user's question.

Requirements:
- Ensure the follow-up query is self-contained and includes necessary context for web search.

Output Format:
- Format your response as a JSON object with these exact keys:
   - "is_sufficient": true or false
   - "knowledge_gap": Describe what information is missing or needs clarification
   - "follow_up_queries": Write a specific question to address this gap

Reflect carefully on the Summaries to identify knowledge gaps and produce a follow-up query. Then, produce your output following this JSON format:

Summaries:
{summaries}"""

answer_instructions = """Generate a high-quality answer to the user's question based on the provided summaries.

Instructions:
- The current date is {current_date}.
- Generate a high-quality answer to the user's question based on the provided summaries and the user's question.
- you MUST include all the citations from the summaries in the answer correctly.
- Reorganize the citations in the answer to match the order of the citations in the summaries.
- Final answer should be well-structured, concise, and directly address the user's question
- You MUST use the same language with the user's query.

User Context:
- {research_topic}

Summaries:
{summaries}"""
