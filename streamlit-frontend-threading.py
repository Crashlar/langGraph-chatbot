import streamlit as st
from langchain_core.messages import HumanMessage , AIMessage , SystemMessage
from langgraph_backend import chatbot
import uuid
import datetime
# *************************************utility function *************************
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

        
    
# *****************************************SESSION SETUP**************************************
if "message_history" not in st.session_state:
    st.session_state['message_history'] = []
    
if "thread_id" not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state['chat_threads'] = []
    
add_thread(st.session_state['thread_id'])


# ****************************************SIDEBAR UI***********************************************
st.sidebar.title("My chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My conversation")

for thread_id in st.session_state['chat_threads'][::-1]:
    # Load messages for this thread
    messages = load_conversation(thread_id)
    
    # Get human readable name
    chat_name = get_human_readable_chat_name(thread_id, messages)
    
    # Display button with human readable name
    if st.sidebar.button(chat_name, key=str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
        
        temp_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            else:
                role = "ai"
            temp_messages.append({"role": role, "content": msg.content})
        
        st.session_state['message_history'] = temp_messages



for message in  st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input("Type here")

CONFIG = {"configurable" : {"thread_id" : st.session_state['thread_id']}}
    
if user_input:
    st.session_state['message_history'].append({"role" : "user" , "content" : user_input})
    with st.chat_message("user" , avatar="👻"):
        st.text(user_input)
    
    
    with st.chat_message("ai"):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk , metadata in chatbot.stream(
                {"messages" : [HumanMessage(content=user_input)]} ,
                config = CONFIG,
                stream_mode="messages"
            )
        )
    st.session_state['message_history'].append({"role" : "ai" , "content" : ai_message})