import os
import PyPDF2
import streamlit as st
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

st.set_page_config(
    page_title="PDF RAG",
    page_icon="😎",
)
load_dotenv()
groq_api_key = os.environ.get('GROQ_API_KEY')


llm_groq = ChatGroq(
    groq_api_key=groq_api_key,
    model_name='mixtral-8x7b-32768'
)



# File uploader
uploaded_file = st.file_uploader("Please upload a PDF file to begin!", type=["pdf"])

if uploaded_file is not None:
    st.write(f"Processing `{uploaded_file.name}`...")

    # Read the PDF file
    pdf = PyPDF2.PdfReader(uploaded_file)
    pdf_text = ""
    for page in pdf.pages:
        pdf_text += page.extract_text()

    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_text(pdf_text)

    # Create metadata for each chunk
    metadatas = [{"source": f"{i}-pl"} for i in range(len(texts))]

    # Create a Chroma vector store
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    docsearch = Chroma.from_texts(texts, embeddings, metadatas=metadatas)

    # Initialize message history for conversation
    message_history = ChatMessageHistory()

    # Memory for conversational context
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    # Create a chain that uses the Chroma vector store
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm_groq,
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        memory=memory,
        return_source_documents=True,
    )

    st.write(f"Processing `{uploaded_file.name}` done. You can now ask questions!")

    # Input box for user to ask questions
    user_question = st.text_input("Ask a question about the PDF:")

    if user_question:
        res = chain({
            "question": user_question
        })
        answer = res["answer"]
        source_documents = res["source_documents"]

        st.write("Answer:")
        st.write(answer)

        if source_documents:
            st.write("Sources:")
            for idx, doc in enumerate(source_documents):
                st.write(f"Source {idx+1}:")
                st.write(doc.page_content)
else:
    st.write("Please upload a PDF file to begin!")
