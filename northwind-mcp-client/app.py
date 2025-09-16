import streamlit as st
from agent import NorthwindAgent
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce log noise in Streamlit

# Page configuration
st.set_page_config(
    page_title="Northwind Database Assistant", 
    page_icon="🗄️",
    layout="centered"
)

# Title
st.title("🗄️ Northwind Database Assistant")
st.write("Ask questions about the Northwind database and I'll help you find the answers!")

# Initialize agent in session state
if "agent" not in st.session_state:
    with st.spinner("Initializing database assistant..."):
        try:
            st.session_state.agent = NorthwindAgent()
            st.success("Database assistant ready!")
        except Exception as e:
            st.error(f"Failed to initialize assistant: {e}")
            st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know about the Northwind database?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent.ask(prompt)
                st.write(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar with example questions
with st.sidebar:
    st.header("🔧 How It Works")
    st.write("""
    This app acts as a **Model Context Protocol (MCP) Client** and communicates with a **MCP Server** that exposes specialized tools for the Northwind database. 
    - Uses an AI agent (powered by GPT-4.1-mini)
    - **MCP Server**: Provides database tools (schema, query, reports)
    - **AI Agent**: Uses LLM + MCP Server tools to understand your questions and generate answers.
    """)
    
    st.divider()
    
    st.header("💡 Example Questions")
    
    example_questions = [
        "List the first 5 customers",
        "What tables are available?",
        "Show me orders for customer FAPSM", 
        "Generate a sales report for August 2006",
        "What columns are in the customer table?"
    ]
    
    for question in example_questions:
        if st.button(question, key=f"example_{hash(question)}"):
            # Add the example question as if the user typed it
            st.session_state.messages.append({"role": "user", "content": question})
            
            # Get response
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent.ask(question)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
            # Rerun to show the new messages
            st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()