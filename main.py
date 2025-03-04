import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool
from langchain_cohere import ChatCohere
from pydantic import BaseModel
from src.prompt.chatbot_system_prompt import CHATBOT_SYSTEM_PROMPT
from src.utils import load_env_variable, remove_greeting
from src.tools import (
    get_available_fields_tool,
    search_table_for_query_tool,
    sql_query_generator_and_executor_tool,
)

load_dotenv()

app = FastAPI(title="Financial Advisor Chatbot")

# Allow CORS for all origins (you can restrict it to specific origins if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or specify a list of allowed origins)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)


COHERE_API_KEY: str = load_env_variable("COHERE_API_KEY", required=True)
COHERE_MODEL: str = load_env_variable("COHERE_MODEL", required=True)
CHATBOT_TEMPERATURE: float = float(
    load_env_variable("CHATBOT_TEMPERATURE", required=True)
)

# Initialize OpenAI LLM
llm = ChatCohere(
    model=COHERE_MODEL,
    temperature=CHATBOT_TEMPERATURE,
    cohere_api_key=COHERE_API_KEY,
)

search = GoogleSerperAPIWrapper()

# Define tools for the agent
tools = [
    Tool(
        name="web_search_assistant",
        func=search.run,
        description="Ideal for retrieving information from the web to supplement or enhance query responses. Use this tool to search for external data, validate assumptions, or find additional context relevant to the user's request.",
    ),
    get_available_fields_tool,
    search_table_for_query_tool,
    sql_query_generator_and_executor_tool,
]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            CHATBOT_SYSTEM_PROMPT
            + "\n\nThe client ID associated with this conversation: {client_id}",
        ),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

# Initialize the agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Create an agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    return_intermediate_steps=False,
)


class ChatRequest(BaseModel):
    query: str
    client_id: str


@app.post("/chat")
async def chat_with_bot(chat_request: ChatRequest):
    """
    Endpoint to process user queries using the agent, with a client_id to ensure
    relevant data is queried.
    """
    try:
        # Pass the client_id to the tool that will execute the SQL query
        query = f"""{chat_request.query}"""

        response = agent_executor.invoke(
            {"input": query, "client_id": chat_request.client_id}
        )

        return remove_greeting(response["output"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run the FastAPI app with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
