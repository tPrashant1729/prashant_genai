import os
import json
from PyPDF2 import PdfReader

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

from langchain_groq import ChatGroq

llm = ChatGroq(model="mixtral-8x7b-32768")

# Load the JSON schema from the file  
with open('./schema.json', 'r') as file:  
    schema = json.load(file)  

# Now you can use the schema variable  
# print(schema)  

reader = PdfReader("./deedy-cv.pdf")

structured_llm = llm.with_structured_output(schema)

parsed = structured_llm.invoke(f"{reader.pages[0].extract_text()}")

# Convert the data to JSON format  
json_data = json.dumps(parsed, indent=4)  

# Print the JSON string  
print(json_data) 