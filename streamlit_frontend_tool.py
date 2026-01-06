import streamlit as st
from langgraph_tool_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid

# =========================== Utilities ===========================
def generate_thread_id():
    return uuid.uuid4()


def get_human_readable_chat_name(thread_id, messages):
    """
    Generate a human-readable name for a chat conversation from message history.
    
    This function extracts the first human (user) message from the conversation
    and creates a concise, readable title by truncating it intelligently at 
    word boundaries. If no messages exist, it returns a default "New Chat" label.
    
    Args:
        thread_id (UUID): Unique identifier for the chat thread (unused in current
                         implementation but preserved for future enhancements).
        messages (List[BaseMessage]): List of conversation messages containing
                                      HumanMessage and AIMessage objects.
    
    Returns:
        str: Human-readable chat title suitable for display in UI.
    
    Examples:
        >>> get_human_readable_chat_name(uuid4(), [HumanMessage("Hello, how are you?")])
        'Hello, how are you?'
        
        >>> get_human_readable_chat_name(uuid4(), [HumanMessage("Can you explain machine learning concepts in simple terms for a beginner?")])
        'Can you explain machine learning concepts...'
        
        >>> get_human_readable_chat_name(uuid4(), [])
        'New Chat'
    """
    if not messages:
        return "New Chat"
    
    # Find first human message
    for msg in messages:
        if isinstance(msg, HumanMessage):
            first_message = msg.content
            
            # Take first 30 characters or first sentence
            if len(first_message) > 30:
                # Try to cut at a space to avoid cutting words
                if ' ' in first_message[:30]:
                    cut_index = first_message[:30].rfind(' ')
                    name = first_message[:cut_index] + "..."
                else:
                    name = first_message[:27] + "..."
            else:
                name = first_message
            
            # Clean up the name (remove extra spaces, newlines)
            name = name.strip()
            name = name.replace('\n', ' ')
            name = ' '.join(name.split())  # Remove multiple spaces
            
            # If name is still empty, use default
            if not name:
                return "Chat Conversation"
            
            return name
    
    # If no human message found
    return "Chat Conversation"



def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get("messages", [])

# ======================= Session Initialization ===================
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

add_thread(st.session_state["thread_id"])

# ============================ Sidebar ============================
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")
for thread_id in st.session_state["chat_threads"][::-1]:
    # Load messages for this thread
    messages = load_conversation(thread_id)
    
    # Get human readable name
    chat_name = get_human_readable_chat_name(thread_id, messages)
    
    # Display button with human readable name
    if st.sidebar.button(chat_name, key=str(thread_id)):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            temp_messages.append({"role": role, "content": msg.content})
        st.session_state["message_history"] = temp_messages

# ============================ Main UI ============================

# Render history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Type here")

if user_input:
    # Show user's message
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn",
    }

    # Assistant streaming block
    with st.chat_message("ai"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    # Save assistant message
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )