import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from langraph_rag_backend import (
    chatbot,
    ingest_pdf,
    retrieve_all_threads,
    thread_document_metadata,
)


# =========================== Utilities ===========================
def generate_thread_id():
    """
    Generate a unique thread identifier for a new chat conversation.
    
    Returns:
        UUID: A universally unique identifier (UUID4) string.
    
    Note:
        Uses UUID version 4 which generates random UUIDs with very low
        collision probability.
    """
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    """
    Reset the current chat session and initialize a new conversation thread.
    
    This function:
    1. Generates a new unique thread ID
    2. Updates the current thread ID in session state
    3. Adds the new thread to the chat threads list
    4. Clears the current message history
    
    Side Effects:
        Modifies session state variables: 'thread_id' and 'message_history'.
    """
    thread_id =     generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    """
    Add a thread ID to the list of chat threads if not already present.
    
    Args:
        thread_id (UUID): The thread identifier to add to the collection.
    
    Side Effects:
        Appends thread_id to st.session_state['chat_threads'] list if it doesn't exist.
    """
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        
def load_conversation(thread_id):
    """
    Load conversation messages for a specific thread from the chatbot backend.
    
    Args:
        thread_id (UUID): The thread identifier for which to load messages.
    
    Returns:
        List[BaseMessage]: List of message objects (HumanMessage/AIMessage) from
                          the conversation. Returns empty list if no messages exist
                          or if thread doesn't exist.
    
    Note:
        Accesses the chatbot's state management system to retrieve stored
        conversation history.
    """
    state =  chatbot.get_state(config={"configurable" : {"thread_id" :  thread_id}})

    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])

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


# ======================= Session Initialization ===================
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

if "ingested_docs" not in st.session_state:
    st.session_state["ingested_docs"] = {}

add_thread(st.session_state["thread_id"])

thread_key = str(st.session_state["thread_id"])
thread_docs = st.session_state["ingested_docs"].setdefault(thread_key, {})
threads = st.session_state["chat_threads"][::-1]
selected_thread = None

# ============================ Sidebar ============================
st.sidebar.title("LangGraph PDF Chatbot")
st.sidebar.markdown(f"**Thread ID:** `{thread_key}`")

if st.sidebar.button("New Chat", use_container_width=True):
    reset_chat()
    st.rerun()

if thread_docs:
    latest_doc = list(thread_docs.values())[-1]
    st.sidebar.success(
        f"Using `{latest_doc.get('filename')}` "
        f"({latest_doc.get('chunks')} chunks from {latest_doc.get('documents')} pages)"
    )
else:
    st.sidebar.info("No PDF indexed yet.")

uploaded_pdf = st.sidebar.file_uploader("Upload a PDF for this chat", type=["pdf"])
if uploaded_pdf:
    if uploaded_pdf.name in thread_docs:
        st.sidebar.info(f"`{uploaded_pdf.name}` already processed for this chat.")
    else:
        with st.sidebar.status("Indexing PDF…", expanded=True) as status_box:
            summary = ingest_pdf(
                uploaded_pdf.getvalue(),
                thread_id=thread_key,
                filename=uploaded_pdf.name,
            )
            thread_docs[uploaded_pdf.name] = summary
            status_box.update(label="✅ PDF indexed", state="complete", expanded=False)

st.sidebar.subheader("Past conversations")
if not threads:
    st.sidebar.write("No past conversations yet.")
else:
    for thread_id in threads:
         # Load messages for this thread
        messages = load_conversation(thread_id)
    
        # Get human readable name
        chat_name = get_human_readable_chat_name(thread_id, messages)
    
        # Display button with human readable name
        if st.sidebar.button( chat_name,   key=f"side-thread-{thread_id}"):
            selected_thread = thread_id

# ============================ Main Layout ========================
st.title("Multi Utility Chatbot")

# Chat area
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Ask about your document or use tools")

if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    CONFIG = {
        "configurable": {"thread_id": thread_key},
        "metadata": {"thread_id": thread_key},
        "run_name": "chat_turn",
    }

    with st.chat_message("ai"):
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, _ in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
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

                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )

    doc_meta = thread_document_metadata(thread_key)
    if doc_meta:
        st.caption(
            f"Document indexed: {doc_meta.get('filename')} "
            f"(chunks: {doc_meta.get('chunks')}, pages: {doc_meta.get('documents')})"
        )

st.divider()

if selected_thread:
    st.session_state["thread_id"] = selected_thread
    messages = load_conversation(selected_thread)

    temp_messages = []
    for msg in messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        temp_messages.append({"role": role, "content": msg.content})
    st.session_state["message_history"] = temp_messages
    st.session_state["ingested_docs"].setdefault(str(selected_thread), {})
    st.rerun()
