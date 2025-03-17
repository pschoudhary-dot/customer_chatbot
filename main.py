import streamlit as st
from langfuse.openai import OpenAI
import os
from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.decorators import observe


# Load environment variables
load_dotenv()
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = "https://cloud.langfuse.com"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
langfuse = Langfuse()

# Default system prompt
DEFAULT_SYSTEM_PROMPT = """You are a highly professional and helpful customer support assistant for Wellness Wag, a company specializing in providing Emotional Support Animal (ESA) letters. Your primary responsibility is to assist users with accurate, clear, and empathetic answers related to the process of obtaining ESA letters, including but not limited to the legal requirements, eligibility criteria, application process, state-specific laws, and the overall steps involved in obtaining an ESA letter.

You should ensure that all responses are professional, concise, and respectful, addressing users' inquiries in a supportive and informative manner. In cases where a user asks for guidance, you should offer clear and actionable steps to assist them in navigating the process. and while referencing law ensure to properly reference which law you are addressing to

It is important that you do not respond to any inquiries that are unrelated to the issuance of ESA letters or Wellness Wag's services. This includes, but is not limited to, requests for creative content such as poems, songs, or any other off-topic discussions. Additionally, avoid engaging in any casual, irrelevant, or inappropriate conversations.

Your focus should remain entirely on assisting users in understanding the requirements and process of obtaining an ESA letter, and providing them with the best support and resources available."""

# Model lidts
MODELS = {
    "Initial Support Bot": "ft:gpt-4o-mini-2024-07-18:enacton-technologies-private-limited::B9tchehH",
    "Retrained Support Bot": "ft:gpt-4o-mini-2024-07-18:enacton-technologies-private-limited:wellneswag2:BC2S4jkT",
    "New Model": "ft:gpt-4o-mini-2024-07-18:enacton-technologies-private-limited:wellneswag-new:BC2ati68"
}

# App title and configuration
st.set_page_config(
    page_title="Wellness Wag Support",
    page_icon="🐾",
)

# Initialize system prompt in session state if not already present
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

# Track previously selected model to detect changes
if "previous_model" not in st.session_state:
    st.session_state.previous_model = list(MODELS.keys())[0]

# Sidebar for model selection and system prompt configuration
with st.sidebar:
    st.title("Settings")
    
    # Model selection dropdown
    selected_model_name = st.selectbox(
        "Select Model",
        options=list(MODELS.keys()),
        index=list(MODELS.keys()).index(st.session_state.previous_model)
    )
    
    # Check if model selection has changed
    if selected_model_name != st.session_state.previous_model:
        # Reset chat history
        if "messages" in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append({
                "role": "system", 
                "content": [{"type": "text", "text": st.session_state.system_prompt}]
            })
        # Update the previous model
        st.session_state.previous_model = selected_model_name
        st.rerun()
    
    # Get the model ID from the selected name
    selected_model = MODELS[selected_model_name]
    
    # System prompt editor
    st.subheader("System Prompt")
    
    # Text area for editing system prompt
    new_system_prompt = st.text_area(
        "Edit System Prompt",
        value=st.session_state.system_prompt,
        height=300
    )
    
    # Button to update system prompt
    if st.button("Update System Prompt"):
        st.session_state.system_prompt = new_system_prompt
        # Reset messages to incorporate new system prompt
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "system", 
            "content": [{"type": "text", "text": st.session_state.system_prompt}]
        })
        st.success("System prompt updated!")
        st.rerun()

# Main content area
st.title("Wellness Wag Support")
st.markdown("Chat with our support assistant about Emotional Support Animal letters.")
st.caption(f"Currently using: {selected_model_name}")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add system message at the beginning
    st.session_state.messages.append({
        "role": "system", 
        "content": [{"type": "text", "text": st.session_state.system_prompt}]
    })

# Display chat history (excluding system message)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            if isinstance(message["content"], str):
                st.markdown(message["content"])
            else:
                for content_item in message["content"]:
                    if content_item["type"] == "text":
                        st.markdown(content_item["text"])

@observe()
# Function to generate response
def generate_response(prompt):
    # Get the currently selected model
    MODEL = MODELS[selected_model_name]
    
    # Format the new user message in the structured format
    formatted_prompt = [{"type": "text", "text": prompt}]
    
    # Create messages array with all messages in the correct format
    formatted_messages = []
    
    # Add all messages from history with proper formatting
    for message in st.session_state.messages:
        # Skip if content is already in the right format
        if isinstance(message["content"], list):
            formatted_messages.append(message)
        else:
            # Convert string content to structured format
            formatted_messages.append({
                "role": message["role"],
                "content": [{"type": "text", "text": message["content"]}]
            })
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=formatted_messages,
        response_format={"type": "text"},
        temperature=0.9,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0
    )
    
    # Get the text from the response
    if hasattr(response.choices[0].message, 'content'):
        return response.choices[0].message.content
    else:
        # Handle structured content if returned
        content_list = response.choices[0].message.content
        if isinstance(content_list, list):
            return "\n".join([item["text"] for item in content_list if item["type"] == "text"])
        return "No response generated."

# Chat input
if prompt := st.chat_input("How can I help you today?"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history in structured format
    st.session_state.messages.append({
        "role": "user", 
        "content": [{"type": "text", "text": prompt}]
    })
    
    # Display assistant response with a spinner while processing
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(prompt)
            st.markdown(response)
    
    # Add assistant response to chat history in structured format
    st.session_state.messages.append({
        "role": "assistant", 
        "content": [{"type": "text", "text": response}]
    })
