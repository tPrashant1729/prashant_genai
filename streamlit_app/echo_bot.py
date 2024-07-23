# import streamlit as st
# import random
# import time
# import datetime

# # Streamed response emulator
# def response_generator():
#     response = random.choice(
#         [
#             "Hello there! How can I assist you today?",
#             "Hi, human! Is there anything I can help you with?",
#             "Do you need help?",
#         ]
#     )
#     for word in response.split():
#         yield word + " "
#         time.sleep(0.05)


# st.title("Simple chat")

# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat messages from history on app rerun
# # for message in st.session_state.messages:
# #     with st.chat_message(message["role"]):
# #         st.markdown(message["content"])
# #         print(st.session_state.messages)

# for message in st.session_state.messages:
#     # print(message)
#     with st.chat_message(message["role"]):
#         st.markdown({message['content']})
#         # st.markdown({message['timestamp']})

# # Accept user input
# if prompt := st.chat_input("What is up?"):
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # Display assistant response in chat message container
#     with st.chat_message("assistant"):
#         response = st.write_stream(response_generator())
#     # Add assistant response to chat history
#     st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

import streamlit as st
import random
import time
import datetime
from groq import Groq
import os

# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


st.title("Groq-Llama-GPT")
groq_api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=groq_api_key,)

if "groq_model" not in st.session_state:
    st.session_state["groq_model"] = "llama3-8b-8192"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    # print('-'*40)
    # print(message)
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        st.markdown(message["timestamp"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    user_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with st.chat_message("user"):
        st.markdown(prompt)
        st.markdown(user_time)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt,"timestamp": user_time})

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["groq_model"],
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
        content = ""
        # Display the model content on the Streamlit page
        for chunk in stream:
            if chunk.choices:
                choice = chunk.choices[0]  # Assuming there is only one choice for simplicity
                if choice.delta.content is not None:
                    content += choice.delta.content
        st.markdown(f"LLaMA 3: {content}")

        # Display assistant time
        assistant_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(assistant_time)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": content, "timestamp": assistant_time})
