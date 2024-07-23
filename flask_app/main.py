import os
import PyPDF2
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_session import Session
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate

load_dotenv()
groq_api_key = os.environ.get('GROQ_API_KEY')

app = Flask(__name__)
app.secret_key = 'your_secret_key'

llm_groq = ChatGroq(
    groq_api_key=groq_api_key,
    model_name='mixtral-8x7b-32768'
)

# Build prompt
template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Always say "thanks for asking!" at the end of the answer. 
{context}
Question: {question}
Helpful Answer:"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and file.filename.endswith('.pdf'):
        pdf_text = extract_text_from_pdf(file)
        texts, metadatas = process_text(pdf_text)
        docsearch = create_vector_store(texts, metadatas)
        message_history = ChatMessageHistory()
        memory = create_memory(message_history)

        chain = ConversationalRetrievalChain.from_llm(
            llm=llm_groq,
            chain_type="stuff",
            retriever=docsearch.as_retriever(),
            memory=memory,
            return_source_documents=True,
            combine_docs_chain_kwargs = {"prompt": QA_CHAIN_PROMPT}
        )

        request.session['chain'] = chain
        flash('File processed successfully. You can now ask questions!')
        return redirect(url_for('ask_question'))

    else:
        flash('Please upload a valid PDF file')
        return redirect(request.url)

@app.route('/ask', methods=['GET', 'POST'])
def ask_question():
    if request.method == 'POST':
        user_question = request.form['question']
        chain = request.session.get('chain')
        
        if chain:
            res = chain({
                "question": user_question
            })
            answer = res["answer"]
            source_documents = res["source_documents"]
            return render_template('answer.html', answer=answer, source_documents=source_documents)

    return render_template('ask.html')

def extract_text_from_pdf(uploaded_file):
    pdf = PyPDF2.PdfReader(uploaded_file)
    pdf_text = ""
    for page in pdf.pages:
        pdf_text += page.extract_text()
    return pdf_text

def process_text(pdf_text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_text(pdf_text)
    metadatas = [{"source": f"{i}-pl"} for i in range(len(texts))]
    return texts, metadatas

def create_vector_store(texts, metadatas):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    docsearch = Chroma.from_texts(texts, embeddings, metadatas=metadatas)
    return docsearch

def create_memory(message_history):
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )
    return memory

if __name__ == '__main__':
    app.run(debug=True)
