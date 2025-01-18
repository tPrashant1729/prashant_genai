import streamlit as st
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
import tempfile
from markitdown import MarkItDown

st.title("Improve Your Self")
st.write("This is a simple example to help you prepare better.")

# Initialize session state
if 'jd' not in st.session_state:
    st.session_state.jd = ""
if 'text' not in st.session_state:
    st.session_state.text = ""
if 'suggestion' not in st.session_state:
    st.session_state.suggestion = ""
if 'ats_called' not in st.session_state:
    st.session_state.ats_called = False
if 'rewritten_resume' not in st.session_state:
    st.session_state.rewritten_resume = ""

ats_agent = Agent(
    name="ATS Agent",
    model=Groq(id="llama-3.3-70b-versatile"),
    show_tool_calls=False,
    markdown=True,
)

rewrite_agent = Agent(
    name="Rewrite Agent",
    model=Groq(id="llama-3.3-70b-versatile"),
    show_tool_calls=False,
    markdown=True,
)

# Input for Job Description (JD)
st.session_state.jd = st.text_area("Enter your Job Description (JD) here", st.session_state.jd)

if st.session_state.jd:
    st.markdown("### Job Description")
    st.markdown(st.session_state.jd)
else:
    st.error("Please enter the Job Description.")

# File uploader for resume
uploaded_file = st.file_uploader("Upload your resume (PDF):", type="pdf")

if uploaded_file is not None:
    try:
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        # Use MarkItDown to convert the PDF to Markdown
        md = MarkItDown()
        markdown_content = md.convert(temp_file_path).text_content

        if markdown_content.strip():
            st.session_state.text = markdown_content
            st.success("Resume uploaded successfully!")
        else:
            st.error("Unable to extract text from the uploaded PDF. Please try another file.")
    except Exception as e:
        st.error(f"An error occurred while processing the PDF: {e}")

if st.session_state.text:
    st.markdown("### Extracted Resume Text")
    st.markdown(st.session_state.text)
else:
    st.warning("Please upload your resume to proceed.")

# Function to stream agent's response
def stream_agent_response(prompt, agent: Agent):
    for delta in agent.run(prompt, stream=True):
        yield delta.content  # Stream each response part as it's generated

# ATS Analysis
if st.session_state.jd and st.session_state.text and not st.session_state.ats_called:

    ats_prompt = (
        f"Compare the job description and resume carefully and provide the ATS score (0-100) and suggestions to improve the resume in bullet points."
        f"\n\n### Job Description:\n{st.session_state.jd}"
        f"\n\n### Resume:\n{st.session_state.text}"
    )

    st.markdown("## Agent's Response")
    suggestion_container = st.empty()
    suggestion_text = ""
    for part in stream_agent_response(ats_prompt, ats_agent):
        suggestion_text += part
        suggestion_container.markdown(suggestion_text)

    # Save suggestions and mark ATS as called
    st.session_state.suggestion = suggestion_text
    st.session_state.ats_called = True


# Rewrite Resume functionality
if st.button("Rewrite Resume"):
    if st.session_state.suggestion:

        rewrite_prompt = (
            f"Rewrite the original resume to improve it based on the following suggestions to gain the highest ATS score possible:\n"
            f"{st.session_state.suggestion}"
            f"\n\n### Original Resume:\n{st.session_state.text}"
        )

        # Display rewritten resume
        st.markdown("## Rewritten Resume")
        rewrite_container = st.empty()
        rewrite_container.empty()
        rewrite_text = ""
        for part in stream_agent_response(rewrite_prompt, rewrite_agent):
            rewrite_text += part
            rewrite_container.markdown(rewrite_text)

        # Save rewritten resume
        st.session_state.rewritten_resume = rewrite_text
    else:
        st.error("No suggestions available. Please ensure ATS analysis is complete before rewriting.")
