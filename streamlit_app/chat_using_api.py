import streamlit as st
from langchain_groq import ChatGroq


st.title('🦜🔗 Quickstart App')

groq_api_key = st.sidebar.text_input('Groq API Key', type='password')

def generate_response(input_text):
    llm = ChatGroq(temperature=0.7, api_key=groq_api_key)
    st.info(llm.invoke(input_text).content)

with st.form('my_form'):
    text = st.text_area('Enter text:', 'What are the three key pieces of advice for learning how to code?')
    submitted = st.form_submit_button('Submit')
    if not groq_api_key.startswith('gsk_'):
        st.warning('Please enter your Groq API key!', icon='⚠')
    if submitted and groq_api_key.startswith('gsk_'):
        generate_response(text)