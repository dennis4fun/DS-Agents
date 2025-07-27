# ai_agent_demo/streamlit_agent_app.py
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, PromptTemplate
import re

# Imports for capturing stdout
import io
import contextlib

# Disable LangSmith tracing if not explicitly used
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["LANGCHAIN_PROJECT"] = ""


# --- Load Environment Variables ---
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# --- Streamlit UI Setup ---
st.set_page_config(page_title="AI Agent Demo: Intelligent Tool Use", layout="wide")
st.title("🤵 AI Agent Demo: Intelligent Tool Use")
st.markdown("Ask the agent questions that require **math calculations**, **simple factual lookups**, or **code generation**.")

# --- Initialize LLM (Agent's Brain) ---
if not openai_api_key:
    st.error("OPENAI_API_KEY not found in .env file. Please set it to run the agent.")
    st.stop()

try:
    llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0, model_name="gpt-3.5-turbo")
    llm_code_gen = ChatOpenAI(openai_api_key=openai_api_key, temperature=0.2, model_name="gpt-3.5-turbo")
except Exception as e:
    st.error(f"Failed to initialize OpenAI LLM: {e}. Check your API key and internet connection.")
    st.stop()

# --- Define Tools (Agent's Skills) ---
def calculator(expression: str) -> str:
    """Useful for when you need to perform exact mathematical calculations. Input should be a precise mathematical expression (e.g., '2+2', '10*5', '30/6')."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: Could not calculate. {e}"

def simple_search(query: str) -> str:
    """Useful for when you need to look up specific factual information that is not a calculation or code generation. This tool has limited internal knowledge. Input should be a clear factual query."""
    if "capital of france" in query.lower():
        return "The capital of France is Paris."
    elif "tallest mountain" in query.lower():
        return "Mount Everest is the tallest mountain."
    elif "population of new york city" in query.lower():
        return "The Population of New York City is approximately 8.5 million."
    else:
        return "Search tool has no information on that specific query in its internal knowledge base."

def code_generator(coding_prompt: str) -> str:
    """Useful for when you need to generate Python code snippets or functions. Input should be a clear and concise coding request."""
    try:
        # FIX: Access the 'content' attribute of the AIMessage object
        code_response_obj = llm_code_gen.invoke(f"Generate Python code for the following request:\n\n{coding_prompt}\n\n```python\n")
        code_response = code_response_obj.content.strip() # Access .content here
        
        if code_response.startswith("```python"):
            code_response = code_response[len("```python"):].strip()
        if code_response.endswith("```"):
            code_response = code_response[:-len("```")].strip()
        return code_response
    except Exception as e:
        return f"Error generating code: {e}"

tools = [
    Tool(
        name="Calculator",
        func=calculator,
        description="Useful for when you need to perform exact mathematical calculations. Input should be a precise mathematical expression (e.g., '2+2', '10*5', '30/6')."
    ),
    Tool(
        name="Search",
        func=simple_search,
        description="Useful for when you need to look up specific factual information that is not a calculation or code generation. This tool has limited internal knowledge. Input should be a clear factual query."
    ),
    Tool(
        name="CodeGenerator",
        func=code_generator,
        description="Useful for when you need to generate Python code snippets or functions. Input should be a clear and concise coding request."
    )
]

# --- Define the Agent ---
template_system = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: You must always think about what to do. Your thought process should be clear and logical.
If the question is a mathematical calculation, you MUST use the Calculator tool.
If the question is a factual lookup, you MUST use the Search tool.
If the question is a coding request, you MUST use the CodeGenerator tool.
If a tool's output indicates it has no information, you must state "I cannot answer that question with the available tools." and then stop.
Do not make up answers.

Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question.
"""
prompt = ChatPromptTemplate.from_messages([
    ("system", template_system),
    ("human", "{input}\n\n{agent_scratchpad}")
])


agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Define st_capture_stdout at the top level
@contextlib.contextmanager
def st_capture_stdout():
    """Context manager to capture stdout and display in Streamlit."""
    old_stdout = io.StringIO()
    with contextlib.redirect_stdout(old_stdout):
        yield
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
                with st_capture_stdout():
                    response = agent_executor.invoke({"input": prompt})
                
                agent_output = response['output']
                
                # Display the agent's final output
                if agent_output.strip().startswith("def ") or agent_output.strip().startswith("class ") or "```python" in agent_output:
                    st.code(agent_output, language="python")
                else:
                    st.markdown(agent_output)
                
                st.session_state.messages.append({"role": "assistant", "content": agent_output})
                
                # Parse and display the captured verbose output in a structured way
                captured_text = st.session_state.captured_output
                
                pattern = re.compile(r'(\nThought:|Action:|Action Input:|Observation:)(.*?)(?=\nThought:|\nAction:|\nAction Input:|\nObservation:|\Z)', re.DOTALL)
                
                parsed_steps = []
                for match in pattern.finditer(captured_text):
                    key = match.group(1).strip().replace(":", "")
                    value = match.group(2).strip()
                    parsed_steps.append((key, value))

                if parsed_steps:
                    with st.expander("Agent's Thought Process (Step-by-Step)"):
                        for key, value in parsed_steps:
                            st.markdown(f"**{key}:**")
                            if key == "Action Input" or key == "Observation":
                                st.code(value)
                            else:
                                st.write(value)
                            st.markdown("---")
                else:
                    if captured_text:
                        with st.expander("Agent's Thought Process (Raw Output)"):
                            st.code(captured_text)

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"An error occurred: {e}"})
