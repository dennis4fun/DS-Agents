## 🤵 AI Agent Demo: Intelligent Tool Use

This project showcases the power of AI Agents built with LangChain, demonstrating how Large Language Models (LLMs) can intelligently decide which "tool" to use to answer complex questions or perform specific tasks. The interactive interface is built using Streamlit.

## ✨ Features

- Intelligent Tool Selection: An AI Agent (powered by OpenAI's `gpt-3.5-turbo`) analyzes user queries and dynamically chooses the most appropriate tool from a set of predefined functions.

- Diverse Toolset: Includes tools for:

- Mathematical Calculations: Performs precise arithmetic operations.

- Factual Lookups: Retrieves specific factual information from an internal knowledge base.

- Code Generation: Generates Python code snippets based on user requests.

- Transparent Reasoning: The Streamlit UI displays the agent's step-by-step thought process, showing how it reasons, selects tools, and processes observations.

- Interactive UI: A user-friendly chat interface built with Streamlit for easy interaction.

## 🛠️ Technologies Used

- Python: The core programming language.

- LangChain: Framework for building LLM applications and orchestrating agents.

- OpenAI API: Provides the Large Language Model (LLM) serving as the agent's "brain."

- Streamlit: For creating the interactive web user interface.

- `python-dotenv`: For secure management of API keys via a `.env` file.

## 🏗️ Project Structure

```bash
DS-Agents/
├── .env                          # Stores API keys (e.g., OPENAI_API_KEY)
├── .streamlit/                   # Streamlit configuration for custom theme
│   └── config.toml
├── environment.yml               # Conda environment definition
├── README.md                     # This README file
└── streamlit_agent_app.py        # The main Streamlit application and agent logic
```

## 🚀 Setup and Running the Project

### Prerequisites

- Python 3.9+: Recommended.

- Conda: For environment management.

- OpenAI API Key: You'll need an API key from platform.openai.com. Ensure your account has sufficient credits.

### Step-by-Step Guide

1. Clone the Repository (or create the files manually):

```bash
git clone <your-repo-url>
cd DS-Agents
```

2. Create a Conda Environment:

- It's recommended to create a dedicated Conda environment using the `environment.yml` file for consistent dependencies.

- If you don't have `environment.yml`, you can create it based on the project's direct dependencies (as provided in previous conversations).

```bash
conda env create -f environment.yml # If you have environment.yml
# OR if you need to create it manually:
# conda create -n ai_agent_env python=3.10
# conda activate ai_agent_env
# pip install streamlit python-dotenv langchain langchain-openai numexpr plotly pandas numpy
```

3. Activate the Environment:

```bash
conda activate ai_agent_env
```

4. Create and Configure the `.env` file:

- In the root of your `DS-Agents` directory (next to `streamlit_agent_app.py`), create a file named `.env`.
- Add your OpenAI API key to this file:

```bash
# DS-Agents/.env
OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
```

- Important: Replace `"YOUR_OPENAI_API_KEY_HERE"` with your actual API key.
  Security Note: Always add `.env` to your `.gitignore` file to prevent sensitive information from being committed to version control.

5. Run the Streamlit Application:

- Ensure your terminal is in the `DS-Agents` directory.
- Run the Streamlit app:

```bash
streamlit run streamlit_agent_app.py --server.port 8505
```

6. Access the UI:

- Open your web browser and go to: `http://localhost:8505`

## 💬 How to Interact with the Agent

Once the Streamlit app is running, you can type your queries into the chat input box at the bottom. The agent will then process your request and decide which tool to use.

### Example Queries:

- Mathematical Calculation:

  - "What is 123 multiplied by 45 and then divided by 3?"

  - "Calculate (50 + 25) - 10."

- Factual Lookup:

  - "What is the capital of France?"

  - "What is the tallest mountain in the world?"

  - "What is the population of New York City?"

- Code Generation:

  - "Create a Python function that takes a list of numbers and returns their average."

  - "Generate Python code to read a text file line by line."

  - "Write a Python function to reverse a string without using slicing."

### Observe the Agent's Reasoning:

After the agent provides its answer, expand the "Agent's Thought Process (Step-by-Step)" section to see how it reasoned, which tool it selected, the input it provided to the tool, and the tool's observation. This provides valuable insight into the agent's decision-making.

Enjoy exploring the world of AI Agents!
