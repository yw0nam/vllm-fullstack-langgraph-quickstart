# %%
from agent import graph
from langchain_core.messages import AIMessageChunk
from agent.tools_and_schemas import (
    SearchQueryList,
    Reflection,
    fetch_url,
    tavily_search,
)

# %%
state = graph.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "요즘 AI LLM에이전트의 시장 동향에 대해 알려줘. 2025년을 기준으로.",
            }
        ],
        "max_research_loops": 3,
        "initial_search_query_count": 1,
    }
)
# %%
import ast, json

temp = {
    "query": "Emerging trends in artificial intelligence agent development for 2025",
    "follow_up_questions": None,
    "answer": None,
    "images": [],
    "results": [
        {
            "title": "10+ Agentic AI Trends and Examples for 2025 - AIMultiple",
            "url": "https://research.aimultiple.com/agentic-ai-trends/",
            "content": "Agentic AI | 4 | **Integration of AI agents with the physical world** | • NVIDIA & GE Healthcare: Diagnostic imaging with AI agents. | 9 | **Agentic AI reshaping team roles** | • AI automation: Engineers scale systems, analysts manage workflows. Tech companies like **NVIDIA** and **GE HealthCare** are already working together on **agentic robotic systems** like **X-ray** and **ultrasound** technologies, where AI agents use medical imaging to interact with the physical world.3 *   **Advances in AI-enabled pipeline automation:**Agentic systems can autonomously handle multi-step workflows such as data ingestion, validation, and incident detection. Capgemini claims that ~80% of surveyed organizations plan to integrate AI agents within 1-3 years for tasks like email generation, coding, and data analysis.",
            "score": 0.8832463,
            "raw_content": None,
        },
        {
            "title": "Agentic AI Trends 2025: The Complete Guide to Autonomous Intelligence ...",
            "url": "https://collabnix.com/agentic-ai-trends-2025-the-complete-guide-to-autonomous-intelligence-revolution/",
            "content": "As we advance through 2025, **agentic AI trends** are reshaping how businesses approach automation, decision-making, and customer engagement. **The Trend**: Agentic AI systems are enabling real-time decision-making at scale, responding to events and opportunities faster than human operators. **Performance Metrics**: Retail organizations report 45% increase in conversion rates and 30% improvement in customer retention with agentic AI implementation. The key to success lies not just in adopting agentic AI technology, but in thoughtfully integrating these capabilities into business strategy, culture, and operations. **The future belongs to organizations that view agentic AI not as a tool, but as a strategic capability that enables new forms of business intelligence, automation, and competitive advantage.** *   Agentic AI What is Agentic AI?",
            "score": 0.8668671,
            "raw_content": None,
        },
        {
            "title": "What Are the Upcoming Trends in AI for 2025? - Analytics Insight",
            "url": "https://www.analyticsinsight.net/artificial-intelligence/what-are-the-upcoming-trends-in-ai-for-2025",
            "content": "What Are the Upcoming Trends in AI for 2025? What Are the Upcoming Trends in AI for 2025? Image 3: What Are the Upcoming Trends in AI for 2025? ### **Growth of Agentic AI** Agentic AI are autonomous systems that make decisions and perform tasks without human assistance. Agentic AI will be used for software development, customer support, cybersecurity, threat assessment, business intelligence, and much more, where automation, efficiency, and responsiveness to context are needed. Image 7: How Microsoft Plans to Let AI Agents Operate Your PC for You Image 8: AI Agents Dominate Web3: Top 10 Tokens Leading the Trend ###### AI Agents Dominate Web3: Top 10 Tokens Leading the Trend *   Generative AI",
            "score": 0.83452857,
            "raw_content": None,
        },
        {
            "title": "Top AI Agent Models in 2025: Architecture, Capabilities, and Future ...",
            "url": "https://so-development.org/top-ai-agent-models-in-2025-architecture-capabilities-and-future-impact/",
            "content": "Unlike traditional models that respond to queries in isolation, AI agents operate persistently, reason about the environment, plan multi-step actions, and interact autonomously with tools, APIs, and users. So, what is an AI agent? Top AI Agent Models in 2025 Gato-like models are embedded in agents that plan physical actions and adapt to real-time environments, critical in smart home devices and autonomous vehicles. Thanks to frameworks like Auto-GPT, AutoDev, and Devin, AI agents can now autonomously perform multi-step software development tasks, including: Legal work involves vast document processing, a task AI agents are increasingly adept at handling thanks to memory-rich models like Claude 3, Gemini 1.5, and Mixtral agents. Challenges in AI Agent Development and Deployment These agents:",
            "score": 0.81418616,
            "raw_content": None,
        },
        {
            "title": "AI trends in 2025: What we've seen and what we'll see next - MC Press ...",
            "url": "https://www.mcpressonline.com/analytics-cognitive/ai-trends-in-2025-what-weve-seen-and-what-well-see-next",
            "content": "*   Image 12  Analytics & Cognitive News Details  10 Jun 25 ### IBM Study: Businesses View AI Agents as Essential, Not Just Experimental    *   Image 14  Analytics & Cognitive News Details  09 Jun 25 ### AskIAM: IBM’s New Agentic AI for Identity and Access Management    *   Image 33  Cloud News Details  25 Sep 2024 ### IBM and Microsoft Open Three New Experience Zones to Provide Global Clients with More Hands-on Access to Cloud and Generative AI Solutions    *   Image 47  Analytics & Cognitive News Details  10 Jun 2025 ### IBM Study: Businesses View AI Agents as Essential, Not Just Experimental    *   Image 49  Analytics & Cognitive News Details  09 Jun 2025 ### AskIAM: IBM’s New Agentic AI for Identity and Access Management   ",
            "score": 0.74161834,
            "raw_content": None,
        },
    ],
    "response_time": 1.98,
}

