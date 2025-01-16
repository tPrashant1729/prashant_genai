import requests
from bs4 import BeautifulSoup

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file


def fetch_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text_content = ''
    for paragraph in soup.find_all('p'):  # Extract text content from <p> tags
        text_content += paragraph.get_text() + ' '
    return text_content

from langchain.docstore.document import Document

urls = ["https://indianexpress.com/article/india/om-birla-election-lok-sabha-speaker-modi-opposition-9415980/" , "https://www.crummy.com/software/BeautifulSoup/bs4/doc/"]

list_text = []
docs = []
for url in urls:
    doc = Document(page_content=fetch_content(url),
              metadata={
                  "source": url
              }
             )
    docs.append(doc)

from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter

chunk_size =1000
chunk_overlap = 150

r_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap, 
    separators=["\n\n", "\n", "(?<=\. )", " ", ""]
)
c_splitter = CharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    separator = '\n'
)

r_pages = r_splitter.split_text(docs[0].page_content)
print(len(r_pages))

cleaned_r_pages = r_splitter.split_documents(docs)
cleaned_c_pages = c_splitter.split_documents(docs)

print(len(cleaned_r_pages))
print(len(cleaned_c_pages))

# Print the cleaned pages
for i, page in enumerate(cleaned_r_pages):
    print(f"Page {i+1}:\n{page}\n{'-'*40}")

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma, FAISS


splits = cleaned_r_pages
embedding = OllamaEmbeddings(model="nomic-embed-text")

vectordb = Chroma.from_documents(
    documents=splits,
    embedding=embedding,
    persist_directory='./'
)

query = "who is om birla"
retriever = vectordb.as_retriever()
docs = retriever.invoke(query)

vectordb.save_local("faiss_index",)

new_db = FAISS.load_local("faiss_index", embedding, allow_dangerous_deserialization = True)

docs = new_db.similarity_search(query)

question = "what is beautifulsoup?"
docs_ss = new_db.similarity_search(question,k=3)
len(docs_ss)

for doc in docs_ss:
    print(doc.metadata)