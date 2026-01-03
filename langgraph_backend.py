from langgraph.graph import StateGraph , START , END
from typing import TypedDict, Annotated
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver  # stores in ram
from langchain_core.messages import BaseMessage 

from dotenv import load_dotenv


load_dotenv()

model = ChatGoogleGenerativeAI(model = "gemini-2.5-flash-lite")

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage] , add_messages]


def chat_node(state : ChatState):
    messages = state['messages']
    result =model.invoke(messages)

    return {"messages" : [result] }


# checkpointer 
checkpointer = InMemorySaver()
graph = StateGraph(ChatState)

graph.add_node("chat_node" , chat_node)

graph.add_edge(START , "chat_node")
graph.add_edge("chat_node" , END)

chatbot  = graph.compile(checkpointer=checkpointer)