# %%
temp["results"]
# %%
out = tavily_search.invoke("who is the famous football player in the world?")
# %%
out
# %%
print(
    "<think>\nOkay, let's tackle this query about the current trends in the AI agent market. The user is asking in Korean, so I need to make sure the answer is in Korean as well. They provided some summaries, but when I tried to access the URLs, they were either garbled or didn't work. Hmm, maybe the links are placeholders or incorrect. I'll have to rely solely on the summaries given.\n\nFirst, I'll go through each summary to extract key points. The first summary mentions the market growth from $7.84 billion in 2025 to $52.62 billion by 2030. That's a significant figure, so I should highlight the growth rate and the factors driving it. The second summary talks about Gartner's SRM Summit and the importance of AI governance platforms. I need to connect that to regulatory trends affecting the market.\n\nThe third summary from New Scientist discusses how AI agents could control the internet, which might relate to ethical concerns or regulatory challenges. The fourth summary from Brunch mentions KT's use of AI agents for market sensing reports, automating tasks. That's a good example of enterprise adoption. The fifth summary from Dongsanum (I think that's the Korean version) talks about AI agents in security, with Juniper Research predicting increased investment. \n\nThe sixth summary from ZUM News lists different AI agent types introduced by companies like OpenAI and Google. The seventh from CIO Korea mentions the need for governance platforms again. The eighth from CIO Korea also talks about cognitive agents and their role in business strategies. The ninth from RCR Wireless News mentions operators spending on AI, which could tie into telecom or network security. The tenth from Dark Reading emphasizes agentic AI's role in real-time threat detection. The eleventh from Property Casualty 360 discusses insurance industry trends. The twelfth from TechCrunch quotes Sam Altman predicting novel insights by 2026. The thirteenth from New Scientist again touches on internet control via AI agents.\n\nWait, some of these summaries might be overlapping or from the same sources. I need to organize them coherently. The main points are market growth, key drivers like generative AI and automation, regulatory challenges, enterprise use cases (like KT's example), security applications, competition among tech giants, and future predictions from industry leaders.\n\nI should structure the answer into sections: market growth, drivers, regulatory trends, enterprise adoption examples, security applications, competition, and future outlook. Make sure to include all the citations properly. Also, check if any summaries mention specific technologies or companies that are leading the market. OpenAI's Operator, Deep Research, Codex, and Google's AlphaEvolve are mentioned, so those should be included as examples of innovation.\n\nNeed to verify if the user wants the answer in Korean, which they do. Also, ensure that all the provided summaries are cited correctly even if the URLs didn't work. Maybe the user expects the answer to reference the summaries as given, even if the links are broken. So I'll proceed by using the content from the summaries as presented, attributing each point to the respective source.\n\nI should start with an introduction about the market growth, then break down each section with supporting details from the summaries. Conclude with the future outlook and the importance of governance. Make sure the answer is comprehensive but concise, covering all the key areas mentioned in the summaries. Also, check for any specific terms or metrics that need emphasis, like the CAGR or investment figures.\n</think>\n\n### 2025년 AI 에이전트 시장 트렌드: 종합 분석\n\n#### 1. **시장 성장과 규모**\n2025년 AI 에이전트 시장은 **78억 4,000만 달러**(약 10.7조 원) 규모로 성장했으며, 2030년에는 **526억 2,000만 달러**(약 71.8조 원)에 달할 것으로 예상됩니다 [1]. 이는 AI 기술의 발전과 산업 전반에 걸친 빠른 도입 속도를 반영합니다. 특히, 생성형 AI의 확산으로 인해 정보 처리와 업무 자동화 분야에서 AI 에이전트의 활용이 급증하고 있습니다 [2].\n\n#### 2. **주요 성장 요인**\n- **생산성 향상**: AI 에이전트는 반복적이고 복잡한 업무를 자동화하여 기업의 효율성을 극대화합니다. 예를 들어, KT는 시장 동향 분석 보고서 작성 업무를 100% 자동화하는 데 성공했습니다 [3].\n- **기술 혁신**: Google, OpenAI, Anthropic 등 주요 기술 기업들이 AI 에이전트를 활용한 과학적 연구와 문제 해결에 집중하고 있습니다. OpenAI는 **Operator**, **Deep Research**, **Codex** 등 다양한 에이전트를 발표했으며, Google은 **AlphaEvolve**를 통해 복잡한 수학 문제를 해결하는 데 성공했습니다 [4].\n- **규제 환경 변화**: AI 에이전트의 자율성과 복잡성 증가로 인해 **AI 거버넌스 플랫폼**의 필요성이 높아지고 있습니다. Gartner는 AI 에이전트의 확산이 기업의 보안 및 디버깅 요구사항을 증가시킬 것이라고 경고했습니다 [5].\n\n#### 3. **보안 및 자율성 강화**\nAI 에이전트는 **네트워크 보안** 분야에서 특히 주목받고 있습니다. Juniper Research에 따르면, 2025년부터 2029년까지 AI 기반 보안 시스템에 대한 연간 투자 금액이 **$2.5억에서 $4.6억**으로 증가할 것으로 예상됩니다 [6]. Agentic AI는 실시간 위협 탐지와 대응을 가능하게 하며, 인간 개입 없이도 기업 데이터를 보호하는 역할을 합니다 [7].\n\n#### 4. **기업의 AI 에이전트 도입 전략**\n기업들은 AI 에이전트 도입을 위해 다양한 전략을 채택하고 있습니다. **기술 제휴**(30%)가 가장 선호되는 방식이며, **내부 개발**(26%)과 **아웃소싱**(17%)도 중요한 선택지로 꼽힙니다 [8]. 이는 AI 에이전트의 기술적 복잡성과 초기 개발 비용을 고려할 때, 협력이 시장 확대에 핵심 역할을 하고 있음을 보여줍니다.\n\n#### 5. **미래 전망과 혁신**\nSam Altman은 AI가 **2026년에 '새로운 통찰'을 제공**할 것이라고 예측하며, AI 에이전트가 기업의 전략적 핵심으로 자리 잡고 있다고 강조했습니다 [9]. 또한, AI 에이전트는 단순 자동화 도구를 넘어 **혁신 주도 기술**로 발전하고 있습니다. 예를 들어, Google의 AlphaEvolve는 복잡한 수학 문제 해결을 가능하게 하며, OpenAI의 Deep Research는 과학적 연구를 혁신적으로 지원합니다 [10].\n\n#### 6. **규제와 윤리적 고려**\nAI 에이전트의 확산과 함께 **규제와 윤리적 문제**도 중요해지고 있습니다. New Scientist는 AI 에이전트가 인터넷을 통제할 수 있는 위험성을 지적하며, 투명성과 책임성 확보가 필요하다고 강조했습니다 [11]. 이에 따라, 기업과 정부는 AI 에이전트의 행동 추적 및 디버깅 기술에 대한 투자를 늘리고 있습니다 [12].\n\n#### 7. **경쟁 구도와 기술 발전**\nAI 에이전트 시장은 **Google, OpenAI, FutureHouse, KT** 등 다양한 기업들이 경쟁적으로 진출하고 있습니다. 각 기업은 자체적인 솔루션을 개발하며, AI 에이전트의 기능과 활용 범위를 확장하고 있습니다 [13]. 이는 시장의 기술 발전 속도를 높이고, 향후 몇 년간의 성장 동력으로 작용할 것입니다.\n\n---\n\n### 결론\n2025년 AI 에이전트 시장은 **기술 혁신**, **업무 자동화**, **보안 강화**, **규제 대응** 등 다양한 요인에 의해 빠르게 성장하고 있습니다. 기업들은 AI 에이전트를 통해 생산성 향상과 경쟁력 강화를 추구하고 있으며, 향후 5년간 시장 규모가 6배 이상 확대될 것으로 전망됩니다. 그러나, AI 에이전트의 자율성과 복잡성 증가에 따라 **거버넌스와 윤리적 고려**가 필수적입니다. 이에 따라, 투자와 혁신은 지속적으로 확대될 것이며, 규제와 기술 발전의 균형이 시장의 성공을 좌우할 것입니다.\n\n---\n\n#### 참고문헌\n1. [AI 에이전트 시장 규모](https://m.news.zum.com/articles/98823044/it%EB%B0%B1%EA%B3%BC-ai%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8-%ED%95%B5%EC%8B%AC%EA%B8%B0%EC%88%A0-a2a%EC%99%80-mcp-%EC%B0%A8%EC%9D%B4%EB%8A%94?)\n2. [생성형 AI의 확산](https://shindonga.donga.com/economy/article/all/13/5651080/1)\n3. [KT의 AI 에이전트 사례](https://www.datanet.co.kr/news/articleView.html?idxno=202704)\n4. [OpenAI와 Google의 혁신](https://www.newscientist.com/article/2483880-can-we-stop-big-tech-from-controlling-the-internet-with-ai-agents/)\n5. [AI 거버넌스 플랫폼](https://www.darkreading.com/cloud-security/agentic-ai-gartner-srm-summit)\n6. [네트워크 보안 투자](https://kr.investing.com/news/transcripts/article-93CH-1513690)\n7. [Agentic AI의 보안 역할](https://brunch.co.kr/@@575g/398)\n8. [AI 도입 전략](https://www.cio.com/article/4004801/ai-%EC%8B%9C%EB%8C%80%EC%8B%9C%EC%9A%B8%EC%9D%98-%EB%B0%8F%EC%9D%98-%EC%95%84%EC%A7%81%EC%9D%80-%EC%B4%88%EA%B8%B0-ai-%EA%B1%B0%EB%B2%84%EB%84%8C%EC%8A%A4-%ED%94%84%EB%9E%98%ED%8F%BC.html)\n9. [Sam Altman의 AI 전망](https://techcrunch.com/2025/06/11/sam-altman-thinks-ai-will-have-novel-insights-next-year/)\n10. [AI 에이전트의 경쟁](https://www.propertycasualty360.com/2025/06/11/around-the-pc-insurance-industry-june-11-2025/?amp=1)\n11. [AI와 인터넷 통제](https://www.newscientist.com/article/2483880-can-we-stop-big-tech-from-controlling-the-internet-with-ai-agents/)\n12. [AI 거버넌스의 중요성](https://www.cio.com/article/4002185/%EC%86%94%EB%A3%A8%EC%85%98%EB%8F%84-%EA%B8%B0%EC%97%85%EB%8F%84-%EC%95%84%EC%A7%81%EC%9D%80-%EC%B4%88%EA%B8%B0-ai-%EA%B1%B0%EB%B2%84%EB%84%8C%EC%8A%A4-%ED%94%84%EB%9E%98%ED%8F%BC.html)\n13. [AI 기술 경쟁](https://www.rcrwireless.com/20250611/carriers/operators-spend-ai)"
)

# %%
