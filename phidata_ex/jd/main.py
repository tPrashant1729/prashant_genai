import os
import streamlit as st
from phi.agent import Agent, RunResponse
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
import tempfile
from markitdown import MarkItDown
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# List of possible API key names
POSSIBLE_API_KEYS = [
    "GROQ_API_KEY", "GROQ_KEY", "GROQAPIKEY", "GROQ_API", "GROQ_SECRET",
    "GROQ_TOKEN", "GROQ_ACCESS_TOKEN"
]


st.title("Improve Your Self")
st.caption("This is a simple example to help you prepare better.")

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

def reset_session_state():
    """Reset session state variables for a new interview session."""
    st.session_state.current_question_index = 0
    st.session_state.scores = []
    st.session_state.user_answers = []
    st.session_state.interview_complete = False


# Initialize session state variables
if 'current_question_index' not in st.session_state:
    reset_session_state()

def find_groq_api_key():
    """
    Search for the Groq API key in different sources:
    1. User-provided input in the Streamlit UI.
    2. .env file in the project directory.
    3. System environment variables (Linux/macOS: .bashrc/.zshrc, Windows: System Env).
    """
    
    # 1️⃣ Check user input in Streamlit UI
    api_key = st.text_input("Enter your Groq API Key:", type="password")
    if api_key:
        return api_key  # User input has the highest priority

    # 2️⃣ Check .env file and environment variables for different key names
    for key_name in POSSIBLE_API_KEYS:
        api_key = os.getenv(key_name) or os.environ.get(key_name)
        if api_key:
            return api_key

    # If no key is found
    return None

with st.sidebar:
    st.header("🔑 API Configuration")
    api_key = find_groq_api_key()

    if api_key:
        st.success("✅ API Key Found!")
    else:
        st.error("❌ No API Key Found! Please provide one in the UI, .env file, or system environment.")

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
    if not st.session_state.jd:
        st.error("Please enter a job description before rewriting the resume.")
    if not st.session_state.text: 
        st.error("Please upload a resume before rewriting it.")
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
        st.error("No suggestions available. Please ensure that you have provided the Job description and uploaded the resume before rewriting.")


class InterviewQuestion(BaseModel):
    question: str = Field(..., description="The text of the interview question.")
    category: Literal["technical", "behavioral", "situational"] = Field(
        ..., description="The category of the question."
    )
    difficulty: Literal["beginner", "intermediate", "advanced"] = Field(
        ..., description="The difficulty level of the question."
    )
    tech_stack: Optional[List[str]] = Field(
        None,
        description="The list of technologies or skills the question is related to.",
    )
    experience_level: Literal["entry-level", "mid-level", "senior"] = Field(
        ..., description="The required experience level for this question."
    )

class JobInterviewQuestions(BaseModel):
    role: str = Field(..., description="The job role for which questions are prepared.")
    tech_stack: List[str] = Field(
        ..., description="The technologies and tools required for the job role."
    )
    experience_level: Literal["entry-level", "mid-level", "senior"] = Field(
        ..., description="The experience level for the candidate."
    )
    questions: List[InterviewQuestion] = Field(
        ..., description="A list of interview questions tailored for the role."
    )

class EvaluationResponse(BaseModel):
    score: int = Field(..., description="The score for the given answer.")
    feedback: str = Field(..., description="Short feedback on the user's answer.")
    correct_answer: str = Field(..., description="The correct answer to the question.")

# Agent setup
search_agent = Agent(
    model=Groq(id="llama-3.1-8b-instant"),
    tools=[DuckDuckGo()],
    markdown=True,
    description="Retrieve and structure interview questions from the web.",
    
)

# Agent that uses JSON mode
pydantic_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    response_model=JobInterviewQuestions,
    markdown=True,
)

score_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True,
    description="Evaluate user answers and provide scores.",
    response_model=EvaluationResponse
)


# Title and job description input
st.markdown("### Interactive Interview Preparation")
st.write("Prepare for your interviews with tailored questions and feedback.")

if st.button("Prepare for Interview") and st.session_state.jd:
    with st.spinner('''Wait a minute :) preparing interview questions for you... '''):
        # Fetch and structure questions
        search_response: RunResponse = search_agent.run(
            f"Create a list of questions for the job role described below:\n{st.session_state.jd}"
        )

        structured_response: RunResponse = pydantic_agent.run(
            f"Structure the questions in the specified Pydantic model format:\n{search_response.content}"
        )

        st.session_state.questions = structured_response.content.questions
        st.success("Questions prepared successfully. Click 'Start Interview' to begin.")

if 'questions' in st.session_state:
    # Start interview

    if st.session_state.current_question_index < len(st.session_state.questions):
        # Display current question
        current_question = st.session_state.questions[st.session_state.current_question_index]
        st.markdown(f"### Question-{st.session_state.current_question_index + 1}:\n{current_question.question}")
        answer = st.text_area("Your Answer:", "")

        if st.button("Submit Answer"):
            st.session_state.user_answers.append(answer)

            # Evaluate answer
            eval_prompt = (
                f"Evaluate the following answer to the question and provide a score (0-10):\n\n"
                f"Question: {current_question.question}\n"
                f"Answer: {answer}\n"
                f"Provide the correct answer as well."
            )
            eval_response: RunResponse = score_agent.run(eval_prompt)

            # Extract score and feedback
            st.session_state.scores.append(eval_response.content.score)
            st.markdown(f"### Score: {eval_response.content.score}/10")
            st.markdown(f"### Feedback:\n{eval_response.content.feedback}")
            st.markdown(f"### Correct_answer:\n{eval_response.content.correct_answer}")
            st.session_state.show_next_question = True

        # Show "Next Question" button
        if st.session_state.get("show_next_question"):
            if st.button("Next Question"):
                st.session_state.current_question_index += 1
                st.session_state.show_next_question = False
                st.rerun()
    # Skip all functionality
    if st.button("Skip All Questions"):
        st.session_state.interview_complete = True

    if st.session_state.current_question_index >= len(st.session_state.questions):
        st.session_state.interview_complete = True


    # Display overall score at the end
    if st.session_state.interview_complete:
        total_score = sum(st.session_state.scores)
        st.markdown("## Interview Complete")
        st.markdown(f"Your Total Score: {total_score}/{len(st.session_state.questions) * 10}")

    if st.button("Reset Questions Score"):
        reset_session_state()
        st.rerun()

else:
    st.info("Enter a job description and click 'Prepare for Interview' to start.")