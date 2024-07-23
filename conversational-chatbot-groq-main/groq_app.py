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

load_dotenv()
groq_api_key = os.environ.get('GROQ_API_KEY')

st.set_page_config(page_title="Plotting Demo", page_icon="📈")
llm_groq = ChatGroq(
    groq_api_key=groq_api_key,
    model_name='mixtral-8x7b-32768'
)

st.title("PDF Conversational Retrieval")

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

# import os
# import PyPDF2
# from langchain_community.embeddings import OllamaEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import Chroma
# from langchain.chains import ConversationalRetrievalChain
# from langchain_community.chat_models import ChatOllama
# from langchain_groq import ChatGroq
# from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain.memory import  ConversationBufferMemory
# import chainlit as cl
# from dotenv import load_dotenv

# load_dotenv()  #
# groq_api_key = os.environ.get('GROQ_API_KEY')

# # llm_local = ChatOllama(model="mistral:instruct")
# # llm_local = ChatOllama(model="llama3")
# llm_groq = ChatGroq(
#             groq_api_key=groq_api_key,
#             #model_name='llama2-70b-4096' 
#             model_name='mixtral-8x7b-32768'
#     )

# @cl.on_chat_start
# async def on_chat_start():
    
#     files = None #Initialize variable to store uploaded files

#     # Wait for the user to upload a file
#     while files is None:
#         files = await cl.AskFileMessage(
#             content="Please upload a pdf file to begin!",
#             accept=["application/pdf"],
#             max_size_mb=100,
#             timeout=180, 
#         ).send()

#     file = files[0] # Get the first uploaded file
    
#     # Inform the user that processing has started
#     msg = cl.Message(content=f"Processing `{file.name}`...")
#     await msg.send()

#     # Read the PDF file
#     pdf = PyPDF2.PdfReader(file.path)
#     pdf_text = ""
#     for page in pdf.pages:
#         pdf_text += page.extract_text()

#     # Split the text into chunks
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     texts = text_splitter.split_text(pdf_text)

#     # Create a metadata for each chunk
#     metadatas = [{"source": f"{i}-pl"} for i in range(len(texts))]

#     # Create a Chroma vector store
#     embeddings = OllamaEmbeddings(model="nomic-embed-text")
#     # embeddings = OllamaEmbeddings(model="mxbai-embed-large")
#     #embeddings = OllamaEmbeddings(model="llama2:7b")
#     docsearch = await cl.make_async(Chroma.from_texts)(
        
#         texts, embeddings, metadatas=metadatas
#     )
    
#     # Initialize message history for conversation
#     message_history = ChatMessageHistory()
    
#     # Memory for conversational context
#     memory = ConversationBufferMemory(
#         memory_key="chat_history",
#         output_key="answer",
#         chat_memory=message_history,
#         return_messages=True,
#     )

#     # Create a chain that uses the Chroma vector store
#     chain = ConversationalRetrievalChain.from_llm(
#         llm = llm_groq,
#         # llm = llm_local,
#         chain_type="stuff",
#         retriever=docsearch.as_retriever(),
#         memory=memory,
#         return_source_documents=True,
#     )

#     # Let the user know that the system is ready
#     msg.content = f"Processing `{file.name}` done. You can now ask questions!"
#     await msg.update()
#     #store the chain in user session
#     cl.user_session.set("chain", chain)


# @cl.on_message
# async def main(message: cl.Message):
        
#      # Retrieve the chain from user session
#     chain = cl.user_session.get("chain") 
#     #call backs happens asynchronously/parallel 
#     cb = cl.AsyncLangchainCallbackHandler()
    
#     # call the chain with user's message content
#     res = await chain.ainvoke(message.content, callbacks=[cb])
#     answer = res["answer"]
#     source_documents = res["source_documents"] 

#     text_elements = [] # Initialize list to store text elements
    
#     # Process source documents if available
#     if source_documents:
#         for source_idx, source_doc in enumerate(source_documents):
#             source_name = f"source_{source_idx}"
#             # Create the text element referenced in the message
#             text_elements.append(
#                 cl.Text(content=source_doc.page_content, name=source_name)
#             )
#         source_names = [text_el.name for text_el in text_elements]
        
#          # Add source references to the answer
#         if source_names:
#             answer += f"\nSources: {', '.join(source_names)}"
#         else:
#             answer += "\nNo sources found"
#     #return results
#     await cl.Message(content=answer, elements=text_elements).send()