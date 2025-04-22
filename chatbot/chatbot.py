# import streamlit as st
# from langchain_core.messages import AIMessage, HumanMessage
# from dotenv import load_dotenv
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_ollama import ChatOllama


# load_dotenv()

# # app config
# # st.set_page_config(page_title="Streaming bot", page_icon="🤖")
# st.title("Chat bot")

# def get_response(user_query, chat_history):

#     template = """
#     You are a helpful assistant. Answer the following questions considering the history of the conversation:

#     Chat history: {chat_history}

#     User question: {user_question}
#     """

#     prompt = ChatPromptTemplate.from_template(template)

    
#     llm = ChatOllama(
#         model="llama3.2:1b",
#         temperature=0,
#         # other params...
#         )
        
#     chain = prompt | llm | StrOutputParser()
    
#     return chain.stream({
#         "chat_history": chat_history,
#         "user_question": user_query,
#     })

# # session state
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = [
#         AIMessage(content="Hello, I am a bot. How can I help you?"),
#     ]

    
# # conversation
# for message in st.session_state.chat_history:
#     if isinstance(message, AIMessage):
#         with st.chat_message("AI"):
#             st.write(message.content)
#     elif isinstance(message, HumanMessage):
#         with st.chat_message("Human"):
#             st.write(message.content)

# # user input
# user_query = st.chat_input("Type your message here...")
# if user_query is not None and user_query != "":
#     st.session_state.chat_history.append(HumanMessage(content=user_query))

#     with st.chat_message("Human"):
#         st.markdown(user_query)

#     with st.chat_message("AI"):
#         response = st.write_stream(get_response(user_query, st.session_state.chat_history))

#     st.session_state.chat_history.append(AIMessage(content=response))

import streamlit as st 
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
# from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI  # Import for OpenAI models

load_dotenv()

# app config
st.set_page_config(page_title="Streaming bot", page_icon="🤖")
st.title("Chat bot")

# Sidebar for model selection
st.sidebar.title("Model Selection")
model_option = st.sidebar.selectbox("Choose a model", ["OpenAI", "Llama"])

# API Key input for OpenAI if selected
if model_option == "OpenAI":
    openai_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

# Function to get response from selected model
def get_response(user_query, chat_history):
    template = """
    You are a helpful assistant. Answer the following questions considering the history of the conversation:

    Chat history: {chat_history}

    User question: {user_question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    if model_option == "OpenAI":
        if openai_api_key:  # Ensure API key is provided
            llm = ChatOpenAI(
                api_key=openai_api_key,
                model="gpt-4o-mini",  # Change to preferred OpenAI model
                temperature=0,
                # other params...
                )
        else:
            st.error("Please enter your OpenAI API key.")
            return None
    else:  # If Llama model is selected
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            # other params...
        )

    chain = prompt | llm | StrOutputParser()

    return chain.stream({
        "chat_history": chat_history,
        "user_question": user_query,
    })

# session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am a bot. How can I help you?"),
    ]

# conversation display
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# user input
user_query = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    if model_option == "OpenAI" and not openai_api_key:
        st.error("OpenAI model selected. Please provide an API key.")
    else:
        with st.chat_message("AI"):
            response = st.write_stream(get_response(user_query, st.session_state.chat_history))

        if response:
            st.session_state.chat_history.append(AIMessage(content=response))
