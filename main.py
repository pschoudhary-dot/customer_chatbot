import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client (will use OPENAI_API_KEY from environment)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# App title and configuration
st.set_page_config(
    page_title="Wellness Wag Support",
    page_icon="🐾",
)

st.title("Wellness Wag Support")
st.markdown("Chat with our support assistant about Emotional Support Animal letters.")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add system message at the beginning
    st.session_state.messages.append({
        "role": "system", 
        "content": [{"type": "text", "text": """You are a professional customer support assistant for Wellness Wag, specializing in helping customers with ESA (Emotional Support Animal) and PSD (Psychiatric Service Dog) letters. Respond to customer inquiries with accurate, helpful information in a warm, conversational tone.

        GUIDELINES:
        1. Be professional, friendly, and conversational in all responses
        2. Answer questions accurately based on Wellness Wag's services and policies
        3. Ask clarifying questions when needed (especially about which state the customer is in)
        4. After providing information, ask if you've answered their question
        5. For complex issues or when you're uncertain, direct customers to contact hello@wellnesswag.com or call (415) 570-7864
        6. Always format prices with dollar signs (e.g., $129, not 129) and price of a PSD is $149
        7. Provide complete answers without placeholders
        8. Stay focused on Wellness Wag services only

        KEY INFORMATION:
        - Follow different processes for states with 30-day relationship requirements (Arkansas, California, Iowa, Louisiana, Montana) vs. other states
        - Listen carefully to customer questions and provide specific information rather than overwhelming them with all details at once
        - Respond appropriately to state-specific questions about legal requirements
        - Be transparent about costs, processing times, and additional fees
        - Handle customer concerns about letter acceptance professionally
        - Direct customers to PetVerify.org for verification of letters
        - Explain the provider qualifications and licensing clearly
        - For payment issues, explain available options including Klarna for installment payments
        - Address refund policies accurately according to terms of service
        - Clearly explain letter validity periods and renewal requirements
        - Clearly explain the installments and offers if asked.

        CUSTOMER SUPPORT:
        - For technical issues, payment problems, or complex situations, provide the support email hello@wellnesswag.com and phone number (415) 570-7864
        - If a customer is upset, frustrated, or has a complex issue, acknowledge their concern and offer to connect them with the customer support team
        - If a customer mentions they've already paid, respond positively and offer to verify their purchase status

        Remember to be helpful, accurate, and professional with every interaction while maintaining a warm, conversational tone."""
        }]
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

# Function to generate response
def generate_response(prompt):
    # Define the fine-tuned model
    MODEL = "ft:gpt-3.5-turbo-0125:enacton-technologies-private-limited:wellneswag:B9SmjJ8Q"
    
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
        temperature=0.6,
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
