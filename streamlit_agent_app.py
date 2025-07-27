# ai_agent_demo/streamlit_agent_app.py
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import OpenAI # Or from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain import hub
import re # For parsing MLflow URL from subprocess output (though not used in this specific agent demo)

# NEW: Imports for capturing stdout
import io
import contextlib

# --- Load Environment Variables ---
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
serpapi_api_key = os.getenv("SERPAPI_API_KEY") # Only if using SerpAPI for search tool

# --- Streamlit UI Setup ---
st.set_page_config(page_title="AI Agent Demo: Intelligent Tool Use", layout="wide")
st.title("🤖 AI Agent Demo: Intelligent Tool Use")
st.markdown("Ask the agent questions that require either **math calculations** or **simple factual lookups**.")

# --- Initialize LLM (Agent's Brain) ---
if not openai_api_key:
    st.error("OPENAI_API_KEY not found in .env file. Please set it to run the agent.")
    st.stop() # Stop the app if API key is missing

try:
    llm = OpenAI(openai_api_key=openai_api_key, temperature=0) # Use a low temperature for more deterministic behavior
except Exception as e:
    st.error(f"Failed to initialize OpenAI LLM: {e}. Check your API key and internet connection.")
    st.stop()

# --- Define Tools (Agent's Skills) ---
def calculator(expression: str) -> str:
    """Useful for when you need to answer questions about math. Input should be a mathematical expression."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: Could not calculate. {e}"

def simple_search(query: str) -> str:
    """Useful for when you need to answer questions about current events or facts. Input should be a search query."""
    if "capital of france" in query.lower():
        return "The capital of France is Paris."
    elif "tallest mountain" in query.lower():
        return "Mount Everest is the tallest mountain."
    elif "population of new york city" in query.lower():
        return "The population of New York City is approximately 8.5 million."
    else:
        # If using SerpAPI:
        # from langchain_community.utilities import SerpAPIWrapper
        # if serpapi_api_key:
        #    search = SerpAPIWrapper(serpapi_api_key=serpapi_api_key)
        #    return search.run(query)
        # else:
        #    return "Search tool not configured (SERPAPI_API_KEY missing)."
        return "I don't have information on that specific search query in my internal knowledge base."

tools = [
    Tool(
        name="Calculator",
        func=calculator,
        description="Useful for when you need to answer questions about math. Input should be a mathematical expression."
    ),
    Tool(
        name="Search",
        func=simple_search,
        description="Useful for when you need to answer questions about current events or facts. Input should be a search query."
    )
]

# --- Define the Agent ---
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# --- Function to run agent and capture verbose output ---
@contextlib.contextmanager
def st_capture_stdout():
    """Context manager to capture stdout and display in Streamlit."""
    old_stdout = io.StringIO()
    with contextlib.redirect_stdout(old_stdout):
        yield old_stdout.getvalue()
    st.session_state.captured_output = old_stdout.getvalue()


# --- Streamlit Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "captured_output" not in st.session_state:
    st.session_state.captured_output = "" # Initialize captured output

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask the agent..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agent thinking..."):
            try:
                # NEW: Capture the agent's verbose output
                with st_capture_stdout() as output:
                    response = agent_executor.invoke({"input": prompt})
                
                agent_output = response['output']
                st.markdown(agent_output)
                st.session_state.messages.append({"role": "assistant", "content": agent_output})
                
                # Display the captured verbose output in an expander
                if st.session_state.captured_output:
                    with st.expander("Agent's Thought Process"):
                        st.code(st.session_state.captured_output)

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"An error occurred: {e}"})
