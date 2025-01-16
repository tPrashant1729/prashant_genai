# from youtube_transcript_api import YouTubeTranscriptApi
# from langchain_community.document_loaders import YoutubeLoader
# video_id = "https://www.youtube.com/watch?v=QsYGlZkevEg"

# loader = YoutubeLoader.from_youtube_url(
#     video_id,
#     add_video_info=False,
#     language=["en", "id", "hi"],
#     translation="hi",
# )
# print(loader.load())
# # transcript_list = YouTubeTranscriptApi.list_transcripts("QsYGlZkevEg")
# # print(transcript_list)

from langchain_groq import ChatGroq
import base64
import io
import dotenv
dotenv.load_dotenv()
import os
api = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="llama-3.2-11b-vision-preview", api_key= api, )
from langchain_core.messages import HumanMessage

# Open the image file in binary mode
with open("/home/dnk131/Downloads/images/realtime-enhance-enhanced.png", "rb") as image_file:
    # Encode the image to Base64
    image_data = image_file.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')

# print(base64_image)

query = "Descibe the image like an experienced artist"
message = HumanMessage(
    content=[
        {"type": "text", "text": query},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_image}"},
        },
    ],
)
response = llm.invoke([message])
print(response.content)