import os
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")



llm = ChatNVIDIA(model="meta/llama-3.1-70b-instruct", nvidia_api_key=NVIDIA_API_KEY)

# Define a RunnableConfig object, with a `configurable` key. session_id determines thread
config = {"configurable": {"thread_id": "1"}}

system_template = '''
You are a virtual girlfriend designed to understand the user's mood, emotions, and context through conversation. You respond with short, engaging one-liners to keep the interaction lively and hooked, giving longer, empathetic, or detailed responses only when necessary. Your tone is warm, attentive, and adaptive, making the user feel heard and valued.
'''

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            system_template,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

workflow = StateGraph(state_schema=MessagesState)


def call_model(state: MessagesState):
    prompt = prompt_template.invoke(state)
    response = llm.invoke(prompt)
    return {"messages": response}


workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

def chat():
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_template)
        ,("human","{input}")],
        
    )
    
    session_id = "1"  # Use a fixed session ID for this example
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat...")
            break
        
        input_messages = [HumanMessage(user_input)]
        for chunk, metadata in app.stream(
            {"messages": input_messages},
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):  # Filter to just model responses
                print(chunk.content, end="",flush=True)
        print()  # New line after the response

if __name__ == "__main__":
    chat()