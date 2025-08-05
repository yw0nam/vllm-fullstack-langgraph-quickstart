
# VLLM Full-Stack LangGraph Quickstart

This repository provides a full-stack quickstart application using Streamlit for the frontend and a LangGraph-powered AI agent for the backend. It's designed to be a real-time AI research agent.

## ✨ Features

*   **Modular Streamlit Frontend:** The user interface is built with Streamlit, with components logically separated into modules for configuration, session state, UI components, and more.
*   **LangGraph Powered Agent:** The core logic is handled by a sophisticated AI agent built with LangGraph, enabling complex, stateful, and tool-using AI workflows.
*   **Real-time Interaction:** Provides a real-time chat interface for users to interact with the AI agent.
*   **Asynchronous Event Processing:** Efficiently handles and processes events from the LangGraph agent.
*   **Clear Project Structure:** The code is organized into a `src` directory for the agent backend and a `components` directory for the Streamlit frontend, promoting maintainability and scalability.

## 🚀 Getting Started

### Prerequisites

*   Python 3.11 or higher
*   An API key for a supported LLM provider (e.g., OpenAI, Google Gemini).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yw0nam/vllm-fullstack-langgraph-quickstart.git
    cd vllm-fullstack-langgraph-quickstart
    ```

2.  **Create a virtual environment and install dependencies:**

    It is highly recommended to use a virtual environment to manage project dependencies. This project uses `uv` for package management, but you can also use `pip`.

    **Using `uv` (recommended):**
    ```bash
    # Install uv if you haven't already
    pip install uv
    uv sync
    ```

3.  **Set up your environment variables:**

    Create a `.env` file in the root directory of the project and add your API keys. For example:

    ```
    MODEL_API_KEY="your_vllm_model_api_key"
    MODEL_API_URL="your_vllm_model_api_url"
    MODEL_NAME="your_model_name"  # e.g., "vllm-gpt-4"
    TAVILY_API_KEY="your_tavily_api_key"
    OPENAI_API_KEY="your_openai_api_key"
    # Or for Google
    # GOOGLE_API_KEY="your_google_api_key"
    ```

### Running the Application

Once the dependencies are installed and your environment variables are set, you can run the Streamlit application:

```bash
uv run streamlit run app.py --server.port 8501

```

This will start the application, and you can access it in your web browser at the local URL provided by Streamlit (usually `http://localhost:8501`).

## Project Structure

```
.
├── app.py                  # Main Streamlit application entry point
├── components/             # Frontend components for the Streamlit app
│   ├── chat_interface.py
│   ├── config.py
│   ├── event_processor.py
│   ├── ...
├── src/
│   └── agent/              # Backend LangGraph agent
│       ├── graph.py        # The core LangGraph definition
│       ├── prompts.py
│       ├── tools_and_schemas.py
│       └── ...
├── pyproject.toml          # Project metadata and dependencies
├── README.md               # This file
└── ...
```

## 🛠️ Key Technologies

*   **Frontend:** [Streamlit](https://streamlit.io/)
*   **Backend/AI Agent:** [LangChain](https://www.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/)
*   **Language:** Python
*   **Dependency Management:** `uv`

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
